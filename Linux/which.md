# which

Created by : Mr Dk.

2022 / 10 / 29 11:35

Hangzhou, Zhejiang, China

---

## Background

`which` 命令用于在环境变量 `PATH` 中寻找某个可执行文件的绝对路径。

## Usage

`which` 默认返回可执行文件在 `PATH` 中找到的第一个绝对路径。如果想要输出所有的匹配，需要添加选项 `-a`：

```shell
$ which touch
/usr/bin/touch

$ which -a touch
/usr/bin/touch
/bin/touch
```

有时出现两个匹配可能是因为存在符号链接，但也有可能是有两个同名的可执行文件：

```shell
$ which -a touch
/usr/bin/touch
/bin/touch

$ ls -alt /usr/bin/touch
-rwxr-xr-x 1 root root 100728 Sep  5  2019 /usr/bin/touch

$ ls -alt /bin/touch
-rwxr-xr-x 1 root root 100728 Sep  5  2019 /bin/touch
```

```shell
$ which -a atq
/usr/bin/atq
/bin/atq

$ ls -alt /usr/bin/atq
lrwxrwxrwx 1 root root 2 Nov 13  2018 /usr/bin/atq -> at

$ ls -alt /bin/atq
lrwxrwxrwx 1 root root 2 Nov 13  2018 /bin/atq -> at
```

## References

[How to Use the which Command in Linux](https://phoenixnap.com/kb/which-command-linux)
