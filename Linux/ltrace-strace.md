# ltrace / strace

Created by : Mr Dk.

2023 / 01 / 08 23:26

Hangzhou, Zhejiang, China

---

## Background

`ltrace` 用于追踪一个程序的所有库函数调用，`strace` 用于追踪一个函数的所有系统调用。此外它们也可以追踪程序运行过程中接收到的信号。

## Usage

```shell
$ strace --help
Usage: strace [-ACdffhikqqrtttTvVwxxyyzZ] [-I N] [-b execve] [-e EXPR]...
              [-a COLUMN] [-o FILE] [-s STRSIZE] [-X FORMAT] [-P PATH]...
              [-p PID]... [--seccomp-bpf]
              { -p PID | [-DDD] [-E VAR=VAL]... [-u USERNAME] PROG [ARGS] }
   or: strace -c[dfwzZ] [-I N] [-b execve] [-e EXPR]... [-O OVERHEAD]
              [-S SORTBY] [-P PATH]... [-p PID]... [--seccomp-bpf]
              { -p PID | [-DDD] [-E VAR=VAL]... [-u USERNAME] PROG [ARGS] }

General:
  -e EXPR        a qualifying expression: OPTION=[!]all or OPTION=[!]VAL1[,VAL2]...
     options:    trace, abbrev, verbose, raw, signal, read, write, fault,
                 inject, status, kvm

Startup:
  -E VAR=VAL, --env=VAR=VAL
                 put VAR=VAL in the environment for command
  -E VAR, --env=VAR
                 remove VAR from the environment for command
  -p PID, --attach=PID
                 trace process with process id PID, may be repeated
  -u USERNAME, --user=USERNAME
                 run command as USERNAME handling setuid and/or setgid

Tracing:
  -b execve, --detach-on=execve
                 detach on execve syscall
  -D             run tracer process as a grandchild, not as a parent
  -DD            run tracer process in a separate process group
  -DDD           run tracer process in a separate session
  -f             follow forks
  -ff            follow forks with output into separate files
  -I INTERRUPTIBLE
     1:          no signals are blocked
     2:          fatal signals are blocked while decoding syscall (default)
     3:          fatal signals are always blocked (default if '-o FILE PROG')
     4:          fatal signals and SIGTSTP (^Z) are always blocked
                 (useful to make 'strace -o FILE PROG' not stop on ^Z)

Filtering:
  -e trace=[!]{[?]SYSCALL[@64|@32|@x32]|[?]/REGEX|GROUP|all|none},
  --trace=[!]{[?]SYSCALL[@64|@32|@x32]|[?]/REGEX|GROUP|all|none}
                 trace only specified syscalls.
     groups:     %creds, %desc, %file, %fstat, %fstatfs %ipc, %lstat,
                 %memory, %net, %process, %pure, %signal, %stat, %%stat,
                 %statfs, %%statfs
  -e signal=SET, --signal=SET
                 trace only the specified set of signals
                 print only the signals from SET
  -e status=SET, --status=SET
                 print only system calls with the return statuses in SET
     statuses:   successful, failed, unfinished, unavailable, detached
  -P PATH, --trace-path=PATH
                 trace accesses to PATH
  -z             print only syscalls that returned without an error code
  -Z             print only syscalls that returned with an error code

Output format:
  -a COLUMN, --columns=COLUMN
                 alignment COLUMN for printing syscall results (default 40)
  -e abbrev=SET, --abbrev=SET
                 abbreviate output for the syscalls in SET
  -e verbose=SET, --verbose=SET
                 dereference structures for the syscall in SET
  -e raw=SET, --raw=SET
                 print undecoded arguments for the syscalls in SET
  -e read=SET, --read=SET
                 dump the data read from the file descriptors in SET
  -e write=SET, --write=SET
                 dump the data written to the file descriptors in SET
  -e kvm=vcpu, --kvm=vcpu
                 print exit reason of kvm vcpu
  -i, --instruction-pointer
                 print instruction pointer at time of syscall
  -k, --stack-traces
                 obtain stack trace between each syscall
  -o FILE, --output=FILE
                 send trace output to FILE instead of stderr
  -A, --output-append-mode
                 open the file provided in the -o option in append mode
  -q             suppress messages about attaching, detaching, etc.
  -qq            suppress messages about process exit status as well.
  -r             print relative timestamp
  -s STRSIZE, --string-limit=STRSIZE
                 limit length of print strings to STRSIZE chars (default 32)
  -t             print absolute timestamp
  -tt            print absolute timestamp with usecs
  -ttt           print absolute UNIX time with usecs
  -T             print time spent in each syscall
  -v, --no-abbrev
                 verbose mode: print entities unabbreviated
  -x             print non-ascii strings in hex
  -xx            print all strings in hex
  -X FORMAT      set the FORMAT for printing of named constants and flags
     formats:    raw, abbrev, verbose
  -y             print paths associated with file descriptor arguments
  -yy            print protocol specific information associated with socket
                 file descriptors

Statistics:
  -c, --summary-only
                 count time, calls, and errors for each syscall and report
                 summary
  -C, --summary  like -c, but also print the regular output
  -O OVERHEAD    set overhead for tracing syscalls to OVERHEAD usecs
  -S SORTBY, --summary-sort-by=SORTBY
                 sort syscall counts by: time, calls, errors, name, nothing
                 (default time)
  -w             summarise syscall latency (default is system time)

Tampering:
  -e inject=SET[:error=ERRNO|:retval=VALUE][:signal=SIG][:syscall=SYSCALL]
            [:delay_enter=DELAY][:delay_exit=DELAY][:when=WHEN],
  --inject=SET[:error=ERRNO|:retval=VALUE][:signal=SIG][:syscall=SYSCALL]
           [:delay_enter=DELAY][:delay_exit=DELAY][:when=WHEN]
                 perform syscall tampering for the syscalls in SET
     delay:      milliseconds or NUMBER{s|ms|us|ns}
     when:       FIRST, FIRST+, or FIRST+STEP
  -e fault=SET[:error=ERRNO][:when=WHEN], --fault=SET[:error=ERRNO][:when=WHEN]
                 synonym for -e inject with default ERRNO set to ENOSYS.
Miscellaneous:
  -d, --debug    enable debug output to stderr
  -h, --help     print help message
  --seccomp-bpf  enable seccomp-bpf filtering
  -V, --version  print version
```

