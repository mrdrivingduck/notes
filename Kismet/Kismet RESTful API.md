# Kismet - RESTful API

Created by : Mr Dk.

2018 / 12 / 03 13:01

Nanjing, Jiangsu, China

---

### About

通过何种方法从 _kismet_ 中获取抓到的 _802.11_ 数据包呢？

以前的 _kismet release_ 中：

* 有一套专门的 _protocol_
* 用户可以自己实现一套客户端，与 _kismet server_ 建立 _TCP_ 连接
* 通过 _TCP_ 的 _I/O stream_ 根据这套专门的协议向 _kismet server_ 发送请求，并获取数据

最新的 _Kismet-2018-08 Release_ 中：

* 使用 _kismet_ 提供的 _REST API_ 获取数据
* _API_ 形式：多个 _URL_
* 用户可以自己实现一套客户端，使用 _HTTP_ 请求对应的 _URL_，并附带相应参数，获取 _JSON_ 格式的数据

### What is REST?

表现层状态转换（_Representational State Transfer, REST_）是一种 __软件架构风格__

由 _Roy Thomas Fielding_ 博士于 _2000_ 年在其博士论文中提出

目的：便于不同的程序在网络中互相传递信息

* 基于 _HTTP_ 协议之上而确定的一组约束和属性
* 允许客户端发出以 _URI_ 访问和操作资源的请求
  * 资源由 _URI_ 指定
  * 对资源的获取、创建、修改和删除，正好对应 _HTTP_ 的 _GET_、_POST_、_PUT_ 和 _DELETE_
  * 资源的表现形式可以是 _XML_、_HTML_，也可以是 _JSON_ 等其它形式

架构约束：

* _Client-Server_ - 通信由客户端单方面发起（_Request-Response_）
* _Stateless_ - 无状态，通信的会话状态由客户端负责维护
* _Cache_ - 缓存
* _Uniform Interface_ - 统一接口
* _Layered System_ - 分层系统，限制组件行为

优势：

* 通信的无状态性可以让不同的服务器处理不同的请求，提高服务器的扩展性
* 浏览器即可作为客户端，简化了软件需求
* 软件依赖性小
* 不需要额外的资源发现机制
* 长期兼容性好

### Kismet REST API

可以查看 _kismet_ 目录下的官网文档

所有数据将以 _JSON_ 的格式返回到客户端

所有 _API_ 包含以下访问点：

* _System Status_
  * `/system/status.json`
  * `/system/timestamp.json`
  * `/system/tracked_fields.html`
* _Device Handling_
  * `devices/last-time/[TS]/devices.json`
  * `/devices/by-key/[DEVICEKY]/device.json`
  * `/devices/by-mac/[DEVICEMAC]/devices.json`
  * ......
* _Device Editing_
* _Phy Handling_
* _Sessions and Logins_
* _Messages_
  * `/messagebus/last-time/[TS]/messages.json`
* _Alerts_
  * `/alerts/definitions.json`
  * `/alerts/last-time/[TS]/alerts.json`
* _Channels_
* _Datasources_
* _GPS_
* _Packet Capture_
* _Plugins_
* _Streams_
* _Logging_
* ......

### Client 实现机制

* 定义消息的封装机制：_Device_ 类、_Alert_ 类等
* 封装好访问不同 _API_ 的 _HTTP_ 请求（_GET_ / _POST_）及对应参数
* 发送 _HTTP_ 请求
* 将获取到的数据封装到预先定义的消息类中，成功得到一个带有数据的消息对象

_e.g._ 本人已经实现的一套 _Java_ 客户端：https://github.com/mrdrivingduck/kismet-Jclient

---

### Summary

_kismet_ 的这套 _REST API_ 机制

使各种语言的客户端都可以通过网络从 _kismet server_ 中获取数据

由于网络与平台无关，也和语言无关

因此大大提高了 _kismet_ 的扩展性，使其能够通过网络扩展到各种系统中

---

