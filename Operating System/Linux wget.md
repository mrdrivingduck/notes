# Linux - wget

Created by : Mr Dk.

2018 / 11 / 26 0:08

Nanjing, Jiangsu, China

---

## About

*wget* 是一个从网络上自动下载文件的自由工具，支持通过 *HTTP*、*HTTPS*、*FTP* 下载，并可以使用 *HTTP* 代理

*wget* 这个名称来源于 *World Wide Web* 与 *get* 的结合

## Purpose

用于在 Linux server 上下载文件。由于 Linux server 没有图形浏览器，虽然网速快，但不方便下载文件。使用 *wget*，只要有待下载文件的 *URL*，就可以飞速下载。

## Example

下载 JDK：

```console
$ wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u181-b13/96a7b8442fe848ef90c96a2fad6ed6d1/jdk-8u181-linux-x64.tar.gz
```

---

## Summary

除去使用文字浏览器之外的另一种下载方式。

---

