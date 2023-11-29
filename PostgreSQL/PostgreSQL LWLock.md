# PostgreSQL - LWLock

Created by: Mr Dk.

2023 / 11 / 29 16:40

Hangzhou, Zhejiang, China

---

## Background

PostgreSQL 中的轻量级锁 LWLock（Light Weight Lock）用于互斥访问共享内存中的数据结构。与 [原子操作](./PostgreSQL%20Atomics.md) 和 [自旋锁](./PostgreSQL%20Spinlock.md) 不同，LWLock 引入了读写访问模式，使其可以被不同进程共享访问或排它访问。实际上 LWLock 就是结合原子操作和自旋实现的，也引入了信号量。另外 LWLock 也支持对某个共享变量的值进行修改和监视，但应用场景相对较少。

本文基于 PostgreSQL `master` 分支（PostgreSQL 17 under dev）当前的 `HEAD` 版本分析原子操作的实现：

```
commit 15c9ac3629936a9bb5010155d3656e913027ccb7
Author: Thomas Munro <tmunro@postgresql.org>
Date:   Wed Nov 29 16:44:19 2023 +1300

    Optimize pg_readv/pg_pwritev single vector case.

    For the trivial case of iovcnt == 1, kernels are measurably slower at
    dealing with the more complex arguments of preadv/pwritev than the
    equivalent plain old pread/pwrite.  The overheads are worth it for
    iovcnt > 1, but for 1 let's just redirect to the cheaper calls.  While
    we could leave it to callers to worry about that, we already have to
    have our own pg_ wrappers for portability reasons so it seems
    reasonable to centralize this knowledge there (thanks to Heikki for this
    suggestion).  Try to avoid function call overheads by making them
    inlinable, which might also allow the compiler to avoid the branch in
    some cases.  For systems that don't have preadv and pwritev (currently:
    Windows and [closed] Solaris), we might as well pull the replacement
    functions up into the static inline functions too.

    Reviewed-by: Heikki Linnakangas <hlinnaka@iki.fi>
    Discussion: https://postgr.es/m/CA+hUKGJkOiOCa+mag4BF+zHo7qo=o9CFheB8=g6uT5TUm2gkvA@mail.gmail.com
```

## Data Structure And States

LWLock 的数据结构如下：

- `tranche`：每种 LWLock 预定义 id，每个 id 都对应一个锁名称
- `state`：32 位的原子变量，表示锁状态
- `waiters`：双向链表，链接了正在等待当前锁的进程 `PGPROC`

```c
/*
 * Code outside of lwlock.c should not manipulate the contents of this
 * structure directly, but we have to declare it here to allow LWLocks to be
 * incorporated into other data structures.
 */
typedef struct LWLock
{
    uint16      tranche;        /* tranche ID */
    pg_atomic_uint32 state;     /* state of exclusive/nonexclusive lockers */
    proclist_head waiters;      /* list of waiting PGPROCs */
#ifdef LOCK_DEBUG
    pg_atomic_uint32 nwaiters;  /* number of waiters */
    struct PGPROC *owner;       /* last exclusive owner of the lock */
#endif
} LWLock;
```

LWLock 的锁模式：

```c
typedef enum LWLockMode
{
    LW_EXCLUSIVE,
    LW_SHARED,
    LW_WAIT_UNTIL_FREE,         /* A special mode used in PGPROC->lwWaitMode,
                                 * when waiting for lock to become free. Not
                                 * to be used as LWLockAcquire argument */
} LWLockMode;
```

LWLock 的锁状态位：

- `LW_FLAG_HAS_WAITERS`：是否存在等待进程
- `LW_FLAG_RELEASE_OK`：在释放锁时立刻唤醒等待进程
- `LW_FLAG_LOCKED`：正在修改 LWLock 内的等待进程列表

```c
#define LW_FLAG_HAS_WAITERS         ((uint32) 1 << 30)
#define LW_FLAG_RELEASE_OK          ((uint32) 1 << 29)
#define LW_FLAG_LOCKED              ((uint32) 1 << 28)
```

