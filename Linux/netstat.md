# netstat

Created by : Mr Dk.

2022 / 12 / 17 16:49

Hangzhou, Zhejiang, China

---

## Background

`netstat` 用于显示网络连接信息。

## Usage

其参数选项主要用于决定在输出中是否展示某些信息。所以输出信息的解读就比较重要。

输出分为两部分：

- Active Internet connections
- Active UNIX domain Sockets

### Internet Connections

其中，对于活跃的互联网连接，输出的信息包含：

- Socket 协议：TCP / UDP / ...
- 接收队列：已经接收但未被拷贝到用户程序的字节数
- 发送队列：远程未确认的字节数
- 本地地址：本地 IP 和端口号（如果不加 `-n`，那么会被翻译为常见域名和应用程序名，比如 `localhost:mysql`）
- 远程地址
- 状态：主要是给 TCP Socket 使用
- 用户：Socket 所属的用户名或用户 ID
- 程序：使用 `--program` 引入这一列，显示这个 Socket 的进程名或进程号
- 定时器：与这个 Socket 相关的 TCP 定时器，需要使用 `--timers` 引入

```shell
$ netstat -a --program --timers
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name     Timer
tcp        0      0 localhost:8005          0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:8002          0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:8000          0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 0.0.0.0:ssh             0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:domain        0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:36147         0.0.0.0:*               LISTEN      2853/node            off (0.00/0/0)
tcp        0      0 localhost:mysql         0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:11211         0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:33060         0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:ipp           0.0.0.0:*               LISTEN      -                    off (0.00/0/0)
tcp        0      0 localhost:36147         localhost:53890         ESTABLISHED 2853/node            off (0.00/0/0)
tcp        0      0 192.168.0.105:ssh       192.168.0.103:61072     ESTABLISHED -                    keepalive (5804.14/0/0)
tcp        0      0 192.168.0.105:59186     143.244.210.202:https   TIME_WAIT   -                    timewait (47.68/0/0)
tcp        0      0 localhost:53890         localhost:36147         ESTABLISHED -                    off (0.00/0/0)
tcp        0      0 192.168.0.105:50736     124.221.154.83:12700    ESTABLISHED -                    keepalive (2.24/0/0)
tcp        0    324 192.168.0.105:ssh       192.168.0.103:57526     ESTABLISHED -                    on (0.20/0/0)
tcp        0      0 localhost:53892         localhost:36147         ESTABLISHED -                    off (0.00/0/0)
tcp        0      0 192.168.0.105:ssh       192.168.0.103:62188     ESTABLISHED -                    keepalive (6399.66/0/0)
tcp        0      0 localhost:36147         localhost:53892         ESTABLISHED 4285/node            off (0.00/0/0)
tcp6       0      0 [::]:ms-wbt-server      [::]:*                  LISTEN      -                    off (0.00/0/0)
tcp6       0      0 ip6-localhost:3350      [::]:*                  LISTEN      -                    off (0.00/0/0)
tcp6       0      0 [::]:http               [::]:*                  LISTEN      -                    off (0.00/0/0)
tcp6       0      0 [::]:ssh                [::]:*                  LISTEN      -                    off (0.00/0/0)
tcp6       0      0 ip6-localhost:ipp       [::]:*                  LISTEN      -                    off (0.00/0/0)
udp        0      0 0.0.0.0:mdns            0.0.0.0:*                           -                    off (0.00/0/0)
udp        0      0 0.0.0.0:47784           0.0.0.0:*                           -                    off (0.00/0/0)
udp        0      0 localhost:domain        0.0.0.0:*                           -                    off (0.00/0/0)
udp        0      0 192.168.0.105:bootpc    192.168.0.1:bootps      ESTABLISHED -                    off (0.00/0/0)
udp        0      0 0.0.0.0:631             0.0.0.0:*                           -                    off (0.00/0/0)
udp        0      0 192.168.0.105:43301     192.168.0.1:domain      ESTABLISHED -                    off (0.00/0/0)
udp6       0      0 [::]:36812              [::]:*                              -                    off (0.00/0/0)
udp6       0      0 [::]:mdns               [::]:*                              -                    off (0.00/0/0)
raw6       0      0 [::]:ipv6-icmp          [::]:*                  7           -                    off (0.00/0/0)
```

