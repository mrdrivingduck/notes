# PostgreSQL - VFD

Created by : Mr Dk.

2022 / 08 / 08 0:27

Hangzhou, Zhejiang, China

---

## Background

PostgreSQL 后端进程经常需要打开大量的文件，包括表文件、索引文件、临时文件（用于排序或构造 hash 表）等。由于操作系统允许一个进程能够打开的文件数量是有上限的，为了防止后端进程打开文件时因超出 OS 的限制而失败，PostgreSQL 提供了 **虚拟文件描述符 (VFD)** 机制。VFD 抽象层能够对使用 VFD API 的代码屏蔽对 OS 文件描述符的管理细节，使更高层的代码能够打开比 OS 限制的数量更多的文件。

本文对 PostgreSQL 内核代码的分析截止主干开发分支 `master` 上的如下版本号：

```
commit afe58c8b746cac1e2c3e9f0fc96a0f69a46c84d3
Author: Alvaro Herrera <alvherre@alvh.no-ip.org>
Date:   Sun Aug 7 10:19:40 2022 +0200

    Remove unportable use of timezone in recent test

    Per buildfarm member snapper

    Discussion: https://postgr.es/m/129951.1659812518@sss.pgh.pa.us

```

## Design

VFD 机制最核心的设计，就是使用一个 LRU (Least-Recently-Used) 缓存池来管理当前进程所有的 **操作系统文件描述符**，同时对更上层的代码暴露出 **虚拟文件描述符 (Virtual File Descriptor)** 供使用。理想情况下，除了 VFD 的内部实现，其它部分内核代码不应该直接调用 C 库函数去操作文件。当 PostgreSQL 后端进程需要打开一个文件，且此时进程已经打开的文件数量将要超过 OS 允许的最大数量时，VFD 从其管理的 OS 文件描述符中选出最近最久未被使用的文件描述符并关闭它，此时打开这个文件就不会被 OS 拒绝。这个过程对使用 VFD API 的更高层代码来说是无感知的，仿佛可以不受数量限制地打开文件一样。

## Virtual File Descriptor

PostgreSQL 中，所有的 VFD 在物理上被组织成一个数组。`VfdCache` 是指向这个数组起始位置的指针，`SizeVfdCache` 保存这个数组的长度。这个数组的长度会随着对 VFD 需求量的增加而动态扩容。

`nfile` 变量记录了 VFD 数组中到底管理了多少个操作系统的文件描述符，这样 VFD 机制才能在打开的文件数量即将超出 OS 限制时，关闭最近最久未被使用的文件描述符。

```c
/*
 * Virtual File Descriptor array pointer and size.  This grows as
 * needed.  'File' values are indexes into this array.
 * Note that VfdCache[0] is not a usable VFD, just a list header.
 */
static Vfd *VfdCache;
static Size SizeVfdCache = 0;

/*
 * Number of file descriptors known to be in use by VFD entries.
 */
static int  nfile = 0;
```

虚拟文件描述符的结构定义如下：

```c
typedef struct vfd
{
    int         fd;             /* current FD, or VFD_CLOSED if none */
    unsigned short fdstate;     /* bitflags for VFD's state */
    ResourceOwner resowner;     /* owner, for automatic cleanup */
    File        nextFree;       /* link to next free VFD, if in freelist */
    File        lruMoreRecently;    /* doubly linked recency-of-use list */
    File        lruLessRecently;
    off_t       fileSize;       /* current size of file (0 if not temporary) */
    char       *fileName;       /* name of file, or NULL for unused VFD */
    /* NB: fileName is malloc'd, and must be free'd when closing the VFD */
    int         fileFlags;      /* open(2) flags for (re)opening the file */
    mode_t      fileMode;       /* mode to pass to open(2) */
} Vfd;
```

其中包括了 VFD 的状态信息：

- `fd` 用于保存真正的 OS 文件描述符，如果未使用，那么将会被设置为 `VFD_CLOSED`
- `fdstate` 保存了 VFD 的状态标志位
- `resowner` 表示这个 VFD 的持有者，方便后续的自动清理

此外，还包括 VFD 数组的管理信息。整个 VFD 数组被组织为两部分：LRU 池和空闲 VFD 列表。

