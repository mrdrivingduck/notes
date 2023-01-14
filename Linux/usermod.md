# usermod

Created by : Mr Dk.

2023 / 01 / 14 23:56

Hangzhou, Zhejiang, China

---

## Background

`usermod` 用于修改用户属性。与用户相关的属性通常保存在 `/etc/` 下，比如 `/etc/passwd` 中。`usermod` 命令将会修改这些文件。

## Usage

`usermod` 一般需要使用超级用户权限来执行：

```shell
$ sudo usermod -h
Usage: usermod [options] LOGIN

Options:
  -c, --comment COMMENT         new value of the GECOS field
  -d, --home HOME_DIR           new home directory for the user account
  -e, --expiredate EXPIRE_DATE  set account expiration date to EXPIRE_DATE
  -f, --inactive INACTIVE       set password inactive after expiration
                                to INACTIVE
  -g, --gid GROUP               force use GROUP as new primary group
  -G, --groups GROUPS           new list of supplementary GROUPS
  -a, --append                  append the user to the supplemental GROUPS
                                mentioned by the -G option without removing
                                him/her from other groups
  -h, --help                    display this help message and exit
  -l, --login NEW_LOGIN         new value of the login name
  -L, --lock                    lock the user account
  -m, --move-home               move contents of the home directory to the
                                new location (use only with -d)
  -o, --non-unique              allow using duplicate (non-unique) UID
  -p, --password PASSWORD       use encrypted password for the new password
  -R, --root CHROOT_DIR         directory to chroot into
  -s, --shell SHELL             new login shell for the user account
  -u, --uid UID                 new UID for the user account
  -U, --unlock                  unlock the user account
  -Z, --selinux-user SEUSER     new SELinux user mapping for the user account
```

### 修改 HOME 目录

使用 `-d` 参数可以修改用户的 HOME 目录：

```shell
sudo usermod -d /home/another mrdrivingduck
```

### 修改用户所属的用户组

使用 `-g` 参数：

```shell
sudo usermod -g some_group mrdrivingduck
```

### 修改用户使用的 Shell

使用 `-s` 参数：

```shell
sudo usermod -s /bin/zsh mrdrivingduck
```

### 修改用户 ID

使用 `-u` 参数：

```shell
sudo usermod -u 1234 mrdrivingduck
```

## References

[usermod command in Linux with Examples](https://www.geeksforgeeks.org/usermod-command-in-linux-with-examples/)

[usermod(8) — Linux manual page](https://man7.org/linux/man-pages/man8/usermod.8.html)