### UNIX Domain Sockets

对于活跃的 UNIX Domain Sockets，打印的信息包含：

- 协议
- 附着到这个 Socket 上的进程数（引用计数）
- 标志位
- Socket 类型
- 状态
- 进程名 / 进程编号
- 路径

```shell
$ netstat -a --program

Active UNIX domain sockets (servers and established)
Proto RefCnt Flags       Type       State         I-Node   PID/Program name     Path
unix  2      [ ACC ]     STREAM     LISTENING     30243    -                    /var/run/docker/libnetwork/c3ceef6d7bab.sock
unix  2      [ ACC ]     STREAM     LISTENING     27523    -                    @/tmp/.ICE-unix/1617
unix  2      [ ACC ]     STREAM     LISTENING     35116    -                    @/tmp/.X11-unix/X0
unix  2      [ ACC ]     STREAM     LISTENING     32384    -                    @/var/lib/gdm3/.cache/ibus/dbus-LepPuSBi
unix  2      [ ]         DGRAM                    35506    2135/systemd         /run/user/1000/systemd/notify
unix  2      [ ]         DGRAM                    30078    -                    /run/user/125/systemd/notify
unix  2      [ ACC ]     STREAM     LISTENING     35509    2135/systemd         /run/user/1000/systemd/private
unix  2      [ ACC ]     STREAM     LISTENING     30081    -                    /run/user/125/systemd/private
unix  2      [ ACC ]     STREAM     LISTENING     35515    2135/systemd         /run/user/1000/bus
unix  2      [ ACC ]     STREAM     LISTENING     32059    -                    /run/user/125/bus
unix  2      [ ACC ]     STREAM     LISTENING     35517    2135/systemd         /run/user/1000/gnupg/S.dirmngr
unix  2      [ ACC ]     STREAM     LISTENING     32061    -                    /run/user/125/gnupg/S.dirmngr
unix  2      [ ACC ]     STREAM     LISTENING     35519    2135/systemd         /run/user/1000/gnupg/S.gpg-agent.browser
```

### 网卡列表

使用 `-i` 及 `-ie`（基本等价于 `ifconfig`）选项，可以看到所有网卡信息：

```shell
$ netstat -i
Kernel Interface table
Iface      MTU    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
docker0   1500        0      0      0 0             0      0      0      0 BMU
enp4s0    1500   340806      0      0 0        134521      0      0      0 BMRU
lo       65536    41882      0      0 0         41882      0      0      0 LRU

$ netstat -ie
Kernel Interface table
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:06:aa:44:da  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

enp4s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.105  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::fdb5:c5e3:982b:21d1  prefixlen 64  scopeid 0x20<link>
        ether c8:5b:76:e4:d6:cf  txqueuelen 1000  (Ethernet)
        RX packets 341106  bytes 461278024 (461.2 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 134869  bytes 17595636 (17.5 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 42420  bytes 9788790 (9.7 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 42420  bytes 9788790 (9.7 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

### 路由信息

使用 `-r` 选项可以看到内核路由表：

```shell
$ netstat -r
Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
default         192.168.0.1     0.0.0.0         UG        0 0          0 enp4s0
link-local      0.0.0.0         255.255.0.0     U         0 0          0 enp4s0
172.17.0.0      0.0.0.0         255.255.0.0     U         0 0          0 docker0
192.168.0.0     0.0.0.0         255.255.255.0   U         0 0          0 enp4s0
```

### 监控

`-c` 参数等价于使用 `watch` 命令持续刷新输出。

## References

[20 Netstat Commands for Linux Network Management](https://www.tecmint.com/20-netstat-commands-for-linux-network-management/)

[netstat(8) — Linux manual page](https://man7.org/linux/man-pages/man8/netstat.8.html)
