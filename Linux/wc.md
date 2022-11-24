# wc

Created by : Mr Dk.

2022 / 11 / 25 0:19

Hangzhou, Zhejiang, China

---

## Background

`wc` 用于打印每个文件的行数、单词数和字节数。

## Usage

```shell
$ wc --help
Usage: wc [OPTION]... [FILE]...
  or:  wc [OPTION]... --files0-from=F
Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified.  A word is a non-zero-length sequence of
characters delimited by white space.

With no FILE, or when FILE is -, read standard input.

The options below may be used to select which counts are printed, always in
the following order: newline, word, character, byte, maximum line length.
  -c, --bytes            print the byte counts
  -m, --chars            print the character counts
  -l, --lines            print the newline counts
      --files0-from=F    read input from the files specified by
                           NUL-terminated names in file F;
                           If F is - then read names from standard input
  -L, --max-line-length  print the maximum display width
  -w, --words            print the word counts
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/wc>
or available locally via: info '(coreutils) wc invocation'
```

如示例所示，文件中有两行、6 个单词、23 个字节：

```shell
$ cat example.txt
aaa bb cccc
dd e fffff

$ wc example.txt
 2  6 23 example.txt
```

通过 `-l` / `-w` / `-c` 参数可以分别打印上述的行数、单词数、字节数：

```shell
$ wc -l example.txt
2 example.txt

$ wc -w example.txt
6 example.txt

$ wc -c example.txt
23 example.txt
```

`-m` 选项用于打印 **字符数**。

`-l` 选项可以打印长度最长的行的长度：

```shell
$ wc -L example.txt
11 example.txt
```

## References

[wc(1) - Linux man page](https://linux.die.net/man/1/wc)

[wc command in Linux with examples](https://www.geeksforgeeks.org/wc-command-linux-examples/)
