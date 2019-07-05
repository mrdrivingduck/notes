# Network - GitHub import to Gitee

Created by : Mr Dk.

2019 / 07 / 05 23:40

Nanjing, Jiangsu, China

---

今天要搞 Google 的 fuzzer - syzkaller

`git clone` 了一下实在是太慢了。。。

在国外的服务器上下载以后打包传回来

好像又把一些 `.git` 目录给丢掉了

而 syzkaller 似乎又恰好需要 `.git` 来进行安装

烦死个人

之前修改 `hosts` 的 GitHub 加速方法也不管用

在网上搜了一下

发现了另一种骚到不行的方法

---

在国内的 Gitee 上登录

点击创建仓库

在最底下有一个 `import` 按钮

需要给出 GitHub 的仓库链接

创建完成后 大概等个三五分钟

Gitee 上就有了和 GitHub 上一样的仓库

然后再从 Gitee 上 `git clone`

享受了国内的网速

握草这招真是够骚的。。。

等下次哪天再有需求再试试 🤩

---

