# readlink

Created by : Mr Dk.

2023 / 04 / 14 19:55

Hangzhou, Zhejiang, China

---

## Background

`realpath` 能够返回任意路径的绝对路径。

## Usage

```shell
$ realpath --help
Usage: realpath [OPTION]... FILE...
Print the resolved absolute file name;
all but the last component must exist

  -e, --canonicalize-existing  all components of the path must exist
  -m, --canonicalize-missing   no components of the path need exist
  -L, --logical                resolve '..' components before symlinks
  -P, --physical               resolve symlinks as encountered (default)
  -q, --quiet                  suppress most error messages
      --relative-to=FILE       print the resolved path relative to FILE
      --relative-base=FILE     print absolute paths unless paths below FILE
  -s, --strip, --no-symlinks   don't expand symlinks
  -z, --zero                   separate output with NUL rather than newline

      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
For complete documentation, run: info coreutils 'realpath invocation'
```

ChatGPT 给出的资料：

> The realpath command in Linux is used to resolve the absolute path of a given file or directory, taking into account any symbolic links or relative paths that may be involved. It returns the canonical, or standardized, path for the specified file or directory.

## Demo

得到一个已有文件的绝对路径：

```shell
$ touch README.md
$ realpath ./README.md
/home/mrdrivingduck/test/README.md
```

`-e` / `-m` 选项可以被用于控制是否允许目标文件不存在：

```shell
$ realpath -e ./README.m
realpath: ‘./README.m’: No such file or directory

$ realpath -m ./README.m
/home/mrdrivingduck/test/README.m
```

对于符号链接来说，`-s` 选项可以选择不展开符号链接：

```shell
$ ln -s polar-doc/docs/README.md README

$ realpath README
/home/mrdrivingduck/test/polar-doc/docs/README.md

$ realpath -s README
/home/mrdrivingduck/test/README
```

## References

[realpath(1) - Linux man page](https://linux.die.net/man/1/realpath)
