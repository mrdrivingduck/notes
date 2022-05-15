# Network - FTP

Created by : Mr Dk.

2020 / 12 / 17 11:33

Nanjing, Jiangsu, China

---

## About

FTP (File Transfer Protocol，文件传输协议) 是 TCP/IP 协议组中的协议之一。FTP 协议包括两个组成部分，其一为 FTP 服务器，其二为 FTP 客户端。其中 FTP 服务器用来存储文件，用户可以使用 FTP 客户端通过 FTP 协议访问位于 FTP 服务器上的资源。在开发网站的时候，通常使用 FTP 协议把网页或程序上传到 Web 服务器上。此外，由于 FTP 传输效率非常高，在网络上传输大的文件时，一般也采用该协议。

FTP 使用明文传输文件，而 SFTP (SSH File Transfer Protocol) 和 SCP (Secure Copy) 使用加密链路传输文件，两者都是 SSH (Secure Shell) 服务的一部分。

- SFTP 可靠性高，可 **断点续传**，效率比 FTP 低一些，但更安全
- SCP 需要知道目标的详细目录，不可断点续传，比 SFTP 更为轻量级

## Working Mode

FTP 使用熟知端口 TCP 21 作为控制端口，发送或接受命令。但是根据工作模式，还会开辟其它端口作为数据端口。

### Port Mode

FTP 的 **主动模式**。客户端通过 21 端口连接到服务器。客户端在自身主机上开辟端口用于数据连接，并将这个端口通过 `PORT` 命令告诉服务器。服务器使用自己的 TCP 20 端口连接到客户端的数据端口传送数据。

> 如果客户端没有公网地址 (在内网以内)，那么服务器没有办法连接到客户端开辟的数据端口上。(除非能够显式 NAT，但是通常来说客户端开辟的端口是随机的)

### Passive Mode

FTP 的 **被动模式**。客户端依旧通过 21 端口连接到服务器，发送 `PASV` 命令。服务器在自身主机上随机打开一个 **高端端口** (大于 1024)，并告诉客户端这个端口的位置。客户端连接到这个服务器高端端口建立数据连接。高端端口的范围可以在 FTP 服务器上进行配置。

---

## Deploy && Install

记录昨天部署一台 FTP 服务器的过程。需求是我的一台内网主机上拥有大量数据需要分享给别人，所以想要搭建一台 FTP 服务器，并给对方开放一个账户。对方能够登录到包含数据的文件夹下，但不希望该账户能访问主机上的其它数据。另外，由于主机位于内网中，还要配置内网穿透。

通过 APT 安装 _vsftpd (very secure FTP daemon)_，它是一个完全免费、开放源代码的 FTP 服务器软件，运行在 UNIX 类操作系统上。小巧轻快、安全易用。

```bash
sudo apt install vsftpd
```

```console
$ service vsftpd status
● vsftpd.service - vsftpd FTP server
     Loaded: loaded (/lib/systemd/system/vsftpd.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2020-12-16 17:39:31 CST; 16h ago
   Main PID: 4224 (vsftpd)
      Tasks: 1 (limit: 38277)
     Memory: 16.6M
     CGroup: /system.slice/vsftpd.service
             └─4224 /usr/sbin/vsftpd /etc/vsftpd.conf

12月 16 17:39:31 zjt-work-ubuntu-20 systemd[1]: Starting vsftpd FTP server...
12月 16 17:39:31 zjt-work-ubuntu-20 systemd[1]: Started vsftpd FTP server.
```

## Configuration

### Create User

创建一个普通用户：

```bash
sudo adduser [--home DIR] [--shell SHELL]
```

创建完毕后，可以在 `passwd` 文件最后看到：

```bash
cat /etc/passwd
```

删除用户：

```bash
sudo userdel [USER]
```

### White List / Black List

编辑 vsftpd 的配置文件 `/etc/vsftpd.conf` 进行配置。

首先启动 vsftpd 的 user list 功能，该用户列表可以作为黑名单或白名单使用。在当前场景下，我肯定是需要一个白名单，并将提供给对方的账户加入在这个白名单中，这样只有提供给他的账户才可以访问文件。

```
userlist_enable=YES
userlist_deny=NO
```

- `userlist_enable=YES` 表示启用用户列表文件 (默认在 `/etc/vsftpd.user_list`，每行一个账户名)
- `userlist_deny=NO` 表示不拒绝列表中的账户 (即白名单)

这样，除了名单中指定的账户外，我的主机默认账户被拒绝登录：

```console
$ ftp localhost
Connected to localhost.
220 (vsFTPd 3.0.3)
Name (localhost:mrdrivingduck): mrdrivingduck
530 Permission denied.
Login failed.
```

### Chroot Jail

