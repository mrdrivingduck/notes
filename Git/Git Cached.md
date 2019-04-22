# Git - Cached

Created by : Mr Dk.

2019 / 04 / 22 16:29

Nanjing, Jiangsu, China

---

## About

__cached__ 指的是 __暂存区__

即 Git 的三棵树中的 Index（中间那一颗）

暂存了本次将会 commit 的状态

正是因为有了 __cached__

运行 `git status` 时

* 会将工作目录中与暂存区中不一致的部分标红显示

运行 `git add xxx` 后

* 将工作目录中的改动保存到暂存区中
* 再次运行 `git status`，工作目录与暂存区状态相同

## .gitignore

cached 中暂存了所有文件的状态

运行 `git status` 时

只会显示和工作目录中文件状态不一致的文件

而 `.gitignore` 文件的作用：

__阻止被忽略的文件从工作目录中加入暂存区__

对于已经存在于暂存区中的待忽略文件

`.gitignore` 文件将会失效

## Clear Cache

如何使 `.gitignore` 文件重新生效呢？

* 首先应当将整个暂存区清空
* 然后将整个工作目录重新导入暂存区
* 这样，需要被忽略的文件将不会被添加进暂存区

清空暂存区全部文件：

```bash
$ git rm -r --cached .
```

（该命令也可以用于从暂存区中移除某个已经暂存的文件）

将工作目录全部导入暂存区：

```bash
$ git add .
```

再查看暂存区状态，会发现 `.gitignore` 已经生效：

```bash
$ git status
```

---

## Summary

做了一个多月的项目

咋有几个文件明明已经被声明为忽略

但还是一直在版本控制中

原来是暂存区缓存的问题

---

