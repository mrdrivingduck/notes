# Python - Pypi Source

Created by : Mr Dk.

2020 / 01 / 05 10:22

Nanjing, Jiangsu, China

---

## About

__pip__ is the package installer for Python.

You can use pip to install packages from the Python Package Index and other indexes.

与 _Maven_ 类似，_pip_ 默认的下载地址在国外 - https://pypi.org/

而国内很多高校和企业都提供了开源镜像站

配置 pip 从国内的开源镜像站下载显著加快了速度 😁

## Windows

1. 在 `C:/Users/${USER}/` 下建立 `pip/`
2. 创建 `pip.ini` 文件
3. 在文件中编辑：
    ```ini
    [global]
    index-url = http://pypi.mirrors.ustc.edu.cn/simple
    [install]
    trusted-host = pypi.mirrors.ustc.edu.cn
    ```

## Linux

1. 在 `~/` 下建立 `.pip/`
2. 创建 `pip.conf` 文件
3. 在文件中编辑：
    ```ini
    [global]
    index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
    ```

## Others

用到了再说

---