## Operations

### Initialization

对 LWLock 初始化工作包含：赋值锁 id，将锁状态初始化为 0 并设置 `LW_FLAG_RELEASE_OK` 标志位，初始化锁的等待链表：

```c
/*
 * LWLockInitialize - initialize a new lwlock; it's initially unlocked
 */
void
LWLockInitialize(LWLock *lock, int tranche_id)
{
    pg_atomic_init_u32(&lock->state, LW_FLAG_RELEASE_OK);
#ifdef LOCK_DEBUG
    pg_atomic_init_u32(&lock->nwaiters, 0);
#endif
    lock->tranche = tranche_id;
    proclist_init(&lock->waiters);
}
```

### Lock Up

以指定的锁模式对 LWLock 上锁。虽然锁模式的定义中除了 `LW_EXCLUSIVE` / `LW_SHARED` 以外还有 `LW_WAIT_UNTIL_FREE`，但这里只允许以前两种模式作为参数上锁。这也是被其它模块使用得最多的函数。

首先，在开始操作共享内存之前需要先屏蔽中断，防止中断信号处理函数干扰。然后进入一个循环中：

1. 原子地试图获取一次锁，如果成功，那么返回
2. 原子地把进程自己的 `PGPROC` 结构原子地加入到锁的等待列表中
3. 再原子地试图获取一次锁，如果成功，那么把当前进程从等待列表中移除并返回
4. 阻塞在信号量上等待被唤醒，被唤醒后重试

获得锁以后，释放阻塞过程中锁住的所有信号量并返回。