```shell
$ ltrace --help
Usage: ltrace [option ...] [command [arg ...]]
Trace library calls of a given program.

  -a, --align=COLUMN  align return values in a secific column.
  -A MAXELTS          maximum number of array elements to print.
  -b, --no-signals    don't print signals.
  -c                  count time and calls, and report a summary on exit.
  -C, --demangle      decode low-level symbol names into user-level names.
  -D, --debug=MASK    enable debugging (see -Dh or --debug=help).
  -Dh, --debug=help   show help on debugging.
  -e FILTER           modify which library calls to trace.
  -f                  trace children (fork() and clone()).
  -F, --config=FILE   load alternate configuration file (may be repeated).
  -h, --help          display this help and exit.
  -i                  print instruction pointer at time of library call.
  -l, --library=LIBRARY_PATTERN only trace symbols implemented by this library.
  -L                  do NOT display library calls.
  -n, --indent=NR     indent output by NR spaces for each call level nesting.
  -o, --output=FILENAME write the trace output to file with given name.
  -p PID              attach to the process with the process ID pid.
  -r                  print relative timestamps.
  -s STRSIZE          specify the maximum string size to print.
  -S                  trace system calls as well as library calls.
  -t, -tt, -ttt       print absolute timestamps.
  -T                  show the time spent inside each call.
  -u USERNAME         run command with the userid, groupid of username.
  -V, --version       output version information and exit.
  -x FILTER           modify which static functions to trace.

Report bugs to ltrace-devel@lists.alioth.debian.org
```

## Strace

尝试读懂 `strace` 的输出：

- 从 `execve` 开始，执行程序
- 查找 `ld.so.cache`，用于查询机器上所有动态库的存放位置
- 依次打开程序依赖的每一个动态链接库，并调用 `read` 装载它们（可以看到 ELF 格式的头部被装载）
- 最后是程序主函数内的系统调用
  - 调用 `open` 打开目录
  - 调用 `write` 打印输出

