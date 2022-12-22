# lsof

Created by : Mr Dk.

2022 / 12 / 22 23:30 🐑

Hangzhou, Zhejiang, China

---

## Background

`lsof`（list open files）用于查看已打开的 **文件**。由于 Linux 中一切皆文件，所以它将输出一切形式的已打开文件：

- 常规文件、目录
- 字符设备、块设备
- 管道
- ...

## Usage

```shell
$ lsof -h
lsof 4.93.2
 latest revision: https://github.com/lsof-org/lsof
 latest FAQ: https://github.com/lsof-org/lsof/blob/master/00FAQ
 latest (non-formatted) man page: https://github.com/lsof-org/lsof/blob/master/Lsof.8
 usage: [-?abhKlnNoOPRtUvVX] [+|-c c] [+|-d s] [+D D] [+|-E] [+|-e s] [+|-f[gG]]
 [-F [f]] [-g [s]] [-i [i]] [+|-L [l]] [+m [m]] [+|-M] [-o [o]] [-p s]
 [+|-r [t]] [-s [p:s]] [-S [t]] [-T [t]] [-u s] [+|-w] [-x [fl]] [--] [names]
Defaults in parentheses; comma-separated set (s) items; dash-separated ranges.
  -?|-h list help          -a AND selections (OR)     -b avoid kernel blocks
  -c c  cmd c ^c /c/[bix]  +c w  COMMAND width (9)    +d s  dir s files
  -d s  select by FD set   +D D  dir D tree *SLOW?*   +|-e s  exempt s *RISKY*
  -i select IPv[46] files  -K [i] list|(i)gn tasKs    -l list UID numbers
  -n no host names         -N select NFS files        -o list file offset
  -O no overhead *RISKY*   -P no port names           -R list paRent PID
  -s list file size        -t terse listing           -T disable TCP/TPI info
  -U select Unix socket    -v list version info       -V verbose search
  +|-w  Warnings (+)       -X skip TCP&UDP* files     -Z Z  context [Z]
  -- end option scan
  -E display endpoint info              +E display endpoint info and files
  +f|-f  +filesystem or -file names     +|-f[gG] flaGs
  -F [f] select fields; -F? for help
  +|-L [l] list (+) suppress (-) link counts < l (0 = all; default = 0)
                                        +m [m] use|create mount supplement
  +|-M   portMap registration (-)       -o o   o 0t offset digits (8)
  -p s   exclude(^)|select PIDs         -S [t] t second stat timeout (15)
  -T qs TCP/TPI Q,St (s) info
  -g [s] exclude(^)|select and print process group IDs
  -i i   select by IPv[46] address: [46][proto][@host|addr][:svc_list|port_list]
  +|-r [t[m<fmt>]] repeat every t seconds (15);  + until no files, - forever.
       An optional suffix to t is m<fmt>; m must separate t from <fmt> and
      <fmt> is an strftime(3) format for the marker line.
  -s p:s  exclude(^)|select protocol (p = TCP|UDP) states by name(s).
  -u s   exclude(^)|select login|UID set s
  -x [fl] cross over +d|+D File systems or symbolic Links
  names  select named files or files on named file systems
Anyone can list all files; /dev warnings disabled; kernel ID check disabled.
```

如果不加任何参数，将输出大一堆看也看不完的信息。所以先按列来捋一捋每列的含义：

```shell
$ lsof | head -n 5
COMMAND       PID     TID TASKCMD              USER   FD      TYPE             DEVICE SIZE/OFF       NODE NAME
systemd         1                              root  cwd       DIR              252,2     4096          2 /
systemd         1                              root  rtd       DIR              252,2     4096          2 /
systemd         1                              root  txt       REG              252,2  1620224     139845 /usr/lib/systemd/systemd
systemd         1                              root  mem       REG              252,2  1369384     140226 /usr/lib/x86_64-linux-gnu/libm-2.31.so
```

其中：

- `COMMAND` 列显示与该进程相关的 UNIX 命令的前九个字符
- `PID` / `TID` 列显示进程号 / 线程号
- `TASKCMD`：任务命令名，在 Linux 上可以与 `COMMAND` 不同
- `USER` 列显示进程所属用户
- `FD` 列显示文件描述符编号（普通文件），或：
  - `cwd`：当前工作目录
  - `rtd`：根目录
  - `pd`：父目录
  - `mem`：内存映射文件
  - `mmap`：内存映射设备
  - `txt`：程序代码或数据
  - ...