LRU 池在逻辑上是一个双向链表，管理了所有正在持有 OS 文件描述符的 VFD。当一个 VFD 被使用后，它就会从 LRU 链表中移动到队头；此时 LRU 双向链表的尾部就是最近最久未被使用过的那个 VFD。

空闲 VFD 列表在逻辑上是一个单向链表。所有未被使用的 VFD 都会被串联在这个单链表中。被使用完毕释放的 VFD 也会被串回这个链表中。

上述两个部分虽然在逻辑上是双向或单向链表，但在形态上还是存放在 VFD 数组中，通过保存以下三个数组下标来代替链表本应该拥有的指针：

- `nextFree` 是下一个空闲 VFD 在数组中的下标，用于串联空闲 VFD 列表
- `lruMoreRecently` 是后一个被使用过的 VFD 在数组中的下标
- `lruLessRecently` 是前一个被使用过的 VFD 在数组中的下标

后两者相当于双向链表中的 `prev` 和 `next` 指针，用于串联 LRU 池。VFD 数组中的第一个元素 `VfdCache[0]` 永远不使用，该元素中的空间将会被分别作为两个链表的头指针。

最后剩下的几个信息，是真正向操作系统打开文件时传入的参数：

- `fileSize` 表示文件大小
- `fileName` 表示文件名
- `fileFlags` 表示打开文件时的标志位
- `fileMode` 表示打开文件时的模式（权限）

## 低层函数

### LruInsert / Insert

`LruInsert()` 函数会向 OS 申请真正打开 VFD 所对应的 OS 文件描述符，然后把这个 VFD 添加到 LRU 池的队头。LRU 池中的 VFD 是真正持有 OS 文件描述符的 VFD。把 VFD 移动到 LRU 池的队头是通过 `Insert()` 函数实现的，它会修改 VFD 的 LRU 双向链表指针。

```c
static void
Insert(File file)
{
    Vfd        *vfdP;

    Assert(file != 0);

    DO_DB(elog(LOG, "Insert %d (%s)",
               file, VfdCache[file].fileName));
    DO_DB(_dump_lru());

    vfdP = &VfdCache[file];

    vfdP->lruMoreRecently = 0;
    vfdP->lruLessRecently = VfdCache[0].lruLessRecently;
    VfdCache[0].lruLessRecently = file;
    VfdCache[vfdP->lruLessRecently].lruMoreRecently = file;

    DO_DB(_dump_lru());
}

/* returns 0 on success, -1 on re-open failure (with errno set) */
static int
LruInsert(File file)
{
    Vfd        *vfdP;

    Assert(file != 0);

    DO_DB(elog(LOG, "LruInsert %d (%s)",
               file, VfdCache[file].fileName));

    vfdP = &VfdCache[file];

    if (FileIsNotOpen(file))
    {
        /* Close excess kernel FDs. */
        ReleaseLruFiles();

        /*
         * The open could still fail for lack of file descriptors, eg due to
         * overall system file table being full.  So, be prepared to release
         * another FD if necessary...
         */
        vfdP->fd = BasicOpenFilePerm(vfdP->fileName, vfdP->fileFlags,
                                     vfdP->fileMode);
        if (vfdP->fd < 0)
        {
            DO_DB(elog(LOG, "re-open failed: %m"));
            return -1;
        }
        else
        {
            ++nfile;
        }
    }

    /*
     * put it at the head of the Lru ring
     */

    Insert(file);

    return 0;
}
```

### LruDelete / Delete

`LruDelete()` 函数会真正释放 VFD 所持有的 OS 文件描述符，然后将 VFD 从 LRU 池中移除，因为这个 VFD 已经不再持有 OS 文件描述符了。移除动作是由 `Delete()` 函数实现的，它负责修改 VFD 的 LRU 指针，重新串联这个 VFD 之前和之后的 VFD。

