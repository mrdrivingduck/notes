# LaTeX - Algorithm

Created by : Mr Dk.

2019 / 05 / 14 20:29

Nanjing, Jiangsu, China

---

## About

如何在 LaTeX 中绘制算法块？使用宏包 - [*algorithm2e*](https://ctan.org/pkg/algorithm2e)。

---

## Usage

### Install

`[]` 中的选项影响算法块的样式。

```latex
\usepackage[ruled]{algorithm2e}
\usepackage[ruled,linesnumbered]{algorithm2e} % with line number
```

### Writing

```latex
\begin{algorithm}
    \caption{Evil Twin Detection Algorithm}
    
    ...

\end{algorithm}
```

```latex
\KwIn{input}
\KwOut{output}
\KwData{input}
\KwResult{output}

\Begin{block inside}
\Begin(begin comment){block inside}

\If{condition}{then block} % if then
\eIf{condition}{then block}{else block} % if this than that
\Switch{condition}{Switch block}
\Case{a case}{case block}
\Other{otherwise block}
\For{condition}{text loop}
\While{condition}{text loop}

\KwRet{[value]} % return
\Return{[value]} % return
```

在每行的最后需要加上 `\;`

* 默认情况下，打印一个 `;`
* 可以通过 `\dontprintsemicolon` 配置

---

