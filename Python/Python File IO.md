# Python - File IO

Created by : Mr Dk.

2018 / 12 / 25 19:28

Nanjing, Jiangsu, China

---

### About

_Python_ 内置了读写文件的函数，用法与 _C_ 兼容

---

### Reading

#### Open File

```python
f = open("filename", "r")      # Normal mode
fb = open("filename", "rb")    # Binary mode
fe = open("filename", "r", encoding="gbk", errors="ignore")
```

由于文件读写时，可能会产生 `IOError`，导致之后的 `close()` 函数不会调用

* 因此 _I/O_ 操作需要写在 `try ... finally` 中关闭文件

为了简洁，_Python_ 引入了 `with` 语句，可以 __自动__ 调用 `close()` 函数

```python
with open("filename", "r") as f:
    str = f.read()
    print(str)
```

#### Reading from File

```python
all_content = f.read()
size_content = f.read(4)
line_content = f.readline()
for line in f.readlines():
    print(line.strip())
```

* `read()` - 一次性读取文件的全部内容，适合小文件
* `read(size)` - 比较保险，每次最多读取 `size` 个字节
* `readline()` - 一次读取一行内容
* `readlines()` - 一次读取所有内容并按行返回 `list`，对 `list` 进行迭代

---

### Writing

#### Open File

```python
f = open("filename", "w")      # Normal mode
fb = open("filename", "wb")    # Binary mode
```

#### Writing to File

可以反复调用 `write()` 函数来写入文件

* 但是函数的调用和实际写入磁盘是 __异步__ 的
* 在最终调用 `close()` 时可能才会将所有缓存全部写入磁盘
* 因此忘记调用 `close()` 可能将导致部分数据丢失

保险、简洁起见，还是使用 `with` 语句：

```python
with open("filename", "w") as f:
    f.write("Hello world!")
```

---

### Summary

文件的打开和关闭方式和 _C_ 差不多

读写操作都比较简单

---

