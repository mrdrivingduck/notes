# Git - Reset

Created by : Mr Dk.

2019 / 04 / 04 17:29

Ningbo, Zhejiang, China

---

## About

用 Git 的时候

有时候会遇到一些需要撤销更改

或者回退的情况

以前是自己一个人玩

基本不会遇到类似的问题

现在正在和别人进行协作

所以肯定会遇到类似的问题

今天花了点时间了解了一下 Git 的管理思维

---

## The Three Trees

不知道为何在 Git 中将其命名为 __树__

其实它的意思是一个 __文件的集合__，而不是数据结构

| Tree              | Role                              |
| ----------------- | --------------------------------- |
| HEAD              | Last commit snapshot, next parent |
| Index             | Proposed next commit snapshot     |
| Working Directory | Sandbox                           |

其中，`HEAD` 和 `Index` 记录在 `/.git` 文件夹中

`Working Derectory` 就是展现的工作目录

### HEAD

HEAD 是当前分支引用的指针，指向分支上的最后一次提交

即 __上一次提交的快照__，是开始一次编辑之前的初始状态

### Index

是 __预期的下一次提交__，也就是 Git 中所谓的 __暂存区域__ - stage

在其中，一些文件将会被替换为新版本

### Working Directory

工作目录中的文件在提交至暂存区之前，可以随意编辑

---

## Workflow

Git 主要通过操作上述三棵树的状态来进行版本控制

直观上来看：

* 将 `Working Directory` 中的变更提交到暂存区 `Index`
* 将暂存区 `Index` 中的变更提交到 `HEAD`
* 树之间可以进行状态转移、切换

![git-reset-workflow](../img/git-reset-workflow.png)

### 一次正常的提交过程

> 假设 Git 仓库中最后一次提交的 `file.txt` 文件的版本为 `V1`

在上一次的 `git commit` 提交完成之后：

![git-last-commit](../img/git-last-commit.png)

接下来，对工作目录中的 `file.txt` 进行了相应的改动，改动后的版本为 `V2`：

![git-edit-file](../img/git-edit-file.png)

接下来，使用 `git add file.txt` 将 `V2` 版本保存到暂存区：

![git-add-file](../img/git-add-file.png)

最后，使用 `git commit` 将 `V2` 版本从暂存区中提交，`HEAD` 指针前进：

![git-commit](../img/git-commit.png)

只要三棵树的状态一致，就认为目录是干净的

在切换分支时：

* 修改 `HEAD` 指针指向对应分支
* 将 `Index` 填充为该次提交的快照
* 将 `Index` 中的内容复制到 `Working Directory` 中

---

## Reset

### Soft

`reset` 做的第一件事是移动 `HEAD` 指针的指向

本质上相当于 __撤销了上一次的 `git commit`__

回滚到了 `git commit` 之前

`git reset --soft` 在这一步结束后停止：

![git-reset-soft](../img/git-reset-soft.png)

在这一步中，可以对 `Index` 进行更新，并重新 `git commit`

### Mixed

`reset` 要做的第二件事

除了上一步的 `HEAD` 指针前移以外，还会恢复 `Index` 的状态

这是 `git reset` 的默认行为

本质是：撤销上一次的 `git commit`，还会取消暂存所有的东西

相当于回滚到 `git commit` 和 `git add` 命令执行之前

`git reset [--mixed]` 在这一步结束后停止

![git-reset-mixed](../img/git-reset-mixed.png)

### Hard

`reset` 做的第三件事是将 `Working Directory` 恢复到 `HEAD` 指向的状态

在这一步下，撤销了所有的 `git commit`、`git add` 和 `Working Directory` 中的所有修改

`git reset --hard` 在这一步结束后停止：

![git-reset-hard](../img/git-reset-hard.png)

`git reset --hard` 是一个危险的操作，因为它强制覆盖了工作目录中的文件，无法恢复

### Review

Git 的 `reset` 命令以特定顺序重写三棵树：

* 移动 `HEAD` 指针 - 指定 `--soft` 则到此停止
* 恢复 `Index` - 指定 `--mixed` 或不指定（默认），则到此停止
* 恢复 `Working Directory` - 指定 `--hard` 则到此停止

### File

可以为 `reset` 提供一个作用路径

将作用范围限定为指定的文件或文件集合

* 由于 `HEAD` 是一个指针，无法同时指向两个提交，因此会跳过这一步
* 但 `Index` 和 `Working Directory` 可以部分更新

假如运行 `git reset file.txt` (`git reset --mixed HEAD file.txt`)

1. 移动 `HEAD` 指针（跳过）
2. 将 `Index` 恢复至 `HEAD` 的对应版本

本质上：将 `file.txt` 从 `HEAD` 复制到 `Index` 中

实际上：产生了 __取消暂存文件__ 的效果：

![git-reset-file](../img/git-reset-file.png)

---

## Summary

挺复杂的 有了图就容易理解多了

归纳一下可能会用的比较多的场景：

1. 取消暂存的文件

   ```bash
   $ git reset HEAD <file_name>
   ```

2. 撤销对文件的修改

   ```bash
   $ git checkout -- <file_name>
   ```

---

