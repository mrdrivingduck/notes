# Git - Commit

Created by : Mr Dk.

2018 / 11 / 26 09:42

Nanjing, Jiangsu, China

---

## About

### 检查当前文件状态（已暂存与未暂存的修改）

```bash
$ git status
```

### 跟踪新文件 / 暂存已修改文件

```bash
$ git add README.md
$ git add .
$ git add -A
```

### 查看提交历史

```bash
$ git log
```

## Commit - 提交更新

每次 commit 一般会带有注释，表示本次提交完成的工作，如下面的 `"Updated ..."`

```bash
$ git commit -m "Updated ..."
```

如果在 commit 后想修改注释：

```bash
$ git commit --amend
```

## 撤销 Commit

使用 `git reset` 命令，附带不同的参数：

`$ git reset --mixed HEAD^` - 默认参数

* 不删除工作空间中的改动代码
* 撤销 commit
* 撤销文件追踪

`$ git reset --soft HEAD^`

* 不删除工作空间中的改动代码
* 撤销 commit
* 不撤销文件追踪

`$ git reset --hard HEAD^`

* 删除工作空间的改动代码
* 撤销 commit
* 撤销文件追踪
* **实际上就是恢复到上一次的 commit 状态**

---

