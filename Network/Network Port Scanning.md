# Network - Port Scanning

Created by : Mr Dk.

2019 / 01 / 29 17:03

Ningbo, Zhejiang, China

---

## 起因

从去年十月份起

在 _Vultr_ 上租用一台新加坡的服务器用于科学上网

或者刷刷 _instagram_

最近几天突然连不上了

想从自己电脑上通过 _Xshell_ 连接到服务器上去看看

结果连 _SSH_ 都连不上了

上网搜索了方法

确认了服务器的 _SSH_ 端口已经被封死

其余端口应该也已经被封死

---

## 国内端口扫描

扫描网站 - [http://coolaf.com/tool/port](http://coolaf.com/tool/port)

输入服务器的 _IP_ 地址和 _SSH_ 端口（`22`）

扫描结果是 - __关闭__

我的服务器在国内被封了...... :sob:

---

## 境外端口扫描

扫描网站 - [https://www.yougetsignal.com/tools/open-ports](https://www.yougetsignal.com/tools/open-ports)

输入服务器的 _IP_ 地址和 _SSH_ 端口

扫描结果显示端口是 _open_ 状态

确认了 _Vultr_ 的服务器没有问题

是我的 _IP_ 地址在国内被封了

---

## Solution

销毁服务器实例

重新创建服务器实例

这样可以获得新的 _IP_ 地址

如果这个 _IP_ 地址可以使用就万事大吉

不然的话还要继续销毁、创建......

脑壳疼...... :unamused:

---