```c
static void
Delete(File file)
{
    Vfd        *vfdP;

    Assert(file != 0);

    DO_DB(elog(LOG, "Delete %d (%s)",
               file, VfdCache[file].fileName));
    DO_DB(_dump_lru());

    vfdP = &VfdCache[file];

    VfdCache[vfdP->lruLessRecently].lruMoreRecently = vfdP->lruMoreRecently;
    VfdCache[vfdP->lruMoreRecently].lruLessRecently = vfdP->lruLessRecently;

    DO_DB(_dump_lru());
}

static void
LruDelete(File file)
{
    Vfd        *vfdP;

    Assert(file != 0);

    DO_DB(elog(LOG, "LruDelete %d (%s)",
               file, VfdCache[file].fileName));

    vfdP = &VfdCache[file];

    /*
     * Close the file.  We aren't expecting this to fail; if it does, better
     * to leak the FD than to mess up our internal state.
     */
    if (close(vfdP->fd) != 0)
        elog(vfdP->fdstate & FD_TEMP_FILE_LIMIT ? LOG : data_sync_elevel(LOG),
             "could not close file \"%s\": %m", vfdP->fileName);
    vfdP->fd = VFD_CLOSED;
    --nfile;

    /* delete the vfd record from the LRU ring */
    Delete(file);
}
```

### ReleaseLruFile / ReleaseLruFiles

这两个函数负责不断关闭 LRU 池中最近最久未被使用的 VFD 所持有的 OS 文件描述符，直到将 LRU 池中的 VFD 数量控制到 OS 允许的安全范围以下。具体的实现方式就是调用上面的 `LruDelete()` 来关闭 OS 文件描述符并从 LRU 池中移除。

```c
/*
 * Release one kernel FD by closing the least-recently-used VFD.
 */
static bool
ReleaseLruFile(void)
{
    DO_DB(elog(LOG, "ReleaseLruFile. Opened %d", nfile));

    if (nfile > 0)
    {
        /*
         * There are opened files and so there should be at least one used vfd
         * in the ring.
         */
        Assert(VfdCache[0].lruMoreRecently != 0);
        LruDelete(VfdCache[0].lruMoreRecently);
        return true;            /* freed a file */
    }
    return false;               /* no files available to free */
}

/*
 * Release kernel FDs as needed to get under the max_safe_fds limit.
 * After calling this, it's OK to try to open another file.
 */
static void
ReleaseLruFiles(void)
{
    while (nfile + numAllocatedDescs + numExternalFDs >= max_safe_fds)
    {
        if (!ReleaseLruFile())
            break;
    }
}
```

### AllocateVfd / FreeVfd

这两个函数负责在 VFD 数组中占用一个空闲的 VFD（但并不打开底层的 OS 文件），以及归还 VFD。

在分配 VFD 时，如果 VFD 数组的空闲链表已经为空，那么就需要使用 `realloc()` 重新分配一个更大的 VFD 数组（通常是原 VFD 数组长度的两倍），并把新分配数组的后一半 VFD 初始化到空闲链表中以备未来使用。然后从空闲链表中摘下一个 VFD 并返回其下标。

```c
static File
AllocateVfd(void)
{
    Index       i;
    File        file;

    DO_DB(elog(LOG, "AllocateVfd. Size %zu", SizeVfdCache));

    Assert(SizeVfdCache > 0);   /* InitFileAccess not called? */

    if (VfdCache[0].nextFree == 0)
    {
        /*
         * The free list is empty so it is time to increase the size of the
         * array.  We choose to double it each time this happens. However,
         * there's not much point in starting *real* small.
         */
        Size        newCacheSize = SizeVfdCache * 2;
        Vfd        *newVfdCache;

        if (newCacheSize < 32)
            newCacheSize = 32;

        /*
         * Be careful not to clobber VfdCache ptr if realloc fails.
         */
        newVfdCache = (Vfd *) realloc(VfdCache, sizeof(Vfd) * newCacheSize);
        if (newVfdCache == NULL)
            ereport(ERROR,
                    (errcode(ERRCODE_OUT_OF_MEMORY),
                     errmsg("out of memory")));
        VfdCache = newVfdCache;

        /*
         * Initialize the new entries and link them into the free list.
         */
        for (i = SizeVfdCache; i < newCacheSize; i++)
        {
            MemSet((char *) &(VfdCache[i]), 0, sizeof(Vfd));
            VfdCache[i].nextFree = i + 1;
            VfdCache[i].fd = VFD_CLOSED;
        }
        VfdCache[newCacheSize - 1].nextFree = 0;
        VfdCache[0].nextFree = SizeVfdCache;

        /*
         * Record the new size
         */
        SizeVfdCache = newCacheSize;
    }

    file = VfdCache[0].nextFree;

    VfdCache[0].nextFree = VfdCache[file].nextFree;

    return file;
}
```

