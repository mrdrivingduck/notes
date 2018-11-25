# Linux - wget

Created by : Mr Dk.

2018 / 11 / 26 0:08

Nanjing, Jiangsu, China

---

### About

_wget_ 是一个从网络上自动下载文件的自由工具，支持通过 _HTTP_、_HTTPS_、_FTP_ 下载，并可以使用 _HTTP_ 代理

_wget_ 这个名称来源于 _World Wide Web_ 与 _get_ 的结合

### Purpose

在 _Linux server_ 上下载文件

由于 _Linux server_ 没有图形浏览器

网速快 但不方便下载文件

使用 _wget_，只要有待下载文件的 _URL_，就可以飞速下载

### Example

下载 _JDK_

```bash
wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u181-b13/96a7b8442fe848ef90c96a2fad6ed6d1/jdk-8u181-linux-x64.tar.gz
```

---

### Summary

除去使用文字浏览器之外的另一种下载方式

---