```c
/*
 * LWLockAcquire - acquire a lightweight lock in the specified mode
 *
 * If the lock is not available, sleep until it is.  Returns true if the lock
 * was available immediately, false if we had to sleep.
 *
 * Side effect: cancel/die interrupts are held off until lock release.
 */
bool
LWLockAcquire(LWLock *lock, LWLockMode mode)
{
    PGPROC     *proc = MyProc;
    bool        result = true;
    int         extraWaits = 0;
#ifdef LWLOCK_STATS
    lwlock_stats *lwstats;

    lwstats = get_lwlock_stats_entry(lock);
#endif

    Assert(mode == LW_SHARED || mode == LW_EXCLUSIVE);

    PRINT_LWDEBUG("LWLockAcquire", lock, mode);

#ifdef LWLOCK_STATS
    /* Count lock acquisition attempts */
    if (mode == LW_EXCLUSIVE)
        lwstats->ex_acquire_count++;
    else
        lwstats->sh_acquire_count++;
#endif                          /* LWLOCK_STATS */

    /*
     * We can't wait if we haven't got a PGPROC.  This should only occur
     * during bootstrap or shared memory initialization.  Put an Assert here
     * to catch unsafe coding practices.
     */
    Assert(!(proc == NULL && IsUnderPostmaster));

    /* Ensure we will have room to remember the lock */
    if (num_held_lwlocks >= MAX_SIMUL_LWLOCKS)
        elog(ERROR, "too many LWLocks taken");

    /*
     * Lock out cancel/die interrupts until we exit the code section protected
     * by the LWLock.  This ensures that interrupts will not interfere with
     * manipulations of data structures in shared memory.
     */
    HOLD_INTERRUPTS();

    /*
     * Loop here to try to acquire lock after each time we are signaled by
     * LWLockRelease.
     *
     * NOTE: it might seem better to have LWLockRelease actually grant us the
     * lock, rather than retrying and possibly having to go back to sleep. But
     * in practice that is no good because it means a process swap for every
     * lock acquisition when two or more processes are contending for the same
     * lock.  Since LWLocks are normally used to protect not-very-long
     * sections of computation, a process needs to be able to acquire and
     * release the same lock many times during a single CPU time slice, even
     * in the presence of contention.  The efficiency of being able to do that
     * outweighs the inefficiency of sometimes wasting a process dispatch
     * cycle because the lock is not free when a released waiter finally gets
     * to run.  See pgsql-hackers archives for 29-Dec-01.
     */
    for (;;)
    {
        bool        mustwait;

        /*
         * Try to grab the lock the first time, we're not in the waitqueue
         * yet/anymore.
         */
        mustwait = LWLockAttemptLock(lock, mode);

        if (!mustwait)
        {
            LOG_LWDEBUG("LWLockAcquire", lock, "immediately acquired lock");
            break;              /* got the lock */
        }

        /*
         * Ok, at this point we couldn't grab the lock on the first try. We
         * cannot simply queue ourselves to the end of the list and wait to be
         * woken up because by now the lock could long have been released.
         * Instead add us to the queue and try to grab the lock again. If we
         * succeed we need to revert the queuing and be happy, otherwise we
         * recheck the lock. If we still couldn't grab it, we know that the
         * other locker will see our queue entries when releasing since they
         * existed before we checked for the lock.
         */

        /* add to the queue */
        LWLockQueueSelf(lock, mode);

        /* we're now guaranteed to be woken up if necessary */
        mustwait = LWLockAttemptLock(lock, mode);

        /* ok, grabbed the lock the second time round, need to undo queueing */
        if (!mustwait)
        {
            LOG_LWDEBUG("LWLockAcquire", lock, "acquired, undoing queue");

            LWLockDequeueSelf(lock);
            break;
        }

        /*
         * Wait until awakened.
         *
         * It is possible that we get awakened for a reason other than being
         * signaled by LWLockRelease.  If so, loop back and wait again.  Once
         * we've gotten the LWLock, re-increment the sema by the number of
         * additional signals received.
         */
        LOG_LWDEBUG("LWLockAcquire", lock, "waiting");

#ifdef LWLOCK_STATS
        lwstats->block_count++;
#endif

        LWLockReportWaitStart(lock);
        if (TRACE_POSTGRESQL_LWLOCK_WAIT_START_ENABLED())
            TRACE_POSTGRESQL_LWLOCK_WAIT_START(T_NAME(lock), mode);

        for (;;)
        {
            PGSemaphoreLock(proc->sem);
            if (proc->lwWaiting == LW_WS_NOT_WAITING)
                break;
            extraWaits++;
        }

        /* Retrying, allow LWLockRelease to release waiters again. */
        pg_atomic_fetch_or_u32(&lock->state, LW_FLAG_RELEASE_OK);

#ifdef LOCK_DEBUG
        {
            /* not waiting anymore */
            uint32      nwaiters PG_USED_FOR_ASSERTS_ONLY = pg_atomic_fetch_sub_u32(&lock->nwaiters, 1);

            Assert(nwaiters < MAX_BACKENDS);
        }
#endif

        if (TRACE_POSTGRESQL_LWLOCK_WAIT_DONE_ENABLED())
            TRACE_POSTGRESQL_LWLOCK_WAIT_DONE(T_NAME(lock), mode);
        LWLockReportWaitEnd();

        LOG_LWDEBUG("LWLockAcquire", lock, "awakened");

        /* Now loop back and try to acquire lock again. */
        result = false;
    }

    if (TRACE_POSTGRESQL_LWLOCK_ACQUIRE_ENABLED())
        TRACE_POSTGRESQL_LWLOCK_ACQUIRE(T_NAME(lock), mode);

    /* Add lock to list of locks held by this backend */
    held_lwlocks[num_held_lwlocks].lock = lock;
    held_lwlocks[num_held_lwlocks++].mode = mode;

    /*
     * Fix the process wait semaphore's count for any absorbed wakeups.
     */
    while (extraWaits-- > 0)
        PGSemaphoreUnlock(proc->sem);

    return result;
}
```

其中，原子地尝试上锁的逻辑是纯 CPU 操作：

1. 原子地读取共享内存中的锁状态
2. 根据锁状态和当前要上锁的模式决定能否上锁，如果可以的话，修改锁状态
3. 将修改后（也可能是没修改）的锁状态通过 CAS 交换到共享内存中的锁状态内存地址上
4. 如果没能成功 CAS，则回到 1 重新做；如果成功，则根据锁状态和模式返回是否需要重试加锁