归还 VFD 的过程很直接：将 VFD 恢复为初始状态，然后将其重新放回空闲链表中。

```c
static void
FreeVfd(File file)
{
    Vfd        *vfdP = &VfdCache[file];

    DO_DB(elog(LOG, "FreeVfd: %d (%s)",
               file, vfdP->fileName ? vfdP->fileName : ""));

    if (vfdP->fileName != NULL)
    {
        free(vfdP->fileName);
        vfdP->fileName = NULL;
    }
    vfdP->fdstate = 0x0;

    vfdP->nextFree = VfdCache[0].nextFree;
    VfdCache[0].nextFree = file;
}
```

### BasicOpenFile：Open 系统调用的替代者

这个函数封装了传统的 `open()` 系统调用。理论上，PostgreSQL 内核的其它部分不应再直接使用 `open()` 系统调用。这个函数将会返回一个裸的 OS 文件描述符，而不是 VFD——所以调用这个函数的代码需要保证这个文件描述符不会被泄露。

该函数内部真正调用了 `open()` 来获取一个 OS 文件描述符。如果失败，那么将会试图从 LRU 池中删除一个已有的文件描述符，然后再度重试，直到成功为止。

```c
/*
 * Open a file with BasicOpenFilePerm() and pass default file mode for the
 * fileMode parameter.
 */
int
BasicOpenFile(const char *fileName, int fileFlags)
{
    return BasicOpenFilePerm(fileName, fileFlags, pg_file_create_mode);
}

/*
 * BasicOpenFilePerm --- same as open(2) except can free other FDs if needed
 *
 * This is exported for use by places that really want a plain kernel FD,
 * but need to be proof against running out of FDs.  Once an FD has been
 * successfully returned, it is the caller's responsibility to ensure that
 * it will not be leaked on ereport()!  Most users should *not* call this
 * routine directly, but instead use the VFD abstraction level, which
 * provides protection against descriptor leaks as well as management of
 * files that need to be open for more than a short period of time.
 *
 * Ideally this should be the *only* direct call of open() in the backend.
 * In practice, the postmaster calls open() directly, and there are some
 * direct open() calls done early in backend startup.  Those are OK since
 * this module wouldn't have any open files to close at that point anyway.
 */
int
BasicOpenFilePerm(const char *fileName, int fileFlags, mode_t fileMode)
{
    int         fd;

tryAgain:
    fd = open(fileName, fileFlags, fileMode);

    if (fd >= 0)
    {
        return fd;              /* success! */
    }

    if (errno == EMFILE || errno == ENFILE)
    {
        int         save_errno = errno;

        ereport(LOG,
                (errcode(ERRCODE_INSUFFICIENT_RESOURCES),
                 errmsg("out of file descriptors: %m; release and retry")));
        errno = 0;
        if (ReleaseLruFile())
            goto tryAgain;
        errno = save_errno;
    }

    return -1;                  /* failure */
}
```

### FileAccess：访问文件

每个高层文件访问接口都会调用 `FileAccess()`。调用这个函数意味着 VFD 持有的 OS 文件描述符将要被使用。那么：

1. 如果这个文件在 OS 层面还没有被打开，那么调用 `LruInsert()` 打开文件并将 VFD 插入 LRU 池
2. 如果这个文件已被打开，那么先将 VFD 从 LRU 池中移除，然后将 VFD 插入到 LRU 池的队头，表示这个 VFD 最近刚刚被访问

```c
/* returns 0 on success, -1 on re-open failure (with errno set) */
static int
FileAccess(File file)
{
    int         returnValue;

    DO_DB(elog(LOG, "FileAccess %d (%s)",
               file, VfdCache[file].fileName));

    /*
     * Is the file open?  If not, open it and put it at the head of the LRU
     * ring (possibly closing the least recently used file to get an FD).
     */

    if (FileIsNotOpen(file))
    {
        returnValue = LruInsert(file);
        if (returnValue != 0)
            return returnValue;
    }
    else if (VfdCache[0].lruLessRecently != file)
    {
        /*
         * We now know that the file is open and that it is not the last one
         * accessed, so we need to move it to the head of the Lru ring.
         */

        Delete(file);
        Insert(file);
    }

    return 0;
}
```

