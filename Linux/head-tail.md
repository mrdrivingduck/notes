# head / tail

Created by : Mr Dk.

2022 / 11 / 02 23:28

Hangzhou, Zhejiang, China

---

## Background

`head` 和 `tail` 被用于打印文件的开头部分和结尾部分至标准输出流。

## Usage

默认打印 10 行：

```shell
$ head a.txt
a
b
c
d
e
f
g
h
i
j

$ tail a.txt
k
l
m
n
o
p
q
r
s
t
```

`-n` 参数可以指定行数，`-c` 参数可以指定字节数：

```shell
$ head -n 3 a.txt
a
b
c

$ tail -n 3 a.txt
r
s
t
```

```shell
$ head -c 2 a.txt
a

$ tail -c 2 a.txt
t
```

## Following

`tail` 命令有着独特的追踪选项 `-f`，因为有时需要监控一个文件尾部的变化。

`--retry` 会尝试打开一个无法被访问的文件，直到打开为止。只对初次打开文件有效：

```shell
$ tail -f --retry a.txt
tail: warning: --retry only effective for the initial open
tail: cannot open 'a.txt' for reading: No such file or directory
tail: 'a.txt' has appeared;  following new file
aaa
```

`--pid=PID` 在指定进程退出后结束追踪模式。

`-s` 指定追踪文件过程中的睡眠时间。

## References

[head(1) — Linux manual page](https://man7.org/linux/man-pages/man1/head.1.html)

[tail(1) — Linux manual page](https://man7.org/linux/man-pages/man1/tail.1.html)
