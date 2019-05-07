# Wireless - wifiphisher

Created by : Mr Dk.

2019 / 01 / 11 22:52

Nanjing, Jiangsu, China

---

## About

A __Rogue Access Point__ framework. - [link](https://github.com/wifiphisher/wifiphisher)

![logo](../img/wifiphisher-logo.png)

_wifiphisher_ 是一款安全工具，由希腊安全研究员 _George Chatzisofroniou_ 开发

由 _Python_ 编写，可对受害者进行定制的 __钓鱼攻击__

* 与传统的 _Wi-Fi_ 攻击不同，不涉及任何 __handshake__ 或 __brute-force__

* 利用 __社会工程学（Social Engineering）__ 技术，使用一种类似欺骗的方法，使受害者在不知不觉中供出密码

  > 建立理论并通过利用自然的、社会的和制度上的途径来逐步地解决各种复杂的社会问题。

---

## Requirements

* _Kali Linux_ - 官方支持发布版，所有新功能都在该平台上测试
* _Wireless network adapter_ - 支持 _AP_ & _Monitor_ mode
* _Drivers_ should support _netlink_

---

## Usages

### 1. Start wireless network adapter

```bash
$ ifconfig wlan0 up
```

![start](../img/wifiphisher-start.png)

### 2. Turn wireless network adapter into MONITOR mode

```bash
$ airmon-ng start wlan0
```

![monitor](../img/wifiphisher-monitor.png)

### 3. Start wifiphisher and select target

```bash
$ wifiphisher
```

![select](../img/wifiphisher-select.png)

### 4. Select attacking scenarios

* _Firmware Upgrade Page_
* _Network Manager Connect_
* _Browser Plugin Update_
* _OAuth Login Page_

![page1](../img/wifiphisher-scn-1.png)

![page2](../img/wifiphisher-scn-2.png)

### 5. Start attacking !

* 建立一个 _Evil Twin_ 热点
* 建立 _WEB_ 服务，配置 _DHCP_ 服务器
* 将所有用户请求 _redirect_ 到高度定制化的 _phishing pages_

---

## Attacking scenarios

### Firmware Upgrade Page

伪造一个路由器固件升级界面，诱使连接上伪造 _AP_ 的受害者输入路由器密码

![firmware-page](../img/wifiphisher-firmware-page.png)

![firmware](../img/wifiphisher-firmware.png)

### Network Manager Connect

伪造一个网络连接失败的界面，并弹出一个重新输入网络密码的窗口，诱使受害者输入密码

![networkmanager-page](../img/wifiphisher-networkmanager-page.png)

![networkmanager](../img/wifiphisher-networkmanager.png)

### Browser Plugin Update

伪造浏览器插件升级，让受害者下载恶意的可执行文件 - 没有尝试

### OAuth Login Page

伪造利用社交网络账号登录的免费热点，诱使受害者输入社交网络的账号密码

![facebook-page](../img/wifiphisher-facebook-page.png)

![facebook](../img/wifiphisher-facebook.png)

---

## Advanced

可自己定义更多的 _phishing scenarios_

* _LinkedIn_ 登录界面（与 _Facebook_ 大同小异）
* _Adobe Flash Player_ 的升级界面，使用户下载恶意的可执行程序
* ......
* 太高级，没有精力自己折腾了

可以自定义 _Evil Twin AP_ 的 _SSID_ 和 _MAC Address_

* _MAC Address_ 的定制与网卡有关，有些网卡不支持指定 _MAC Address_
* 在下面的例子中
  * 伪造一个 _SSID_ 为 `mrdk` 的 _AP_
  * 试图指定 _MAC_ 地址但失败了，因此该网卡不同发动 _MAC_ 地址相同的 _Evil Twin_ 攻击

![mrdk](../img/wifiphisher-custom.png)

![custom-mrdk](../img/wifiphisher-custom-mrdk.png)

---

## Summary

这是去年十月份刚进实验室时

老师让我们无线研究小组试用的钓鱼工具

由于当时自己忙于开发 _WIDS_

因此这款工具是别的同学在玩

最近做实验需要一个 _Evil Twin_ 环境

所以又回过头来试试这个工具

不过这个工具好像不支持 _Retransmission Evil Twin_ 啊？？？

似乎只能主动钓鱼 不能作为中间人被动监听嘛

连上流氓 _AP_ 的客户端只能乖乖输入密码 不能上网......

---

