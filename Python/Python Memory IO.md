# Python - Memory IO

Created by : Mr Dk.

2018 / 12 / 25 19:28

Nanjing, Jiangsu, China

---

## About

_StringIO_ & _BytesIO_

类似 _Java_ 中的 `StringBuilder` ？？？

## StringIO

需要导入内置 `io` 模块

写入

* 先初始化一个 `StringIO`
* 再像文件一个写入即可
* 使用 `getvalue()` 函数获得最后的结果

读取

* 先初始化一个 `StringIO`
* 再像文件一样读取即可

```python
from io import StringIO

out = StringIO()
out.write("Hello")
out.write(" ")
out.write("world!")
print(out.getvalue())

in = StringIO("Hello!\nHi!\nGoodbye!")
while True:
    str = in.readline()
    if str == '':
        break
    print(s.strip())
```

## BytesIO

`StringIO` 只能操作字符串，如果需要操作二进制数据，需要使用 `BytesIO`

```python
from io import BytesIO

out = BytesIO()
out.write("你好".encode("utf-8"))
print(out.getvalue())

in = BytesIO(b"\xe4\xb8\xad\xe6\x96\x87")
print(in.read())
```

---

## Summary

感慨 _Python_ 的内置封装真多

怪不得对新手友好......

---

