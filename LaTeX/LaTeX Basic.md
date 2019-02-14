# LaTeX - Basic

Created by : Mr Dk.

2019 / 02 / 13 23:34

Ningbo, Zhejiang, China

---

### About

LaTeX, WiKipedia:

> LaTeX（/ˈlɑːtɛx/，常被读作 /ˈlɑːtɛk/ 或 /ˈleɪtɛk/ ），排版时通常使用 LaTeX，是一种基于 TeX 的排版系统，由美国计算机科学家莱斯利·兰伯特在 20 世纪 80 年代初期开发，利用这种格式系统的处理，即使用户没有排版和程序设计的知识也可以充分发挥由 TeX 所提供的强大功能，不必一一亲自去设计或校对，能在几天，甚至几小时内生成很多具有书籍质量的印刷品。对于生成复杂表格和数学公式，这一点表现得尤为突出。因此它非常适用于生成高印刷质量的科技和数学、物理文档。这个系统同样适用于生成从简单的信件到完整书籍的所有其他种类的文档。

一种我很认可的理解方式：https://blog.csdn.net/shujuelin/article/details/79340373

>  LaTeX 和 Web Page 的工作方式很类似，都由源文件（`.tex` 或 `.html`）经由引擎（TeX 或 Browser）渲染产生最终效果（`.pdf` 文件或页面）。
>
> 在 Web 中，规范的写法是在 `.html` 文件中写入页面结构和内容，由 `.css` 文件控制页面生成的样式；在 LaTeX 中，在 `.tex` 中写入文档的结构和内容，由 `.cls`、`.sty` 文件控制样式。从而做到内容与样式分离。

---

### Installation & Configuration

1. 根据 OS 选择一个 TeX 的发行版进行安装
   * 在 `Windows` 平台上，选择了好友推荐的 `MiKTeX`，直接在官网下载安装即可
2. 选择一个合适的 LaTeX 编辑器
   * `MiKTeX` 也有自带的编辑器
   * 我和朋友的口味一致，喜欢用 `Visual Studio Code`

在 `Visual Studio Code` 中安装 `LaTeX Workshop` 插件

* `LaTeX Workshop` 默认编译链是 `latexmk`，需要在 `MiKTeX console` 中安装软件包
* `latexmk` 编译引擎依赖 _Perl_ 环境 - 在 `Windows` 上可选用 `Strawberry Perl`

---

### Support for Chinese

#### CTeX

在文档中加入 `\usepackage[UTF8]{ctex}` 即可，包管理工具自动下载依赖包

```latex
\documentclass{article}
\usepackage[UTF8]{ctex}
\begin{document}
    Here comes \LaTeX! 你好
\end{document}
```

#### CJK

在文档中加入 `\usepackage{CJK}`，包管理工具也会自动下载依赖包

```latex
\documentclass{article}
\usepackage{CJK}
\begin{document}
\begin{CJK}{UTF8}{song}
    Here comes \LaTeX! 你好
\end{CJK}
\end{document}
```

---

### Build

`ctrl` + `shift` + `P`：选择 `LaTeX Workshop: Build LaTeX project` 命令，生成 `.pdf` 文件

（其实不需要，只要 `.tex` 文件保存后就会自动进行编译）

---

### Summary

想到之后写论文肯定会用到

所以赶紧学习一波

这里感谢我的大佬同学 _Triple-Z_

本文参考了他的博客 - https://blog.triplez.cn/build-a-great-latex-workflow/

这篇日志主要记录了环境的搭建和配置

接下来就是学习各种排版、表格、插图等语法了

---