```c
/*
 * Internal function that tries to atomically acquire the lwlock in the passed
 * in mode.
 *
 * This function will not block waiting for a lock to become free - that's the
 * callers job.
 *
 * Returns true if the lock isn't free and we need to wait.
 */
static bool
LWLockAttemptLock(LWLock *lock, LWLockMode mode)
{
    uint32      old_state;

    Assert(mode == LW_EXCLUSIVE || mode == LW_SHARED);

    /*
     * Read once outside the loop, later iterations will get the newer value
     * via compare & exchange.
     */
    old_state = pg_atomic_read_u32(&lock->state);

    /* loop until we've determined whether we could acquire the lock or not */
    while (true)
    {
        uint32      desired_state;
        bool        lock_free;

        desired_state = old_state;

        if (mode == LW_EXCLUSIVE)
        {
            lock_free = (old_state & LW_LOCK_MASK) == 0;
            if (lock_free)
                desired_state += LW_VAL_EXCLUSIVE;
        }
        else
        {
            lock_free = (old_state & LW_VAL_EXCLUSIVE) == 0;
            if (lock_free)
                desired_state += LW_VAL_SHARED;
        }

        /*
         * Attempt to swap in the state we are expecting. If we didn't see
         * lock to be free, that's just the old value. If we saw it as free,
         * we'll attempt to mark it acquired. The reason that we always swap
         * in the value is that this doubles as a memory barrier. We could try
         * to be smarter and only swap in values if we saw the lock as free,
         * but benchmark haven't shown it as beneficial so far.
         *
         * Retry if the value changed since we last looked at it.
         */
        if (pg_atomic_compare_exchange_u32(&lock->state,
                                           &old_state, desired_state))
        {
            if (lock_free)
            {
                /* Great! Got the lock. */
#ifdef LOCK_DEBUG
                if (mode == LW_EXCLUSIVE)
                    lock->owner = MyProc;
#endif
                return false;
            }
            else
                return true;    /* somebody else has the lock */
        }
    }
    pg_unreachable();
}
```

把当前进程加入到锁的等待列表中包含三个步骤：

1. 对等待队列加锁（原子操作 + 自旋）
2. 将当前进程加入到等待队列中
3. 对等待队列解锁（原子操作）

把当前进程从等待列表中移除的流程类似，不再赘述。

```c
/*
 * Add ourselves to the end of the queue.
 *
 * NB: Mode can be LW_WAIT_UNTIL_FREE here!
 */
static void
LWLockQueueSelf(LWLock *lock, LWLockMode mode)
{
    /*
     * If we don't have a PGPROC structure, there's no way to wait. This
     * should never occur, since MyProc should only be null during shared
     * memory initialization.
     */
    if (MyProc == NULL)
        elog(PANIC, "cannot wait without a PGPROC structure");

    if (MyProc->lwWaiting != LW_WS_NOT_WAITING)
        elog(PANIC, "queueing for lock while waiting on another one");

    LWLockWaitListLock(lock);

    /* setting the flag is protected by the spinlock */
    pg_atomic_fetch_or_u32(&lock->state, LW_FLAG_HAS_WAITERS);

    MyProc->lwWaiting = LW_WS_WAITING;
    MyProc->lwWaitMode = mode;

    /* LW_WAIT_UNTIL_FREE waiters are always at the front of the queue */
    if (mode == LW_WAIT_UNTIL_FREE)
        proclist_push_head(&lock->waiters, MyProc->pgprocno, lwWaitLink);
    else
        proclist_push_tail(&lock->waiters, MyProc->pgprocno, lwWaitLink);

    /* Can release the mutex now */
    LWLockWaitListUnlock(lock);

#ifdef LOCK_DEBUG
    pg_atomic_fetch_add_u32(&lock->nwaiters, 1);
#endif
}
```

