# cut

Created by : Mr Dk.

2022 / 12 / 01 23:56

Hangzhou, Zhejiang, China

---

## Background

`cut` 用于从每行文本中挑选出想要的内容。

## Usage

```shell
$ cut --help
Usage: cut OPTION... [FILE]...
Print selected parts of lines from each FILE to standard output.

With no FILE, or when FILE is -, read standard input.

Mandatory arguments to long options are mandatory for short options too.
  -b, --bytes=LIST        select only these bytes
  -c, --characters=LIST   select only these characters
  -d, --delimiter=DELIM   use DELIM instead of TAB for field delimiter
  -f, --fields=LIST       select only these fields;  also print any line
                            that contains no delimiter character, unless
                            the -s option is specified
  -n                      (ignored)
      --complement        complement the set of selected bytes, characters
                            or fields
  -s, --only-delimited    do not print lines not containing delimiters
      --output-delimiter=STRING  use STRING as the output delimiter
                            the default is to use the input delimiter
  -z, --zero-terminated    line delimiter is NUL, not newline
      --help     display this help and exit
      --version  output version information and exit

Use one, and only one of -b, -c or -f.  Each LIST is made up of one
range, or many ranges separated by commas.  Selected input is written
in the same order that it is read, and is written exactly once.
Each range is one of:

  N     N'th byte, character or field, counted from 1
  N-    from N'th byte, character or field, to end of line
  N-M   from N'th to M'th (included) byte, character or field
  -M    from first to M'th (included) byte, character or field

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/cut>
or available locally via: info '(coreutils) cut invocation'
```

测试文件：

```shell
$ cat example.txt
aaa bb cccc
dd e fffff
```

### 按字节定位

`-b` 参数指示在每行中取出想要的字节（1 表示第一个字节）。其参数可以有如下形式：

- 逗号分隔的枚举值
- 具有左右边界的范围
- 没有左边界的范围（从第一个字节到右边界）
- 没有右边界的范围（从左边界到最后一个字节）

```shell
$ cut -b 1,3,5 example.txt
aab
d

$ cut -b 1-3 example.txt
aaa
dd

$ cut -b 1- example.txt
aaa bb cccc
dd e fffff

$ cut -b -3 example.txt
aaa
dd
```

### 按字符定位

`-c` 参数指示在每行中取出想要的字符，使用方式与 `-b` 类似。

### 按 field 定位

`-f` 参数按特定分隔符来选择每一行中的 field。分隔符默认为 TAB，但可以使用 `-d` 参数指定：

```shell
$ cut -f 2 -d ' ' example.txt
bb
e
```

如果分隔符不存在，那么这一行也会被打印出来，除非使用 `-s` 参数。

### 取反

使用 `--complement` 用于选择出不在范围以内的所有信息：

```shell
$ cut --complement -f 2 -d ' ' example.txt
aaa cccc
dd fffff
```

### 输出分隔符

使用 `--output-delimiter` 指定输出的分隔符：

```shell
$ cut --complement --output-delimiter ':' -f 2 -d ' ' example.txt
aaa:cccc
dd:fffff
```

## References

[cut command in Linux with examples](https://www.geeksforgeeks.org/cut-command-linux-examples/)

[cut(1) — Linux manual page](https://man7.org/linux/man-pages/man1/cut.1.html)
