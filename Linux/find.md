# find

Created by : Mr Dk.

2022 / 11 / 10 0:15

Hangzhou, Zhejiang, China

---

## Background

`find` 用于根据指定的规则，从指定的目录开始搜索目录树。

## Usage

```shell
$ find --help
Usage: find [-H] [-L] [-P] [-Olevel] [-D debugopts] [path...] [expression]

default path is the current directory; default expression is -print
expression may consist of: operators, options, tests, and actions:
operators (decreasing precedence; -and is implicit where no others are given):
      ( EXPR )   ! EXPR   -not EXPR   EXPR1 -a EXPR2   EXPR1 -and EXPR2
      EXPR1 -o EXPR2   EXPR1 -or EXPR2   EXPR1 , EXPR2
positional options (always true): -daystart -follow -regextype

normal options (always true, specified before other expressions):
      -depth --help -maxdepth LEVELS -mindepth LEVELS -mount -noleaf
      --version -xdev -ignore_readdir_race -noignore_readdir_race
tests (N can be +N or -N or N): -amin N -anewer FILE -atime N -cmin N
      -cnewer FILE -ctime N -empty -false -fstype TYPE -gid N -group NAME
      -ilname PATTERN -iname PATTERN -inum N -iwholename PATTERN -iregex PATTERN
      -links N -lname PATTERN -mmin N -mtime N -name PATTERN -newer FILE
      -nouser -nogroup -path PATTERN -perm [-/]MODE -regex PATTERN
      -readable -writable -executable
      -wholename PATTERN -size N[bcwkMG] -true -type [bcdpflsD] -uid N
      -used N -user NAME -xtype [bcdpfls]      -context CONTEXT

actions: -delete -print0 -printf FORMAT -fprintf FILE FORMAT -print
      -fprint0 FILE -fprint FILE -ls -fls FILE -prune -quit
      -exec COMMAND ; -exec COMMAND {} + -ok COMMAND ;
      -execdir COMMAND ; -execdir COMMAND {} + -okdir COMMAND ;

Valid arguments for -D:
exec, opt, rates, search, stat, time, tree, all, help
Use '-D help' for a description of the options, or see find(1)

Please see also the documentation at http://www.gnu.org/software/findutils/.
You can report (and track progress on fixing) bugs in the "find"
program via the GNU findutils bug-reporting page at
https://savannah.gnu.org/bugs/?group=findutils or, if
you have no web access, by sending email to <bug-findutils@gnu.org>.
```

`find` 命令的参数分为：

- 选项：
  - `-H` / `-L` / `-P` 控制对待符号链接的方式
  - `-O` 表示后续搜索表达式的重排序优化等级
  - `-D` 用于打印一些调试信息
- 起始搜索位置
- 搜索表达式（五花八门）

### Search

按文件名搜索：

```shell
find ./ -name aaa.txt
```

按文件 pattern 搜索：

```shell
find ./ -name aaa.txt
```

按文件权限搜索：

```shell
find ./ -perm 664
```

按文件类型搜索：

```shell
find ./ -type f -name "*.txt"
```

- `b`：block (buffered) special
- `c`：character (unbuffered) special
- `d`：directory
- `p`：named pipe (FIFO)
- `f`：regular file
- `l`：symbolic link
- `s`：socket
- `D`：door (Solaris)

此外，还可以按文件大小、文件修改时间、文件所属用户等信息作为搜索条件。

### Actions

对匹配的文件执行命令。匹配命中的文件名会被填写到 `{}` 中：

```shell
find ./ -name sample.txt -exec rm -i {} \;
```

此外，还可以删除文件、格式化打印文件名等。

## References

[find(1) — Linux manual page](https://man7.org/linux/man-pages/man1/find.1.html)

[find command in Linux with examples](https://www.geeksforgeeks.org/find-command-in-linux-with-examples/)