对等待队列加锁的操作类似于自旋锁的实现，通过尝试、随机退避，将 `LW_FLAG_LOCKED` 设置到共享内存里的锁状态上：

```c
/*
 * Lock the LWLock's wait list against concurrent activity.
 *
 * NB: even though the wait list is locked, non-conflicting lock operations
 * may still happen concurrently.
 *
 * Time spent holding mutex should be short!
 */
static void
LWLockWaitListLock(LWLock *lock)
{
    uint32      old_state;
#ifdef LWLOCK_STATS
    lwlock_stats *lwstats;
    uint32      delays = 0;

    lwstats = get_lwlock_stats_entry(lock);
#endif

    while (true)
    {
        /* always try once to acquire lock directly */
        old_state = pg_atomic_fetch_or_u32(&lock->state, LW_FLAG_LOCKED);
        if (!(old_state & LW_FLAG_LOCKED))
            break;              /* got lock */

        /* and then spin without atomic operations until lock is released */
        {
            SpinDelayStatus delayStatus;

            init_local_spin_delay(&delayStatus);

            while (old_state & LW_FLAG_LOCKED)
            {
                perform_spin_delay(&delayStatus);
                old_state = pg_atomic_read_u32(&lock->state);
            }
#ifdef LWLOCK_STATS
            delays += delayStatus.delays;
#endif
            finish_spin_delay(&delayStatus);
        }

        /*
         * Retry. The lock might obviously already be re-acquired by the time
         * we're attempting to get it again.
         */
    }

#ifdef LWLOCK_STATS
    lwstats->spin_delay_count += delays;
#endif
}
```

对等待队列解锁相对来说简单些，原子地将 `LW_FLAG_LOCKED` 复位即可：

```c
/*
 * Unlock the LWLock's wait list.
 *
 * Note that it can be more efficient to manipulate flags and release the
 * locks in a single atomic operation.
 */
static void
LWLockWaitListUnlock(LWLock *lock)
{
    uint32      old_state PG_USED_FOR_ASSERTS_ONLY;

    old_state = pg_atomic_fetch_and_u32(&lock->state, ~LW_FLAG_LOCKED);

    Assert(old_state & LW_FLAG_LOCKED);
}
```

### Conditional Lock Up

`LWLockAcquire` 确保了返回时上锁一定是成功的；`LWLockConditionalAcquire` 只做尝试上锁这一步并返回结果，由调用者的代码来处理上锁成功或失败后的情况：

1. 屏蔽中断
2. 尝试上锁
3. 如果成功，直接返回；如果失败，恢复响应中断并返回

```c
/*
 * LWLockConditionalAcquire - acquire a lightweight lock in the specified mode
 *
 * If the lock is not available, return false with no side-effects.
 *
 * If successful, cancel/die interrupts are held off until lock release.
 */
bool
LWLockConditionalAcquire(LWLock *lock, LWLockMode mode)
{
    bool        mustwait;

    Assert(mode == LW_SHARED || mode == LW_EXCLUSIVE);

    PRINT_LWDEBUG("LWLockConditionalAcquire", lock, mode);

    /* Ensure we will have room to remember the lock */
    if (num_held_lwlocks >= MAX_SIMUL_LWLOCKS)
        elog(ERROR, "too many LWLocks taken");

    /*
     * Lock out cancel/die interrupts until we exit the code section protected
     * by the LWLock.  This ensures that interrupts will not interfere with
     * manipulations of data structures in shared memory.
     */
    HOLD_INTERRUPTS();

    /* Check for the lock */
    mustwait = LWLockAttemptLock(lock, mode);

    if (mustwait)
    {
        /* Failed to get lock, so release interrupt holdoff */
        RESUME_INTERRUPTS();

        LOG_LWDEBUG("LWLockConditionalAcquire", lock, "failed");
        if (TRACE_POSTGRESQL_LWLOCK_CONDACQUIRE_FAIL_ENABLED())
            TRACE_POSTGRESQL_LWLOCK_CONDACQUIRE_FAIL(T_NAME(lock), mode);
    }
    else
    {
        /* Add lock to list of locks held by this backend */
        held_lwlocks[num_held_lwlocks].lock = lock;
        held_lwlocks[num_held_lwlocks++].mode = mode;
        if (TRACE_POSTGRESQL_LWLOCK_CONDACQUIRE_ENABLED())
            TRACE_POSTGRESQL_LWLOCK_CONDACQUIRE(T_NAME(lock), mode);
    }
    return !mustwait;
}
```

