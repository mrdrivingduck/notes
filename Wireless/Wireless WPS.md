# Wireless - WPS

Created by : Mr Dk.

2018 / 12 / 03 21:49

Nanjing, Jiangsu, China

---

## Concept

_WPS_ stands for _Wi-Fi Protected Setup_

It is a wireless network security standard

Created by _Wi-Fi Alliance_ and introduced in _2006_

---

## Goal

_WPS_ tries to make connections between a router and wireless devices faster and easier

* _WPS_ works only for wireless networks that use a password encrypted with _WPA / WPA2_ personal
* _WEP_ is not supported

---

## Mode

If you want to connect a wireless device to a wireless network, you need to know -

* _SSID_ (network name)
* _PSK_ (password of network)

Without these two elements, you can't connect to a _Wi-Fi_ network

What can _WPS_ do?

1. Press the _WPS_ on router to turn on discovery of new devices. Then, go to your device and select the network you want to connect to. The device is __automatically__ connected to the wireless network __without entering the network password__.
2. For devices with _WPS_ buttons. Pressing the _WPS_ button on the router and then on those devices. You don't have to input any data during this process. _WPS_ automatically sends the network password, and devices remember it for future use.
3. All routers with _WPS_ enabled have a __PIN__ code that is automatically generated, and it cannot be changed by users. Some devices without a _WPS_ button but with _WPS_ support will ask for that _PIN_. If you enter it, they authenticate themselves and connect to the wireless network.
4. Some devices without a _WPS_ button but with _WPS_ support will generate a client _PIN_. You can enter this _PIN_ in router's wireless configuration panels, and the router will use it to add that device to the network.

First two ways are rapid, the last two ways do not provide any benefits regarding the time it takes to connect devices to your wireless network.



## Problem

The _PIN_ is __insecure__ and __easy to hack__

* Eight-digit _PIN_ is stored by routers __in two blocks of four digits__ each
* The router checks the first four digits __separately__ from the last four digits
* A hacker can __brute-force__ the _PIN_ in as little as _4 to 10_ hours
* Once the _PIN_ is brute forced, _PSK_ is found

---

## Summary

_WPS_ 是一个可选的较为矛盾的标准

一方面它简化了无线网络的配置难度

另一方面，它可能招致攻击

_Kali Linux_ 中的 _Reaver_ 工具正是通过暴力破解 _PIN_ 取得 _PSK_

该工具的有效性待实验验证

如果有效，则另写一篇 _note_ 记录

---

