# LaTeX - ref link

Created by : Mr Dk.

2019 / 05 / 14 20:33

Nanjing, Jiangsu, China

---

## About

在论文中的某些字上设置超链接

跳转到对应的表格、公式或图上

---

## Usage

使用 `\lable{}` 标记被引用的表格 / 公式 / 图片

使用 `\ref{}` 链接到对应的引用处

e.g. - 

```latex
\begin{table}[!htbp]
    \begin{tabular}{|c|c|c|c|c|}
        \hline
        SSID & Vendor & Model & Type & AP-Tag \\
        \hline
        A***1 & TP-Link & TL-WR886N & Hardware & A(1) \\
        \hline
        c***1 & TP-Link & TL-WR886N & Hardware & A(2) \\
        \hline
        m***k & TP-Link & TL-WDR5610 & Hardware & B(1) \\
        \hline
        W***y & TP-Link & TL-WDR5610 & Hardware & B(2) \\
        \hline
        T***r & TP-Link & TL-WR740N & Hardware & C \\
        \hline
        A***2 & ASUS & RT-AC68U & Hardware & D \\ 
        \hline
        D***4 & D-Link & DIR-850L & Hardware & E \\
        \hline
        m***k & Phicomm & FIR302B & Hardware & F \\
        \hline
        n***l & Juniper & / & Hardware & G \\
        \hline
        n***l & Trapeze & / & Hardware & H \\
        \hline
        c***o & ALFA & AWUS036NH & Software(Linux) & I \\
        \hline
        Z***O & Microsoft & / & Software(Windows) & J \\
        \hline
        c***o & HUAWEI & / & Mobile(Android) & K \\
        \hline
        i***X & Apple & / & Mobile(iOS) & L \\
        \hline
    \end{tabular}
    \caption{AP}
    \label{ap-info} 
\end{table}

% ...

表格中的Tag为表 \ref{ap-info} 中的接入点编号
```

---