- `TYPE` 列显示该文件的类型：
  - `DIR`：目录
  - `REG`：普通文件
  - `PIPE`：管道
  - `LINK`：符号链接
  - `IPv4`
  - `IPv6`
  - ...
- `DEVICE` 列显示设备编号
- `SIZE/OFF` 列获取文件的大小或当前偏移（如果可以获取）
- `NODE` 列显示节点编号（不同类型的文件有不同的含义）
- `NAME` 列显示文件所在的文件系统的挂载点

### 按进程号过滤

使用 `-p` 参数只显示某个进程打开的文件。比如用 `vim` 打开一个文件 `a.txt`，然后在另一个窗口通过 `ps` 找到这个进程的 pid：

```shell
$ lsof -p 2757806
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
vim     2757806 root  cwd    DIR  252,2     4096     19 /root
vim     2757806 root  rtd    DIR  252,2     4096      2 /
vim     2757806 root  txt    REG  252,2  2906824 131279 /usr/bin/vim.basic
vim     2757806 root  mem    REG  252,2    51856 140272 /usr/lib/x86_64-linux-gnu/libnss_files-2.31.so
vim     2757806 root  mem    REG  252,2  3035952 131313 /usr/lib/locale/locale-archive
vim     2757806 root  mem    REG  252,2    47064 138541 /usr/lib/x86_64-linux-gnu/libogg.so.0.8.4
vim     2757806 root  mem    REG  252,2   182344 138629 /usr/lib/x86_64-linux-gnu/libvorbis.so.0.4.8
vim     2757806 root  mem    REG  252,2    14880 140397 /usr/lib/x86_64-linux-gnu/libutil-2.31.so
vim     2757806 root  mem    REG  252,2   108936 131566 /usr/lib/x86_64-linux-gnu/libz.so.1.2.11
vim     2757806 root  mem    REG  252,2   182560 131219 /usr/lib/x86_64-linux-gnu/libexpat.so.1.6.11
vim     2757806 root  mem    REG  252,2    39368 138503 /usr/lib/x86_64-linux-gnu/libltdl.so.7.3.1
vim     2757806 root  mem    REG  252,2   100520 138577 /usr/lib/x86_64-linux-gnu/libtdb.so.1.4.3
vim     2757806 root  mem    REG  252,2    38904 138630 /usr/lib/x86_64-linux-gnu/libvorbisfile.so.3.3.7
vim     2757806 root  mem    REG  252,2   584392 138554 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.9.0
vim     2757806 root  mem    REG  252,2  2029592 131261 /usr/lib/x86_64-linux-gnu/libc-2.31.so
vim     2757806 root  mem    REG  252,2   157224 140375 /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
vim     2757806 root  mem    REG  252,2  5449112 132283 /usr/lib/x86_64-linux-gnu/libpython3.8.so.1.0
vim     2757806 root  mem    REG  252,2    18848 140219 /usr/lib/x86_64-linux-gnu/libdl-2.31.so
vim     2757806 root  mem    REG  252,2    22456 138457 /usr/lib/x86_64-linux-gnu/libgpm.so.2
vim     2757806 root  mem    REG  252,2    39088 138376 /usr/lib/x86_64-linux-gnu/libacl.so.1.1.2253
vim     2757806 root  mem    REG  252,2    71680 138399 /usr/lib/x86_64-linux-gnu/libcanberra.so.0.2.5
vim     2757806 root  mem    REG  252,2   163200 138579 /usr/lib/x86_64-linux-gnu/libselinux.so.1
vim     2757806 root  mem    REG  252,2   192032 138600 /usr/lib/x86_64-linux-gnu/libtinfo.so.6.2
vim     2757806 root  mem    REG  252,2  1369384 140226 /usr/lib/x86_64-linux-gnu/libm-2.31.so
vim     2757806 root  mem    REG  252,2   191504 130833 /usr/lib/x86_64-linux-gnu/ld-2.31.so
vim     2757806 root    0u   CHR  136,0      0t0      3 /dev/pts/0
vim     2757806 root    1u   CHR  136,0      0t0      3 /dev/pts/0
vim     2757806 root    2u   CHR  136,0      0t0      3 /dev/pts/0
vim     2757806 root    4u   REG  252,2    12288     52 /root/.a.txt.swp
```

