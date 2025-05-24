# PostgreSQL - Resource Owner

Created by: Mr Dk.

2025 / 05 / 24 15:49

Hangzhou, Zhejiang, China

---

## 背景

在数据库运行的过程中，需要动态获取各种资源，比如锁、buffer、快照、文件句柄等。为了防止这些资源未被按时归还，从而引发泄漏，需要一种可靠的机制来记录并追踪已经分配的资源：在应当释放资源的时机进行释放，或检查资源是否已被释放。由此可以避免有限的资源逐渐被泄漏完，引发数据库异常。

一类较为经典的易泄漏资源就是堆内存。PostgreSQL 由 C 语言实现，而堆内存管理一直是 C 语言中一个令人头疼的问题。在堆上动态分配内存后，开发者需要谨慎地留意指针的生命周期：把指向某段堆内存的指针传递赋值了几次后，可能就忘记这段内存是否需要被释放，是否已经被释放了。带来的问题是各种各样的 memory leak、double free、use after free。PostgreSQL 通过引入 [Memory Context](https://github.com/postgres/postgres/blob/master/src/backend/utils/mmgr/README) 对象解决这个问题。Memory Context 组织了一个树状的内存分配结构，在进入某个代码模块时，从当前的 Memory Context 对象中创建一个子对象，分配一大段内存，并记录到树中：该模块内的所有内存分配都从这个子对象中进行；当离开这个模块时，递归释放掉这个子对象的所有内存并把子对象从树中移除。这样，离开这个模块时就不必担心该模块存在堆内存泄漏。

类似地，各种数据库级别的对象也可以用这种方式管理起来。区别是这些对象的分配或释放方式各不相同，释放的时机也各不相同 (比如根据 2PL 协议，表锁需要在事务结束时才释放)。PostgreSQL 使用 Resource Owner 模块来统一追踪和管理这些资源：为一个事务创建一个 Resource Owner 对象，事务执行期间还可以创建更多子对象；在事务异常中止时，释放已经分配的所有资源；在事务正常提交时，检查是否存在残留资源未被释放。

PostgreSQL 17 对 Resource Owner 模块做了大幅重构，用通用化的设计统一追踪各类资源，解决了之前版本中与各类资源处理逻辑紧耦合的问题，提升了可扩展性。未来想要追踪新的资源类型将会更加容易：

```
commit b8bff07daa85c837a2747b4d35cd5a27e73fb7b2
Author: Heikki Linnakangas <heikki.linnakangas@iki.fi>
Date:   Wed Nov 8 13:30:50 2023 +0200

    Make ResourceOwners more easily extensible.

    Instead of having a separate array/hash for each resource kind, use a
    single array and hash to hold all kinds of resources. This makes it
    possible to introduce new resource "kinds" without having to modify
    the ResourceOwnerData struct. In particular, this makes it possible
    for extensions to register custom resource kinds.

    The old approach was to have a small array of resources of each kind,
    and if it fills up, switch to a hash table. The new approach also uses
    an array and a hash, but now the array and the hash are used at the
    same time. The array is used to hold the recently added resources, and
    when it fills up, they are moved to the hash. This keeps the access to
    recent entries fast, even when there are a lot of long-held resources.

    All the resource-specific ResourceOwnerEnlarge*(),
    ResourceOwnerRemember*(), and ResourceOwnerForget*() functions have
    been replaced with three generic functions that take resource kind as
    argument. For convenience, we still define resource-specific wrapper
    macros around the generic functions with the old names, but they are
    now defined in the source files that use those resource kinds.

    The release callback no longer needs to call ResourceOwnerForget on
    the resource being released. ResourceOwnerRelease unregisters the
    resource from the owner before calling the callback. That needed some
    changes in bufmgr.c and some other files, where releasing the
    resources previously always called ResourceOwnerForget.

    Each resource kind specifies a release priority, and
    ResourceOwnerReleaseAll releases the resources in priority order. To
    make that possible, we have to restrict what you can do between
    phases. After calling ResourceOwnerRelease(), you are no longer
    allowed to remember any more resources in it or to forget any
    previously remembered resources by calling ResourceOwnerForget.  There
    was one case where that was done previously. At subtransaction commit,
    AtEOSubXact_Inval() would handle the invalidation messages and call
    RelationFlushRelation(), which temporarily increased the reference
    count on the relation being flushed. We now switch to the parent
    subtransaction's resource owner before calling AtEOSubXact_Inval(), so
    that there is a valid ResourceOwner to temporarily hold that relcache
    reference.

    Other end-of-xact routines make similar calls to AtEOXact_Inval()
    between release phases, but I didn't see any regression test failures
    from those, so I'm not sure if they could reach a codepath that needs
    remembering extra resources.

    There were two exceptions to how the resource leak WARNINGs on commit
    were printed previously: llvmjit silently released the context without
    printing the warning, and a leaked buffer io triggered a PANIC. Now
    everything prints a WARNING, including those cases.

    Add tests in src/test/modules/test_resowner.

    Reviewed-by: Aleksander Alekseev, Michael Paquier, Julien Rouhaud
    Reviewed-by: Kyotaro Horiguchi, Hayato Kuroda, Álvaro Herrera, Zhihong Yu
    Reviewed-by: Peter Eisentraut, Andres Freund
    Discussion: https://www.postgresql.org/message-id/cbfabeb0-cd3c-e951-a572-19b365ed314d%40iki.fi
```

## 层次化管理结构

Resource Owner 对象的数据结构通过父级、同级、子级三个指针来记录层次关系：

```c
struct ResourceOwnerData
{
    ResourceOwner parent;       /* NULL if no parent (toplevel owner) */
    ResourceOwner firstchild;   /* head of linked list of children */
    ResourceOwner nextchild;    /* next child of same parent */
    const char *name;           /* name (just for debugging) */

    /* ... */
}

extern ResourceOwner ResourceOwnerCreate(ResourceOwner parent,
                                         const char *name);
extern void ResourceOwnerDelete(ResourceOwner owner);
```

使用 `ResourceOwnerCreate` 接口创建 Resource Owner 对象时，父级对象将会被记录到新对象的 `parent` 中，同时新对象也将父级对象原先的 `firstchild` 记录到自己的 `nextchild` 中，然后将自己记录为父级对象的 `firstchild`：

```c
/*
 * ResourceOwnerCreate
 *      Create an empty ResourceOwner.
 *
 * All ResourceOwner objects are kept in TopMemoryContext, since they should
 * only be freed explicitly.
 */
ResourceOwner
ResourceOwnerCreate(ResourceOwner parent, const char *name)
{
    ResourceOwner owner;

    owner = (ResourceOwner) MemoryContextAllocZero(TopMemoryContext,
                                                   sizeof(struct ResourceOwnerData));
    owner->name = name;

    if (parent)
    {
        owner->parent = parent;
        owner->nextchild = parent->firstchild;
        parent->firstchild = owner;
    }

    return owner;
}
```

后续对 Resource Owner 对象进行资源释放时，可以通过这几个指针递归释放所有子对象持有的资源。

## 资源动态追踪

有了 Resource Owner 对象后，通过下面的接口可以追踪资源：

- `ResourceOwnerRemember` 用于记录资源分配
- `ResourceOwnerForget` 用于在资源归还时移除记录
- `ResourceOwnerEnlarge` 用于在记录资源前确保 Resource Owner 的空间能够追踪这个资源

```c
extern void ResourceOwnerEnlarge(ResourceOwner owner);
extern void ResourceOwnerRemember(ResourceOwner owner, Datum value, const ResourceOwnerDesc *kind);
extern void ResourceOwnerForget(ResourceOwner owner, Datum value, const ResourceOwnerDesc *kind);
```

在 Resource Owner 内部通过一个定长数组 + [开放寻址](https://en.wikipedia.org/wiki/Open_addressing) 的哈希表来记录资源：

```c
/*
 * Size of the fixed-size array to hold most-recently remembered resources.
 */
#define RESOWNER_ARRAY_SIZE 32

/*
 * Initially allocated size of a ResourceOwner's hash table.  Must be power of
 * two because we use (capacity - 1) as mask for hashing.
 */
#define RESOWNER_HASH_INIT_SIZE 64

struct ResourceOwnerData
{
    /* ... */

    /*
     * Number of items in the locks cache, array, and hash table respectively.
     * (These are packed together to avoid padding in the struct.)
     */
    uint8       nlocks;         /* number of owned locks */
    uint8       narr;           /* how many items are stored in the array */
    uint32      nhash;          /* how many items are stored in the hash */

    /*
     * The fixed-size array for recent resources.
     *
     * If 'sorted' is set, the contents are sorted by release priority.
     */
    ResourceElem arr[RESOWNER_ARRAY_SIZE];

    /*
     * The hash table.  Uses open-addressing.  'nhash' is the number of items
     * present; if it would exceed 'grow_at', we enlarge it and re-hash.
     * 'grow_at' should be rather less than 'capacity' so that we don't waste
     * too much time searching for empty slots.
     *
     * If 'sorted' is set, the contents are no longer hashed, but sorted by
     * release priority.  The first 'nhash' elements are occupied, the rest
     * are empty.
     */
    ResourceElem *hash;
    uint32      capacity;       /* allocated length of hash[] */
    uint32      grow_at;        /* grow hash when reach this */

    /* The local locks cache. */
    LOCALLOCK  *locks[MAX_RESOWNER_LOCKS];  /* list of owned locks */
};
```

当需要记录资源时，先将资源放入定长数组中；如果数组满了，就将定长数组中的所有内容移入哈希表；当哈希表的容量达到阈值时还需要扩容哈希表。在查找资源时，需要搜索定长数组和哈希表。

设置一个定长数组的原因是，大部分资源使用的生命周期很短，因此可以在定长数组中快速地线性搜索资源并移除记录。

## 资源释放和泄漏检测

事务结束时，通过下面的函数确保资源释放：

```c
extern void ResourceOwnerRelease(ResourceOwner owner,
                                 ResourceReleasePhase phase,
                                 bool isCommit,
                                 bool isTopLevel);
```

具体地，分为两种情况：

- 事务提交：意味着资源分配和资源释放的代码都被完整执行了，此时 Resource Owner 对象内不应该残留未被释放的资源；如果有，则意味着内核代码有问题
- 事务中止：意味着代码执行到某个位置后发生异常，不再向下执行；此时已经分配并记录在 Resource Owner 对象中的资源需要被全部释放

此外，每类资源释放的阶段和优先级也有细微区别。有些资源分别需要在表锁被释放之前/之后释放，在同一个阶段释放的资源也有先后关系。所以每一类对象都需要注册自己的释放阶段、释放优先级，以及释放本类资源的回调函数；如果检测到资源泄漏，还可以注册一个打印泄漏资源信息的回调函数：

```c
/*
 * Resource releasing is done in three phases: pre-locks, locks, and
 * post-locks.  The pre-lock phase must release any resources that are visible
 * to other backends (such as pinned buffers); this ensures that when we
 * release a lock that another backend may be waiting on, it will see us as
 * being fully out of our transaction.  The post-lock phase should be used for
 * backend-internal cleanup.
 *
 * Within each phase, resources are released in priority order.  Priority is
 * just an integer specified in ResourceOwnerDesc.  The priorities of built-in
 * resource types are given below, extensions may use any priority relative to
 * those or RELEASE_PRIO_FIRST/LAST.  RELEASE_PRIO_FIRST is a fine choice if
 * your resource doesn't depend on any other resources.
 */
typedef enum
{
    RESOURCE_RELEASE_BEFORE_LOCKS = 1,
    RESOURCE_RELEASE_LOCKS,
    RESOURCE_RELEASE_AFTER_LOCKS,
} ResourceReleasePhase;

/*
 * In order to track an object, resowner.c needs a few callbacks for it.
 * The callbacks for resources of a specific kind are encapsulated in
 * ResourceOwnerDesc.
 *
 * Note that the callbacks occur post-commit or post-abort, so the callback
 * functions can only do noncritical cleanup and must not fail.
 */
typedef struct ResourceOwnerDesc
{
    const char *name;           /* name for the object kind, for debugging */

    /* when are these objects released? */
    ResourceReleasePhase release_phase;
    ResourceReleasePriority release_priority;

    /*
     * Release resource.
     *
     * This is called for each resource in the resource owner, in the order
     * specified by 'release_phase' and 'release_priority' when the whole
     * resource owner is been released or when ResourceOwnerReleaseAllOfKind()
     * is called.  The resource is implicitly removed from the owner, the
     * callback function doesn't need to call ResourceOwnerForget.
     */
    void        (*ReleaseResource) (Datum res);

    /*
     * Format a string describing the resource, for debugging purposes.  If a
     * resource has not been properly released before commit, this is used to
     * print a WARNING.
     *
     * This can be left to NULL, in which case a generic "[resource name]: %p"
     * format is used.
     */
    char       *(*DebugPrint) (Datum res);

} ResourceOwnerDesc;
```

### 示例：追踪文件句柄资源

以 **文件句柄** 这个资源为例。在文件句柄被打开和关闭时，分别使用 `ResourceOwnerRememberFile` 和 `ResourceOwnerForgetFile` 在 Resource Owner 对象中记录和移除文件句柄。如果事务异常中止，那么在释放掉表锁之后，通过注册的 `ResOwnerReleaseFile` 回调函数关闭文件句柄；如果事务提交时检测到文件句柄存在残留，则释放资源后通过 `ResOwnerPrintFile` 回调函数打印警告信息：

```c
static const ResourceOwnerDesc file_resowner_desc =
{
    .name = "File",
    .release_phase = RESOURCE_RELEASE_AFTER_LOCKS,
    .release_priority = RELEASE_PRIO_FILES,
    .ReleaseResource = ResOwnerReleaseFile,
    .DebugPrint = ResOwnerPrintFile
};

/* Convenience wrappers over ResourceOwnerRemember/Forget */
static inline void
ResourceOwnerRememberFile(ResourceOwner owner, File file)
{
    ResourceOwnerRemember(owner, Int32GetDatum(file), &file_resowner_desc);
}
static inline void
ResourceOwnerForgetFile(ResourceOwner owner, File file)
{
    ResourceOwnerForget(owner, Int32GetDatum(file), &file_resowner_desc);
}
```

### 资源释放顺序

由于 Resource Owner 对象需要按照资源注册的释放阶段和释放优先级进行按序释放，所以在事务结束前，或后台工作进程退出前，需要调用 `ResourceOwnerRelease` 三次，分别释放三个阶段中的所有资源。以事务中止为例：

```c
/*
 *  AbortTransaction
 */
static void
AbortTransaction(void)
{
    /* ... */

    /*
     * Post-abort cleanup.  See notes in CommitTransaction() concerning
     * ordering.  We can skip all of it if the transaction failed before
     * creating a resource owner.
     */
    if (TopTransactionResourceOwner != NULL)
    {
        /* ... */

        ResourceOwnerRelease(TopTransactionResourceOwner,
                             RESOURCE_RELEASE_BEFORE_LOCKS,
                             false, true);
        /* ... */
        ResourceOwnerRelease(TopTransactionResourceOwner,
                             RESOURCE_RELEASE_LOCKS,
                             false, true);
        ResourceOwnerRelease(TopTransactionResourceOwner,
                             RESOURCE_RELEASE_AFTER_LOCKS,
                             false, true);
        /* ... */
    }

    /*
     * State remains TRANS_ABORT until CleanupTransaction().
     */
    RESUME_INTERRUPTS();
}
```

因此，在 Resource Owner 对象开始做第一次释放之前，需要先对当前对象内记录的所有资源进行排序。具体的方式是将定长数组和哈希表中的资源全部汇聚到一起，然后按照释放阶段和释放优先级进行快速排序，并通过 `sorted` 字段标记当前对象内的所有资源已被排序，下一阶段的释放不再需要重复排序：

```c
static void
ResourceOwnerReleaseInternal(ResourceOwner owner,
                             ResourceReleasePhase phase,
                             bool isCommit,
                             bool isTopLevel)
{
    /* ... */

    /* Recurse to handle descendants */
    for (child = owner->firstchild; child != NULL; child = child->nextchild)
        ResourceOwnerReleaseInternal(child, phase, isCommit, isTopLevel);

    /* ... */
    if (!owner->sorted)
    {
        ResourceOwnerSort(owner);
        owner->sorted = true;
    }

    /* ... */
}

/*
 * Comparison function to sort by release phase and priority
 */
static int
resource_priority_cmp(const void *a, const void *b)
{
    const ResourceElem *ra = (const ResourceElem *) a;
    const ResourceElem *rb = (const ResourceElem *) b;

    /* Note: reverse order */
    if (ra->kind->release_phase == rb->kind->release_phase)
        return pg_cmp_u32(rb->kind->release_priority, ra->kind->release_priority);
    else if (ra->kind->release_phase > rb->kind->release_phase)
        return -1;
    else
        return 1;
}
```

## 完整示例：追踪 Buffer Pin 资源

在使用一个 Buffer Pool 中的 buffer 之前，需要先 pin 住这个 buffer，防止其它进程将这个 buffer 换出 Buffer Pool；在使用完毕后，应当及时 unpin，否则这个 buffer 将永远无法被换出 Buffer Pool。当 Buffer Pool 中全是这样的 buffer 时，其它数据页面将永远无法被访问了。因此，buffer pin 是一个需要被谨慎追踪的资源。

PostgreSQL 定义了对 buffer pin 资源的追踪函数：

```c
const ResourceOwnerDesc buffer_pin_resowner_desc =
{
    .name = "buffer pin",
    .release_phase = RESOURCE_RELEASE_BEFORE_LOCKS,
    .release_priority = RELEASE_PRIO_BUFFER_PINS,
    .ReleaseResource = ResOwnerReleaseBufferPin,
    .DebugPrint = ResOwnerPrintBufferPin
};

/* Convenience wrappers over ResourceOwnerRemember/Forget */
static inline void
ResourceOwnerRememberBuffer(ResourceOwner owner, Buffer buffer)
{
    ResourceOwnerRemember(owner, Int32GetDatum(buffer), &buffer_pin_resowner_desc);
}
static inline void
ResourceOwnerForgetBuffer(ResourceOwner owner, Buffer buffer)
{
    ResourceOwnerForget(owner, Int32GetDatum(buffer), &buffer_pin_resowner_desc);
}
```

这两个函数会分别在 pin / unpin buffer 时被调用：

```c
/*
 * PinBuffer -- make buffer unavailable for replacement.
 *
 * ...
 */
static bool
PinBuffer(BufferDesc *buf, BufferAccessStrategy strategy)
{
    /* ... */

    ref->refcount++;
    Assert(ref->refcount > 0);
    ResourceOwnerRememberBuffer(CurrentResourceOwner, b);
    return result;
}

/*
 * UnpinBuffer -- make buffer available for replacement.
 *
 * This should be applied only to shared buffers, never local ones.  This
 * always adjusts CurrentResourceOwner.
 */
static void
UnpinBuffer(BufferDesc *buf)
{
    Buffer      b = BufferDescriptorGetBuffer(buf);

    ResourceOwnerForgetBuffer(CurrentResourceOwner, b);
    UnpinBufferNoOwner(buf);
}
```

当 pin 住一个 buffer 后出现异常时，`UnpinBuffer` 就没有机会被执行了，那么其中的 `ResourceOwnerForgetBuffer` 也不会被执行，Resource Owner 对象中就残留了这个 buffer pin 资源。在后续由 Resource Owner 主导的资源释放过程中，buffer pin 资源注册的 `ResOwnerReleaseBufferPin` 函数将会被回调，从而释放这个 buffer pin 资源：

```c
static void
ResOwnerReleaseBufferPin(Datum res)
{
    Buffer      buffer = DatumGetInt32(res);

    /* Like ReleaseBuffer, but don't call ResourceOwnerForgetBuffer */
    if (!BufferIsValid(buffer))
        elog(ERROR, "bad buffer ID: %d", buffer);

    if (BufferIsLocal(buffer))
        UnpinLocalBufferNoOwner(buffer);
    else
        UnpinBufferNoOwner(GetBufferDescriptor(buffer - 1));
}
```

综上，不管事务运行过程中是否出现异常，buffer pin 资源都能够被释放，从而保证 Buffer Pool 的正确运转。

## 相关信息

- [Notes About Resource Owners](https://github.com/postgres/postgres/blob/master/src/backend/utils/resowner/README)

- [ResourceOwner refactoring](https://www.postgresql.org/message-id/flat/cbfabeb0-cd3c-e951-a572-19b365ed314d%40iki.fi)
