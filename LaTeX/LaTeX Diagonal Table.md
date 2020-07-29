# LaTeX - Diagonal Table

Created by : Mr Dk.

2019 / 05 / 13 19:21

Nanjing, Jiangsu, China

---

## About

原生 LaTeX 不支持绘制斜线表头，需要借助宏包 *diagbox* 实现：

* [GitHub](https://github.com/leo-liu/tex-pkg)
* [CTAN](https://ctan.org/pkg/diagbox/)

---

## Usage

```latex
\usepackage{diagbox}
```

```latex
\begin{tabular}{|l|ccc|}
    \hline
    \diagbox{Time}{Room}{Day} & Mon & Tue & Wed \\
    \hline
    Morning & used & used & \\
    Afternoon & & used & used \\
    \hline
\end{tabular}
```

---

## Parameter

```latex
\diagbox[dir=⟨direction⟩]{A}{B}
```

* NW - 西北（default）
* NE - 东北
* SW - 西南
* SE - 东南

内外边距

斜线宽度

斜线颜色

......

---

