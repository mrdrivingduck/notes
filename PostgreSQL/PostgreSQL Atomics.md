# PostgreSQL - Atomics

Created by: Mr Dk.

2023 / 10 / 30 0:09

Hangzhou, Zhejiang, China

---

## Background

原子操作是多进程/多线程编程中非常重要的原语，可以用于解决并发访问共享内存时出现的竞态条件。原子操作在语义上保证了对共享内存的修改仅需要调用一次 API 就可以完成，在实现上还需要解决可能潜在出现的编译器指令重排序和处理器乱序执行，此外还得兼顾性能。不少高级语言都直接提供了原子数据类型和原子操作 API，比如 C++ 11 的 [`std::atomic`](https://cplusplus.com/reference/atomic/) 和 JDK 的 [`java.util.concurrent.atomic`](https://docs.oracle.com/javase/tutorial/essential/concurrency/atomic.html)。在 C 语言编写的大型软件系统中，也都各自实现了原子操作 API 作为基础设施，用于实现更加上层的无锁数据结构和算法，比如 Linux kernel 的 [`atomic_t`](https://docs.kernel.org/core-api/wrappers/atomic_t.html)，Nginx 的 `ngx_atomic_t`。在 PostgreSQL 中，也实现了 `pg_atomic_*` 的原子数据类型和 API。

本文基于 PostgreSQL `master` 分支（PostgreSQL 17 under dev）当前的 `HEAD` 版本分析原子操作的实现：

```
commit 26f988212eada9c586223cbbf876c7eb455044d9
Author: Peter Eisentraut <peter@eisentraut.org>
Date:   Thu Oct 26 13:03:43 2023 +0200

    Add "Add trailing commas to enum definitions" to .git-blame-ignore-revs

    Discussion: https://www.postgresql.org/message-id/flat/386f8c45-c8ac-4681-8add-e3b0852c1620%40eisentraut.org
```

## Overview

PostgreSQL 原子操作的目标是能够原子地操作内存并保证缓存一致性，其实现方式是实现具备优秀的跨 CPU 可移植性和跨 OS 可移植性的工程典范。其大致的思路为：从慢而全，到快而专。

1. 用 OS 提供的信号量实现最原始但最完整的 API
2. 如果 PostgreSQL 在当前平台上能够支持硬件自旋锁（Spinlock），那么使用硬件自旋替代 OS 信号量实现原子操作
3. 如果构建 PostgreSQL 时使用的编译器具有内置的原子数据类型和原子操作 API，那么使用编译器的内置类型和 API；它们的可移植性由编译器来保证
4. 如果构建 PostgreSQL 的目标 CPU 平台支持更加高效的硬件指令来实现原子操作，那么使用相应硬件指令

在实际的代码中，原子数据类型和原子操作 API 的声明顺序与上述思路是颠倒的，这样能够使 C 预处理器优先选择当前条件下性能最好的实现方式进行条件编译；如果当前条件下无法满足部分前提，再使用性能稍差但更普适的实现方式。

## API

PostgreSQL 在 `src/include/port/atomics.h` 中定义了所有对外暴露的 API，这层 API 会被条件编译为适合当前平台的最佳实现。

首先提供的是屏障，包含编译器屏障指令和 CPU 屏障指令。编译器需要保证对程序的指令重排序不会跨越编译器屏障，但这是一个很弱的保证，因为现代 CPU 基本都是乱序执行指令的，代码段中的指令按顺序排列不意味着它们会被顺序执行。CPU 的读屏障、写屏障、内存屏障分别禁止 CPU 乱序执行屏障前后的读读操作、写写操作、所有操作：

```c
#define pg_compiler_barrier() pg_compiler_barrier_impl()
#define pg_read_barrier()     pg_read_barrier_impl()
#define pg_write_barrier()    pg_write_barrier_impl()
#define pg_memory_barrier()   pg_memory_barrier_impl()
```

标识位（flag）原子操作：

- 初始化
- TAS
- 检查标识
- 清除标识

```c
static inline void pg_atomic_init_flag(volatile pg_atomic_flag *ptr);
static inline bool pg_atomic_test_set_flag(volatile pg_atomic_flag *ptr);
static inline bool pg_atomic_unlocked_test_flag(volatile pg_atomic_flag *ptr);
static inline void pg_atomic_clear_flag(volatile pg_atomic_flag *ptr);
```

32 位原子操作：

- 初始化
- 原子读
- 原子写
- 原子非锁定写
- 原子内存交换
- 原子内存比较并交换（CAS）
- 原子加/减/与/或运算

```c
static inline void pg_atomic_init_u32(volatile pg_atomic_uint32 *ptr, uint32 val);
static inline uint32 pg_atomic_read_u32(volatile pg_atomic_uint32 *ptr);
static inline void pg_atomic_write_u32(volatile pg_atomic_uint32 *ptr, uint32 val);
static inline void pg_atomic_unlocked_write_u32(volatile pg_atomic_uint32 *ptr, uint32 val);
static inline uint32 pg_atomic_exchange_u32(volatile pg_atomic_uint32 *ptr, uint32 newval);
static inline bool pg_atomic_compare_exchange_u32(volatile pg_atomic_uint32 *ptr,
                                                  uint32 *expected, uint32 newval);
static inline uint32 pg_atomic_fetch_add_u32(volatile pg_atomic_uint32 *ptr, int32 add_);
static inline uint32 pg_atomic_fetch_sub_u32(volatile pg_atomic_uint32 *ptr, int32 sub_);
static inline uint32 pg_atomic_fetch_and_u32(volatile pg_atomic_uint32 *ptr, uint32 and_);
static inline uint32 pg_atomic_fetch_or_u32(volatile pg_atomic_uint32 *ptr, uint32 or_);
static inline uint32 pg_atomic_add_fetch_u32(volatile pg_atomic_uint32 *ptr, int32 add_);
static inline uint32 pg_atomic_sub_fetch_u32(volatile pg_atomic_uint32 *ptr, int32 sub_);
```

64 位原子操作：

- 初始化
- 原子读
- 原子写
- 原子内存交换
- 原子内存比较并交换（CAS）
- 原子加/减/与/或运算

```c
static inline void pg_atomic_init_u64(volatile pg_atomic_uint64 *ptr, uint64 val);
static inline uint64 pg_atomic_read_u64(volatile pg_atomic_uint64 *ptr);
static inline void pg_atomic_write_u64(volatile pg_atomic_uint64 *ptr, uint64 val);
static inline uint64 pg_atomic_exchange_u64(volatile pg_atomic_uint64 *ptr, uint64 newval);
static inline bool pg_atomic_compare_exchange_u64(volatile pg_atomic_uint64 *ptr,
                                                  uint64 *expected, uint64 newval);
static inline uint64 pg_atomic_fetch_add_u64(volatile pg_atomic_uint64 *ptr, int64 add_);
static inline uint64 pg_atomic_fetch_sub_u64(volatile pg_atomic_uint64 *ptr, int64 sub_);
static inline uint64 pg_atomic_fetch_and_u64(volatile pg_atomic_uint64 *ptr, uint64 and_);
static inline uint64 pg_atomic_fetch_or_u64(volatile pg_atomic_uint64 *ptr, uint64 or_);
static inline uint64 pg_atomic_add_fetch_u64(volatile pg_atomic_uint64 *ptr, int64 add_);
static inline uint64 pg_atomic_sub_fetch_u64(volatile pg_atomic_uint64 *ptr, int64 sub_);
```

对于上述列出的 API，并不是每一个 API 都最终对应一个硬件原语：部分 API 是通过其它基础 API 与基本运算组合而得到的。比如 `pg_atomic_fetch_add_u32` 就是通过 `pg_atomic_compare_exchange_u32_impl` 与加法运算实现的，因此其性能高低受其依赖的基础 API 的性能影响。这部分实现在 `src/include/port/atomics/generic.h` 中：

```c
/*
 * Provide additional operations using supported infrastructure. These are
 * expected to be efficient if the underlying atomic operations are efficient.
 */
#include "port/atomics/generic.h"
```

以 32 位变量的原子加减运算为例：原子加法实际上是通过 32 位的 CAS 实现的，原子减法实际上是通过复用原子加法的代码实现的。

```c
#if !defined(PG_HAVE_ATOMIC_FETCH_ADD_U32) && defined(PG_HAVE_ATOMIC_COMPARE_EXCHANGE_U32)
#define PG_HAVE_ATOMIC_FETCH_ADD_U32
static inline uint32
pg_atomic_fetch_add_u32_impl(volatile pg_atomic_uint32 *ptr, int32 add_)
{
    uint32 old;
    old = ptr->value;           /* ok if read is not atomic */
    while (!pg_atomic_compare_exchange_u32_impl(ptr, &old, old + add_))
        /* skip */;
    return old;
}
#endif

#if !defined(PG_HAVE_ATOMIC_FETCH_SUB_U32) && defined(PG_HAVE_ATOMIC_COMPARE_EXCHANGE_U32)
#define PG_HAVE_ATOMIC_FETCH_SUB_U32
static inline uint32
pg_atomic_fetch_sub_u32_impl(volatile pg_atomic_uint32 *ptr, int32 sub_)
{
    return pg_atomic_fetch_add_u32_impl(ptr, -sub_);
}
#endif
```

## Fallback Implementations

对于完全没有原子操作或硬件自旋支持的构建环境，PostgreSQL 对上述所有 API 提供了完整的软件模拟实现。如果构建环境传入未传入任何原子操作相关的宏定义，那么软件模拟实现将会作为后备实现而被启用：

```c
/*
 * Provide a full fallback of the pg_*_barrier(), pg_atomic**_flag and
 * pg_atomic_* APIs for platforms without sufficient spinlock and/or atomics
 * support. In the case of spinlock backed atomics the emulation is expected
 * to be efficient, although less so than native atomics support.
 */
#include "port/atomics/fallback.h"
```

比如，对于 32 位的原子变量，其数据类型结构体将会被定义为如下的样子：

- `sema` 变量用作锁
- `value` 保存实际数据

```c
#if !defined(PG_HAVE_ATOMIC_U32_SUPPORT)

#define PG_HAVE_ATOMIC_U32_SIMULATION

#define PG_HAVE_ATOMIC_U32_SUPPORT
typedef struct pg_atomic_uint32
{
    /* Check pg_atomic_flag's definition above for an explanation */
#if defined(__hppa) || defined(__hppa__)    /* HP PA-RISC */
    int         sema[4];
#else
    int         sema;
#endif
    volatile uint32 value;
} pg_atomic_uint32;

#endif /* PG_HAVE_ATOMIC_U32_SUPPORT */
```

有了上述的类型定义以后，原子变量运算的所有 API 将以这样的模式实现：先对原子变量自旋锁定，然后运算赋值，最后解锁。在 [自旋锁](./PostgreSQL%20Spinlock.md) 的文章中已经分析过，如果当前构建环境提供了硬件自旋的能力，那么自旋锁 API 将会被编译为高效的硬件指令；否则将会回退使用 OS 信号量来模拟。比如原子加法的实现如下：

```c
uint32
pg_atomic_fetch_add_u32_impl(volatile pg_atomic_uint32 *ptr, int32 add_)
{
    uint32      oldval;

    SpinLockAcquire((slock_t *) &ptr->sema);
    oldval = ptr->value;
    ptr->value += add_;
    SpinLockRelease((slock_t *) &ptr->sema);
    return oldval;
}
```

比如 CAS 操作的语义将不得不用多行代码来啰嗦地模拟：

```c
bool
pg_atomic_compare_exchange_u32_impl(volatile pg_atomic_uint32 *ptr,
                                    uint32 *expected, uint32 newval)
{
    bool        ret;

    /*
     * Do atomic op under a spinlock. It might look like we could just skip
     * the cmpxchg if the lock isn't available, but that'd just emulate a
     * 'weak' compare and swap. I.e. one that allows spurious failures. Since
     * several algorithms rely on a strong variant and that is efficiently
     * implementable on most major architectures let's emulate it here as
     * well.
     */
    SpinLockAcquire((slock_t *) &ptr->sema);

    /* perform compare/exchange logic */
    ret = ptr->value == *expected;
    *expected = ptr->value;
    if (ret)
        ptr->value = newval;

    /* and release lock */
    SpinLockRelease((slock_t *) &ptr->sema);

    return ret;
}
```

## Compiler-Specific Implementation

目前很多编译器从某个特定版本开始已经内置了原子操作的 API。如果能够检测到当前构建环境中的编译器符合要求，那么使用编译器的内置 API 可以具有更好的可移植性和性能：

```c
/*
 * Compiler specific, but architecture independent implementations.
 *
 * Provide architecture independent implementations of the atomic
 * facilities. At the very least compiler barriers should be provided, but a
 * full implementation of
 * * pg_compiler_barrier(), pg_write_barrier(), pg_read_barrier()
 * * pg_atomic_compare_exchange_u32(), pg_atomic_fetch_add_u32()
 * using compiler intrinsics are a good idea.
 */
/*
 * gcc or compatible, including clang and icc.  Exclude xlc.  The ppc64le "IBM
 * XL C/C++ for Linux, V13.1.2" emulates gcc, but __sync_lock_test_and_set()
 * of one-byte types elicits SIGSEGV.  That bug was gone by V13.1.5 (2016-12).
 */
#if (defined(__GNUC__) || defined(__INTEL_COMPILER)) && !(defined(__IBMC__) || defined(__IBMCPP__))
#include "port/atomics/generic-gcc.h"
#elif defined(_MSC_VER)
#include "port/atomics/generic-msvc.h"
#elif defined(__SUNPRO_C) && !defined(__GNUC__)
#include "port/atomics/generic-sunpro.h"
#else
/*
 * Unsupported compiler, we'll likely use slower fallbacks... At least
 * compiler barriers should really be provided.
 */
#endif
```

比如，对于 GCC 及其兼容编译器，32 位原子变量的数据类型被定义为：

```c
/* generic gcc based atomic uint32 implementation */
#if !defined(PG_HAVE_ATOMIC_U32_SUPPORT) \
    && (defined(HAVE_GCC__ATOMIC_INT32_CAS) || defined(HAVE_GCC__SYNC_INT32_CAS))

#define PG_HAVE_ATOMIC_U32_SUPPORT
typedef struct pg_atomic_uint32
{
    volatile uint32 value;
} pg_atomic_uint32;

#endif /* defined(HAVE_GCC__ATOMIC_INT32_CAS) || defined(HAVE_GCC__SYNC_INT32_CAS) */
```

相对应的 CAS 操作和原子加法都被实现为 [GCC 内置 API](https://gcc.gnu.org/onlinedocs/gcc/_005f_005fatomic-Builtins.html)（[Clang](https://llvm.org/docs/Atomics.html) 也兼容这些 API）：

```c
/* prefer __atomic, it has a better API */
#if !defined(PG_HAVE_ATOMIC_COMPARE_EXCHANGE_U32) && defined(HAVE_GCC__ATOMIC_INT32_CAS)
#define PG_HAVE_ATOMIC_COMPARE_EXCHANGE_U32
static inline bool
pg_atomic_compare_exchange_u32_impl(volatile pg_atomic_uint32 *ptr,
                                    uint32 *expected, uint32 newval)
{
    /* FIXME: we can probably use a lower consistency model */
    return __atomic_compare_exchange_n(&ptr->value, expected, newval, false,
                                       __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
}
#endif

#if !defined(PG_HAVE_ATOMIC_FETCH_ADD_U32) && defined(HAVE_GCC__SYNC_INT32_CAS)
#define PG_HAVE_ATOMIC_FETCH_ADD_U32
static inline uint32
pg_atomic_fetch_add_u32_impl(volatile pg_atomic_uint32 *ptr, int32 add_)
{
    return __sync_fetch_and_add(&ptr->value, add_);
}
#endif
```

## Architecture-Specific Implementation

最终，对于特定架构的 CPU 硬件，做定制化的处理。可能是通过内联汇编实现更加高效的操作，也可能是仅仅关闭某个操作的实现：

```c
/*
 * First a set of architecture specific files is included.
 *
 * These files can provide the full set of atomics or can do pretty much
 * nothing if all the compilers commonly used on these platforms provide
 * usable generics.
 *
 * Don't add an inline assembly of the actual atomic operations if all the
 * common implementations of your platform provide intrinsics. Intrinsics are
 * much easier to understand and potentially support more architectures.
 *
 * It will often make sense to define memory barrier semantics here, since
 * e.g. generic compiler intrinsics for x86 memory barriers can't know that
 * postgres doesn't need x86 read/write barriers do anything more than a
 * compiler barrier.
 *
 */
#if defined(__arm__) || defined(__arm) || defined(__aarch64__)
#include "port/atomics/arch-arm.h"
#elif defined(__i386__) || defined(__i386) || defined(__x86_64__)
#include "port/atomics/arch-x86.h"
#elif defined(__ppc__) || defined(__powerpc__) || defined(__ppc64__) || defined(__powerpc64__)
#include "port/atomics/arch-ppc.h"
#elif defined(__hppa) || defined(__hppa__)
#include "port/atomics/arch-hppa.h"
#endif
```

比如，对于 32 位的 ARM 架构来说，64 位原子操作是非常慢的，所以直接禁止使用 64 位的原子操作：

```c
/*
 * 64 bit atomics on ARM32 are implemented using kernel fallbacks and thus
 * might be slow, so disable entirely. On ARM64 that problem doesn't exist.
 */
#if !defined(__aarch64__)
#define PG_DISABLE_64_BIT_ATOMICS
#else
/*
 * Architecture Reference Manual for ARMv8 states aligned read/write to/from
 * general purpose register is atomic.
 */
#define PG_HAVE_8BYTE_SINGLE_COPY_ATOMICITY
```

而对于 x86_64 架构来说，由于 CAS 操作和原子加法操作都有直接对应的硬件指令，那么直接在内联汇编中编写硬件指令，获得最佳的性能：

```c
#define PG_HAVE_ATOMIC_COMPARE_EXCHANGE_U32
static inline bool
pg_atomic_compare_exchange_u32_impl(volatile pg_atomic_uint32 *ptr,
                                    uint32 *expected, uint32 newval)
{
    char    ret;

    /*
     * Perform cmpxchg and use the zero flag which it implicitly sets when
     * equal to measure the success.
     */
    __asm__ __volatile__(
        "   lock                \n"
        "   cmpxchgl    %4,%5   \n"
        "   setz        %2      \n"
:       "=a" (*expected), "=m"(ptr->value), "=q" (ret)
:       "a" (*expected), "r" (newval), "m"(ptr->value)
:       "memory", "cc");
    return (bool) ret;
}

#define PG_HAVE_ATOMIC_FETCH_ADD_U32
static inline uint32
pg_atomic_fetch_add_u32_impl(volatile pg_atomic_uint32 *ptr, int32 add_)
{
    uint32 res;
    __asm__ __volatile__(
        "   lock                \n"
        "   xaddl   %0,%1       \n"
:       "=q"(res), "=m"(ptr->value)
:       "0" (add_), "m"(ptr->value)
:       "memory", "cc");
    return res;
}
```

## References

[GCC - 6.55 Built-in Functions for Memory Model Aware Atomic Operations](https://gcc.gnu.org/onlinedocs/gcc/_005f_005fatomic-Builtins.html)

[LLVM Atomic Instructions and Concurrency Guide](https://llvm.org/docs/Atomics.html)

[Kunpeng - 关于原子操作和弱内存序](https://kunpengcompute.github.io/2020/09/20/guan-yu-yuan-zi-cao-zuo-he-ruo-nei-cun-xu/)
