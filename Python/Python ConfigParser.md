# Python - ConfigParser

Created by : Mr Dk.

2018 / 12 / 28 12:56

Nanjing, Jiangsu, China

---

### About

_ConfigParser_ 是 _Python_ 内置的配置文件转换模块

_Python 3.7_ [官网文档](https://docs.python.org/3.7/library/configparser.html)的描述：

> This module provides the `ConfigParser` class which implements a basic configuration language which provides a structure similar to what’s found in Microsoft Windows INI files.  You can use this to write Python programs which can be customized by end users easily.

### Configuration Files

```ini
[DEFAULT]
ServerAliveInterval = 45
Compression = yes
CompressionLevel = 9
ForwardX11 = yes

[bitbucket.org]
User = hg

[topsecret.server.com]
Port = 50022
ForwardX11 = no
```

包含 `section`、`key`、`value` 三个层次

### Writing

```python
import configparser

config = configparser.ConfigParser()
config['DEFAULT'] = {'ServerAliveInterval': '45',
    'Compression': 'yes',
    'CompressionLevel': '9'}
config['bitbucket.org'] = {}
config['bitbucket.org']['User'] = 'hg'

with open("example.ini", "w") as configfile:
    config.write(configfile)
```

* 实际上相当于是一个 `dict`
* 可以用类似数组下标的方式初始化、赋值

### Reading

```python
import configparser

conf = configparser.ConfigParser()
conf.read("confi.ini")

# all sections in a list
conf.sections()
# all options(keys) from a section in a list
conf.options("mysql")
# all options(keys) and their value from a section
# in a list with two tuples
conf.items("mysql")
# get value from a section and key
conf.get("mysql", "port")
```

### Interpolation

`%(xxx)s`

```ini
[Paths]
home_dir: /Users
my_dir: %(home_dir)s/lumberjack
my_pictures: %(my_dir)s/Pictures
```

`${section:option}`

```ini
[Paths]
home_dir: /Users
my_dir: ${home_dir}/lumberjack
my_pictures: ${my_dir}/Pictures
```

---

### Summary

前两天看了一下今年三月份写的 _cnsoft_ 程序

那时候因为还不知道要用配置文件

到现在为止已经不知道部署过多少次了

每次都要改源码的方式修改环境配置......

就在前两天，还又重新部署了一次呢

所以说 以后写大型程序

都一定要用配置文件

可能还需要好几套配置文件

一套用于开发、调试

一套用于发布运行

---