### Lock Or Wait

实现思路和上述两种上锁方式差不多，只是语义上有区别。如果能够上锁成功，那么直接上锁并返回；如果无法上锁成功，那么等到能够上锁的时候才返回，但不上锁。区别在于将进程加入等待列表时，锁模式使用的是 `LW_WAIT_UNTIL_FREE`，并且当前进程的 `PGPROC` 将会被插入等待列表的队头而不是队尾。后续当锁可用时，这些进程将会被优先唤醒。

### Release

释放 LWLock 时：

1. 根据上锁时所使用的锁模式，原子地修改锁状态
2. 如果当前锁已经无人使用，而又有等待进程的话，唤醒所有能够获取该锁的进程
3. 恢复响应中断

```c
/*
 * LWLockRelease - release a previously acquired lock
 */
void
LWLockRelease(LWLock *lock)
{
    LWLockMode  mode;
    uint32      oldstate;
    bool        check_waiters;
    int         i;

    /*
     * Remove lock from list of locks held.  Usually, but not always, it will
     * be the latest-acquired lock; so search array backwards.
     */
    for (i = num_held_lwlocks; --i >= 0;)
        if (lock == held_lwlocks[i].lock)
            break;

    if (i < 0)
        elog(ERROR, "lock %s is not held", T_NAME(lock));

    mode = held_lwlocks[i].mode;

    num_held_lwlocks--;
    for (; i < num_held_lwlocks; i++)
        held_lwlocks[i] = held_lwlocks[i + 1];

    PRINT_LWDEBUG("LWLockRelease", lock, mode);

    /*
     * Release my hold on lock, after that it can immediately be acquired by
     * others, even if we still have to wakeup other waiters.
     */
    if (mode == LW_EXCLUSIVE)
        oldstate = pg_atomic_sub_fetch_u32(&lock->state, LW_VAL_EXCLUSIVE);
    else
        oldstate = pg_atomic_sub_fetch_u32(&lock->state, LW_VAL_SHARED);

    /* nobody else can have that kind of lock */
    Assert(!(oldstate & LW_VAL_EXCLUSIVE));

    if (TRACE_POSTGRESQL_LWLOCK_RELEASE_ENABLED())
        TRACE_POSTGRESQL_LWLOCK_RELEASE(T_NAME(lock));

    /*
     * We're still waiting for backends to get scheduled, don't wake them up
     * again.
     */
    if ((oldstate & (LW_FLAG_HAS_WAITERS | LW_FLAG_RELEASE_OK)) ==
        (LW_FLAG_HAS_WAITERS | LW_FLAG_RELEASE_OK) &&
        (oldstate & LW_LOCK_MASK) == 0)
        check_waiters = true;
    else
        check_waiters = false;

    /*
     * As waking up waiters requires the spinlock to be acquired, only do so
     * if necessary.
     */
    if (check_waiters)
    {
        /* XXX: remove before commit? */
        LOG_LWDEBUG("LWLockRelease", lock, "releasing waiters");
        LWLockWakeup(lock);
    }

    /*
     * Now okay to allow cancel/die interrupts.
     */
    RESUME_INTERRUPTS();
}
```

其中，唤醒所有能够获取该锁的进程的流程如下：

