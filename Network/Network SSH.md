# Network - SSH

Created by : Mr Dk.

2019 / 05 / 31 10:09

Nanjing, Jiangsu, China

---

## About

[Wikipedia](https://en.wikipedia.org/wiki/Secure_Shell):

> **Secure Shell (SSH)** is a cryptographic network protocol for operating network services securely over an unsecured network. Typical applications include **remote command-line login** and **remote command execution**, but any network service can be secured with SSH.
>
> SSH provides a secure channel over an unsecured network in a **client–server** architecture, connecting an **SSH client** application with an **SSH server**. The protocol specification distinguishes between two major versions, referred to as **SSH-1** and **SSH-2**. The standard TCP port for SSH is **22**. SSH is generally used to access **Unix-like** operating systems, but it can also be used on **Microsoft Windows**. Windows 10 uses **OpenSSH** as its default SSH client.
>
> SSH was designed as a replacement for Telnet and for unsecured remote shell protocols such as the Berkeley rlogin, rsh, and rexec protocols. Those protocols send information, notably passwords, in plaintext, rendering them susceptible to interception and disclosure using packet analysis. The encryption used by SSH is intended to provide **confidentiality** and **integrity** of data over an unsecured network, such as the Internet, although files leaked by _Edward Snowden_ indicate that the _National Security Agency_ can sometimes decrypt SSH, allowing them to read the contents of SSH sessions.

## Definition

SSH 利用公钥密码学认证远程计算机。认证基于私钥，密钥本身不会通过网络传播。SSH 只认证 **提供公钥的一方是否也拥有对应的私钥**：因此 **认证未知公钥** 相当重要。如果接受了攻击者的公钥，将导致未授权的攻击者成为合法用户。

SSH 通常用于登录远程机器并执行命令，也支持 **SSH File Transfer Protocol (SFTP)** 和 **Secure Copy Protocol (SCP)**。SSH 使用服务器-客户端模型。SSH 服务的熟知 TCP 端口是 `22`。

## Theory

在第一次客户端连接到远程服务器时：

```console
$ ssh user@host
The authenticity of host '104.168.166.54 (104.168.166.54)' can't be established.
ECDSA key fingerprint is SHA256:skmJDYbFdTFiftzRApMGQpRZHiuc8w36R3MkvKninQo.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '104.168.166.54' (ECDSA) to the list of known hosts.
```

以上信息表示无法验证远程服务器的身份，只知道其公钥指纹。用户需要自行比对公钥指纹，和远程服务器公开的公钥指纹，对远程服务器的身份认证。否则，攻击者可能截获到客户端的登录请求后，向客户端发放伪造的公钥，从而成为中间人 (Man-In-The-Middle)，通过伪造公钥获取用户登录到远程服务器的账号、密码。再使用用户的账号、密码 SSH 连接到远程服务器上，从而导致 SSH 的安全机制完全失效。

假设用户接受该公钥，则公钥会被保存在客户端的 `~/.ssh/known_hosts` 中，下次再连接该远程服务器时，会直接使用该公钥。每个 SSH 用户都有自己的 `known_hosts`，同时系统也有一个 `/etc/ssh/ssh_known_hosts`，保存一些对所有用户都可信赖的远程服务器公钥。

## Log In by Password

通过用户名 + 密码来登录远程服务器。

1. SSH 服务器受到客户端的登录请求，将公钥发送给客户端
2. 客户端接收并信任该公钥，将登录用户名、密码通过公钥加密后发送
3. 服务器通过私钥解密，并判断用户名、密码是否合法

## Log In by Public Key

使用口令登录时，每次都需要输入密码，比较麻烦。如果说，客户端能够将自己的公钥存放在远程服务器上，那么就可以通过公钥直接进行登录。

- 远程服务器向客户端发送随机字符串
- 客户端用自己的私钥加密后，发送给远程服务器
- 服务器用存储的客户端公钥解密
- 如果解密后与原字符串相同，则认证成功，允许登录

### Key Generation

这种方法必须要求客户端有自己的公私钥对，如果没有则需要生成：

```console
$ ssh-keygen -t rsa -C "..."
```

会问一大堆问题，比如是否想密钥保存在 `~/.ssh/id_rsa` 等。如果觉得密钥不安全，还可以对密钥设口令，每次使用时需要认证口令。生成完成后，密钥默认生成在：

- 私钥位于 `~/.ssh/id_rsa`
- 公钥位于 `~/.ssh/id_rsa.pub`

### Key Management

下一步，将客户端公钥放到服务器上即可。服务器将可登录的客户端公钥存放在 `~/.ssh/authorized_keys` 中，将公钥直接追加在该文件末尾即可。也可以在客户端直接通过命令将公钥拷贝：

```console
$ ssh-copy-id user@host
```

当然，拷贝这一步暂时还是需要像口令登录一样输入密码的，不然任何人都可以把自己的公钥放到服务器上去了。从此以后，再次登录就不需要密码了：

```console
$ ssh user@host
```

## Host Configuration

以上步骤完成后，每次 SSH 到远程服务器还是很麻烦，主要是 IP 地址太难记了。SSH 提供了一个配置文件，可以将 `user`、`host` 和私钥保存在配置文件中，并取一个别名。配置文件的格式如下：

编辑 `~/.ssh/config` (如果没有就新建一个)

```
Host MyServerName
    HostName 104.168.166.54
    User root
    IdentityFile ~/.ssh/id_rsa
```

保存配置后，以后可以直接通过别名进行登录：

```console
$ ssh MyServerName
```

## Issue

### Disconnect

SSH 连接后，如果窗口在一段时间内不去管它，服务器就会自动断开连接，导致已有的一些交互性工作丢失。在 SSH 的客户端和服务端都可以配置心跳，使连接能继续保持下去。

服务端配置 - 编辑 `/etc/ssh/sshd_config`：

```
ClientAliveInterval 10
ClientAliveCountMax 3
```

然后重启 sshd 服务。配置的含义是每 10s 向客户端发送一个心跳包。如果连续三个心跳包都没有得到客户端的回应，就与客户端断开连接。另外，`TCPKeeyAlive` 被配置为 `yes` 也有类似效果。开启这个选项会使用 TCP keep alive 来保持连接。与上一个选项的区别在于，SSH 自身的 keep alive 信号是应用层信息，是经过加密的；而 TCP 层的 keep alive 是可以被欺骗的。

对于 SSH 客户端，也可以配置主动发送心跳包的时间。一些常用的 SSH 客户端 _XShell_、_Terminus_ 也有类似的功能。对于 Terminal 用户，配置过程与服务端类似 - 编辑 `/etc/ssh/ssh_config`：

```
ServerAliveInterval 10
ServerAliveCountMax 3
```

### On MacOS

在 macOS 14 Mojave 的 Terminal 上使用 SSH 时，出现问题：

```console
$ ssh root@user
packet_write_wait: Connection to 104.168.166.54 port 22: Broken pipe
```

解决的方法是，在配置文件中为所有的用户添加一条属性：

```
Host *
    IPQoS=throughput
```

然后就可以成功 SSH 到远程服务器了。

---