```shell
$ strace ls
execve("/usr/bin/ls", ["ls"], 0x7ffdad55a440 /* 27 vars */) = 0
brk(NULL)                               = 0x5653fca64000
arch_prctl(0x3001 /* ARCH_??? */, 0x7ffeab671c90) = -1 EINVAL (Invalid argument)
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=33738, ...}) = 0
mmap(NULL, 33738, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7faeadc47000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libselinux.so.1", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0@p\0\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0644, st_size=163200, ...}) = 0
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7faeadc45000
mmap(NULL, 174600, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7faeadc1a000
mprotect(0x7faeadc20000, 135168, PROT_NONE) = 0
mmap(0x7faeadc20000, 102400, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x6000) = 0x7faeadc20000
mmap(0x7faeadc39000, 28672, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1f000) = 0x7faeadc39000
mmap(0x7faeadc41000, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x26000) = 0x7faeadc41000
mmap(0x7faeadc43000, 6664, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7faeadc43000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\300A\2\0\0\0\0\0"..., 832) = 832
pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
pread64(3, "\4\0\0\0\20\0\0\0\5\0\0\0GNU\0\2\0\0\300\4\0\0\0\3\0\0\0\0\0\0\0", 32, 848) = 32
pread64(3, "\4\0\0\0\24\0\0\0\3\0\0\0GNU\0\30x\346\264ur\f|Q\226\236i\253-'o"..., 68, 880) = 68
fstat(3, {st_mode=S_IFREG|0755, st_size=2029592, ...}) = 0
pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
pread64(3, "\4\0\0\0\20\0\0\0\5\0\0\0GNU\0\2\0\0\300\4\0\0\0\3\0\0\0\0\0\0\0", 32, 848) = 32
pread64(3, "\4\0\0\0\24\0\0\0\3\0\0\0GNU\0\30x\346\264ur\f|Q\226\236i\253-'o"..., 68, 880) = 68
mmap(NULL, 2037344, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7faeada28000
mmap(0x7faeada4a000, 1540096, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x22000) = 0x7faeada4a000
mmap(0x7faeadbc2000, 319488, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x19a000) = 0x7faeadbc2000
mmap(0x7faeadc10000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1e7000) = 0x7faeadc10000
mmap(0x7faeadc16000, 13920, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7faeadc16000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libpcre2-8.so.0", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\340\"\0\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0644, st_size=584392, ...}) = 0
mmap(NULL, 586536, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7faead998000
mmap(0x7faead99a000, 409600, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x2000) = 0x7faead99a000
mmap(0x7faead9fe000, 163840, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x66000) = 0x7faead9fe000
mmap(0x7faeada26000, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x8d000) = 0x7faeada26000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libdl.so.2", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0 \22\0\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0644, st_size=18848, ...}) = 0
mmap(NULL, 20752, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7faead992000
mmap(0x7faead993000, 8192, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1000) = 0x7faead993000
mmap(0x7faead995000, 4096, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x3000) = 0x7faead995000
mmap(0x7faead996000, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x3000) = 0x7faead996000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libpthread.so.0", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\0\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\220q\0\0\0\0\0\0"..., 832) = 832
pread64(3, "\4\0\0\0\24\0\0\0\3\0\0\0GNU\0{E6\364\34\332\245\210\204\10\350-\0106\343="..., 68, 824) = 68
fstat(3, {st_mode=S_IFREG|0755, st_size=157224, ...}) = 0
pread64(3, "\4\0\0\0\24\0\0\0\3\0\0\0GNU\0{E6\364\34\332\245\210\204\10\350-\0106\343="..., 68, 824) = 68
mmap(NULL, 140408, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7faead96f000
mmap(0x7faead975000, 69632, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x6000) = 0x7faead975000
mmap(0x7faead986000, 24576, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x17000) = 0x7faead986000
mmap(0x7faead98c000, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1c000) = 0x7faead98c000
mmap(0x7faead98e000, 13432, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7faead98e000
close(3)                                = 0
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7faead96d000
arch_prctl(ARCH_SET_FS, 0x7faead96e400) = 0
mprotect(0x7faeadc10000, 16384, PROT_READ) = 0
mprotect(0x7faead98c000, 4096, PROT_READ) = 0
mprotect(0x7faead996000, 4096, PROT_READ) = 0
mprotect(0x7faeada26000, 4096, PROT_READ) = 0
mprotect(0x7faeadc41000, 4096, PROT_READ) = 0
mprotect(0x5653facf8000, 4096, PROT_READ) = 0
mprotect(0x7faeadc7d000, 4096, PROT_READ) = 0
munmap(0x7faeadc47000, 33738)           = 0
set_tid_address(0x7faead96e6d0)         = 2311490
set_robust_list(0x7faead96e6e0, 24)     = 0
rt_sigaction(SIGRTMIN, {sa_handler=0x7faead975bf0, sa_mask=[], sa_flags=SA_RESTORER|SA_SIGINFO, sa_restorer=0x7faead983420}, NULL, 8) = 0
rt_sigaction(SIGRT_1, {sa_handler=0x7faead975c90, sa_mask=[], sa_flags=SA_RESTORER|SA_RESTART|SA_SIGINFO, sa_restorer=0x7faead983420}, NULL, 8) = 0
rt_sigprocmask(SIG_UNBLOCK, [RTMIN RT_1], NULL, 8) = 0
prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
statfs("/sys/fs/selinux", 0x7ffeab671be0) = -1 ENOENT (No such file or directory)
statfs("/selinux", 0x7ffeab671be0)      = -1 ENOENT (No such file or directory)
brk(NULL)                               = 0x5653fca64000
brk(0x5653fca85000)                     = 0x5653fca85000
openat(AT_FDCWD, "/proc/filesystems", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0444, st_size=0, ...}) = 0
read(3, "nodev\tsysfs\nnodev\ttmpfs\nnodev\tbd"..., 1024) = 411
read(3, "", 1024)                       = 0
close(3)                                = 0
access("/etc/selinux/config", F_OK)     = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=3035952, ...}) = 0
mmap(NULL, 3035952, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7faead687000
close(3)                                = 0
ioctl(1, TCGETS, {B38400 opost isig icanon echo ...}) = 0
ioctl(1, TIOCGWINSZ, {ws_row=30, ws_col=120, ws_xpixel=0, ws_ypixel=0}) = 0
openat(AT_FDCWD, ".", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 3
fstat(3, {st_mode=S_IFDIR|0700, st_size=4096, ...}) = 0
getdents64(3, /* 25 entries */, 32768)  = 784
getdents64(3, /* 0 entries */, 32768)   = 0
close(3)                                = 0
fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(0x88, 0), ...}) = 0
write(1, "blog  mrdrivingduck.github.io  s"..., 42blog  mrdrivingduck.github.io  snap  temp
) = 42
close(1)                                = 0
close(2)                                = 0
exit_group(0)                           = ?
+++ exited with 0 +++
```

