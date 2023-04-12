# readlink

Created by : Mr Dk.

2023 / 04 / 12 19:55

Hangzhou, Zhejiang, China

---

## Background

`readlink` 用于打印符号链接的内容。

## Usage

```shell
$ readlink --help
Usage: readlink [OPTION]... FILE...
Print value of a symbolic link or canonical file name

  -f, --canonicalize            canonicalize by following every symlink in
                                every component of the given name recursively;
                                all but the last component must exist
  -e, --canonicalize-existing   canonicalize by following every symlink in
                                every component of the given name recursively,
                                all components must exist
  -m, --canonicalize-missing    canonicalize by following every symlink in
                                every component of the given name recursively,
                                without requirements on components existence
  -n, --no-newline              do not output the trailing delimiter
  -q, --quiet,
  -s, --silent                  suppress most error messages
  -v, --verbose                 report error messages
  -z, --zero                    separate output with NUL rather than newline
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
For complete documentation, run: info coreutils 'readlink invocation'
```

ChatGPT 给出的资料：

> The readlink command in Linux is used to print the symbolic link value of a given file or directory. It can also be used to resolve multiple levels of symbolic links, showing the final destination of a chain of symbolic links.

## Demo

### An Existing Target

创建一个指向实际存在文件的符号链接。

```shell
$ touch target.txt
$ ln -s target.txt l1
```

直接使用 `readlink`，将会打印符号链接中保存的实际值：

```shell
$ readlink l1
target.txt
```

加入 `-f` 参数可以打印全路径，前提是 **最后一级之前** 的所有路径都存在：

```shell
$ readlink -f l1
/home/mrdrivingduck/target.txt
```

### Non-existing Target

创建一个指向实际不存在文件的符号链接。

```shell
$ ln -s bbb l2
```

此时，使用 `-f` 参数依旧可以打印结果，因为最后一级之前的所有路径已存在，最后一级的文件不存在。

```shell
$ readlink -f l2
/home/mrdrivingduck/bbb
```

`-m` 参数也可以打印结果，因为它会忽略缺失文件：

```shell
$ readlink -m l2
/home/mrdrivingduck/bbb
```

`-e` 参数将无法打印结果，因为它要求目标必须存在。加上 `-v` 参数可以显示错误信息：

```shell
$ readlink -e l2
$ readlink -e -v l2
readlink: l2: No such file or directory
```

## References

[readlink(1) - Linux man page](https://linux.die.net/man/1/readlink)