1. 由于需要操作锁的等待列表，所以通过原子操作 + 自旋对等待列表加锁
2. 遍历等待列表，将符合唤醒条件的进程从等待列表中移除，加入到唤醒列表中，并修改进程的等待状态为 `LW_WS_PENDING_WAKEUP`；如果当前已经准备唤醒一个想要独占锁的进程，就不再唤醒更多进程了
3. 通过 CAS 操作原子地修改锁的状态直至成功
4. 遍历唤醒列表，修改所有进程的等待状态为 `LW_WS_NOT_WAITING`，并释放信号量唤醒阻塞在信号量上的进程

```c
/*
 * Wakeup all the lockers that currently have a chance to acquire the lock.
 */
static void
LWLockWakeup(LWLock *lock)
{
    bool        new_release_ok;
    bool        wokeup_somebody = false;
    proclist_head wakeup;
    proclist_mutable_iter iter;

    proclist_init(&wakeup);

    new_release_ok = true;

    /* lock wait list while collecting backends to wake up */
    LWLockWaitListLock(lock);

    proclist_foreach_modify(iter, &lock->waiters, lwWaitLink)
    {
        PGPROC     *waiter = GetPGProcByNumber(iter.cur);

        if (wokeup_somebody && waiter->lwWaitMode == LW_EXCLUSIVE)
            continue;

        proclist_delete(&lock->waiters, iter.cur, lwWaitLink);
        proclist_push_tail(&wakeup, iter.cur, lwWaitLink);

        if (waiter->lwWaitMode != LW_WAIT_UNTIL_FREE)
        {
            /*
             * Prevent additional wakeups until retryer gets to run. Backends
             * that are just waiting for the lock to become free don't retry
             * automatically.
             */
            new_release_ok = false;

            /*
             * Don't wakeup (further) exclusive locks.
             */
            wokeup_somebody = true;
        }

        /*
         * Signal that the process isn't on the wait list anymore. This allows
         * LWLockDequeueSelf() to remove itself of the waitlist with a
         * proclist_delete(), rather than having to check if it has been
         * removed from the list.
         */
        Assert(waiter->lwWaiting == LW_WS_WAITING);
        waiter->lwWaiting = LW_WS_PENDING_WAKEUP;

        /*
         * Once we've woken up an exclusive lock, there's no point in waking
         * up anybody else.
         */
        if (waiter->lwWaitMode == LW_EXCLUSIVE)
            break;
    }

    Assert(proclist_is_empty(&wakeup) || pg_atomic_read_u32(&lock->state) & LW_FLAG_HAS_WAITERS);

    /* unset required flags, and release lock, in one fell swoop */
    {
        uint32      old_state;
        uint32      desired_state;

        old_state = pg_atomic_read_u32(&lock->state);
        while (true)
        {
            desired_state = old_state;

            /* compute desired flags */

            if (new_release_ok)
                desired_state |= LW_FLAG_RELEASE_OK;
            else
                desired_state &= ~LW_FLAG_RELEASE_OK;

            if (proclist_is_empty(&wakeup))
                desired_state &= ~LW_FLAG_HAS_WAITERS;

            desired_state &= ~LW_FLAG_LOCKED;   /* release lock */

            if (pg_atomic_compare_exchange_u32(&lock->state, &old_state,
                                               desired_state))
                break;
        }
    }

    /* Awaken any waiters I removed from the queue. */
    proclist_foreach_modify(iter, &wakeup, lwWaitLink)
    {
        PGPROC     *waiter = GetPGProcByNumber(iter.cur);

        LOG_LWDEBUG("LWLockRelease", lock, "release waiter");
        proclist_delete(&wakeup, iter.cur, lwWaitLink);

        /*
         * Guarantee that lwWaiting being unset only becomes visible once the
         * unlink from the link has completed. Otherwise the target backend
         * could be woken up for other reason and enqueue for a new lock - if
         * that happens before the list unlink happens, the list would end up
         * being corrupted.
         *
         * The barrier pairs with the LWLockWaitListLock() when enqueuing for
         * another lock.
         */
        pg_write_barrier();
        waiter->lwWaiting = LW_WS_NOT_WAITING;
        PGSemaphoreUnlock(waiter->sem);
    }
}
```
