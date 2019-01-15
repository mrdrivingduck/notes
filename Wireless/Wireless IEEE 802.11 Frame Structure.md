# Wireless - IEEE 802.11 Frame Structure

Created by : Mr Dk.

2019 / 01 / 15 15:28

Nanjing, Jiangsu, China

---

### General Format

![general-frame](../img/802.11-general-frame.png)

* _MAC Frame Header_ + _Frame Body_ + _FCS_

#### Frame Control

![frame-control](../img/802.11-general-framecontrol.png)

其中的 `type` 和 `subtype` 用于指定具体的帧类型

* _Control Frame_
* _Management Frame_
* _Data Frame_

#### Duration/ID

#### Address

* Address1 - _Destination Address_
* Address2 - _Source Address_
* Address3 - _Basic Service Set ID (BSSID)_

#### Sequence-Control

* 重组帧
* 丢弃重复的帧

#### Frame Body

* 携带上层数据（_Payload_）

#### FCS

* 循环冗余码（_Cyclic Redundancy Check, CRC_）
* 保护 _Frame Header_ + _Frame Body_
* 若 _FCS_ 运算出错，则立即丢弃该帧，不应答

---

### Data Frame

![dataframe](../img/802.11-data.png)

_STA_ 在收到数据帧时，首先检查 _BSSID_，若 _BSSID_ 与 _STA_ 相同时，才会向上层协议栈解析

#### IBSS Frame

![data-ibss](../img/802.11-data-ibss.png)

#### From AP Frame

![data-from-ap](../img/802.11-data-from-ap.png)

区分 _TA_ 和 _SA_

* _802.11_ 标准将应答发送到 _Transmitter Address_ （发送端 _AP_）
* 上层协议会将应答发送给 _Source Address_

#### To AP Frame

![data-to-ap](../img/802.11-data-to-ap.png)

#### WDS Frame

当 _AP_ 被部署为无线桥接时，_Address4_ 会被用到

![data-wds](../img/802.11-data-wds.png)

---

### Control Frame

#### RTS Frame

![control-rts](../img/802.11-control-rts.png)

* 在 _CSMA/CA_ 中用于取得传输介质的控制权

#### CTS Frame

![control-cts](../img/802.11-control-cts.png)

* “允许发送”

#### ACK Frame

![control-ack](../img/802.11-control-ack.png)

* “应答”

#### PS-Poll Frame

![control-ps-poll](../img/802.11-control-ps-poll.png)

---

### Management Frame

![management-general](../img/802.11-management-general.png)

_Frame Body_ 中包含固定字段（_Fixed Fields_）和长度不定的 _Information Elements_

根据 _Frame Control_ 中的 _Sub-Type_，可以分为许多中子类型：

| Sub-Type | Frame Type              |
| -------- | ----------------------- |
| 0000     | Association Request     |
| 0001     | Association Response    |
| 0010     | Re-association Request  |
| 0011     | Re-association Response |
| 0100     | Probe Request           |
| 0101     | Probe Response          |
| 1000     | Beacon                  |
| 1001     | ATIM                    |
| 1010     | Disassociation          |
| 1011     | Authentication          |
| 1100     | Deauthentication        |

#### Authentication Frame

![management-authen-request](../img/802.11-management-authen-request.png)

#### Association Request Frame

![management-asso-request](../img/802.11-management-asso-request.png)

* 经过 _Authentication_ 后进行，试图加入网络

#### Re-association Request Frame

![management-reasso-request](../img/802.11-management-reasso-request.png)

#### (Re-)Association Response Frame

![management-asso-response](../img/802.11-management-asso-response.png)

#### Disassociation & De-authentication Frame

![management-deauth](../img/802.11-management-deauthen.png)

#### Beacon Frame

![management-beacon](../img/802.11-management-beacon.png)

* 定期发送 _Beacon_ 帧以宣告某个网络的存在

#### Probe Request Frame

![management-probe-request](../img/802.11-management-probe-request.png)

* 收到该帧的 _STA_ 会判断对方能否加入网络

#### Probe Response Frame

![management-response](../img/802.11-management-probe-response.png)

#### ATIM Frame

![management-atim](../img/802.11-management-atim.png)

---

### Summary

在 _IEEE_ 官网下载了 _802.11_ 标准文档

但是有 _3000_ 多页的 _PDF_

实在是吃不消

在 _CSDN_ 上看了一些资料

算是快速入门了解一下

可以马上应用到 _Scapy_ 的 _Packet Manipulation_ 中

图片来自 _[CSDN](https://blog.csdn.net/u012503786/article/details/78783874)_，侵删

---

