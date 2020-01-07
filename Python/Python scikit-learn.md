# Python - scikit-learn

Created by : Mr Dk.

2019 / 05 / 14 20:13

Nanjing, Jiangsu, China

---

## About

Machine Learning in Python

* Simple and efficient tools for data mining and data analysis
* Accessible to everybody, and reusable in various contexts
* Built on NumPy, SciPy, and matplotlib
* Open source, commercially usable - BSD license

<https://scikit-learn.org/stable/>

<https://github.com/scikit-learn/scikit-learn>

通用的机器学习模块

* 模块高度抽象化
* 基本所有的分类器可以在 3 - 5 行内完成

---

## Features Structure

算法输入为一个特征向量数组

里面的每个元素为一个特征向量

特征向量的每个元素为各维度的特征值

```
[
    [ a1, b1, ..., z1 ],
    [ a2, b2, ..., z2 ],
    ...
    [ an, bn, ..., zn ]
]
```

如果是分类算法，算法还需要输入标签数组：

```
[
    0, 1, 1, 0, ..., 0, 1
]
```

---

## Standardization

用于数据预处理

```python
from sklearn.preprocessing import StandardScaler

origin_data = [
    [ 1, 2, 3, ..., 6 ],
    [ 2, 4, 6, ..., 8 ],
    ...
]
ss = StandardScaler()
std_data = ss.fit_transform(origin_data)
```

`std_data` 的形式与 `origin_data` 一致

但其中的数值已经经过了标准化

---

## Classification

首先需要将训练数据、标签、测试数据准备好

* 训练数据和测试数据的格式

  ```
  [
      [ a1, b1, ..., z1 ],
      [ a2, b2, ..., z2 ],
      ...
      [ an, bn, ..., zn ]
  ]
  ```

* 标签格式

  ```
  [
      0, 1, 1, 0, ..., 0, 1
  ]
  ```

选用相应的算法执行

* 实例化算法，选择参数
* 对算法调用 `.fit()`，输入训练数据和标签，训练模型
* 对模型调用 `.predict()`，输入测试数据
* 返回值为预测的标签，格式与模型训练时输入标签的格式一致

```python
from sklearn.naive_bayes import GaussianNB

clf_gau_nb = GaussianNB().fit(training_data, training_label)

res = clf_gau_nb.predict(testing_data)
```

---

## Summary

Python + sklearn 让机器学习的实现变得简单。。。

能让不明白这个算法原理的人可以直接上手使用

最近做毕设实验

只用到了其中的标准化模块（Z-score）

和几个分类算法：

* Linear Regression
* Logistic Regression
* Support Vector Machine
* Gaussian Naïve-Bayes

根据官网的介绍

可以完成分类、回归、聚类、降维、模型选择、预处理的功能

可把它 🐂🍺 坏了

---

