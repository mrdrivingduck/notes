# grep

Created by : Mr Dk.

2022 / 11 / 27 14:17

Hangzhou, Zhejiang, China

---

## Background

`grep` 用于打印文件中与给定条件匹配的行。

## Usage

```shell
$ grep --help
Usage: grep [OPTION]... PATTERNS [FILE]...
Search for PATTERNS in each FILE.
Example: grep -i 'hello world' menu.h main.c
PATTERNS can contain multiple patterns separated by newlines.

Pattern selection and interpretation:
  -E, --extended-regexp     PATTERNS are extended regular expressions
  -F, --fixed-strings       PATTERNS are strings
  -G, --basic-regexp        PATTERNS are basic regular expressions
  -P, --perl-regexp         PATTERNS are Perl regular expressions
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -f, --file=FILE           take PATTERNS from FILE
  -i, --ignore-case         ignore case distinctions in patterns and data
      --no-ignore-case      do not ignore case distinctions (default)
  -w, --word-regexp         match only whole words
  -x, --line-regexp         match only whole lines
  -z, --null-data           a data line ends in 0 byte, not newline

Miscellaneous:
  -s, --no-messages         suppress error messages
  -v, --invert-match        select non-matching lines
  -V, --version             display version information and exit
      --help                display this help text and exit

Output control:
  -m, --max-count=NUM       stop after NUM selected lines
  -b, --byte-offset         print the byte offset with output lines
  -n, --line-number         print line number with output lines
      --line-buffered       flush output on every line
  -H, --with-filename       print file name with output lines
  -h, --no-filename         suppress the file name prefix on output
      --label=LABEL         use LABEL as the standard input file name prefix
  -o, --only-matching       show only nonempty parts of lines that match
  -q, --quiet, --silent     suppress all normal output
      --binary-files=TYPE   assume that binary files are TYPE;
                            TYPE is 'binary', 'text', or 'without-match'
  -a, --text                equivalent to --binary-files=text
  -I                        equivalent to --binary-files=without-match
  -d, --directories=ACTION  how to handle directories;
                            ACTION is 'read', 'recurse', or 'skip'
  -D, --devices=ACTION      how to handle devices, FIFOs and sockets;
                            ACTION is 'read' or 'skip'
  -r, --recursive           like --directories=recurse
  -R, --dereference-recursive  likewise, but follow all symlinks
      --include=GLOB        search only files that match GLOB (a file pattern)
      --exclude=GLOB        skip files that match GLOB
      --exclude-from=FILE   skip files that match any file pattern from FILE
      --exclude-dir=GLOB    skip directories that match GLOB
  -L, --files-without-match  print only names of FILEs with no selected lines
  -l, --files-with-matches  print only names of FILEs with selected lines
  -c, --count               print only a count of selected lines per FILE
  -T, --initial-tab         make tabs line up (if needed)
  -Z, --null                print 0 byte after FILE name

Context control:
  -B, --before-context=NUM  print NUM lines of leading context
  -A, --after-context=NUM   print NUM lines of trailing context
  -C, --context=NUM         print NUM lines of output context
  -NUM                      same as --context=NUM
      --color[=WHEN],
      --colour[=WHEN]       use markers to highlight the matching strings;
                            WHEN is 'always', 'never', or 'auto'
  -U, --binary              do not strip CR characters at EOL (MSDOS/Windows)

When FILE is '-', read standard input.  With no FILE, read '.' if
recursive, '-' otherwise.  With fewer than two FILEs, assume -h.
Exit status is 0 if any line (or file if -L) is selected, 1 otherwise;
if any error occurs and -q is not given, the exit status is 2.

Report bugs to: bug-grep@gnu.org
GNU grep home page: <http://www.gnu.org/software/grep/>
General help using GNU software: <https://www.gnu.org/gethelp/>
```

### Example

```shell
$ cat example.txt
aaa bb cccc
dd e fffff
```

### Output

以下选项影响输出内容。

`-v` 打印 **不匹配** 的内容。

`-c` 参数打印匹配的行数，而不是匹配的行：

```shell
$ grep -c bb example.txt
1
```

`-l` / `-L` 打印匹配或不匹配条件的文件名：

```shell
$ grep -l bb example.txt
example.txt
```

`-o` 只打印匹配的模式串，而不是一整行：

```shell
$ grep -o bb example.txt
bb
```

`-n` 额外打印匹配上的文件行号：

```shell
$ grep -n bb example.txt
1:aaa bb cccc
```

`-A` / `-B` / `-C` 打印匹配位置的前 / 后 / 前后 N 行：

```shell
$ grep -A1 bb example.txt
aaa bb cccc
dd e fffff
```

### Matching

`-R` 参数递归匹配目录下的所有文件：

```shell
$ grep -R -l bb ./
./.oh-my-zsh/tools/upgrade.sh
./.oh-my-zsh/tools/changelog.sh
```

`-i` 参数在匹配时忽视大小写：

```shell
$ grep -i BB example.txt
aaa bb cccc
```

`-w` / `-x` 只匹配整个词或整行，而不是匹配子串：

```shell
$ grep -w b example.txt

$ grep -w bb example.txt
aaa bb cccc

$ grep -x 'bb' example.txt

$ grep -x 'aaa bb cccc' example.txt
aaa bb cccc
```

`grep` 实际上可以使用正则表达式进行匹配：

```shell
$ grep '^aaa' example.txt
aaa bb cccc
```

`-e` 参数指定多个正则表达式：

```shell
$ grep -e '^aaa' -e 'f$'  example.txt
aaa bb cccc
dd e fffff
```

也可以直接把正则表达式写到一个文件里，然后通过 `-f` 参数引用：

```shell
$ grep -f pattern.txt  example.txt
```

## References

[grep command in Unix/Linux](https://www.geeksforgeeks.org/grep-command-in-unixlinux/)

[grep(1) — Linux manual page](https://man7.org/linux/man-pages/man1/grep.1.html)
