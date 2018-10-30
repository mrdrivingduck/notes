## Linux - 文字界面网页浏览器

Created by : Mr Dk.

2018 / 10 / 30 09:58

Nanjing, Jiangsu, China

---

### 起因

在 _GitHub_ 上 release 了一个工程，并把工程的 _.jar_ 文件上传了

想把 _.jar_ 文件下载下来试试，看看有没有出错

但是由于网络环境问题，死活下载不动，虽然它只有 __7KB__

### 想法

我在 _vultr_ 上有一台运行在新加坡的 _vps_

`ping` 我自己的 _GitHub Pages_ 速度飞快

设想如果我能够通过它下载文件

先将文件下载到那台 _vps_ 上

再通过 `Xftp` 传回本机，岂不妙哉~

但是那台 _vps_ 运行的是 _Ubuntu Server 18.04_

只有命令行，没有图形界面

所以我该怎么进入到那个网页并下载？

### 对策

经过上网搜索

_Linux_ 提供了好几款基于命令行的 _web_ 浏览器

_links2_、_links_、_lynx_，最后我选用了 _links2_ 进行尝试

* 使用 `Xshell`，通过 `SSH` 登录到 _vps_
* 安装 _links2_

```bash
$ sudo apt-get install links2
```

* 使用 _links2_ 访问网页 - 比如我访问了我自己的 _homepage_

```bash
$ links2 mrdrivingduck.vip
```

* 利用 `↑`、`↓` 选择需要跳转的链接，使用 `Enter` 进行页面跳转
* 找到下载链接并按 `Enter`，会弹出提示框，输入保存文件的名称
* 开始下载
* 下载完成后，文件会保存在启动 _links2_ 的路径下
* 使用 `Xftp`，将下载好的文件传输到本地即可

---

