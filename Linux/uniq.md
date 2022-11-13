# uniq

Created by : Mr Dk.

2022 / 11 / 14 0:18

Hangzhou, Zhejiang, China

---

## Background

`uniq` 用来对输入做按行为单位的去重。实现过去重算法的人都清楚，想要真正实现去重，输入必须是排过序的，这样重复元素一定会在相邻的位置排列，从而被方便地移除。`uniq` 只实现去重，并不管排序。在绝大部分情况下，`uniq` 可能需要与 `sort` 搭配使用，才能起到预期的效果。

## Usage

```shell
$ uniq --help
Usage: uniq [OPTION]... [INPUT [OUTPUT]]
Filter adjacent matching lines from INPUT (or standard input),
writing to OUTPUT (or standard output).

With no options, matching lines are merged to the first occurrence.

Mandatory arguments to long options are mandatory for short options too.
  -c, --count           prefix lines by the number of occurrences
  -d, --repeated        only print duplicate lines, one for each group
  -D                    print all duplicate lines
      --all-repeated[=METHOD]  like -D, but allow separating groups
                                 with an empty line;
                                 METHOD={none(default),prepend,separate}
  -f, --skip-fields=N   avoid comparing the first N fields
      --group[=METHOD]  show all items, separating groups with an empty line;
                          METHOD={separate(default),prepend,append,both}
  -i, --ignore-case     ignore differences in case when comparing
  -s, --skip-chars=N    avoid comparing the first N characters
  -u, --unique          only print unique lines
  -z, --zero-terminated     line delimiter is NUL, not newline
  -w, --check-chars=N   compare no more than N characters in lines
      --help     display this help and exit
      --version  output version information and exit

A field is a run of blanks (usually spaces and/or TABs), then non-blank
characters.  Fields are skipped before chars.

Note: 'uniq' does not detect repeated lines unless they are adjacent.
You may want to sort the input first, or use 'sort -u' without 'uniq'.
Also, comparisons honor the rules specified by 'LC_COLLATE'.

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/uniq>
or available locally via: info '(coreutils) uniq invocation'
```

使用一个测试文件 `example.txt`：

```
aaa aaa aaa
aaa aaa aaa
bbb aaa aaa
bbb aaa aaa
ccc aaa
```

### 输出重复次数

使用 `-c` 参数可以输出每个唯一行的重复次数：

```shell
$ uniq -c example.txt
      2 aaa aaa aaa
      2 bbb aaa aaa
      1 ccc aaa
```

### 输出行

`-D` 参数可以输出所有 **重复** 的行，但不做去重：

```shell
$ uniq -D example.txt
aaa aaa aaa
aaa aaa aaa
bbb aaa aaa
bbb aaa aaa
```

`-d` 参数可以输出所有 **重复** 的行，并做去重：

```shell
$ uniq -d example.txt
aaa aaa aaa
bbb aaa aaa
```

`-u` 参数可以输出所有的 **唯一** 行：

```shell
$ uniq -u example.txt
ccc aaa
```

### 非完整行去重

使用 `-f N` 参数可以在开始比较行的唯一性之前跳过 `N` 个域（空格分隔开的字符组为一个域）。在上述示例中，每行忽略第一个字符组并去重后，应当只会有两个唯一的字符组。以下输出就是两个字符组的 leader：

```shell
$ uniq -f 1 example.txt
aaa aaa aaa
ccc aaa
```

使用 `-s N` 参数可以在开始比较行的唯一性之前跳过 `N` 个字符。与 `-f` 选项类似：

```shell
$ uniq -s 4 example.txt
aaa aaa aaa
ccc aaa
```

使用 `-w N` 参数可以只使用前 `N` 个字符来比较行的唯一性：

```shell
$ uniq -w 3 example.txt
aaa aaa aaa
bbb aaa aaa
ccc aaa
```

使用 `-i` 参数可以在进行行比较时忽略大小写。

## References

[uniq Command in LINUX with examples - GeeksforGeeks](https://www.geeksforgeeks.org/uniq-command-in-linux-with-examples/)

[uniq(1) — Linux manual page](https://man7.org/linux/man-pages/man1/uniq.1.html)
