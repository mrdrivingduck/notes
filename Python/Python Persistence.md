# Python - Persistence

Created by : Mr Dk.

2020 / 01 / 07 13:41

Nanjing, Jiangsu, China

---

即 __持久化__ : 将 __瞬时数据__ (如内存中的数据，不能永久保存) 持久化为 __持久数据__

为什么有这样的需求 😦

哦最近在用 Python 训练 ML 模型

训练完以后程序直接开始用模型预测数据

结果跑到一半出错了，程序结束，之前的模型也没了

但是由于我不知道模型在内存中的具体形式

也没法用文件操作将其写入文件进行持久化 🥱

---

## _pickle_

Python 的内置模块 _pickle_ 提供了序列化与反序列化的功能

可以直接将内存中的对象保存到文件中，而不用操心对象具体的形式

如果说 _JSON_ 是为了提供一种通用的序列化格式 (且人类可读)

那么 _pickle_ 就是一种 Python 特有的序列化格式 (仅 Python 程序能够使用)

### _dump_

将对象写入文件

需要以 __二进制写入__ 模式打开文件

函数原型:

```python
pickle.dump(obj, file, protocol=None, *, fix_imports=True, buffer_callback=None)
```

```python
with open("tmp.pk", "wb") as f:
    pickle.dump(data, f)
```

### _read_

从文件中读取对象

需要以 __二进制读取__ 模式打开文件

函数原型:

```python
pickle.load(file, *, fix_imports=True, encoding="ASCII", errors="strict", buffers=None)
```

```python
with open("tmp.pk", "rb") as f:
    data = pickle.load(f)
```

### Protocols

目前 (Python 3.8.1) 的 _pickle_ 模块中有 6 种不同的序列化协议版本

* 0 - 人类可读协议，与之前的 Python 版本兼容
* 1 - 旧的二进制协议，与之前的 Python 版本兼容
* 2 - 新的有效协议 (Python 2.3 后)
* 3 - 支持字节对象的协议 (Python 3.0 后)
* 4 - 支持大对象、更多种对象、对一些数据格式进行了优化 (Python 3.4 后) (Python 3.8 的默认协议)
* 5 - (Python 3.8 后)

在调用 `dump()` 时，可以附加协议

在调用 `load()` 时，协议版本会被自动检测

---

## Model Persistence in _scikit-learn_

在调用 _sklearn_ 进行机器学习模型训练时

有时也需要对训练出的模型进行持久化

除了使用 _pickle_ 外，_sklearn_ 自带了更有效的 `joblib`

* 对于带有较大数组的对象来说更加有效

```python
from joblib import dump, load
dump(clf, "filename.joblib")
```

```python
clf = load("filename.joblib") 
```

---

## References

https://docs.python.org/3/library/pickle.html

https://scikit-learn.org/stable/modules/model_persistence.html

---

