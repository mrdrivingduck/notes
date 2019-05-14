# LaTeX - Figure

Created by : Mr Dk.

2019 / 05 / 14 20:51

Nanjing, Jiangsu, China

---

## About

在 LaTeX 中插入矢量图

---

## Drawing

使用 Python 中的 _seaborn_ 模块进行绘制

该模块基于 matplotlib

所以可以直接调用 matplotlib 的 `savefig()` 函数：

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="darkgrid")

df = pd.read_csv(filepath_or_buffer='data/accuracy.csv')

sns.lineplot(x="AP", y="Accuracy",
             hue="Algorithm",
             data=df)

plt.ylim(0.6, 1.05)
plt.show()
plt.savefig('out/accuracy.pdf', format='pdf')
```

保存格式可以为：

* `.pdf`
* `.svg`

为了方便插入到 LaTeX 中，输出 `.pdf` 比较好

---

## Insertion

```latex
\begin{figure}[!htbp]
    \includegraphics{accuracy.pdf}
    \caption{Algorithms comparison}
    \label{}
\end{figure}
```

---

