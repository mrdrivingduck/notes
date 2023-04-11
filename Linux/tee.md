# tee

Created by : Mr Dk.

2023 / 04 / 11 11:19

Hangzhou, Zhejiang, China

---

## Background

`tee` 能够从标准输入中读取数据，然后写出到标准输出以及一个或多个文件中。相当于一个一对多的 adapter。

## Usage

```shell
$ tee --help
Usage: tee [OPTION]... [FILE]...
Copy standard input to each FILE, and also to standard output.

  -a, --append              append to the given FILEs, do not overwrite
  -i, --ignore-interrupts   ignore interrupt signals
      --help     display this help and exit
      --version  output version information and exit

If a FILE is -, copy again to standard output.

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
For complete documentation, run: info coreutils 'tee invocation'
```

ChatGPT 给出的资料：

> In Linux, the "tee" command is used to read from standard input and write to both standard output and one or more files. It allows the user to redirect the output of a command to both the screen and a file simultaneously. The syntax for using tee is as follows:
>
> ```shell
> command | tee filename
> ```
>
> This will run the "command" and print its output to the screen, while also writing it to the file specified by "filename".

## Demo

`-a` 参数用于追加写入文件，而不是从头开始写入文件。

```shell
$ echo "Hello" | tee test.txt
Hello

$ cat test.txt
Hello

$ echo "Hello" | tee -a test.txt
Hello

$ cat test.txt
Hello
Hello

```

## References

[tee(1) — Linux manual page](https://man7.org/linux/man-pages/man1/tee.1.html)

[tee command in Linux with examples - GeeksforGeeks](https://www.geeksforgeeks.org/tee-command-linux-example/)