可以看到 `vim` 进程打开了：

- 当前目录和根目录（应该是继承自 shell）
- `vim.basic` 程序
- 一大堆共享库（内存映射）
- 在字符设备上打开了三个文件，描述符分别为 0、1、2（标准输入、输出、错误流）
- 打开了 `.a.txt.swp` swap 文件

### 按进程名过滤

使用 `-c` 参数按 `COMMAND` 列过滤输出。

### 按用户过滤

使用 `-u` 参数按 `USER` 列过滤输出。

### 查看网络连接

使用 `-i` 参数可以查看所有网络连接：

```shell
$ lsof -i
COMMAND       PID            USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
systemd         1            root   54u  IPv4     15244      0t0  TCP *:sunrpc (LISTEN)
systemd         1            root   55u  IPv4     15245      0t0  UDP *:sunrpc
systemd         1            root   56u  IPv6     15248      0t0  TCP *:sunrpc (LISTEN)
systemd         1            root   57u  IPv6     15251      0t0  UDP *:sunrpc
rpcbind       706            _rpc    4u  IPv4     15244      0t0  TCP *:sunrpc (LISTEN)
rpcbind       706            _rpc    5u  IPv4     15245      0t0  UDP *:sunrpc
rpcbind       706            _rpc    6u  IPv6     15248      0t0  TCP *:sunrpc (LISTEN)
rpcbind       706            _rpc    7u  IPv6     15251      0t0  UDP *:sunrpc
systemd-n     744 systemd-network   19u  IPv4     21626      0t0  UDP nat:bootpc
```

再加上 `tcp` / `udp` 可以查看所有的 TCP / UDP 网络连接：

```shell
$ lsof -i tcp | tail -n 1
sshd      2757815            root    4u  IPv4 190764835      0t0  TCP nat:ssh->112.10.217.238:48291 (ESTABLISHED)
```

这里的端口号被翻译为常用端口名称。可以加一个 `:` 按端口号或端口范围来过滤：

```shell
$ lsof -i tcp:22
COMMAND     PID USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
sshd        867 root    3u  IPv4     24169      0t0  TCP *:ssh (LISTEN)
sshd        867 root    4u  IPv6     24180      0t0  TCP *:ssh (LISTEN)
sshd    2757815 root    4u  IPv4 190764835      0t0  TCP nat:ssh->112.10.217.238:48291 (ESTABLISHED)
sshd    2761102 root    4u  IPv4 190787885      0t0  TCP nat:ssh->112.5.81.26:32966 (ESTABLISHED)
sshd    2761103 sshd    4u  IPv4 190787885      0t0  TCP nat:ssh->112.5.81.26:32966 (ESTABLISHED)

$ lsof -i tcp:20-23
COMMAND     PID USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
sshd        867 root    3u  IPv4     24169      0t0  TCP *:ssh (LISTEN)
sshd        867 root    4u  IPv6     24180      0t0  TCP *:ssh (LISTEN)
sshd    2757815 root    4u  IPv4 190764835      0t0  TCP nat:ssh->112.10.217.238:48291 (ESTABLISHED)
sshd    2761187 root    4u  IPv4 190788164      0t0  TCP nat:ssh->138.2.152.212:48566 (ESTABLISHED)
sshd    2761188 sshd    4u  IPv4 190788164      0t0  TCP nat:ssh->138.2.152.212:48566 (ESTABLISHED)
```

### 只显示进程号

`-t` 参数可以只输出进程号。这个选项可以和 `kill` 结合使用。比如说干掉某个用户所有已经打开文件的进程：

```shell
kill -9 `lsof -t -u xxx`
```

### 周期运行（监控）

使用 `-r` 参数可以指定间隔运行的秒数。

## References

[lsof 一切皆文件](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/lsof.html)

[Linux 命令神器：lsof 入门](https://linux.cn/article-4099-1.html)

[lsof(8) — Linux manual page](https://man7.org/linux/man-pages/man8/lsof.8.html)
