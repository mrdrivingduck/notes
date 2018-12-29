# Python - Logging

Created by : Mr Dk.

2018 / 12 / 29 14:52

Nanjing, Jiangsu, China

---

### Why

为什么要使用日志功能？ - `logging` 与 `print()` 之间的比较

* `logging` 可以实现分级输出的功能
  * 在开发环境或者生产环境中，需要显示的日志信息不一样
  * `print()` 函数在开发环境中可能需要被注释掉
  * 在 `logging` 中只需要指定日志输出的等级就能显示分级日志
* `logging` 支持与第三方模块共同输出
* `logging` 不仅支持输出至控制台，还可以输出至日志文件中
* `logging` 可以配置多个 `handler`，以输出不同信息
* `logging` 支持从文件中读取配置
* ......

### Usage

引用内置模块 `logging`，直接使用 `basicConfig()` 进行配置后即可使用

``` python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

logging.debug(...)
logging.info(...)
logging.warning(...)
logging.error(...)
logging.critical(...)
```

这种方式实际上是给 _root logger_ 添加了一个 `handler`

当程序与别的使用了 `logging` 的第三方模块一起运行时，会影响第三方模块 `logger` 的行为

所以应当为自己的程序单独定义一个 `logger`：

* 若 `logging.getLogger()` 的参数为空，则返回 `root logger`
* 若 `logging.getLogger()` 的参数中指定的 `logger` 不存在，则将创建一个 `logger`
* 若 `logging.getLogger()` 的参数中指定的 `logger` 已存在，则将返回同一个 `logger`

``` python
import logging

hdr = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
hdr.setFormatter(formatter)

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(hdr)
```

### Configuration File

待补充

---

### Summary

`logging` 这个东西确实很有用

随着程序规模的越来越大

确实发现各语言诸如 `print()` 之类的函数

已经无法满足需求了

今天用 _tornado_ 框架写 _WEB server_ 时

就引入了日志

控制台不仅能输出 _server_ 的日志

还会输出第三方模块 _Scapy_ 的日志

这样大大提高了 _DEBUG_ 效率

---

