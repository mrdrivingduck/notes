# gzip

Created by : Mr Dk.

2022 / 10 / 26 23:13

Hangzhou, Zhejiang, China

---

## Background

`gzip` 工具用于对文件进行压缩或解压缩。每个独立的文件会被压缩为一个独立的文件，压缩后的文件包含压缩头部和压缩数据，以 `.gz` 结尾。`gzip` 使用 [Lempel-Ziv coding (LZ77)](https://en.wikipedia.org/wiki/LZ77_and_LZ78) 无损压缩算法进行压缩。压缩或解压缩后的文件将会保留相同的所有权、访问模式和修改时间。符号链接会被跳过，因为 `gzip` 只压缩正经文件。

`gzip` 和 `zip` 都是非常常用的压缩工具，但 `gzip` 在压缩大量文件时比 `zip` 表现更好。`gzip` 的常用使用场景是将所有的文件归档到一个独立的归档文件中，然后再对这个独立的归档文件进行压缩。相比之下，`zip` 会将每一个文件单独压缩后，归档到一个压缩包中。这意味着如果想解压缩其中的一个文件，`zip` 的压缩包只需要局部解压即可，而 `gzip` 需要完整解压；但 `gzip` 可以更好地利用多个文件之间的冗余进行压缩，`zip` 就不行了。所以把尽可能多的文件并在一起输入给 `gzip` 会有更好的效果。

## Syntax

```shell:no-line-numbers
$ gzip --help
Usage: gzip [OPTION]... [FILE]...
Compress or uncompress FILEs (by default, compress FILES in-place).

Mandatory arguments to long options are mandatory for short options too.

  -c, --stdout      write on standard output, keep original files unchanged
  -d, --decompress  decompress
  -f, --force       force overwrite of output file and compress links
  -h, --help        give this help
  -k, --keep        keep (don't delete) input files
  -l, --list        list compressed file contents
  -L, --license     display software license
  -n, --no-name     do not save or restore the original name and timestamp
  -N, --name        save or restore the original name and timestamp
  -q, --quiet       suppress all warnings
  -r, --recursive   operate recursively on directories
      --rsyncable   make rsync-friendly archive
  -S, --suffix=SUF  use suffix SUF on compressed files
      --synchronous synchronous output (safer if system crashes, but slower)
  -t, --test        test compressed file integrity
  -v, --verbose     verbose mode
  -V, --version     display version number
  -1, --fast        compress faster
  -9, --best        compress better

With no FILE, or when FILE is -, read standard input.

Report bugs to <bug-gzip@gnu.org>.
```

## Example

对一个文件进行压缩，`gzip` 会给压缩后的文件添加 `.gz` 后缀后删除原文件。

```shell:no-line-numbers
gzip a.txt
```

相反地，使用 `-d` / `--decompress` 选项进行解压缩，解压缩后的内容会被输出到不带 `.gz` 后缀的文件中，原压缩文件被删除：

```shell:no-line-numbers
gzip -d a.txt.gz
```

如果目录中已经存在相应的 `.gz` 文件，则会出现是否需要覆盖的提示信息；使用 `-f` / `--force` 可以强制已有文件：

```shell:no-line-numbers
$ gzip a.txt
gzip: a.txt.gz already exists; do you wish to overwrite (y or n)?
$ gzip -f a.txt
```

压缩文件的同时，保留压缩前的文件：使用 `-k` / `--keep`。

```shell:no-line-numbers
gzip -k a.txt
```

`-r` / `--recursive` 选项递归压缩一个目录及其子目录。该目录下的所有文件会被单独压缩：

```shell:no-line-numbers
gzip -r folder/
```

使用 `-1` / `--fast` 或 `-9` / `--best` 来决定压缩率，根据需求来衡量压缩后文件的大小，和压缩/解压缩所需要的计算量。

使用 `-v` / `--verbose` 来打印压缩或解压缩过程中的详细信息：

```shell:no-line-numbers
$ gzip -v a.txt
a.txt:  -20.0% -- replaced with a.txt.gz
```

使用 `-l` / `--list` 查看压缩后文件的信息：

```shell:no-line-numbers
$ gzip -l a.txt.gz
         compressed        uncompressed  ratio uncompressed_name
                 36                  10 -20.0% a.txt
```

## References

[Gzip Command in Linux](https://www.geeksforgeeks.org/gzip-command-linux/)

[gzip(1) - Linux man page](https://linux.die.net/man/1/gzip)