## Ltrace

对系统自带的可执行文件使用 `ltrace` 时，却没有任何输出：

```shell
$ ltrace ls
blog  mrdrivingduck.github.io  snap  temp
+++ exited (status 0) +++
```

带上 `-S` 参数，也可以顺带打印系统调用。输出中只有系统调用，还是没有库函数调用：

```shell
$ ltrace -S ls
SYS_brk(0)                                                                = 0x559c89633000
SYS_arch_prctl(0x3001, 0x7fffb6b633e0, 0x7f78077c22d0, 0x7f78077ca8b8)    = -22
SYS_access("/etc/ld.so.preload", 04)                                      = -2
SYS_openat(0xffffff9c, 0x7f78077cbb80, 0x80000, 0)                        = 3
SYS_fstat(3, 0x7fffb6b625e0)                                              = 0
SYS_mmap(0, 0x83ca, 1, 2)                                                 = 0x7f780779d000
SYS_close(3)                                                              = 0
SYS_openat(0xffffff9c, 0x7f78077d5e10, 0x80000, 0)                        = 3
SYS_read(3, "\177ELF\002\001\001", 832)                                   = 832
SYS_fstat(3, 0x7fffb6b62630)                                              = 0
SYS_mmap(0, 8192, 3, 34)                                                  = 0x7f780779b000
SYS_mmap(0, 0x2aa08, 1, 2050)                                             = 0x7f7807770000
SYS_mprotect(0x7f7807776000, 135168, 0)                                   = 0
SYS_mmap(0x7f7807776000, 0x19000, 5, 2066)                                = 0x7f7807776000
SYS_mmap(0x7f780778f000, 0x7000, 1, 2066)                                 = 0x7f780778f000
SYS_mmap(0x7f7807797000, 8192, 3, 2066)                                   = 0x7f7807797000
SYS_mmap(0x7f7807799000, 6664, 3, 50)                                     = 0x7f7807799000
SYS_close(3)                                                              = 0
SYS_openat(0xffffff9c, 0x7f780779b4e0, 0x80000, 0)                        = 3
SYS_read(3, "\177ELF\002\001\001\003", 832)                               = 832
SYS_pread(3, 0x7fffb6b62380, 784, 64)                                     = 784
SYS_pread(3, 0x7fffb6b62350, 32, 848)                                     = 32
SYS_pread(3, 0x7fffb6b62300, 68, 880)                                     = 68
SYS_fstat(3, 0x7fffb6b62610)                                              = 0
SYS_pread(3, 0x7fffb6b62260, 784, 64)                                     = 784
SYS_pread(3, 0x7fffb6b61f40, 32, 848)                                     = 32
SYS_pread(3, 0x7fffb6b61f20, 68, 880)                                     = 68
SYS_mmap(0, 0x1f1660, 1, 2050)                                            = 0x7f780757e000
SYS_mmap(0x7f78075a0000, 0x178000, 5, 2066)                               = 0x7f78075a0000
SYS_mmap(0x7f7807718000, 0x4e000, 1, 2066)                                = 0x7f7807718000
SYS_mmap(0x7f7807766000, 0x6000, 3, 2066)                                 = 0x7f7807766000
SYS_mmap(0x7f780776c000, 0x3660, 3, 50)                                   = 0x7f780776c000
SYS_close(3)                                                              = 0
SYS_openat(0xffffff9c, 0x7f780779b9d0, 0x80000, 0)                        = 3
SYS_read(3, "\177ELF\002\001\001", 832)                                   = 832
SYS_fstat(3, 0x7fffb6b625f0)                                              = 0
SYS_mmap(0, 0x8f328, 1, 2050)                                             = 0x7f78074ee000
SYS_mmap(0x7f78074f0000, 0x64000, 5, 2066)                                = 0x7f78074f0000
SYS_mmap(0x7f7807554000, 0x28000, 1, 2066)                                = 0x7f7807554000
SYS_mmap(0x7f780757c000, 8192, 3, 2066)                                   = 0x7f780757c000
SYS_close(3)                                                              = 0
SYS_openat(0xffffff9c, 0x7f780779bee0, 0x80000, 0)                        = 3
SYS_read(3, "\177ELF\002\001\001", 832)                                   = 832
SYS_fstat(3, 0x7fffb6b625d0)                                              = 0
SYS_mmap(0, 0x5110, 1, 2050)                                              = 0x7f78074e8000
SYS_mmap(0x7f78074e9000, 8192, 5, 2066)                                   = 0x7f78074e9000
SYS_mmap(0x7f78074eb000, 4096, 1, 2066)                                   = 0x7f78074eb000
SYS_mmap(0x7f78074ec000, 8192, 3, 2066)                                   = 0x7f78074ec000
SYS_close(3)                                                              = 0
SYS_openat(0xffffff9c, 0x7f780779c480, 0x80000, 0)                        = 3
SYS_read(3, "\177ELF\002\001\001", 832)                                   = 832
SYS_pread(3, 0x7fffb6b625d0, 68, 824)                                     = 68
SYS_fstat(3, 0x7fffb6b62590)                                              = 0
SYS_pread(3, 0x7fffb6b621f0, 68, 824)                                     = 68
SYS_mmap(0, 0x22478, 1, 2050)                                             = 0x7f78074c5000
SYS_mmap(0x7f78074cb000, 0x11000, 5, 2066)                                = 0x7f78074cb000
SYS_mmap(0x7f78074dc000, 0x6000, 1, 2066)                                 = 0x7f78074dc000
SYS_mmap(0x7f78074e2000, 8192, 3, 2066)                                   = 0x7f78074e2000
SYS_mmap(0x7f78074e4000, 0x3478, 3, 50)                                   = 0x7f78074e4000
SYS_close(3)                                                              = 0
SYS_mmap(0, 8192, 3, 34)                                                  = 0x7f78074c3000
SYS_arch_prctl(4098, 0x7f78074c4400, 0xffff8087f8b3b2d0, 64)              = 0
SYS_mprotect(0x7f7807766000, 16384, 1)                                    = 0
SYS_mprotect(0x7f78074e2000, 4096, 1)                                     = 0
SYS_mprotect(0x7f78074ec000, 4096, 1)                                     = 0
SYS_mprotect(0x7f780757c000, 4096, 1)                                     = 0
SYS_mprotect(0x7f7807797000, 4096, 1)                                     = 0
SYS_mprotect(0x559c88f1f000, 4096, 1)                                     = 0
SYS_mprotect(0x7f78077d3000, 4096, 1)                                     = 0
SYS_munmap(0x7f780779d000, 33738)                                         = 0
SYS_set_tid_address(0x7f78074c46d0, 0x7fffb6b634b8, 0x7f78074c4400, 0x7f78077d3f68) = 0x234b10
SYS_set_robust_list(0x7f78074c46e0, 24, 0x7f78074c4400, 0x7f78077d3f68)   = 0
SYS_rt_sigaction(32, 0x7fffb6b63200, 0, 8)                                = 0
SYS_rt_sigaction(33, 0x7fffb6b63200, 0, 8)                                = 0
SYS_rt_sigprocmask(1, 0x7fffb6b63378, 0, 8)                               = 0
SYS_prlimit64(0, 3, 0, 0x7fffb6b63360)                                    = 0
SYS_statfs("/sys/fs/selinux", 0x7fffb6b63330)                             = -2
SYS_statfs("/selinux", 0x7fffb6b63330)                                    = -2
SYS_brk(0)                                                                = 0x559c89633000
SYS_brk(0x559c89654000)                                                   = 0x559c89654000
SYS_openat(0xffffff9c, 0x7f780778f777, 0x80000, 0)                        = 3
SYS_fstat(3, 0x7fffb6b631f0)                                              = 0
SYS_read(3, "nodev\tsysfs\nnodev\ttmpfs\nnodev\tbd"..., 1024)             = 411
SYS_read(3, "", 1024)                                                     = 0
SYS_close(3)                                                              = 0
SYS_access("/etc/selinux/config", 00)                                     = -2
SYS_openat(0xffffff9c, 0x7f7807739fd0, 0x80000, 0)                        = 3
SYS_fstat(3, 0x7f780776b9e0)                                              = 0
SYS_mmap(0, 0x2e5330, 1, 2)                                               = 0x7f78071dd000
SYS_close(3)                                                              = 0
SYS_ioctl(1, 0x5401, 0x7fffb6b632b0, 0x7f7807767640)                      = 0
SYS_ioctl(1, 0x5413, 0x7fffb6b63370, 0x7f7807767640)                      = 0
SYS_openat(0xffffff9c, 0x559c896399a0, 0x90800, 0)                        = 3
SYS_fstat(3, 0x7fffb6b62ef0)                                              = 0
SYS_getdents64(3, 0x559c896399f0, 0x8000, 0)                              = 784
SYS_getdents64(3, 0x559c896399f0, 0x8000, 2)                              = 0
SYS_close(3)                                                              = 0
SYS_fstat(1, 0x7fffb6b60a30)                                              = 0
SYS_write(1, "blog  mrdrivingduck.github.io  s"..., 42blog  mrdrivingduck.github.io  snap  temp
)                   = 42
SYS_close(1)                                                              = 0
SYS_close(2)                                                              = 0
SYS_exit_group(0 <no return ...>
+++ exited (status 0) +++
```

经过查阅资料，较新版本 Ubuntu 系统中的程序不是以懒加载动态链接库的形式编译的，而 `ltrace` 的工作原理是在可执行文件的 PLT 中插入断点。如果程序不以懒加载动态链接库的形式编译，那么 PLT 中的断点压根不会被触发到，所以无法追踪到库函数调用。如果在 GCC 编译器选项中加入 `-z lazy`，则可以看到库函数的调用。

## References

[Linux — Why “ltrace” does not work on new versions of Ubuntu?](https://medium.com/@boutnaru/linux-why-ltrace-does-not-work-on-new-versions-of-ubuntu-b2d89b55b70f)

[ltrace(1) — Linux manual page](https://man7.org/linux/man-pages/man1/ltrace.1.html)

[strace(1) — Linux manual page](https://man7.org/linux/man-pages/man1/strace.1.html)
