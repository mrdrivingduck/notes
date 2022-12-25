# df

Created by : Mr Dk.

2022 / 12 / 26 0:20

Hangzhou, Zhejiang, China

---

## Background

`df` 用于查看文件系统使用量信息。

## Usage

```shell
$ df --help
Usage: df [OPTION]... [FILE]...
Show information about the file system on which each FILE resides,
or all file systems by default.

Mandatory arguments to long options are mandatory for short options too.
  -a, --all             include pseudo, duplicate, inaccessible file systems
  -B, --block-size=SIZE  scale sizes by SIZE before printing them; e.g.,
                           '-BM' prints sizes in units of 1,048,576 bytes;
                           see SIZE format below
  -h, --human-readable  print sizes in powers of 1024 (e.g., 1023M)
  -H, --si              print sizes in powers of 1000 (e.g., 1.1G)
  -i, --inodes          list inode information instead of block usage
  -k                    like --block-size=1K
  -l, --local           limit listing to local file systems
      --no-sync         do not invoke sync before getting usage info (default)
      --output[=FIELD_LIST]  use the output format defined by FIELD_LIST,
                               or print all fields if FIELD_LIST is omitted.
  -P, --portability     use the POSIX output format
      --sync            invoke sync before getting usage info
      --total           elide all entries insignificant to available space,
                          and produce a grand total
  -t, --type=TYPE       limit listing to file systems of type TYPE
  -T, --print-type      print file system type
  -x, --exclude-type=TYPE   limit listing to file systems not of type TYPE
  -v                    (ignored)
      --help     display this help and exit
      --version  output version information and exit

Display values are in units of the first available SIZE from --block-size,
and the DF_BLOCK_SIZE, BLOCK_SIZE and BLOCKSIZE environment variables.
Otherwise, units default to 1024 bytes (or 512 if POSIXLY_CORRECT is set).

The SIZE argument is an integer and optional unit (example: 10K is 10*1024).
Units are K,M,G,T,P,E,Z,Y (powers of 1024) or KB,MB,... (powers of 1000).

FIELD_LIST is a comma-separated list of columns to be included.  Valid
field names are: 'source', 'fstype', 'itotal', 'iused', 'iavail', 'ipcent',
'size', 'used', 'avail', 'pcent', 'file' and 'target' (see info page).

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation at: <https://www.gnu.org/software/coreutils/df>
or available locally via: info '(coreutils) df invocation'
```

### 文件系统类型

使用 `-T` 参数打印文件系统的类型：

```shell
$ df -T
Filesystem     Type     1K-blocks    Used Available Use% Mounted on
udev           devtmpfs    966120       0    966120   0% /dev
tmpfs          tmpfs       203016    1016    202000   1% /run
/dev/vda2      ext4      41222348 9665792  29783868  25% /
tmpfs          tmpfs      1015068      24   1015044   1% /dev/shm
tmpfs          tmpfs         5120       0      5120   0% /run/lock
tmpfs          tmpfs      1015068       0   1015068   0% /sys/fs/cgroup
/dev/loop3     squashfs     64768   64768         0 100% /snap/core20/1695
/dev/loop4     squashfs    119552  119552         0 100% /snap/core/14399
/dev/loop0     squashfs     45696   45696         0 100% /snap/certbot/2582
/dev/loop1     squashfs     64768   64768         0 100% /snap/core20/1738
/dev/loop2     squashfs     45824   45824         0 100% /snap/certbot/2618
tmpfs          tmpfs       203012       0    203012   0% /run/user/0
```

### 打印所有文件系统

使用 `-a` 参数打印所有的文件系统，包括伪文件系统、不可访问的文件系统：

```shell
$ df -a -T
Filesystem     Type        1K-blocks    Used Available Use% Mounted on
sysfs          sysfs               0       0         0    - /sys
proc           proc                0       0         0    - /proc
udev           devtmpfs       966120       0    966120   0% /dev
devpts         devpts              0       0         0    - /dev/pts
tmpfs          tmpfs          203016    1016    202000   1% /run
/dev/vda2      ext4         41222348 9665864  29783796  25% /
securityfs     securityfs          0       0         0    - /sys/kernel/security
tmpfs          tmpfs         1015068      24   1015044   1% /dev/shm
tmpfs          tmpfs            5120       0      5120   0% /run/lock
tmpfs          tmpfs         1015068       0   1015068   0% /sys/fs/cgroup
cgroup2        cgroup2             0       0         0    - /sys/fs/cgroup/unified
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/systemd
pstore         pstore              0       0         0    - /sys/fs/pstore
none           bpf                 0       0         0    - /sys/fs/bpf
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/net_cls,net_prio
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/pids
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/perf_event
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/cpu,cpuacct
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/blkio
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/freezer
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/rdma
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/cpuset
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/hugetlb
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/memory
cgroup         cgroup              0       0         0    - /sys/fs/cgroup/devices
systemd-1      -                   -       -         -    - /proc/sys/fs/binfmt_misc
hugetlbfs      hugetlbfs           0       0         0    - /dev/hugepages
mqueue         mqueue              0       0         0    - /dev/mqueue
debugfs        debugfs             0       0         0    - /sys/kernel/debug
tracefs        tracefs             0       0         0    - /sys/kernel/tracing
sunrpc         rpc_pipefs          0       0         0    - /run/rpc_pipefs
configfs       configfs            0       0         0    - /sys/kernel/config
fusectl        fusectl             0       0         0    - /sys/fs/fuse/connections
tracefs        tracefs             0       0         0    - /sys/kernel/debug/tracing
binfmt_misc    binfmt_misc         0       0         0    - /proc/sys/fs/binfmt_misc
/dev/loop3     squashfs        64768   64768         0 100% /snap/core20/1695
/dev/loop4     squashfs       119552  119552         0 100% /snap/core/14399
/dev/loop0     squashfs        45696   45696         0 100% /snap/certbot/2582
/dev/loop1     squashfs        64768   64768         0 100% /snap/core20/1738
/dev/loop2     squashfs        45824   45824         0 100% /snap/certbot/2618
tmpfs          tmpfs          203012       0    203012   0% /run/user/0
```