## 高层文件操作接口

### 打开文件

`PathNameOpenFilePerm()` 将会根据参数打开文件，并返回一个 VFD。经历了以下步骤：

1. 调用 `AllocateVfd()` 从 VFD 数组中拿到一个空闲 VFD 并初始化
2. 调用 `ReleaseLruFiles()` 把 LRU 池中的 VFD 减少到操作系统允许的水平
3. 调用 `BasicOpenFilePerm()` 打开一个 OS 文件描述符，并关联到新分配的 VFD 上
4. 调用 `Insert()` 把新分配的 VFD 添加到 LRU 池中
5. 返回新分配的 VFD

```c
/*
 * Open a file with PathNameOpenFilePerm() and pass default file mode for the
 * fileMode parameter.
 */
File
PathNameOpenFile(const char *fileName, int fileFlags)
{
    return PathNameOpenFilePerm(fileName, fileFlags, pg_file_create_mode);
}

/*
 * open a file in an arbitrary directory
 *
 * NB: if the passed pathname is relative (which it usually is),
 * it will be interpreted relative to the process' working directory
 * (which should always be $PGDATA when this code is running).
 */
File
PathNameOpenFilePerm(const char *fileName, int fileFlags, mode_t fileMode)
{
    char       *fnamecopy;
    File        file;
    Vfd        *vfdP;

    DO_DB(elog(LOG, "PathNameOpenFilePerm: %s %x %o",
               fileName, fileFlags, fileMode));

    /*
     * We need a malloc'd copy of the file name; fail cleanly if no room.
     */
    fnamecopy = strdup(fileName);
    if (fnamecopy == NULL)
        ereport(ERROR,
                (errcode(ERRCODE_OUT_OF_MEMORY),
                 errmsg("out of memory")));

    file = AllocateVfd();
    vfdP = &VfdCache[file];

    /* Close excess kernel FDs. */
    ReleaseLruFiles();

    vfdP->fd = BasicOpenFilePerm(fileName, fileFlags, fileMode);

    if (vfdP->fd < 0)
    {
        int         save_errno = errno;

        FreeVfd(file);
        free(fnamecopy);
        errno = save_errno;
        return -1;
    }
    ++nfile;
    DO_DB(elog(LOG, "PathNameOpenFile: success %d",
               vfdP->fd));

    vfdP->fileName = fnamecopy;
    /* Saved flags are adjusted to be OK for re-opening file */
    vfdP->fileFlags = fileFlags & ~(O_CREAT | O_TRUNC | O_EXCL);
    vfdP->fileMode = fileMode;
    vfdP->fileSize = 0;
    vfdP->fdstate = 0x0;
    vfdP->resowner = NULL;

    Insert(file);

    return file;
}
```

### 关闭文件

`FileClose()` 将会关闭一个 VFD 所对应的一切：

1. 如果 VFD 对应的 OS 文件描述符已被打开，那么调用 `close()` 关掉它，然后调用 `Delete()` 从 LRU 池里移除这个 VFD
2. 如果 VFD 对应的文件被设置了 **关闭时删除** 的标志（临时文件），那么调用 `unlink()` 删掉它！
3. 调用 `FreeVfd()` 清空这个 VFD 并重新归还到 VFD 数组的空闲链表中

