# groupadd

Created by : Mr Dk.

2023 / 02 / 06 22:55

Hangzhou, Zhejiang, China

---

## Background

`groupadd` 用于创建一个用户组。在 Linux 中，从用户级别来维护各个用户的权限比较麻烦，所以引入了 **用户组** 的概念，可以通过为用户组赋权从而给组内所有的用户赋权。

## Usage

```shell
$ groupadd -h
Usage: groupadd [options] GROUP

Options:
  -f, --force                   exit successfully if the group already exists,
                                and cancel -g if the GID is already used
  -g, --gid GID                 use GID for the new group
  -h, --help                    display this help message and exit
  -K, --key KEY=VALUE           override /etc/login.defs defaults
  -o, --non-unique              allow to create groups with duplicate
                                (non-unique) GID
  -p, --password PASSWORD       use this encrypted password for the new group
  -r, --system                  create a system account
  -R, --root CHROOT_DIR         directory to chroot into
  -P, --prefix PREFIX_DIR       directory prefix
      --extrausers              Use the extra users database
```

## Files

所有已被创建的用户组保存在 `/etc/group` 文件中：

```shell
$ cat /etc/group
root:x:0:
daemon:x:1:
bin:x:2:
sys:x:3:
adm:x:4:syslog,ubuntu
tty:x:5:syslog
disk:x:6:
lp:x:7:
mail:x:8:
news:x:9:
uucp:x:10:
man:x:12:
proxy:x:13:
kmem:x:15:
dialout:x:20:
fax:x:21:
voice:x:22:
cdrom:x:24:ubuntu
floppy:x:25:
tape:x:26:
sudo:x:27:ubuntu
audio:x:29:
dip:x:30:ubuntu
www-data:x:33:
backup:x:34:
operator:x:37:
list:x:38:
irc:x:39:
src:x:40:
gnats:x:41:
shadow:x:42:
utmp:x:43:
video:x:44:
sasl:x:45:
plugdev:x:46:ubuntu
staff:x:50:
games:x:60:
users:x:100:
nogroup:x:65534:
systemd-journal:x:101:
systemd-network:x:102:
systemd-resolve:x:103:
systemd-timesync:x:104:
crontab:x:105:
messagebus:x:106:
input:x:107:
kvm:x:108:
render:x:109:
syslog:x:110:
tss:x:111:
uuidd:x:112:
tcpdump:x:113:
ssh:x:114:
landscape:x:115:
lxd:x:116:ubuntu
systemd-coredump:x:999:
ubuntu:x:1000:
ntp:x:117:
bind:x:118:
netdev:x:119:
lighthouse:x:1001:lighthouse
```

其格式为：

```
group_name:password:group_id:list-of-members
```

## GID

创建用户组时，需要使用一个编号作为用户组的 ID。默认情况下，这个数值为唯一且非负数，除非使用 `-o` 参数指定允许非唯一 GID。

`-g` / `--gid` 可以显式指定想要使用的 GID，否则就将从指定范围内选择一个。选择的范围被定义在 `/etc/login.defs` 中：

```shell
$ cat /etc/login.defs | grep GID
GID_MIN                  1000
GID_MAX                 60000
#SYS_GID_MIN              100
#SYS_GID_MAX              999
```

上述值可以通过 `-K GID_MIN=500 -K GID_MAX=700` 改写。

## System User Group

如果想创建一个系统用户组，需要使用 `-r` / `--system`，这样会从 `SYS_GID_MIN` / `SYS_GID_MAX` 的范围中分配 GID。系统用户组与普通用户组并无权限上的区别，只是分配 GID 的范围不一样，用于人为区分。

## References

[groupadd command in Linux with examples](https://www.geeksforgeeks.org/groupadd-command-in-linux-with-examples/)

[ask Ubuntu - What is a "system" group, as opposed to a normal group?](https://askubuntu.com/questions/523949/what-is-a-system-group-as-opposed-to-a-normal-group)
