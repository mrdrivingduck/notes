# LaTeX - Horizontal Table

Created by : Mr Dk.

2019 / 05 / 18 10:46

Nanjing, Jiangsu, China

---

## About

绘制水平并排排列的两张表。使用宏包 - *algorithm2e*。

---

## Usage

利用 `minipage` 实现。可以有总的 `caption` 和各表格独自的 `caption`。

```latex
\begin{minipage}[!htbp]{0.9\linewidth}
    \begin{minipage}[t]{0.4\linewidth}
        \makeatletter\def\@captype{table}\makeatother
        \caption{后端HTTP响应成功参数格式}
        \label{response-success}
        \centering
        \begin{tabular}{ccc}
            \hline
            域 & 类型 & 描述 \\
            \hline
            token & String & 会话令牌 \\
            % \hline
            id & String & 会话ID \\
            % \hline
            version & String & 接口版本 \\
            % \hline
            result & Object & 操作结果 \\
            \hline
        \end{tabular}
    \end{minipage}
    \quad
    \begin{minipage}[t]{0.4\linewidth}
        \makeatletter\def\@captype{table}\makeatother
        \caption{后端HTTP响应失败参数格式}
        \label{response-error}
        \centering
        \begin{tabular}{ccc}
            \hline
            域 & 类型 & 描述 \\
            \hline
            token & String & 会话令牌 \\
            % \hline
            id & String & 会话ID \\
            % \hline
            version & String & 接口版本 \\
            % \hline
            error & Object & 错误状态码 \\
            \hline
        \end{tabular}
    \end{minipage}
\end{minipage}
```

---