```c
/*
 * close a file when done with it
 */
void
FileClose(File file)
{
    Vfd        *vfdP;

    Assert(FileIsValid(file));

    DO_DB(elog(LOG, "FileClose: %d (%s)",
               file, VfdCache[file].fileName));

    vfdP = &VfdCache[file];

    if (!FileIsNotOpen(file))
    {
        /* close the file */
        if (close(vfdP->fd) != 0)
        {
            /*
             * We may need to panic on failure to close non-temporary files;
             * see LruDelete.
             */
            elog(vfdP->fdstate & FD_TEMP_FILE_LIMIT ? LOG : data_sync_elevel(LOG),
                 "could not close file \"%s\": %m", vfdP->fileName);
        }

        --nfile;
        vfdP->fd = VFD_CLOSED;

        /* remove the file from the lru ring */
        Delete(file);
    }

    if (vfdP->fdstate & FD_TEMP_FILE_LIMIT)
    {
        /* Subtract its size from current usage (do first in case of error) */
        temporary_files_size -= vfdP->fileSize;
        vfdP->fileSize = 0;
    }

    /*
     * Delete the file if it was temporary, and make a log entry if wanted
     */
    if (vfdP->fdstate & FD_DELETE_AT_CLOSE)
    {
        struct stat filestats;
        int         stat_errno;

        /*
         * If we get an error, as could happen within the ereport/elog calls,
         * we'll come right back here during transaction abort.  Reset the
         * flag to ensure that we can't get into an infinite loop.  This code
         * is arranged to ensure that the worst-case consequence is failing to
         * emit log message(s), not failing to attempt the unlink.
         */
        vfdP->fdstate &= ~FD_DELETE_AT_CLOSE;


        /* first try the stat() */
        if (stat(vfdP->fileName, &filestats))
            stat_errno = errno;
        else
            stat_errno = 0;

        /* in any case do the unlink */
        if (unlink(vfdP->fileName))
            ereport(LOG,
                    (errcode_for_file_access(),
                     errmsg("could not delete file \"%s\": %m", vfdP->fileName)));

        /* and last report the stat results */
        if (stat_errno == 0)
            ReportTemporaryFileUsage(vfdP->fileName, filestats.st_size);
        else
        {
            errno = stat_errno;
            ereport(LOG,
                    (errcode_for_file_access(),
                     errmsg("could not stat file \"%s\": %m", vfdP->fileName)));
        }
    }

    /* Unregister it from the resource owner */
    if (vfdP->resowner)
        ResourceOwnerForgetFile(vfdP->resowner, file);

    /*
     * Return the Vfd slot to the free list
     */
    FreeVfd(file);
}
```

### 其它文件操作

除去文件的打开与关闭以外，其它文件操作需要基于 **文件已被打开** 的假设进行。这些文件操作都被 PostgreSQL 内核做了一层封装。在进行真正的文件操作之前，需要先使用打开文件后持有的 VFD 调用一次 `FileAccess()` 函数。这个函数能够保证：

1. VFD 内部持有的 OS 文件描述符已经打开（如果没打开，那就立刻打开，或许会导致其它 OS 文件描述符被关闭）
2. VFD 在 LRU 池中的位置移动到队头，因为这个 VFD 对应的 OS 文件描述符最近被使用了

以文件库函数 `read()` 的包装 `FileRead()` 为例：

```c
int
FileRead(File file, char *buffer, int amount, off_t offset,
         uint32 wait_event_info)
{
    int         returnCode;
    Vfd        *vfdP;

    Assert(FileIsValid(file));

    DO_DB(elog(LOG, "FileRead: %d (%s) " INT64_FORMAT " %d %p",
               file, VfdCache[file].fileName,
               (int64) offset,
               amount, buffer));

    returnCode = FileAccess(file);
    if (returnCode < 0)
        return returnCode;

    vfdP = &VfdCache[file];

retry:
    pgstat_report_wait_start(wait_event_info);
    returnCode = pread(vfdP->fd, buffer, amount, offset);
    pgstat_report_wait_end();

    if (returnCode < 0)
    {
        /* OK to retry if interrupted */
        if (errno == EINTR)
            goto retry;
    }

    return returnCode;
}
```

## Summary

PostgreSQL 内核中的 VFD 机制用于防止 PostgreSQL 后端进程受 OS 对进程打开文件数量的限制。VFD 内部维护了一个 LRU 池来管理所有被打开的 OS 文件描述符。使用 VFD 的高层接口来操作文件，就可以享受到 VFD 为我们屏蔽掉的文件描述符管理所带来的的便利。

VFD 的实现思想与操作系统的进程调度有些类似。OS 上的进程有成百上千个，而 CPU 只有一个（或几个）。从使用者的角度看，这些进程似乎都在同时执行，只有 OS 知道每一个时刻只有一个进程在一个 CPU 核心上运行；在 PostgreSQL 中，类似地，从 VFD 使用者的角度看，似乎能够同时持有远超操作系统数量限制的文件描述符，但只有 VFD 知道，每一个时刻打开的 OS 文件描述符数量必定小于操作系统对进程打开文件数量的限制。

一招瞒天过海。
