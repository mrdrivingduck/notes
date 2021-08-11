# Linux - Execve

Created by : Mr Dk.

2020 / 08 / 21 15:37

Nanjing, Jiangsu, China

---

Linux 中的 `execve()` 是一个系统调用，用于产生一个新进程，通常需要与 `fork()` 一起使用。进程通过调用 `fork()` 将当前进程完全复制一份 (只有 pid 不同)，然后再调用 `execve()` 将新进程的内存映像全部替换为想要执行的程序。

在大三学习 *操作系统* 课程时自行实现过一个 [shell](https://github.com/mrdrivingduck/dksh)，但对于其中有一些细节还是没有太明白。

## 关于 cd 和 pwd

Shell 的整体设计思想很 straight-forward：使用一个进程作为 shell 主进程，当接收到命令后，从主进程 `fork()` 出一个子进程，在子进程中调用 `execve()` 执行相应的程序。子进程结束后，回到主进程，继续接收下一条命令。在子进程调用 `execve()` 之前，需要使用 `pipe()`、`dup2()` 等系统调用处理好管道、重定向等问题。

但是 `cd` 命令就很好玩。如果通过上述流程执行 `cd`，会发现并没有效果。原因其实也很简单，每个进程在其 PCB 中记录了进程的当前工作目录 (pwd)。在阅读 Linux 内核早期版本源代码时，会看到有一个 `pwd` 属性存在于 `task_struct` 结构体中。我们希望修改的是 shell 主进程的 `pwd`，而通过上述机制启动 `/bin/cd`，不管这个程序做了什么，都是在子进程中，与主进程一点关系都没有。所以只能直接在主进程中使用 `chdir()` 系统调用完成这个功能。

真正的 shell 也证实了这一点：`cd` 由 shell 直接内部支持：

```console
$ where cd
cd: shell built-in command
```

而 `pwd` 命令是获取当前进程 PCB 中的 `pwd`。虽然说有一个 `/bin/pwd` 通过 `fork()` + `execve()` 启动也能得到一个正确的结果，但是理论上来说，直接从主进程的 PCB 中得到 `pwd` 不就好了？事实上 shell 也对 `pwd` 做了内置的支持，就是这么干的，因为这样显然更快：

```console
$ where pwd
pwd: shell built-in command
/bin/pwd
```

## 关于环境变量

在自行实现 shell 时，通常会调用封装了 `execve()` 的 POSIX C 库：

```c
#include <unistd.h>

extern char **environ;

int execl(const char *path, const char *arg, ...
                /* (char  *) NULL */);
int execlp(const char *file, const char *arg, ...
                /* (char  *) NULL */);
int execle(const char *path, const char *arg, ...
                /*, (char *) NULL, char * const envp[] */);
int execv(const char *path, char *const argv[]);
int execvp(const char *file, char *const argv[]);
int execvpe(const char *file, char *const argv[],
                char *const envp[]);
```

它们之间有何区别呢？首先，可以确定的是，`execve()` 这个系统调用的参数。除了需要调用的程序所在路径以外，还有调用程序的 **参数** 和 **环境变量**。

```c
int execve(const char * filename, char * const argv[], char * const envp[]);
```

`execl()`、`execlp()` 和 `execle()` 中的 `char *arg` 是未限定长度的可变参数，最终以 `NULL` 结尾。显然，这些参数最终会被处理为 `argv[]` 并传递给内核。而带有 `envp[]` 数组的函数则提供了环境变量信息。

`execve()` 系统调用进入内核后，内核显然需要根据第一个参数 `filename` 打开这个文件。内核支持使用 **绝对路径** 或 **相对路径** 打开文件。而对于文件名中没有 `/` 的路径，内核显然是打不开的，`execve()` 就会失败返回。如果没有环境变量的支持，在 shell 中直接键入 `ls`，内核是找不到它的，只有键入 `/bin/ls` 或到 `/bin` 下调用 `./ls` 才行。这里就体现出了环境变量的作用。

在上述函数族中，对于没有 `envp[]` 参数的库函数，在调用函数时，会隐式将当前进程的环境变量赋值到 `execve()` 的 `envp[]` 参数中。使用 strace 工具执行 `ls` 为例：

```console
$ strace ls
execve("/bin/ls", ["ls"], 0x7ffedc768f40 /* 23 vars */) = 0
...
```

可以看到，传入了 23 个环境变量。(Shell) 进程目前已有的环境变量可以通过下面的方式查看：

```console
$ env
USER=mrdrivingduck
SHLVL=1
HOME=/home/mrdrivingduck
OLDPWD=/home/mrdrivingduck/test
WSL_DISTRO_NAME=Ubuntu-18.04
LOGNAME=mrdrivingduck
WSL_INTEROP=/run/WSL/280_interop
NAME=ZJT-SURFACEBOOK2
_=/usr/bin/env
TERM=xterm-256color
PATH=/home/mrdrivingduck/.vscode-server/bin/db40434f562994116e5b21c24015a2e40b2504e6/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
LANG=C.UTF-8
SHELL=/bin/zsh
PWD=/home/mrdrivingduck/test
HOSTTYPE=x86_64
WSLENV=VSCODE_WSL_EXT_LOCATION/up
ZSH=/home/mrdrivingduck/.oh-my-zsh
...
```

如果 POSIX C 库函数发现 `filename` 中没有 `/`，就会到环境变量中尝试拼接出文件的绝对路径，再调用 `execve()`。做一个小小的验证：

```c
#include <stdio.h>
#include <unistd.h>

int main()
{
    char *argv[] = { "ls", NULL };
    // char *evnp[] = { "aaa=1", "bbb=2", NULL };
    execvp("ls", argv);
    return 0;
}
```

这个程序使用 shell 进程的内置环境变量。用 strace 执行这个程序。给出的程序名是 `ls`，看看 shell (或者说 `execvp()` 库函数) 替我们做了些啥：

```console
$ strace ./test 
execve("./test", ["./test"], 0x7ffca90f0de0 /* 33 vars */) = 0
brk(NULL)                               = 0x56142cb23000

...

execve("/home/mrdrivingduck/.vscode-server/bin/db40434f562994116e5b21c24015a2e40b2504e6/bin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/usr/local/sbin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/usr/local/bin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/usr/sbin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/usr/bin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/sbin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = -1 ENOENT (No such file or directory)
execve("/bin/ls", ["ls"], 0x7ffe5ca16dd8 /* 33 vars */) = 0
brk(NULL)                               = 0x556ee5f06000

...

fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 2), ...}) = 0
write(1, "test  test.c\n", 13test  test.c
)          = 13
close(1)                                = 0
close(2)                                = 0
exit_group(0)                           = ?
+++ exited with 0 +++
```

Shell 首先以 `./test` 和内置环境变量执行了测试程序。之后发现 `ls` 不是一个绝对路径或相对路径，于是使用环境变量中的 `PATH` 依次拼接出了文件绝对路径，并调用 `execve()` 系统调用。显然，前几个都失败了，因为文件不存在；直到拼接为 `/bin/ls` 时，内核找到了相应的可执行文件。之后，这个程序被成功执行，打印了当前目录下的所有文件名。

然而，如果调用了带有 `envp[]` 参数的库函数，那么进程内置的环境变量将不再传递到 `execve()` 系统调用中。看看另一个测试程序：

```c
#include <stdio.h>
#include <unistd.h>

int main()
{
    char *argv[] = { "ls", NULL };
    char *evnp[] = { "aaa=1", "bbb=2", NULL };
    execve("ls", argv, evnp);
    return 0;
}
```

它的 strace 结果如下：

```console
$ strace ./test 
execve("./test", ["./test"], 0x7ffdee5a50d0 /* 33 vars */) = 0
brk(NULL)                               = 0x55882ca47000

...

execve("ls", ["ls"], 0x7fff37460b70 /* 2 vars */) = -1 ENOENT (No such file or directory)
exit_group(0)                           = ?
+++ exited with 0 +++
```

首先，shell 以 **内置的 33 个环境变量** 和 **相对路径** 替我执行了测试程序。在测试程序中调用 `execve()` 时，由于程序显式给出了环境变量，因此环境变量个数变为了 **两个**。由于环境变量中不再包含 `PATH`，因此 shell 也不知道如何将这个 `ls` 补全为一个完整的文件路径。调用了一次 `execve()` 系统调用后得到了失败结果，原因是 `ENOENT` (找不到文件或路径)。

由此可以看出，`envp[]` 参数会完全替换父进程的环境变量。如果需要使用到父进程中的一些环境变量，那么需要对 `envp[]` 的构造做一些处理工作。另外，内核只能通过绝对路径或相对路径找到文件；那么将没有 `/` 的文件名通过 `PATH` 环境变量扩展为内核能够识别的合法文件名，就是 shell (或者说是 `execvp()`) 的责任了。

另外提及一下环境变量的生命周期。环境变量分为：

* 永久变量
* 临时变量

永久变量被记录在配置文件中。每当 shell 启动时，会将这些变量读取到进程环境变量中；而临时性变量只能在 shell 中通过 `export` 设置，设置完毕后会立即生效，但关闭 shell 后将会失效 (易失的)。

---

## References

[execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)

[Linux and Unix pwd command tutorial with examples](https://shapeshed.com/unix-pwd/)

[Wikipedia - exec (system call)](https://en.wikipedia.org/wiki/Exec_(system_call))

[Wikipedia - cd (command)](https://en.wikipedia.org/wiki/Cd_(command))

[Wikipedia - pwd](https://en.wikipedia.org/wiki/Pwd)

---

