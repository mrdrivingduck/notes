# LaTeX - *Beamer*

Created by : Mr Dk.

2019 / 11 / 23 15:21

Nanjing, Jiangsu, China

---

## About

[Beamer](https://github.com/josephwright/beamer) is a LaTeX class for producing presentations and slides.

> The beamer LATEX class can be used for producing slides. The class works in both PostScript and direct PDF output modes, using the [pgf](https://ctan.org/pkg/pgf) graphics system for visual effects.
>
> Content is created in the frame environment, and each frame can be made up of a number of slides using a simple notation for specifying material to appear on each slide within a frame. Short versions of title, authors, institute can also be specified as optional parameters. Whole frame graphics are supported by plain frames. The class supports figure and table environments, transparency effects, varying slide transitions and animations. Beamer also provides compatibility with other packages like [prosper](https://ctan.org/pkg/prosper).
>
> The package now incorporates the functionality of the former `translator` package, which is used for customizing the package for use in other language environments.
>
> Beamer depends on the following other packages: [atbegshi](https://ctan.org/pkg/atbegshi), [etoolbox](https://ctan.org/pkg/etoolbox), [hyperref](https://ctan.org/pkg/hyperref), [ifpdf](https://ctan.org/pkg/ifpdf), [pgf](https://ctan.org/pkg/pgf), and [translator](https://ctan.org/pkg/translator).

---

## Command

在安装了 *beamer* 宏包后，就可以使用 *beamer* 中的内置命令了。

```tex
\somebeamercommand[⟨optional arguments⟩]{⟨first argument⟩}{⟨second argument⟩}
```

```tex
\begin{somebeamerenvironment}[⟨optional arguments⟩]{⟨first argument⟩}
    ⟨environment contents⟩
\end{somebeamerenvironment}
```

---

## Structure

文件的开头，声明这是一个 beamer document，以及关于 slides 的一些基本信息。然后在 document 中声明每一页 slide (也就是一个 `frame`)：

```tex
\documentclass{beamer}
\mode<presentation> 

\title{YOUR TITLE}
\date{\today}
\author[mrdrivingduck]{Jingtang Zhang \\ \texttt{jingtangzhang@nuaa.edu.cn}}
\institute{NUAA}

\begin{document}

    % document content

    \begin{frame}
        % a page
    \end{frame}

    \begin{frame}
        % a page
    \end{frame}

\end{document}
```

---

## Style

分为样式主题和颜色主题两种。关于 *beamer* 中自带样式的比较，可以在 [这个网站](https://hartwork.org/beamer-theme-matrix/) 中查看：

```tex
\usetheme{Montpellier}
\usecolortheme{dolphin}
\usefonttheme[onlylarge]{structuresmallcapsserif}
```

此外还可以自己调整：

```tex
\setbeamerfont{title}{shape=\itshape,family=\rmfamily}
\setbeamercolor{title}{fg=red!80!black,bg=red!20!white}
```

---

## The Title Page Frame

将 slide 中已经声明的 metadata 显示在页面上，形成 slide 的封面。

```tex
\begin{frame}
    \titlepage
\end{frame}
```

---

## The Table of Contents

大纲 / 目录：

```tex
\begin{frame}
    \frametitle{Outline}
    \tableofcontents[pausesections]
\end{frame}
```

---

## Sections and Subsections

将 slide 组织为几个 section：

```tex
\section{Motivation}
\subsection{The Basic Problem That We Studied}
```

```tex
\documentclass{beamer} % This is the file main.tex

\usetheme{Berlin}
\title{Example Presentation Created with the Beamer Package} \author{Till Tantau} \date{\today}

\begin{document}

\begin{frame}
    \titlepage
\end{frame}

\section*{Outline}
    \begin{frame}
        \tableofcontents
    \end{frame}

\section{Introduction}
    \subsection{Overview of the Beamer Class}
    \subsection{Overview of Similar Classes}
\section{Usage}
    \subsection{...}
    \subsection{...}
\section{Examples}
    \subsection{...}
    \subsection{...}

\begin{frame}

\end{frame} % to enforce entries in the table of contents

\end{document} 
```

---

## Frames

Frame 对应了一个页面，可能会被渲染成多页：

```tex
\begin{frame}
    \frametitle{What Are Prime Numbers?}
    \framesubtitle{The proof uses \textit{reductio ad absurdum}.}
    
    \begin{definition}
        A \alert{prime number} is a number that has exactly two divisors.
    \end{definition}

    \begin{proof}
        \begin{enumerate}
            \item<1-> Suppose $p$ were the largest prime number.
            \item<2-> Let $q$ be the product of the first $p$ numbers.
            \item<3-> Then $q + 1$ is not divisible by any of them.
            \item<1-> But $q + 1$ is greater than $1$, thus divisible by some prime number not in the first $p$ numbers.\qedhere
            % \qedhere 使这一条一直显示
            % 别的 item 将会被渲染成多页依次显示
        \end{enumerate}
    \end{proof}

\end{frame}
```

其中内置了很多有用的环境 (命令)

* `frametitle` 和 `framesubtitle` 用于指示 frame 的小标题
* 一些数学风格的样式：
    * 定义 (definition)
    * 定理 (theorem)
    * 引理 (lemma)
    * 证明 (proof)
    * 结论 (corollary)
    * 例子 (example)

---

更多使用细节：

http://mirrors.ctan.org/macros/latex/contrib/beamer/doc/beameruserguide.pdf

---

