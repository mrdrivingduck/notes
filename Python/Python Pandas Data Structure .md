# Python - Pandas Data Structure

Created by : Mr Dk.

2019 / 05 / 05 17:41

Nanjing, Jiangsu, China

---

## About

<https://pypi.org/project/pandas/> - 

```bash
$ pip install pandas
```

> __pandas__ is a Python package providing fast, flexible, and expressive data structures designed to make working with structured (tabular, multidimensional, potentially heterogeneous) and time series data both easy and intuitive. It aims to be the fundamental high-level building block for doing practical, __real world__ data analysis in Python. Additionally, it has the broader goal of becoming __the most powerful and flexible open source data analysis / manipulation tool available in any language__. It is already well on its way toward this goal.

>  The two primary data structures of pandas, __Series__ (1-dimensional) and __DataFrame__ (2-dimensional), handle the vast majority of typical use cases in finance, statistics, social science, and many areas of engineering. For R users, __DataFrame__ provides everything that R’s `data.frame` provides and much more. pandas is built on top of [NumPy](http://www.numpy.org/) and is intended to integrate well within a scientific computing environment with many other 3rd party libraries.

Wiki - 

>  __pandas__ is a software library written for the Python programming language for data manipulation and analysis. In particular, it offers data structures and operations for manipulating __numerical tables__ and __time series__.

Baidu - 

> pandas 是基于 NumPy 的一种工具，该工具是为了解决数据分析任务而创建的。Pandas 纳入了大量库和一些标准的数据模型，提供了高效地操作大型数据集所需的工具。pandas提供了大量能使我们快速便捷地处理数据的函数和方法。

---

## Data Structure

```python
import numpy as np
import pandas as pd
```

### Series

* One-dimensional labeled array
* Capable of holding any data type
  * integers
  * strings
  * floating point numbers
  * Python objects
  * etc.
* The axis labels are collectively referred to as the __index__

```python
s = pd.Series(data, index=index)
```

其中，`data` 可以是 - 

* A Python __dict__
* An `ndarray` of `numpy`
* A scalar value

#### From ndarray

如果 `data` 是 `ndarray`

* `index` 必须和 `data` 等长
* 如果没有 `index`，则自动生成 `[0, ..., len(data) - 1]` 的 index

> pandas 支持非唯一的 index 值。但如果操作不支持重复 index，将产生异常。

#### From dict

dict 的 key 作为 index，value 作为 data

若不指定 index，则不同版本可能按照不同的 index 顺序构造序列

* Python >= 3.6 and Pandas version >= 0.23 - index 服从 dict 的插入顺序
* Python < 3.6 or Pandas < 0.23 - index 服从 dict key 的词典顺序

若数据缺失 - `NaN`

>  NaN (not a number) is the standard missing data marker used in pandas.

#### From scalar value

如果 `data` 是数值

* `index` 必须被提供
* 数值会被重复至匹配 index 长度

#### ndarray-like

和 `ndarray` 类似，Series 可以根据下标索引任意读取、截取

可以通过 `Series.array()` 获取 Extension Array

也可以通过 `Series.to_numpy()` 转换为 NumPy 的 ndarray

#### dict-like

根据索引字符串可以取得 value

#### Name Attribute

```python
s = pd.Series(np.random.randn(5), name='something')
s2 = s.rename("different")
```

> `s` and `s2` refer to different objects.

### DataFrame

* 2-dimensional labeled data structure
* Columns of potentially different types

__index__ - (row labels)

__columns__ - (column labels)

#### From dict of Series or dicts

* dict key 作为 column
* Serie index 作为 index

若在构造函数中指定 index 或 column，则替换为对应指定值

#### From dict of ndarrays / lists

### Panel

> Warning
>
> In 0.20.0, `Panel` is deprecated and will be removed in a future version.

行吧 既然都要过时了 不谈

---

## Summary

py 真尼玛烦 我好烦我好烦

但这个库用到的场合实在是太多了...

再烦也得学

---

