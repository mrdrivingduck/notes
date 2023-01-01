# du

Created by : Mr Dk.

2023 / 01 / 01 23:11

Hangzhou, Zhejiang, China

---

## Background

`du` 用于查看文件的空间使用量。

## Usage

```shell
$ du --help
Usage: du [OPTION]... [FILE]...
  or:  du [OPTION]... --files0-from=F
Summarize disk usage of the set of FILEs, recursively for directories.

Mandatory arguments to long options are mandatory for short options too.
  -0, --null            end each output line with NUL, not newline
  -a, --all             write counts for all files, not just directories
      --apparent-size   print apparent sizes, rather than disk usage; although
                          the apparent size is usually smaller, it may be
                          larger due to holes in ('sparse') files, internal
                          fragmentation, indirect blocks, and the like
  -B, --block-size=SIZE  scale sizes by SIZE before printing them; e.g.,
                           '-BM' prints sizes in units of 1,048,576 bytes;
                           see SIZE format below
  -b, --bytes           equivalent to '--apparent-size --block-size=1'
  -c, --total           produce a grand total
  -D, --dereference-args  dereference only symlinks that are listed on the
                          command line
  -d, --max-depth=N     print the total for a directory (or file, with --all)
                          only if it is N or fewer levels below the command
                          line argument;  --max-depth=0 is the same as
                          --summarize
      --files0-from=F   summarize disk usage of the
                          NUL-terminated file names specified in file F;
                          if F is -, then read names from standard input
  -H                    equivalent to --dereference-args (-D)
  -h, --human-readable  print sizes in human readable format (e.g., 1K 234M 2G)
      --inodes          list inode usage information instead of block usage
  -k                    like --block-size=1K
  -L, --dereference     dereference all symbolic links
  -l, --count-links     count sizes many times if hard linked
  -m                    like --block-size=1M
  -P, --no-dereference  don't follow any symbolic links (this is the default)
  -S, --separate-dirs   for directories do not include size of subdirectories
      --si              like -h, but use powers of 1000 not 1024
  -s, --summarize       display only a total for each argument
  -t, --threshold=SIZE  exclude entries smaller than SIZE if positive,
                          or entries greater than SIZE if negative
      --time            show time of the last modification of any file in the
                          directory, or any of its subdirectories
      --time=WORD       show time as WORD instead of modification time:
                          atime, access, use, ctime or status
      --time-style=STYLE  show times using STYLE, which can be:
                            full-iso, long-iso, iso, or +FORMAT;
                            FORMAT is interpreted like in 'date'
  -X, --exclude-from=FILE  exclude files that match any pattern in FILE
      --exclude=PATTERN    exclude files that match PATTERN
  -x, --one-file-system    skip directories on different file systems
      --help     display this help and exit
      --version  output version information and exit

Display values are in units of the first available SIZE from --block-size,
and the DU_BLOCK_SIZE, BLOCK_SIZE and BLOCKSIZE environment variables.
Otherwise, units default to 1024 bytes (or 512 if POSIXLY_CORRECT is set).

The SIZE argument is an integer and optional unit (example: 10K is 10*1024).
Units are K,M,G,T,P,E,Z,Y (powers of 1024) or KB,MB,... (powers of 1000).

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/du>
or available locally via: info '(coreutils) du invocation'
```

### 打印当前目录下所有子目录的空间占用

```shell
$ du
4       ./certbot/2582
4       ./certbot/2618
4       ./certbot/common
16      ./certbot
20      .
```

如果也需要打印文件的大小占用，则使用 `-a` 参数：

```shell
$ du -a
4       ./certbot/2582
4       ./certbot/2618
4       ./certbot/common
0       ./certbot/current
16      ./certbot
20      .
```

### 以人类可读的格式打印

使用 `-h` 参数：

```shell
$ du -h
4.0K    ./certbot/2582
4.0K    ./certbot/2618
4.0K    ./certbot/common
16K     ./certbot
20K     .
```

### 打印文件的最后修改时间

使用 `--time` 参数：

```shell
$ du -h --time
4.0K    2022-03-03 10:15        ./certbot/2582
4.0K    2022-03-03 10:15        ./certbot/2618
4.0K    2022-03-03 10:15        ./certbot/common
16K     2022-12-17 08:07        ./certbot
20K     2022-12-17 08:07        .
```

### 递归深度控制

当什么参数都不加时，默认递归到最深层。

使用 `-d` 参数可以指定递归的最深层层数：

```shell
$ du -h -d 1
16K     ./certbot
20K     .
```

使用 `-s` 参数可以只递归到当前层，等价于 `-d 0`：

```shell
$ du -h -s
20K     .
```

## References

[Linux commands: du and the options you should be using](https://www.redhat.com/sysadmin/du-command-options)

[du(1) — Linux manual page](https://man7.org/linux/man-pages/man1/du.1.html)
