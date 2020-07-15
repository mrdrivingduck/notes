# Git - Branch & Merge Command

Created by : Mr Dk.

2019 / 04 / 22 11:02

Nanjing, Jiangsu, China

---

## About

学习通过 Git Bash 操作分支及其合并的命令及其含义

* 本地分支 / 远程分支
* 分支操作 / 合并操作 / 冲突处理

---

## Branch Commands

### git branch

列出所有的本地分支，并用 `*` 标记当前分支：

```console
$ git branch
```

### git branch -r

列出所有远程分支：

```console
$ git branch -r
```

### git branch -a

列出所有本地分支和远程分支：

```console
$ git branch -a
```

上述命令中的信息可能会过时，因此需要保持远程分支信息在本地的同步：

```console
$ git remote update origin --prune
```

### git branch -vv

查看本地分支及其对应的远程分支：

```console
$ git branch -vv
```

### git branch --set-upstream-to=<branch_name>

将本地分支关联到远程分支：

```console
$ git branch --set-upstream-to=origin/dev
```

### Effect

<img src="../img/git-branch-cmd.png" alt="git-branch-cmd" style="zoom:50%;" />

### git branch <branch_name>

创建 `dev` 分支，但依旧停留在当前分支上：

```console
$ git branch dev
```

### git checkout <branch_name>

切换到 `dev` 分支。此时运行 `git branch -vv`，远程分支中还没有分支和 `dev` 分支对应。如果两个分支上的文件状态不同时，Git 会将文件目录中的文件状态恢复为不同分支对应的状态。

```console
$ git checkout dev
```

### git push --set-upstream origin dev

将本地提交推送到远程提交中的 `dev` 分支，并将本地分支和远程分支关联。

### Effect

<img src="../img/git-branch-set-upstream.png" alt="git-branch-set-upstream" style="zoom:50%;" />

---

## Merge Commands

当需要将 `dev` 分支合并到 `master` 分支时，首先需要使用 `git checkout master` 切换到 `master` 分支。

### git merge <branch_name>

将 `dev` 分支合并到当前分支。

```console
$ git merge dev
```

### git branch -d <branch_name>

删除本地的 `dev` 分支。

```console
$ git branch -d dev
```

### git push origin --delete <branch_name>

删除本地的 `dev` 分支后，远程的 `dev` 分支依旧存在。可以在网页上手动删除，也可以在命令行中直接删除：

```console
$ git push origin --delete dev
```

### Effect

<img src="../img/git-merge-cmd.png" alt="git-merge-cmd" style="zoom:50%;" />

合并后，本地分支的提交次数应该比远程分支提前 (**ahead**)。此时，使用 `git push` 将本地分支的提交到远程分支：

<img src="../img/git-push-merged-branch.png" alt="git-push-merged-branch" style="zoom:50%;" />

此时，本地的 `dev` 分支已被删除，但远程的 `dev` 分支依旧存在。在命令行中将远程 `dev` 删除：

<img src="../img/git-rm-remote-branch.png" alt="git-rm-remote-branch" style="zoom:50%;" />

---

## Conflict

人为制造了两个文件状态冲突的分支，并试图进行分支合并：

### Effect

<img src="../img/git-merge-conflict.png" alt="git-merge-conflict" style="zoom:50%;" />

产生冲突的部分如下：

<img src="../img/git-conflict-code.png" alt="git-conflict-code" style="zoom:50%;" />

目前分支处于 `master|MERGING` 的状态，在解决冲突并 commit 之后，分支回到 `master` 状态，本地分支合并成功。此后将 merge 推送到远程分支：

<img src="../img/git-push-conflict.png" alt="git-push-conflict" style="zoom:50%;" />

删除合并后的无用本地和远程分支：

<img src="../img/git-push-rm-merged-branch.png" alt="git-push-rm-merged-branch" style="zoom:50%;" />

---

