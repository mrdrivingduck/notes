# Wireless - Sniffing with Wireshark

Created by : Mr Dk.

2019 / 03 / 01 11:18

Nanjing, Jiangsu, China

---

### About

Wikipedia - 

> __Wireshark__ is a free and open-source packet analyzer. It is used for network troubleshooting, analysis, software and communications protocol development, and education. Originally named Ethereal, the project was renamed Wireshark in May 2006 due to trademark issues.
>
> Wireshark is cross-platform, using the _Qt_ widget toolkit in current releases to implement its user interface, and using _pcap_ to capture packets; it runs on Linux, macOS, BSD, Solaris, some other Unix-like operating systems, and Microsoft Windows. There is also a terminal-based (non-GUI) version called _TShark_. Wireshark, and the other programs distributed with it such as _TShark_, are free software, released under the terms of the __GNU General Public License__.

---

### Sniffing 802.11 Frames

Sniffing should be done under _Linux_ - 

```bash
$ sudo apt install wireshark
```

To capture 802.11 frames, the network adapter should be running at __monitor mode__ - 

```bash
$ ifconfig
$ sudo ifconfig wlx0087345038d3 down
$ sudo iwconfig wlx0087345038d3 mode monitor
$ sudo ifconfig wlx0087345038d3 up
$ ifconfig
$ iwconfig
```

```bash
$ sudo wireshark
```

Select the corresponding adapter and start sniffing

---

### Filtering Rules

#### MAC Address Filtering

```
wlan contains 00:11:22:33:44:55 
```

#### Frame Type Filtering

```
wlan.fc.type == 0/1/2
```

#### Frame Sub-Type Filtering

```
wlan.fc.type_subtype == 0x00
```

---

### Summary

如果是单纯的抓包分析

Wireshark 比 Scapy 强太多了

---

