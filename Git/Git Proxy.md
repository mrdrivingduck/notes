# Git - Proxy

Created by : Mr Dk.

2020 / 02 / 19 13:28

Ningbo, Zhejiang, China

---

受限于国内的网络环境，用 Git 从 GitHub 上 `clone` / `fetch` / `pull` / `push` 都痛苦异常。这段时间放假在家，家里的网速比实验室里的还慢，用 [配置 GitHub DNS](../Network/Network%20GitHub%20Accelerating.md) 的方法已经不太奏效了。就算 IP 地址没有被污染，从国内连到国外相应服务器的延迟依旧很高。因此，试图配置 Git 的代理，借由在境外租用的服务器，来加速 Git 对 GitHub 的访问。

GitHub 有 HTTPS 和 SSH 两种访问方式。在我自己的电脑上，由于我有自己的 RSA 公私钥，所以一般使用 SSH 方式。对这两种访问方式，设置代理的方式也有所不同。

## HTTPS Proxy

这种网上的解决方式是最多的，直接在 Git 命令行中设置即可。

```console
$ git config –global http.proxy http://[user:password@]10.167.32.133:8080
$ git config –global http.proxy https://[user:password@]10.167.32.133:8080
```

相应的撤销代理方法：

```console
$ git config --global --unset http.proxy
$ git config --global --unset https.proxy
```

## SSH Proxy

### Windows

在 Baidu 上没有找到解决方案，后来通过 Google 看了一篇 [博客](https://communary.net/2017/01/12/getting-git-to-work-through-a-proxy-server-in-windows/) 发现符合我的应用场景，并且经过测试方法是有效的。我的应用场景是 [*Git for Windows*](https://gitforwindows.org/) + [*V2Ray*](https://github.com/2dust/v2rayN) 的本地代理。

具体的设置方式是在 SSH 的配置文件 (`~/.ssh/config`) 中添加规则。规则中的代理命令需要使用到一个叫做 `connect.exe` 的程序。这个程序不用另外下载，在 Git for Windows 的安装目录下已经提供：`<Git_Path>/Git/mingw64/bin/`。该程序的使用方式如下：

```bat
$ connect
connect --- simple relaying command via proxy.
Version 1.105
usage: C:\Program Files\Git\mingw64\bin\connect.exe [-dnhst45] [-p local-port]
          [-H proxy-server[:port]] [-S [user@]socks-server[:port]]
          [-T proxy-server[:port]]
          [-c telnet-proxy-command]
          host port
```

根据该程序的使用方法，可以使用 `-H` 参数下的 HTTP 代理和 `-S` 参数下的 SOCKS 代理 (其它代理反正我也没有不就深究含义)。我这边的 V2Ray 支持 HTTP 和 SOCKS 两种代理，只是端口号不一样，所以我就使用了 SOCKS 代理。在本地 SSH 的配置文件中添加如下规则：

```
Host github.com
    ProxyCommand "C:\Program Files\Git\mingw64\bin\connect.exe" -S 127.0.0.1:10808 %h %p
    IdentityFile "~/.ssh/id_rsa"
    TCPKeepAlive yes
    IdentitiesOnly yes
    User git
    Port 22
    Hostname github.com
```

添加好规则之后，之后再通过 SSH 访问 GitHub 时，就会通过代理访问，速度大大加快：

![git-proxy](../img/git-proxy.png)

如果不使用 SOCKS 代理，使用 HTTP 代理也是可以的，把参数协议和 IP 地址、端口号换一下应该就可以了，就不折腾了。算是解决了因为网络带来的一些烦恼。

### Linux

Linux 下主要是 `ProxyCommand` 的不同：

```
Host github.com
    ProxyCommand nc -x 127.0.0.1:10808 %h %p
    IdentityFile "~/.ssh/id_rsa"
    TCPKeepAlive yes
    IdentitiesOnly yes
    User git
    Port 22
    Hostname github.com
```

---

## References

[Getting git to work through a proxy server (in Windows)](https://communary.net/2017/01/12/getting-git-to-work-through-a-proxy-server-in-windows/)

[Use Proxy for Git/GitHub](https://gist.github.com/coin8086/7228b177221f6db913933021ac33bb92)

---

