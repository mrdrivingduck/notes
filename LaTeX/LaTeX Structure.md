# LaTeX - Structure

Created by : Mr Dk.

2019 / 02 / 14 12:12

Ningbo, Zhejiang, China

---

## About

学习了使用 _LaTeX_ 进行论文结构的撰写

---

## Title

``` latex
\documentclass{article}

\title{Overview of LaTeX}
\author{Mr Dk.}
\date{\today}

\begin{document}
    \maketitle    % show the title
    \clearpage    % start a new page

    ...

\end{document}
```

---

## Abstract

``` latex
\documentclass{article}

\begin{document}

    \begin{abstract}
        % Here is abstract
    \end{abstract}

\end{document}
```

---

## Section

``` latex
\documentclass{article}

\begin{document}

    \section{Introduction}
        % Here is Section 1

    \section{Related Work}
        % Here is Section 2 

        \subsection{Sub 1}
            % Here is Section 2.1

        \subsection{Sub 2}
            % Here is Section 2.2

\end{document}
```

---

## Summary

这只是入门级的用法

编译出来的 `.pdf` 文档不太好看

和读过的论文的格式不太一样

可能不同的论文有不同的样式文件吧

---

