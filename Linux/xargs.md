# xargs

Created by : Mr Dk.

2022 / 12 / 05 01:11

Hangzhou, Zhejiang, China

---

## Background

`xargs` 用于从标准输入流中构造并执行命令。很多 Linux 程序是从标准输入流中接收输入参数的，这种程序可以作为管道的接收端，接收另一个程序输出到管道中的数据。然而有一些 Linux 程序是通过参数来接收输入的，这类程序无法作为管道的接收端。`xargs` 可以作为一个 adapter，在管道的接收端使用标准输入流接收数据，然后将数据构造为另一个 Linux 程序的参数，并执行这个程序。

## Usage

```shell
$ xargs --help
Usage: xargs [OPTION]... COMMAND [INITIAL-ARGS]...
Run COMMAND with arguments INITIAL-ARGS and more arguments read from input.

Mandatory and optional arguments to long options are also
mandatory or optional for the corresponding short option.
  -0, --null                   items are separated by a null, not whitespace;
                                 disables quote and backslash processing and
                                 logical EOF processing
  -a, --arg-file=FILE          read arguments from FILE, not standard input
  -d, --delimiter=CHARACTER    items in input stream are separated by CHARACTER,
                                 not by whitespace; disables quote and backslash
                                 processing and logical EOF processing
  -E END                       set logical EOF string; if END occurs as a line
                                 of input, the rest of the input is ignored
                                 (ignored if -0 or -d was specified)
  -e, --eof[=END]              equivalent to -E END if END is specified;
                                 otherwise, there is no end-of-file string
  -I R                         same as --replace=R
  -i, --replace[=R]            replace R in INITIAL-ARGS with names read
                                 from standard input; if R is unspecified,
                                 assume {}
  -L, --max-lines=MAX-LINES    use at most MAX-LINES non-blank input lines per
                                 command line
  -l[MAX-LINES]                similar to -L but defaults to at most one non-
                                 blank input line if MAX-LINES is not specified
  -n, --max-args=MAX-ARGS      use at most MAX-ARGS arguments per command line
  -o, --open-tty               Reopen stdin as /dev/tty in the child process
                                 before executing the command; useful to run an
                                 interactive application.
  -P, --max-procs=MAX-PROCS    run at most MAX-PROCS processes at a time
  -p, --interactive            prompt before running commands
      --process-slot-var=VAR   set environment variable VAR in child processes
  -r, --no-run-if-empty        if there are no arguments, then do not run COMMAND;
                                 if this option is not given, COMMAND will be
                                 run at least once
  -s, --max-chars=MAX-CHARS    limit length of command line to MAX-CHARS
      --show-limits            show limits on command-line length
  -t, --verbose                print commands before executing them
  -x, --exit                   exit if the size (see -s) is exceeded
      --help                   display this help and exit
      --version                output version information and exit

Please see also the documentation at http://www.gnu.org/software/findutils/.
You can report (and track progress on fixing) bugs in the "xargs"
program via the GNU findutils bug-reporting page at
https://savannah.gnu.org/bugs/?group=findutils or, if
you have no web access, by sending email to <bug-findutils@gnu.org>.
```

### 参数识别

`xargs` 默认通过标准输入流中获得的空格来分割参数。但万一输入流中的数据本身就包含空格呢？`-0` 参数可以让 `xargs` 使用输入流中的 `\0` 字符来分割参数。假设我们有一个文件名中带空格的文件，把这个文件名通过 `xargs` 输入给 `rm` 程序，将会看到：

```shell
$ ls
'a a.txt'

$ find ./ -type f | xargs rm
rm: cannot remove './a': No such file or directory
rm: cannot remove 'a.txt': No such file or directory
```

这说明 `xargs` 从输入流中把 `a` 识别为了一个参数，把 `a.txt` 识别为了一个参数，然后把这两个参数传给了 `rm`。显然 `rm` 找不到这两个文件。所以我们需要：

1. 使用 `-print0` 让 `find` 程序对每一条输出结果加一个 `\0`
2. 使用 `-0` 让 `xargs` 使用 `\0` 来识别参数

```shell
$ find ./ -type f -print0 | xargs -0 rm
```

使用 `-d` 参数可以自定义参数分隔字符。

### 命令浏览

使用 `-t` 参数可以让 `xargs` 打印将要执行的命令。以上一个例子为例，可以很容易地看出为什么执行失败了：因为 `rm` 接收了两个被拆分的参数：

```shell
$ find ./ -type f | xargs -t rm
rm ./a a.txt
rm: cannot remove './a': No such file or directory
rm: cannot remove 'a.txt': No such file or directory

$ find ./ -type f -print0 | xargs -t -0 rm
rm './a a.txt'
```

### 手动确认执行

使用 `-p` 参数可以让 `xargs` 打印将要执行的命令，并让用户手动确定后才开始执行。以上面的例子为例，只有按下回车后，命令才会被真正执行：

```shell
$ find ./ -type f -print0 | xargs -p -0 rm
rm './a a.txt' ?...
```

### 参数占位符

如果将要执行的命令中会多次使用同一个参数该怎么做呢？以上面的例子为例，如果想要先打印文件名，再删除那个文件，就不得不引用 `find` 的输出结果两次。使用 `-I` 参数可以指定一个占位符：

```shell
$ find ./ -type f -print0 | xargs -0 -I % sh -c 'echo %; rm "%";'
./a a.txt
```

文件名被成功打印，同时文件也被成功删除。

### 从文件获取输入

前面的例子全部使用标准输入流（实际上是管道）获取输入。`xargs` 也支持使用 `-a` 参数从文件中获取输入。

### 参数个数指定

当 `xargs` 获取到多个参数时，应该把这些参数一股脑灌给将要执行的命令，还是将每个参数作为后续命令的唯一参数，多次执行后续命令呢？使用 `-n` 参数来控制输入给后续命令的参数个数：

```shell
$ touch a b c
$ find ./ -type f -print0 | xargs -t -0 -n 1 rm
rm ./b
rm ./a
rm ./c

$ touch a b c
$ find ./ -type f -print0 | xargs -t -0 rm
rm ./b ./a ./c
```

## References

[Linux and Unix xargs command tutorial with examples](https://shapeshed.com/unix-xargs/)

[xargs(1) — Linux manual page](https://man7.org/linux/man-pages/man1/xargs.1.html)

[How to Use the Linux xargs Command](https://phoenixnap.com/kb/xargs-command)
