# HTTP - Message Format

Created by : Mr Dk.

2018 / 11 / 08 09:36

Nanjing, Jiangsu, China

---

### Concept

* 请求报文（request message） - _Web_ 客户端 &rarr; _Web_ 服务器
* 应答报文（response message） - _Web_ 服务器 &rarr; _Web_ 客户端

### Structure of message

* 请求报文
  * 请求行（request line）
    * 方法（method） - `GET`、`POST`、...
    * URL
    * HTTP version
  * 报头（header）
  * 空白行（blank line） - 报头部分的结束标志
  * 正文（body） - 可空
* 应答报文
  * 状态行（status line）
    * HTTP version
    * 状态码 - `404`、`200`、...
    * 状态短语
  * 报头（header）
  * 空白行（blank line）
  * 正文（body）

### Structure of header

四种类型 - 

* 通用头部
* 请求头部
* 应答头部
* 正文头部

其中，请求报文中只含有 - 

* 通用头部
* 请求头部
* 正文头部

应答报文中只含有 - 

* 通用头部
* 应答头部
* 正文头部

#### 通用头部

给出关于报文的通用信息

| 字段          | 说明               |
| ------------- | ------------------ |
| Cache-control | 高速缓存信息       |
| Connection    | 连接是否应该关闭   |
| Date          | 当前日期           |
| MIME-version  | MIME 版本          |
| Upgrade       | 优先使用的通信协议 |

#### 请求头部

只会在 __请求报文__ 中出现，指明客户端配置与客户优先使用的文档格式

| 字段                | 说明                                 |
| ------------------- | ------------------------------------ |
| Accept              | 客户端能够接受的数据格式             |
| Accept-charset      | 客户端能够处理的字符集               |
| Accept-encoding     | 客户端能够处理的编码方案             |
| Accept-language     | 客户端能够接受的语言                 |
| Authorization       | 客户端具有何种授权                   |
| From                | 客户端的电子邮件地址                 |
| Host                | 客户端的主机和端口号                 |
| If-modified-since   | 只在比指定日期更新时才发送这个文档   |
| If-match            | 只在与指定标记匹配时才发送这个文档   |
| If-not-match        | 只在与指定标记不匹配时才发送这个文档 |
| If-range            | 只发送缺少的那部分文档               |
| If-unmodified-since | 如果在指定日期之后还未改变则发送文档 |
| Referrer            | 被链接文档的 URL                     |
| User-agent          | 客户程序                             |

#### 应答头部

只出现在 __应答报文__ 中，指明服务器的配置与关于请求的特殊信息

| 字段         | 说明                             |
| ------------ | -------------------------------- |
| Accept-range | 服务器接收客户端请求的范围       |
| Age          | 文档的使用期限                   |
| Public       | 可以支持的方法清单               |
| Retry-after  | 指明的日期之后，服务器才能够使用 |
| Server       | 服务器名与版本号                 |

#### 正文头部

说明关于文档正文的信息

| 字段             | 说明                     |
| ---------------- | ------------------------ |
| Allow            | URL 可使用的合法方法     |
| Content-encoding | 编码方案                 |
| Content-language | 语言                     |
| Content-length   | 文档长度                 |
| Content-range    | 文档范围                 |
| Content-type     | 数据类型                 |
| Etag             | 正文标记                 |
| Expires          | 内容可能改变的时间与日期 |
| Last-modified    | 上次内容改变的时间与日期 |
| Location         | 被创建和被移动的文档位置 |

---

### Summary

在进行 _HTTP_ 编程时需要用到个别字段

做完笔记心里大致有个数了

---

