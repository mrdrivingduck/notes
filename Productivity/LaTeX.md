# LaTeX

Created by : Mr Dk.

2019 / 02 / 13 23:34

Ningbo, Zhejiang, China

---

## About

LaTeX（/ˈlɑːtɛx/，常被读作 /ˈlɑːtɛk/ 或 /ˈleɪtɛk/ ），排版时通常使用 LaTeX，是一种基于 TeX 的排版系统，由美国计算机科学家莱斯利·兰伯特在 20 世纪 80 年代初期开发，利用这种格式系统的处理，即使用户没有排版和程序设计的知识也可以充分发挥由 TeX 所提供的强大功能，不必一一亲自去设计或校对，能在几天，甚至几小时内生成很多具有书籍质量的印刷品。对于生成复杂表格和数学公式，这一点表现得尤为突出。因此它非常适用于生成高印刷质量的科技和数学、物理文档。这个系统同样适用于生成从简单的信件到完整书籍的所有其他种类的文档。

[一种不错的理解方式](https://blog.csdn.net/shujuelin/article/details/79340373)

LaTeX 和 Web Page 的工作方式很类似，都由源文件（`.tex` 或 `.html`）经由引擎（TeX 或 Browser）渲染产生最终效果（`.pdf` 文件或页面）。在 Web 中，规范的写法是在 `.html` 文件中写入页面结构和内容，由 `.css` 文件控制页面生成的样式；在 LaTeX 中，在 `.tex` 中写入文档的结构和内容，由 `.cls`、`.sty` 文件控制样式。从而做到内容与样式分离。

## Installation & Configuration

别废话了，咱就是说，在 Linux 上安装最便捷，编译效率也最高。在 VSCode 中使用 Remote-WSL 或 Remote-SSH 插件连上 Linux 主机，用下面的命令一键安装后，再为 VSCode 安装上 LaTeX Workshop 插件就可以开箱使用了：

```bash
sudo apt install texlive-full
```

## References

[Triple'Z's blog](https://blog.triplez.cn/build-a-great-latex-workflow/)

[Dev on Windows with WSL - LaTeX](https://dowww.spencerwoo.com/3-vscode/3-5-latex.html)
