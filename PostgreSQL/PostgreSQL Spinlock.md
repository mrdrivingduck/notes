# PostgreSQL - Spinlock

Created by: Mr Dk.

2023 / 10 / 04 15:44

Ningbo, Zhejiang, China

---

## Background

在各类基础软件和编程语言中，[自旋锁（Spinlock）](https://en.wikipedia.org/wiki/Spinlock)是一个常用的组件。自旋锁的基础语义是 **忙等**：当进程/线程在获取该锁时，如果发现锁正被占用，那么将会循环测试锁是否已经可用，直到成功获取锁，CPU 在这段时间内没有做任何有意义的工作；而不是让出 CPU，引发上下文切换，使 CPU 能够执行其它进程/线程。

从语义出发，自旋锁适用于等待获取锁的自旋开销低于进程调度和上下文切换的场景中。基于自旋锁的使用场景，一方面需要软件设计者谨慎评估在自己设计的软件中对这把锁的争抢程度和持有时间是否乐观，理论上不应让等待自旋锁可用的空转开销超过进程调度和上下文切换的开销，锁持有时间也不宜过久；另一方面，需要基于 CPU 架构选择最为高效的自旋锁实现方式，这通常需要使用到由硬件支持的机器指令。

PostgreSQL 中也有自旋锁基础设施，供内核代码的各模块使用。自旋锁在实现上是否合理高效直接影响到 PostgreSQL 的整体性能。PostgreSQL 的自旋锁代码分为 CPU 架构无关（位于 `spin.c` / `spin.h`）和 CPU 架构相关（位于 `s_lock.c` / `s_lock.h`）两部分。与 CPU 架构无关的代码是较上层的抽象，保证自旋锁代码的跨平台统一性和可移植性；与 CPU 架构相关的代码则是具体 ISA 的内联汇编指令，保证自旋锁的高效性。

本文基于 PostgreSQL `master` 分支（PostgreSQL 17 under devel）当前的 `HEAD` 版本分析自旋锁的实现，特别是在 [x86_64](https://en.wikipedia.org/wiki/X86-64) 和 [AArch64](https://en.wikipedia.org/wiki/AArch64) 两种常见服务器 CPU 架构上的实现：

```
commit b1a8dc846da4d96d903dcb5733f68a1e02d82a23
Author: Andres Freund <andres@anarazel.de>
Date:   Sat Sep 30 12:10:15 2023 -0700

    meson: macos: Correct -exported_symbols_list syntax for Sonoma compat

    -exported_symbols_list=... works on Ventura and earlier, but not on
    Sonoma. The easiest way to fix it is to -Wl,-exported_symbols_list,@0@ which
    actually seems more appropriate anyway, it's obviously a linker argument. It
    is easier to use the -Wl,, syntax than passing multiple arguments, due to the
    way the export_fmt is used (a single string that's formatted), but if it turns
    out to be necessary, we can go for multiple arguments as well.

    Reviewed-by: Tom Lane <tgl@sss.pgh.pa.us>
    Discussion: https://postgr.es/m/20230928222248.jw6s7yktpfsfczha@alap3.anarazel.de
    Backpatch: 16-, where the meson based buildsystem was added
```

## API Level

### Hardware Independent API

PostgreSQL 提供了以下自旋锁 API 供内核其它模块使用。这些 API 是 CPU 架构无关的，其语义分别为：

- `SpinLockInit`：初始化自旋锁到未锁定的状态
- `SpinLockAcquire`：获取自旋锁，如果发生锁冲突则等待；如果在一定时间内（约一分钟）还是无法获取锁，那么使程序 `abort()`
- `SpinLockRelease`：释放之前已经获取到的自旋锁
- `SpinLockFree`：测试当前锁状态是否可用，不改变锁的状态

```c
void SpinLockInit(volatile slock_t *lock);
void SpinLockAcquire(volatile slock_t *lock);
void SpinLockRelease(volatile slock_t *lock);
bool SpinLockFree(slock_t *lock);
```

这些 API 以宏定义的形式实现：

```c
#define SpinLockInit(lock)  S_INIT_LOCK(lock)
#define SpinLockAcquire(lock) S_LOCK(lock)
#define SpinLockRelease(lock) S_UNLOCK(lock)
#define SpinLockFree(lock)  S_LOCK_FREE(lock)
```

### Hardware Dependent API

上述宏定义由更底层与 CPU 架构相关的 API 实现。每种 CPU 架构都需要分别实现以下五个 API，前四个 API 的语义如前所述一致，`SPIN_DELAY` 的语义为：在自旋锁等待循环中的延时操作。这意味着 PostgreSQL 的自旋锁并不会一直傻了吧唧地自旋。

```c
void S_INIT_LOCK(slock_t *lock);
int S_LOCK(slock_t *lock);
void S_UNLOCK(slock_t *lock);
bool S_LOCK_FREE(slock_t *lock);
void SPIN_DELAY(void);
```

这些 API 本身需要确保编译器不会把获取锁、访问临界区、释放锁三个步骤进行指令重排序。

函数参数中的 `slock_t` 数据类型也需要根据具体的 CPU 架构而被分别重定义，这意味着在每种 CPU 架构上自旋锁的数据类型可能是不一样的。

### Test And Set API

在上述五个 API 中，`S_LOCK` 是执行频率最高、执行时间最长的，因此最需要通过硬件来进行高效实现。绝大部分 CPU 架构都提供了 TAS（Test And Set）硬件指令，所以 PostgreSQL 又抽象出了一层 API 用于实现 `S_LOCK`，其语义分别为：

- `TAS`：原子地获取锁，立刻返回；返回 0 表示成功，返回非 0 表示失败
- `TAS_SPIN`：原子地获取锁，默认情况下与 `TAS` 相同，但被用于等待之前已经发生争用的锁

```c
int TAS(slock_t *lock);
int TAS_SPIN(slock_t *lock);
```

`S_LOCK` 具体如何使用 `TAS` 和 `TAS_SPIN` 因具体的 CPU 架构而异。在部分 CPU 架构上，先轮询锁的可用性，仅当锁空闲时再重试加锁，会有更好的性能。

## Default Implementation

对于上述七个与 CPU 架构相关的 API，PostgreSQL 分别提供了一种默认实现。如果某种 CPU 架构在默认实现中就可以正确且高效地运转，那么就不需再做任何适配；否则，可以为某种特定的 CPU 架构重写相应的 API，覆盖默认的实现。

### Lock Initialization

初始化锁的默认实现复用了释放锁操作的默认实现，因为两者都是将自旋锁恢复到默认的未锁定状态：

```c
#if !defined(S_INIT_LOCK)
#define S_INIT_LOCK(lock)   S_UNLOCK(lock)
#endif   /* S_INIT_LOCK */
```

### Lock Acquire

加锁操作 `S_LOCK` 的默认实现是通过 `TAS` 宏判断锁的可用性，如果可用，则调用与 CPU 架构无关的 `s_lock()` 函数试图加锁，否则直接返回失败：

```c
/*
 * Default Definitions - override these above as needed.
 */

#if !defined(S_LOCK)
#define S_LOCK(lock) \
    (TAS(lock) ? s_lock((lock), __FILE__, __LINE__, __func__) : 0)
#endif   /* S_LOCK */

/*
 * Platform-independent out-of-line support routines
 */
extern int s_lock(volatile slock_t *lock, const char *file, int line, const char *func);
```

`s_lock()` 会循环使用 `TAS_SPIN` 宏试图获取锁，如果锁获取失败，则会进行延时等待：

```c
/*
 * s_lock(lock) - platform-independent portion of waiting for a spinlock.
 */
int
s_lock(volatile slock_t *lock, const char *file, int line, const char *func)
{
    SpinDelayStatus delayStatus;

    init_spin_delay(&delayStatus, file, line, func);

    while (TAS_SPIN(lock))
    {
        perform_spin_delay(&delayStatus);
    }

    finish_spin_delay(&delayStatus);

    return delayStatus.delays;
}
```

具体的延时等待策略是什么呢？首先通过 `SPIN_DELAY` 宏进行硬件层面的延时，然后统计目前已经自旋的次数：如果自旋次数达到一定阈值时，就需要从 1ms 开始调用 `pg_usleep` 使进程开始睡眠，并逐渐随机延长睡眠时间；当睡眠时间超过 1s 时，又重新回到 1ms；当自旋次数超过更大的阈值时，直接 PANIC 退出。

```c
#define MIN_SPINS_PER_DELAY 10
#define MAX_SPINS_PER_DELAY 1000
#define NUM_DELAYS          1000
#define MIN_DELAY_USEC      1000L
#define MAX_DELAY_USEC      1000000L

/*
 * Wait while spinning on a contended spinlock.
 */
void
perform_spin_delay(SpinDelayStatus *status)
{
    /* CPU-specific delay each time through the loop */
    SPIN_DELAY();

    /* Block the process every spins_per_delay tries */
    if (++(status->spins) >= spins_per_delay)
    {
        if (++(status->delays) > NUM_DELAYS)
            s_lock_stuck(status->file, status->line, status->func);

        if (status->cur_delay == 0) /* first time to delay? */
            status->cur_delay = MIN_DELAY_USEC;

        /*
         * Once we start sleeping, the overhead of reporting a wait event is
         * justified. Actively spinning easily stands out in profilers, but
         * sleeping with an exponential backoff is harder to spot...
         *
         * We might want to report something more granular at some point, but
         * this is better than nothing.
         */
        pgstat_report_wait_start(WAIT_EVENT_SPIN_DELAY);
        pg_usleep(status->cur_delay);
        pgstat_report_wait_end();

#if defined(S_LOCK_TEST)
        fprintf(stdout, "*");
        fflush(stdout);
#endif

        /* increase delay by a random fraction between 1X and 2X */
        status->cur_delay += (int) (status->cur_delay *
                                    pg_prng_double(&pg_global_prng_state) + 0.5);
        /* wrap back to minimum delay when max is exceeded */
        if (status->cur_delay > MAX_DELAY_USEC)
            status->cur_delay = MIN_DELAY_USEC;

        status->spins = 0;
    }
}
```

### Check Lock Free

判断锁可用性操作的默认实现是直接判断锁变量是否为 `0`：

```c
#if !defined(S_LOCK_FREE)
#define S_LOCK_FREE(lock)   (*(lock) == 0)
#endif   /* S_LOCK_FREE */
```

### Lock Release

释放锁操作的默认实现是直接把锁变量清零：

```c
#if !defined(S_UNLOCK)
/*
 * Our default implementation of S_UNLOCK is essentially *(lock) = 0.  This
 * is unsafe if the platform can reorder a memory access (either load or
 * store) after a following store; platforms where this is possible must
 * define their own S_UNLOCK.  But CPU reordering is not the only concern:
 * if we simply defined S_UNLOCK() as an inline macro, the compiler might
 * reorder instructions from inside the critical section to occur after the
 * lock release.  Since the compiler probably can't know what the external
 * function s_unlock is doing, putting the same logic there should be adequate.
 * A sufficiently-smart globally optimizing compiler could break that
 * assumption, though, and the cost of a function call for every spinlock
 * release may hurt performance significantly, so we use this implementation
 * only for platforms where we don't know of a suitable intrinsic.  For the
 * most part, those are relatively obscure platform/compiler combinations to
 * which the PostgreSQL project does not have access.
 */
#define USE_DEFAULT_S_UNLOCK
extern void s_unlock(volatile slock_t *lock);
#define S_UNLOCK(lock)      s_unlock(lock)
#endif   /* S_UNLOCK */

#ifdef USE_DEFAULT_S_UNLOCK
void
s_unlock(volatile slock_t *lock)
{
#ifdef TAS_ACTIVE_WORD
    /* HP's PA-RISC */
    *TAS_ACTIVE_WORD(lock) = -1;
#else
    *lock = 0;
#endif
}
#endif
```

### Spin Delay

CPU 层面延时自旋的默认实现为空：

```c
#if !defined(SPIN_DELAY)
#define SPIN_DELAY()    ((void) 0)
#endif   /* SPIN_DELAY */
```

### Test And Set

对支持 TAS 硬件指令的 CPU 架构，`TAS` 默认将会使用相应的硬件内联汇编指令实现的 `tas()` 函数：

```c
#if !defined(TAS)
extern int  tas(volatile slock_t *lock);        /* in port/.../tas.s, or
                                                 * s_lock.c */

#define TAS(lock)       tas(lock)
#endif   /* TAS */
```

`TAS_SPIN` 的默认实现与 `TAS` 相同：

```c
#if !defined(TAS_SPIN)
#define TAS_SPIN(lock)  TAS(lock)
#endif   /* TAS_SPIN */
```

## Implementations

### Semaphores

对于不支持任何 TAS 指令的 CPU 架构，PostgreSQL 提供了使用信号量模拟的纯软件实现。这是一个纯后备的实现，因为软件实现的性能是极差的，而且现实生活中几乎找不到不支持 TAS 指令的 CPU。但分析这种后备实现有助于在不看汇编的前提下理解上述机制。信号量实现版本的宏定义如下，其中：

- `slock_t` 类型被定义为 `int`
- `S_INIT_LOCK` 被重写为信号量初始化函数 `s_init_lock_sema`
- `TAS` 被重写为试图获取信号量的函数 `tas_sema`
- `S_UNLOCK` 被重写为释放信号量的函数 `s_unlock_sema`

```c
/*
 * Fake spinlock implementation using semaphores --- slow and prone
 * to fall foul of kernel limits on number of semaphores, so don't use this
 * unless you must!  The subroutines appear in spin.c.
 */
typedef int slock_t;

extern bool s_lock_free_sema(volatile slock_t *lock);
extern void s_unlock_sema(volatile slock_t *lock);
extern void s_init_lock_sema(volatile slock_t *lock, bool nested);
extern int  tas_sema(volatile slock_t *lock);

#define S_LOCK_FREE(lock)   s_lock_free_sema(lock)
#define S_UNLOCK(lock)   s_unlock_sema(lock)
#define S_INIT_LOCK(lock)   s_init_lock_sema(lock, false)
#define TAS(lock)   tas_sema(lock)
```

根据前文所述的默认实现，由于信号量不存在硬件级别的延时操作，所以 `SPIN_DELAY` 宏展开以后将会为空；`TAS_SPIN` 与 `TAS` 完全相同；`S_LOCK` 被默认展开为：

```c
#if !defined(S_LOCK)
#define S_LOCK(lock) \
    (TAS(lock) ? s_lock((lock), __FILE__, __LINE__, __func__) : 0)
#endif   /* S_LOCK */
```

### x86_64

在 x86_64 架构下，`slock_t` 被定义为 `unsigned char` 单字节变量，`TAS` 操作可以通过硬件进行更加高效的实现：通过 `LOCK` 指令锁定北桥信号（现在似乎已经是锁定缓存了），再通过 `XCHGB` 指令原子地将 `1` 试图设置到这个单字节锁变量中。

`TAS_SPIN` 被重写为首先对锁变量进行判断，仅当锁变量未被占用时才会试图通过 `TAS` 持有锁。

`SPIN_DELAY` 被重写为 `rep; nop`，这两条指令与 `PAUSE` 指令等价，但可以用于更多不支持 `PAUSE` 指令的 CPU。根据 Intel 的指令集规范，建议在自旋等待循环中加入延时指令，作为对处理器的提示以提升性能：

> Improves the performance of spin-wait loops. When executing a “spin-wait loop,” a Pentium 4 or Intel Xeon processor suffers a severe performance penalty when exiting the loop because it detects a possible memory order violation. The PAUSE instruction provides a hint to the processor that the code sequence is a spin-wait loop. The processor uses this hint to avoid the memory order violation in most situations, which greatly improves processor performance. For this reason, it is recommended that a PAUSE instruction be placed in all spin-wait loops.

```c
#ifdef __x86_64__       /* AMD Opteron, Intel EM64T */
#define HAS_TEST_AND_SET

typedef unsigned char slock_t;

#define TAS(lock) tas(lock)

/*
 * On Intel EM64T, it's a win to use a non-locking test before the xchg proper,
 * but only when spinning.
 *
 * See also Implementing Scalable Atomic Locks for Multi-Core Intel(tm) EM64T
 * and IA32, by Michael Chynoweth and Mary R. Lee. As of this writing, it is
 * available at:
 * http://software.intel.com/en-us/articles/implementing-scalable-atomic-locks-for-multi-core-intel-em64t-and-ia32-architectures
 */
#define TAS_SPIN(lock)    (*(lock) ? 1 : TAS(lock))

static __inline__ int
tas(volatile slock_t *lock)
{
    slock_t     _res = 1;

    __asm__ __volatile__(
        "   lock            \n"
        "   xchgb   %0,%1   \n"
:       "+q"(_res), "+m"(*lock)
:       /* no inputs */
:       "memory", "cc");
    return (int) _res;
}

#define SPIN_DELAY() spin_delay()

static __inline__ void
spin_delay(void)
{
    /*
     * Adding a PAUSE in the spin delay loop is demonstrably a no-op on
     * Opteron, but it may be of some use on EM64T, so we keep it.
     */
    __asm__ __volatile__(
        " rep; nop          \n");
}

#endif   /* __x86_64__ */
```

### AArch64

在 ARM 架构下，`slock_t` 数据类型被定义为 `int`。`TAS` 宏被重写为使用 [GNU 内置函数](https://gcc.gnu.org/onlinedocs/gcc-4.1.2/gcc/Atomic-Builtins.html) `__sync_lock_test_and_set` 来获取锁；相对应地，释放锁的 `S_UNLOCK` 宏也需要被重写为相应的 `__sync_lock_release`。根据 ARM 官方给出的编译器迁移和兼容性指南，在内联汇编中使用 `LDREX` / `STREX`（Load/Store Exclusive）来实现 TAS 已经过时，应当使用 GNU 内置提供的 `__sync*` 函数族。

另外，来自 AWS 团队的工程师发现在多核 ARM64 处理器（显然他用的应该是 [Graviton2](https://en.wikipedia.org/wiki/AWS_Graviton)）自旋等待时使用 `ISB` 指令作为延时在高并发场景中有性能提升，因此从 [PostgreSQL 15](https://www.postgresql.org/message-id/flat/78338F29-9D7F-4DC8-BD71-E9674CE71425%40amazon.com) 开始，AArch64 架构下的 `SPIN_DELAY` 被重写为使用 `ISB` 内联汇编。虽然 ARM 架构下也提供了功能类似的 `YIELD` 指令，但 `ISB` 所占用的时间及节省的功耗使其成为对标 x86_64 架构下 `PAUSE` 指令的最佳选择：

> On arm64 we have seen on several databases that ISB (instruction synchronization barrier) is better to use than yield in a spin loop. The yield instruction is a nop. The isb instruction puts the processor to sleep for some short time. isb is a good equivalent to the pause instruction on x86.
>
> ISB SY doesn't stall for long, just saves a bit of power vs. spamming loads in a tight loop.

```c
/*
 * On ARM and ARM64, we use __sync_lock_test_and_set(int *, int) if available.
 *
 * We use the int-width variant of the builtin because it works on more chips
 * than other widths.
 */
#if defined(__arm__) || defined(__arm) || defined(__aarch64__)
#ifdef HAVE_GCC__SYNC_INT32_TAS
#define HAS_TEST_AND_SET

#define TAS(lock) tas(lock)

typedef int slock_t;

static __inline__ int
tas(volatile slock_t *lock)
{
    return __sync_lock_test_and_set(lock, 1);
}

#define S_UNLOCK(lock) __sync_lock_release(lock)

/*
 * Using an ISB instruction to delay in spinlock loops appears beneficial on
 * high-core-count ARM64 processors.  It seems mostly a wash for smaller gear,
 * and ISB doesn't exist at all on pre-v7 ARM chips.
 */
#if defined(__aarch64__)

#define SPIN_DELAY() spin_delay()

static __inline__ void
spin_delay(void)
{
    __asm__ __volatile__(
        " isb;              \n");
}

#endif   /* __aarch64__ */
#endif   /* HAVE_GCC__SYNC_INT32_TAS */
#endif   /* __arm__ || __arm || __aarch64__ */
```

## References

[stackoverflow - What does "rep; nop;" mean in x86 assembly? Is it the same as the "pause" instruction?](https://stackoverflow.com/questions/7086220/what-does-rep-nop-mean-in-x86-assembly-is-it-the-same-as-the-pause-instru)

[GCC - Built-in functions for atomic memory access](https://gcc.gnu.org/onlinedocs/gcc-4.1.2/gcc/Atomic-Builtins.html)

[PostgreSQL - Add spin_delay() implementation for Arm in s_lock.h](https://www.postgresql.org/message-id/flat/78338F29-9D7F-4DC8-BD71-E9674CE71425%40amazon.com)

[stackoverflow - Why does hint::spin_loop use ISB on aarch64?](https://stackoverflow.com/questions/70810121/why-does-hintspin-loop-use-isb-on-aarch64)

[关于原子操作和弱内存序](https://kunpengcompute.github.io/2020/09/20/guan-yu-yuan-zi-cao-zuo-he-ruo-nei-cun-xu/)
