# Wireless - WPS Cracking by Reaver

Created by : Mr Dk.

2018 / 12 / 07 10:19

Nanjing, Jiangsu, China

---

### Tools

_Kali Linux_ 中的 _reaver_

* Reaver v1.6.5 WiFi Protected Setup Attack Tool; Copyright (c) 2011, Tactical Network Solutions, Craig Heffner
* 用于攻击支持 _WPS_ 的设备

_Kali Linux_ 中的 _wash_

* Wash v1.6.5 WiFi Protected Setup Scan Tool; Copyright (c) 2011, Tactical Network Solutions, Craig Heffner
* 用于扫描周围支持 _WPS_ 的设备

_Kali Linux_ 中的 _aircrack-ng_

* 用于将网卡设定为监控模式

### Theory

支持 _WPS_ 功能的无线路由器，只要获得它的 _PIN_

就可以获得它的 _PSK_，从而自动连入网络

从而简化路由器的连接配置过程

_reaver_ 通过穷举的方式暴力破解这个 _PIN_

从而获得无线网络的密码

### Procudure

#### Insert a USB-wireless-interface

```bash
$ ifconfig
```

![reaver-init](../img/reaver-init.png)

_wlan0_ is the wireless interface I have just inserted

#### Turn the wireless-interface into monitor mode

```bash
$ airmon-ng start wlan0
```

![reaver-mon](../img/reaver-mon.png)

#### Check whether the monitor mode is on

```bash
$ ifconfig
```

![reaver-ifconfig](../img/reaver-ifconfig.png)

_wlan0mon_ is the wireless-interface which has been turned into monitor mode

#### Search for the Routers which support WPS

```bash
$ wash -i wlan0mon
```

![reaver-wash](../img/reaver-wash.png)

实测很多路由器已经有了保护措施：

* 不回应破解
* 穷举到一定次数后开启保护

另外和网卡放置的角度也有关系

* 使用放在我右手边的网卡破解一直失败
* 使用放在我右手边靠窗的网卡就能破解成功

经过尝试和选择，身边唯一能被破解的网络 —— `TP-LINK_qwer`

#### Start cracking by reaver

```bash
$ reaver -i wlan0mon -b EC:88:8F:51:DD:A2 -vv
```

由于 _8_ 位的 _PIN_ 是分为两个 _4_ 位分开存放的

_reaver_ 会先穷举前四位 _PIN_

在我的破解过程中，在进度大约到 _15%_ 时，突然跳到了 _90%_

说明前四位已被破解，直接进入了后四位的破解，因此进度大大增加

![reaver-result](../img/reaver-result.png)

后四位 _PIN_ 也破解完毕

由此 _8_ 位 _PIN_ 已被全部破解出来，_PSK_ 也被获得

_AP SSID_ - `TP-LINK_qwer`; _PIN_ - `18914863`；_PSK_ - `nuaa@413`

如果已知路由器的 _PIN_，就可以直接使用 `-p PIN` 参数直接获得 _PSK_

---

### Summary

这个破解太受条件限制了

在宿舍和实验室里找了好久

才找到这么一个唯一可以被破解的无线路由器

说明现在的路由器厂商已经非常注意防御此类破解了

令我比较郁闷的是

_kismet_ 号称可以在检测到暴力破解 _WPS_ 时发出警告

然而并没有警告啊。。。。。。

---

