# Network - SSH

Created by : Mr Dk.

2019 / 05 / 31 10:09

Nanjing, Jiangsu, China

---

## About

Wikipedia - 

>  __Secure Shell (SSH)__ is a cryptographic network protocol for operating network services securely over an unsecured network. Typical applications include __remote command-line login__ and __remote command execution__, but any network service can be secured with SSH.
>
> SSH provides a secure channel over an unsecured network in a __client–server__ architecture, connecting an __SSH client__ application with an __SSH server__. The protocol specification distinguishes between two major versions, referred to as __SSH-1__ and __SSH-2__. The standard TCP port for SSH is __22__. SSH is generally used to access __Unix-like__ operating systems, but it can also be used on __Microsoft Windows__. Windows 10 uses __OpenSSH__ as its default SSH client.
>
> SSH was designed as a replacement for Telnet and for unsecured remote shell protocols such as the Berkeley rlogin, rsh, and rexec protocols. Those protocols send information, notably passwords, in plaintext, rendering them susceptible to interception and disclosure using packet analysis. The encryption used by SSH is intended to provide __confidentiality__ and __integrity__ of data over an unsecured network, such as the Internet, although files leaked by _Edward Snowden_ indicate that the _National Security Agency_ can sometimes decrypt SSH, allowing them to read the contents of SSH sessions.

---

## Definition

SSH 利用公钥密码学认证远程计算机

认证基于私钥，密钥本身不会通过网络传播

__SSH 只认证提供公钥的一方是否也拥有对应的私钥__

在 SSH 的所有版本中，__认证未知公钥__ 相当重要

如果接受了攻击者的公钥，将导致未授权的攻击者成为合法用户

SSH 通常用于登录远程机器并执行命令

也支持 __SSH File Transfer Protocol (SFTP)__ 和 __Secure Copy Protocol (SCP)__

SSH 使用服务器-客户端模型

SSH 服务器的标准 TCP 端口是 `22`

---

## Theory

在第一次客户端连接到远程服务器时：

```bash
$ ssh user@host
The authenticity of host '104.168.166.54 (104.168.166.54)' can't be established.
ECDSA key fingerprint is SHA256:skmJDYbFdTFiftzRApMGQpRZHiuc8w36R3MkvKninQo.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '104.168.166.54' (ECDSA) to the list of known hosts.
```

表示无法验证远程服务器的身份，只知道其公钥指纹

用户需要自行比对公钥指纹，和远程服务器公布的公钥指纹，进行合法性验证

否则，攻击者可能截获到客户端的登录请求后

向客户端发放伪造的公钥，从而成为中间人 (Man-In-The-Middle)

通过伪造公钥获取用户登录到远程服务器的账号、密码

再 SSH 到远程服务器上，则 SSH 的安全机制完全失效

假设用户接受该公钥，则公钥会被保存在客户端的 `~/.ssh/known_hosts` 中

下次再连接该远程服务器时，会直接使用该公钥

每个 SSH 用户都有自己的 known_hosts

同时系统也有一个 `/etc/ssh/ssh_known_hosts`

保存一些对所有用户都可信赖的远程服务器公钥

---

## Log In by Password

1. SSH 服务器受到客户端的登录请求，将公钥发送给客户端
2. 客户端接收并信任该公钥，将登录用户名、密码通过公钥加密后发送
3. 服务器通过私钥解密，并判断用户名、密码是否合法

---

## Log In by Public Key

使用口令登录时，每次都需要输入密码，比较麻烦

如果说，客户端能够将自己的公钥存放在远程服务器上

那么就可以通过公钥直接进行登录

* 远程服务器向客户端发送随机字符串
* 客户端用自己的私钥加密后，发送给远程服务器
* 服务器用存储的客户端公钥解密
* 如果解密后与原字符串相同，则认证成功，允许登录

### Key Generation

这种方法必须要求客户端有自己的公私钥对，如果没有则需要生成：

```bash
$ ssh-keygen -t rsa -C "..."
```

会问一大堆问题，比如是否想密钥保存在 `~/.ssh/id_rsa` 等

如果觉得密钥不安全，还可以对密钥设口令，每次使用时需要认证口令

生成完成后，默认

* 私钥位于 `~/.ssh/id_rsa`
* 公钥位于 `~/.ssh/id_rsa.pub`

将客户端公钥放到服务器上即可

### Key Management

服务器将可登录的客户端公钥存放在 `~/.ssh/authorized_keys` 中

将公钥直接追加在该文件末尾即可

也可以在客户端直接通过命令将公钥拷贝：

```bash
$ ssh-copy-id user@host
```

当然，拷贝这一步暂时还是需要像口令登录一样输入密码的

不然任何人都可以把自己的公钥放到服务器上去了

从此以后，再次登录就不需要密码了：

```bash
$ ssh user@host
```

---

## Host Configuration

以上步骤完成后，每次 SSH 到远程服务器还是很麻烦

主要是 IP 地址太难记了

SSH 提供了一个配置文件

可以将 `user`、`host` 和私钥保存在配置文件中，并取一个别名

配置文件的格式如下：

编辑 `~/.ssh/config` （如果没有就新建一个）

```
Host MyServerName
    HostName 104.168.166.54
    User root
    IdentityFile ~/.ssh/id_rsa
```

保存后，以后可以直接通过别名进行登录：

```bash
$ ssh MyServerName
```

---

## Summary

昨天与 _chaoweilanmao_ 折腾了一天

折腾的来源在于，每次登录 _HostWind_ 上面的 VPS 太麻烦了

首先，_HostWind_ 的账号是他的，我记不住，每次得问 😒

登录上去以后

查一下我们那台美国 VPS 的 IP 地址和密码，才能 SSH 到 VPS 上

虽然在 win 上装了 Xshell，保存了 VPS 的配置

但是现在 win、macOS、Linux shell 都已经直接支持 SSH

所以想通过命令行直接连接，又苦于记不住 IP 和口令 😑

一开始不知道公钥登录和配置文件

我们准备自己开发一个登录脚本

后来搜了下才知道可以通过公钥 + 配置文件的方式简化登录

不得不说公钥密码体制真的很有用

不仅可以用于加密，还可以用于认证，这两点都在 SSH 上体现了：

1. 公钥用于加密数据，加密后的数据只有接收方用自己的私钥才能解密

   体现在 SSH 服务器下发公钥时，客户端通过该公钥加密用于登录的用户名和密码 🔐

2. 私钥用于认证，加密后的数据谁都可以解密（因为公钥公开）

   但能够认证加密方的身份（因为只有加密方有私钥）

   体现在公钥登录时，客户端将公钥放置到服务器上 🔑

   从而可以在登录时，通过本机的私钥向服务器认证自身的身份

由此，SSH 应该是了解得差不多了，有空再看看 SFTP 和 SCP 叭 😁

---



