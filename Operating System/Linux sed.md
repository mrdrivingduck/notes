# Linux - sed

Created by : Mr Dk.

2019 / 07 / 09 19:38

Nanjing, Jiangsu, China

---

## What Can it Do ?

利用脚本来处理文本文件

```bash
$ sed [-hnV][-e<script>][-f<script文件>][文本文件]
```

---

## Option

* `-e<script>` 或 `--expression=<script>`
* `-f<script_file>` 或 `--file=<script_file>`
* `-n` 或 `--quiet` 或 `--silent` 仅显示脚本处理后的结果

---

## Script

* `a` - 追加在当前行的下一行
* `c` - 取代整行
* `d` - 删除
* `i` - 插入在当前行的上一行
* `p` - 打印
* `s` - 取代字符串（支持正则表达式）

---

## Application

将某个目录下文件中所有的特定字符串替换成另一个字符串

Fine. 是这样 最近一个项目正在收尾

但是我觉得整个项目做得太烂

所以想把所有代码源文件里的作者名 - `mrdrivingduck` 、`Mr Dk.` 之类的

全都替换成 `zjt` 拉倒了

反正也没人知道 zjt 是谁

显然，找文件中出现的特定字符串用的是 `grep` 命令

然后再用 `sed` 命令实现替换

由于 `sed` 命令的参数是文件名

因此必须使 `grep` 的输出是文件名格式

同时，为了搜索目录下所有文件，还需要加入递归选项：

```bash
$ grep -rl "mrdrivingduck" ./*
```

综合起来，用 **命令替换** 使 bash 先执行 `grep`

再将结果作为 `sed` 的输入：

```bash
$ sed -i "s/mrdrivingduck/zjt/g" `grep -rl "mrdrivingduck" ./*`
```

提升一波效率 😏

---

