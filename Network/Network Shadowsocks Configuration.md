# Network - Shadowsocks Configuration

Created by : Mr Dk.

2019 / 01 / 29 18:08

Ningbo, Zhejiang, China

---

## Installation

```bash
$ apt update
$ apt install python-pip python-gevent python-m2crypto
$ pip install --upgrade setuptools
$ pip install shadowsocks
```

## Configuration

```bash
$ mkdir /etc/shadowsocks
$ vim /etc/shadowsocks/config.json
```

```json
{
    "server":"IP Address",
    "server_port":443,
    "password":"Password",
    "timeout":600,
    "method":"aes-256-cfb",
    "fast_open": false
}
```

## Modification

```bash
$ vim /usr/local/lib/python2.7/dist-packages/shadowsocks/crypto/openssl.py
```

替换 `libcrypto.EVP_CIPHER_CTX_cleanup` 为 `libcrypto.EVP_CIPHER_CTX_reset`

* 这是 _Ubuntu 18.04_ 中才有的毛病
* 替换位置在第 `52` 行和第 `111` 行

## Start Up

```bash
$ ssserver -c /etc/shadowsocks/config.json -d start
```

## Stop

```bash
$ ssserver -c /etc/shadowsocks/config.json -d stop
```

---

## Summary

记录一下

下次自己部署 _VPS_ 就不用百度了

---

