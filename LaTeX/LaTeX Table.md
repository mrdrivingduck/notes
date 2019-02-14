# LaTeX - Table

Created by : Mr Dk.

2019 / 02 / 14 12:52

Ningbo, Zhejiang, China

---

### About

学习了使用 _LaTeX_ 绘制表格

---

### Table with no Lines

* `{tabular}{xxx}` 表示表格列数，有几个 `x` 就有几列
* `x` 可以取 `l`、`c`、`r`，分别代表左对齐、居中、右对齐
* 每行中的每一列用 `&` 分开，行尾使用换行符 `\\`

``` latex
\begin{tabular}{ccc}
    1.1 & 1.2 & 1.3 \\
    2.1 & 2.2 & 2.3 \\
\end{tabular}
```

---

### Table with Lines

* `{tabular}{|c|c|c|}` 可以定义竖线
* `\hline` 可以定义横线

``` latex
\begin{tabular}{|c|c|c|}
    \hline
    1.1 & 1.2 & 1.3 \\
    \hline
    2.1 & 2.2 & 2.3 \\
    \hline
\end{tabular}
```

* 使用 `booktabs` 包可以画出表格上端和下端的加粗线

---

### Complete Table

* 在 `{table}[]` 后使用参数
    * `!` - 忽略美观因素，尽可能按照参数指定的方式排版；无法排版时，使用下一个参数
    * `h` - here，将表格排版在当前文字位置
    * `t` - top，将表格排版在下一页页首
    * `b` - bottom，将表格排版在当前页底部
* 使用 `\caption{xxx}` 来添加表名

``` latex
\begin{table}[!htbp]
    \centering

    \begin{tabular}{|c|c|c|}
        \hline
        1.1 & 1.2 & 1.3 \\
        \hline
        2.1 & 2.2 & 2.3 \\
        \hline
    \end{tabular}

    \caption{Testing Table}

\end{table}
```

---

### Summary

累了 其它复杂表格

等要用到的时候再研究吧

今天情人节

我他妈还在心态爆炸 累了

---

