# Linux - Text Browser

Created by : Mr Dk.

2018 / 10 / 30 09:58

Nanjing, Jiangsu, China

---

## 起因

在 GitHub 上 release 了一个工程，并把工程的 `.jar` 文件上传了。想把文件下载下来试试，看看有没有出错，但是由于网络环境问题，死活下载不动，虽然它只有 **7KB**。

## 对策

经过上网搜索，Linux 提供了好几款基于命令行的 web 浏览器：*links2*、*links*、*lynx*，最后我选用了 *links2* 进行尝试。

```bash
$ sudo apt install links2
```

* 使用 *links2* 访问网页 - 比如我访问了我自己的主页

```bash
$ links2 mrdrivingduck.vip
```

* 利用 `↑`、`↓` 选择需要跳转的链接，使用 `Enter` 进行页面跳转
* 找到下载链接并按 `Enter`，会弹出提示框，输入保存文件的名称
* 开始下载
* 下载完成后，文件会保存在启动 *links2* 的路径下
* 使用 `Xftp`，将下载好的文件传输到本地即可

---

