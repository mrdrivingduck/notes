# Ubuntu - Desktop Recover (Python)

Created by : Mr Dk.

2020 / 09 / 06 13:20

Nanjing, Jiangsu, China

---

## Ubuntu Desktop & Python 3

今天试图在本地运行华为的 *MindSpore* AI 工具集，要求使用 Python 3.7.5 以上版本。看了看 Ubuntu 本机的 Python 版本：

```console
$ python3
Python 3.6.9 (default, Jul 17 2020, 12:50:27)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

版本不够新。于是我用 APT 安装了 Python 3.7，并试图把 Python 3.6 给卸载掉。大问题来了。在使用 `apt remove python3` 时，提示顺带还会删除一大堆东西。我也没太在意，直接回车了。卸载完毕后，我发现自己的 Terminal、Ubuntu Software 等基础工具全部没了。幸亏我没有重启电脑，否则据说连桌面都进不去了。幸亏这台电脑连接了局域网，我在自己的笔记本上通过 SSH 还能通过命令行向这台电脑输入命令。

看来 Ubuntu 桌面极大依赖于特定版本的 Python。所以补救措施是，把所有被卸载掉的部分 [装回来](https://blog.csdn.net/sinat_31131353/article/details/87948471)：

```bash
sudo apt install python3
sudo apt install ubuntu-minimal ubuntu-standard ubuntu-desktop
```

然后重启电脑。

## Terminal & Python 3

之后，我试图使用 [管理多版本 GCC](https://mrdrivingduck.github.io/blog/#/markdown?repo=notes&path=Compiler%2FCompiler%20Multi-version%20GCC.md) 的方式来管理多版本的 Python 3。方法是可行的，但是将 `python3` 的指向从 `python3.6` 改到 `python3.7` 后，Terminal 运行不起来了。

我通过远程 SSH 输入命令查看问题：

```console
$ gnome-terminal
Traceback (most recent call last):
  File "/usr/bin/gnome-terminal", line 9, in <module>
    from gi.repository import GLib, Gio
  File "/usr/lib/python3/dist-packages/gi/__init__.py", line 42, in <module>
    from . import _gi
ImportError: cannot import name '_gi' from 'gi' (/usr/lib/python3/dist-packages/gi/__init__.py)
```

暂时没有研究怎么解决问题。在用完 Python 3.7 之后，使用 `update-alternatives --config python3` 将 `python3` 指回 `python3.6` 即可。

---

