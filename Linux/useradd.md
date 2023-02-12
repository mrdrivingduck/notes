# useradd

Created by : Mr Dk.

2023 / 02 / 12 23:53

Hangzhou, Zhejiang, China

---

## Background

`useradd` 用于创建一个新用户。

## Usage

```shell
$ useradd -h
Usage: useradd [options] LOGIN
       useradd -D
       useradd -D [options]

Options:
      --badnames                do not check for bad names
  -b, --base-dir BASE_DIR       base directory for the home directory of the
                                new account
      --btrfs-subvolume-home    use BTRFS subvolume for home directory
  -c, --comment COMMENT         GECOS field of the new account
  -d, --home-dir HOME_DIR       home directory of the new account
  -D, --defaults                print or change default useradd configuration
  -e, --expiredate EXPIRE_DATE  expiration date of the new account
  -f, --inactive INACTIVE       password inactivity period of the new account
  -g, --gid GROUP               name or ID of the primary group of the new
                                account
  -G, --groups GROUPS           list of supplementary groups of the new
                                account
  -h, --help                    display this help message and exit
  -k, --skel SKEL_DIR           use this alternative skeleton directory
  -K, --key KEY=VALUE           override /etc/login.defs defaults
  -l, --no-log-init             do not add the user to the lastlog and
                                faillog databases
  -m, --create-home             create the user's home directory
  -M, --no-create-home          do not create the user's home directory
  -N, --no-user-group           do not create a group with the same name as
                                the user
  -o, --non-unique              allow to create users with duplicate
                                (non-unique) UID
  -p, --password PASSWORD       encrypted password of the new account
  -r, --system                  create a system account
  -R, --root CHROOT_DIR         directory to chroot into
  -P, --prefix PREFIX_DIR       prefix directory where are located the /etc/* files
  -s, --shell SHELL             login shell of the new account
  -u, --uid UID                 user ID of the new account
  -U, --user-group              create a group with the same name as the user
  -Z, --selinux-user SEUSER     use a specific SEUSER for the SELinux user mapping
      --extrausers              Use the extra users database
```

## UID

创建用户时，需要使用一个编号作为用户组的 ID。默认情况下，这个数值为唯一且非负数，除非使用 `-o` 参数指定允许非唯一 UID。

`-u` / `--uid` 可以显式指定想要使用的 UID，否则就将从指定范围内选择一个。选择的范围被定义在 `/etc/login.defs` 中：

```shell
$ cat /etc/login.defs | grep UID
UID_MIN                  1000
UID_MAX                 60000
#SYS_UID_MIN              100
#SYS_UID_MAX              999
```

`-r` / `--system` 用于创建一个系统用户，使用 `SYS_UID_MIN` 到 `SYS_UID_MAX` 中间的 UID。

上述配置文件中的值可以通过 `-K UID_MIN=500 -K UID_MAX=700` 改写。

## Home Directory

通过 `-d` / `--home-dir` 选项指定新用户的 HOME 目录。`-m`/ `--create-home` 用于在相应目录不存在的时候创建。

## Password

`-p` / `--password` 用于指定用户的密码。密码以密文形式保存在 `/etc/shadow` 中。

## User Group

使用 `-g` / `--gid` 指定新用户需要加入的用户组，这个用户组必须已经存在。

使用 `-G` / `--groups` 指定新用户要加入的一系列用户组，以逗号分隔。

## Shell

使用 `-s` / `--shell` 指定新用户使用的 shell。

## References

[useradd(8) — Linux manual page](https://man7.org/linux/man-pages/man8/useradd.8.html)