### 打印使用量

以人类可读的格式打印：

```shell
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            944M     0  944M   0% /dev
tmpfs           199M 1016K  198M   1% /run
/dev/vda2        40G  9.3G   29G  25% /
tmpfs           992M   24K  992M   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           992M     0  992M   0% /sys/fs/cgroup
/dev/loop3       64M   64M     0 100% /snap/core20/1695
/dev/loop4      117M  117M     0 100% /snap/core/14399
/dev/loop0       45M   45M     0 100% /snap/certbot/2582
/dev/loop1       64M   64M     0 100% /snap/core20/1738
/dev/loop2       45M   45M     0 100% /snap/certbot/2618
tmpfs           199M     0  199M   0% /run/user/0
```

以指定单位打印使用量：`-B` + 单位：

```shell
$ df -Bk
Filesystem     1K-blocks     Used Available Use% Mounted on
udev             966120K       0K   966120K   0% /dev
tmpfs            203016K    1016K   202000K   1% /run
/dev/vda2      41222348K 9665988K 29783672K  25% /
tmpfs           1015068K      24K  1015044K   1% /dev/shm
tmpfs              5120K       0K     5120K   0% /run/lock
tmpfs           1015068K       0K  1015068K   0% /sys/fs/cgroup
/dev/loop3        64768K   64768K        0K 100% /snap/core20/1695
/dev/loop4       119552K  119552K        0K 100% /snap/core/14399
/dev/loop0        45696K   45696K        0K 100% /snap/certbot/2582
/dev/loop1        64768K   64768K        0K 100% /snap/core20/1738
/dev/loop2        45824K   45824K        0K 100% /snap/certbot/2618
tmpfs            203012K       0K   203012K   0% /run/user/0

$ df -Bm
Filesystem     1M-blocks  Used Available Use% Mounted on
udev                944M    0M      944M   0% /dev
tmpfs               199M    1M      198M   1% /run
/dev/vda2         40257M 9440M    29086M  25% /
tmpfs               992M    1M      992M   1% /dev/shm
tmpfs                 5M    0M        5M   0% /run/lock
tmpfs               992M    0M      992M   0% /sys/fs/cgroup
/dev/loop3           64M   64M        0M 100% /snap/core20/1695
/dev/loop4          117M  117M        0M 100% /snap/core/14399
/dev/loop0           45M   45M        0M 100% /snap/certbot/2582
/dev/loop1           64M   64M        0M 100% /snap/core20/1738
/dev/loop2           45M   45M        0M 100% /snap/certbot/2618
tmpfs               199M    0M      199M   0% /run/user/0

$ df -Bg
Filesystem     1G-blocks  Used Available Use% Mounted on
udev                  1G    0G        1G   0% /dev
tmpfs                 1G    1G        1G   1% /run
/dev/vda2            40G   10G       29G  25% /
tmpfs                 1G    1G        1G   1% /dev/shm
tmpfs                 1G    0G        1G   0% /run/lock
tmpfs                 1G    0G        1G   0% /sys/fs/cgroup
/dev/loop3            1G    1G        0G 100% /snap/core20/1695
/dev/loop4            1G    1G        0G 100% /snap/core/14399
/dev/loop0            1G    1G        0G 100% /snap/certbot/2582
/dev/loop1            1G    1G        0G 100% /snap/core20/1738
/dev/loop2            1G    1G        0G 100% /snap/certbot/2618
tmpfs                 1G    0G        1G   0% /run/user/0
```

### 查看 inode

使用 `-i` 参数查看 inode 使用量：

```shell
$ df -i
Filesystem      Inodes  IUsed   IFree IUse% Mounted on
udev            241530    420  241110    1% /dev
tmpfs           253767    657  253110    1% /run
/dev/vda2      2600960 113254 2487706    5% /
tmpfs           253767      7  253760    1% /dev/shm
tmpfs           253767      4  253763    1% /run/lock
tmpfs           253767     18  253749    1% /sys/fs/cgroup
/dev/loop3       11897  11897       0  100% /snap/core20/1695
/dev/loop4       12857  12857       0  100% /snap/core/14399
/dev/loop0        7452   7452       0  100% /snap/certbot/2582
/dev/loop1       11897  11897       0  100% /snap/core20/1738
/dev/loop2        7457   7457       0  100% /snap/certbot/2618
tmpfs           253767     22  253745    1% /run/user/0
```

## References

[12 Useful “df” Commands to Check Disk Space in Linux](https://www.tecmint.com/how-to-check-disk-space-in-linux/)

[Check your disk space use with the Linux df command](https://www.redhat.com/sysadmin/Linux-df-command)

[linux - df (1)](http://ibg.colorado.edu/~lessem/psyc5112/usail/man/linux/df.1.html)
