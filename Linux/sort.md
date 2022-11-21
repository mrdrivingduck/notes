# sort

Created by : Mr Dk.

2022 / 11 / 21 23:27

Hangzhou, Zhejiang, China

---

## Background

`sort` 用于对文件中的行进行排序。默认的排序方式是按照 ASCII 码大小排序，可以指定选项进行数值排序。

## Usage

```shell
$ sort --help
Usage: sort [OPTION]... [FILE]...
  or:  sort [OPTION]... --files0-from=F
Write sorted concatenation of all FILE(s) to standard output.

With no FILE, or when FILE is -, read standard input.

Mandatory arguments to long options are mandatory for short options too.
Ordering options:

  -b, --ignore-leading-blanks  ignore leading blanks
  -d, --dictionary-order      consider only blanks and alphanumeric characters
  -f, --ignore-case           fold lower case to upper case characters
  -g, --general-numeric-sort  compare according to general numerical value
  -i, --ignore-nonprinting    consider only printable characters
  -M, --month-sort            compare (unknown) < 'JAN' < ... < 'DEC'
  -h, --human-numeric-sort    compare human readable numbers (e.g., 2K 1G)
  -n, --numeric-sort          compare according to string numerical value
  -R, --random-sort           shuffle, but group identical keys.  See shuf(1)
      --random-source=FILE    get random bytes from FILE
  -r, --reverse               reverse the result of comparisons
      --sort=WORD             sort according to WORD:
                                general-numeric -g, human-numeric -h, month -M,
                                numeric -n, random -R, version -V
  -V, --version-sort          natural sort of (version) numbers within text

Other options:

      --batch-size=NMERGE   merge at most NMERGE inputs at once;
                            for more use temp files
  -c, --check, --check=diagnose-first  check for sorted input; do not sort
  -C, --check=quiet, --check=silent  like -c, but do not report first bad line
      --compress-program=PROG  compress temporaries with PROG;
                              decompress them with PROG -d
      --debug               annotate the part of the line used to sort,
                              and warn about questionable usage to stderr
      --files0-from=F       read input from the files specified by
                            NUL-terminated names in file F;
                            If F is - then read names from standard input
  -k, --key=KEYDEF          sort via a key; KEYDEF gives location and type
  -m, --merge               merge already sorted files; do not sort
  -o, --output=FILE         write result to FILE instead of standard output
  -s, --stable              stabilize sort by disabling last-resort comparison
  -S, --buffer-size=SIZE    use SIZE for main memory buffer
  -t, --field-separator=SEP  use SEP instead of non-blank to blank transition
  -T, --temporary-directory=DIR  use DIR for temporaries, not $TMPDIR or /tmp;
                              multiple options specify multiple directories
      --parallel=N          change the number of sorts run concurrently to N
  -u, --unique              with -c, check for strict ordering;
                              without -c, output only the first of an equal run
  -z, --zero-terminated     line delimiter is NUL, not newline
      --help     display this help and exit
      --version  output version information and exit

KEYDEF is F[.C][OPTS][,F[.C][OPTS]] for start and stop position, where F is a
field number and C a character position in the field; both are origin 1, and
the stop position defaults to the line's end.  If neither -t nor -b is in
effect, characters in a field are counted from the beginning of the preceding
whitespace.  OPTS is one or more single-letter ordering options [bdfgiMhnRrV],
which override global ordering options for that key.  If no key is given, use
the entire line as the key.  Use --debug to diagnose incorrect key usage.

SIZE may be followed by the following multiplicative suffixes:
% 1% of memory, b 1, K 1024 (default), and so on for M, G, T, P, E, Z, Y.

*** WARNING ***
The locale specified by the environment affects sort order.
Set LC_ALL=C to get the traditional sort order that uses
native byte values.

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/sort>
or available locally via: info '(coreutils) sort invocation'
```

使用一个测试文件 `example.txt`：

```shell
$ cat example.txt
233
543
138
3556
```

### 降序排序

使用 `-r` 选项：

```shell
$ sort -r example.txt
543
3556
233
138
```

### 按数值排序

使用 `-n` 选项：

```shell
$ sort -n example.txt
138
233
543
3556
```

### 按特定列排序

使用 `-k 2` 对第二列进行排序。

### 检查是否有序

使用 `-c` 参数：

```shell
$ sort -c example.txt
sort: example.txt:3: disorder: 138
```

### 去重

使用 `-u` 参数移除排序后重复的元素。

### 归并

使用 `-m` 参数合并多个已经有序的文件。

### 性能

排序时影响性能的两个重大因素：内存大小、并行度。

- 使用 `-S 10G` / `-S 50%` 可以指定用于排序的内存大小或物理内存百分比
- 使用 `--parallel=8` 可以指定排序并行度

## References

[SORT command in Linux/Unix with examples - GeeksforGeeks](https://www.geeksforgeeks.org/sort-command-linuxunix-examples/)

[sort(1) — Linux manual page](https://man7.org/linux/man-pages/man1/sort.1.html)