将用户登录后的 root 目录锁定在一个特定目录下，形成一个 _监狱_。用户通过 `cd ..` 命令无法逃出这个监狱，从而保证用户只能访问特定的目录。Linux 的 `chroot` 命令能够做到这件事。编辑 `/etc/vsftpd.conf`：

```
chroot_local_user=NO
chroot_list_enable=YES
allow_writeable_chroot=NO
```

- `chroot_local_user` 表示一个全局设定，设置是否将所有用户锁定在 jail 内
- `chroot_list_enable` 表示是否启用针对特定用户的 **例外** 设定，即黑名单或白名单，取决于 `chroot_local_user` 的设定 - 名单文件默认位于 `/etc/vsftpd.chroot_list`
- `allow_writeable_chroot` - 是否允许用户登录后被 chroot 锁定的路径可写 (是一个安全策略)

> 如果将 `allow_writeable_chroot` 设置为 `NO`，可能会遇到 `500 OOPS: vsftpd: refusing to run with writable root inside chroot ()` 的错误。有两种方法可以解决这个问题。
>
> 将 `allow_writeable_chroot` 设置为 `YES` 可以直接绕开安全检查，免去了很多不必要的麻烦，但是可能会带来 **安全问题** ([ROARING BEAST ATTACK](https://serverfault.com/questions/743949/vsftp-why-is-allow-writeable-chroot-yes-a-bad-idea))。
>
> 另一种方法是让用户被锁定到的路径 **不可写**，但是如果需要路径能够被浏览，那么就要保留路径的 **可读** 和 **可执行** 权限。因此，这种方法实际上是最安全的。
>
> 我本以为将开放账户的 root 路径下的文件夹权限设置一下就行了。没想到，由于我存放数据的 NTFS 文件系统位于一个移动硬盘上，使用 `chmod` 居然无法更改目录权限 😥。参考 [这个解决方案](http://blog.itpub.net/31536365/viewspace-2154308/) 后，我只能到 `/etc/fstab` 中手动设置：
>
> - 通过 `sudo fdisk -l` 查询这个硬盘的 UUID
> - 通过 `cat /etc/passwd` 查询当前主机用户的 uid、gid
> - 在 `/etc/fstab` 中设置硬盘挂载点、设置目录拥有者为主机用户、主机用户拥有 `7` 权限、其它用户只有 `5` 权限。
>
> 这样，开放账户登录到该路径后，将不具有写权限；而我的主机用户可以继续向硬盘中写入数据。

### Passive Mode && frp

由于 FTP 客户端也在内网中，显然，FTP 服务器无法使用主动模式，那么需要显式将 vsftpd 配置为 **被动模式**。此外，还遇到了一些错误，通过参考 [这篇文章](https://blog.csdn.net/zengd0/article/details/109403079)，还要加一些额外配置。在 `/etc/vsftpd.conf` 中：

```
pasv_enable=YES
pasv_promiscuous=YES
pasv_address=118.31.10.213
pasv_addr_resolve=YES
listen_ipv6=NO
listen=YES
pasv_min_port=12792
pasv_max_port=12793
```

其中，`pasv_address` 是 frp 服务器的运行地址，是必须的；`pasv_min_port` 和 `pasv_max_port` 确定了 FTP 服务器上打开数据端口的范围，这些端口需要被穿透到 frp 服务器的相同端口上。所以整体的 frp 端口穿透方案如下 (包括控制端口 21)：

```ini
[ftp]
type = tcp
local_ip = 127.0.0.1
local_port = 21
remote_port = 2121

[frp-pasv-1]
type = tcp
local_ip = 127.0.0.1
local_port = 12792
remote_port = 12792

[frp-pasv-2]
type = tcp
local_ip = 127.0.0.1
local_port = 12793
remote_port = 12793
```

FTP 客户端应当以被动模式连接 frp 服务器的 `2121` (FTP 服务器控制端口的远程端口)。注意，frp 的所有远程端口都应当在云服务器的安全组白名单内。

### Others

Ubuntu 20.04 上还可能在 vsftpd 服务的日志中看到错误，解决方案 [在此](https://askubuntu.com/questions/1239503/ubuntu-20-04-and-20-10-etc-securetty-no-such-file-or-directory)。

---

## Summary

这等折腾，very interesting 😄

## References

[CSDN - vsftpd -- 用户名单文件 ftpusers 和 user_list](https://blog.csdn.net/feit2417/article/details/82903314)

[CSDN - vsftpd 配置: chroot_local_user 与 chroot_list_enable 详解](https://blog.csdn.net/gybshen/article/details/79782884)

[Arch Linux - Very Secure FTP Daemon (简体中文)](<https://wiki.archlinux.org/index.php/Very_Secure_FTP_Daemon_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)>)

[Ben Scobie - Fixing 500 OOPS: vsftpd: refusing to run with writable root inside chroot ()](https://www.benscobie.com/fixing-500-oops-vsftpd-refusing-to-run-with-writable-root-inside-chroot/)
