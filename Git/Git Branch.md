# Git - Branch

Created by : Mr Dk.

2019 / 03 / 30 14:21

Nanjing, Jiangsu, China

---

## About

Git 这个东西我觉得主要是想法很独特

每一次提交，会产生指向上一个提交对象的指针

每个 __提交对象__ 指向版本快照

版本快照记录本次提交的一些元数据，产生了哪些变化等等

![git-work-tree](../img/git-work-tree.png)

默认会有一个 `master` 分支指针指向 __提交对象__

会有一个 `HEAD` 指针指向当前操作的分支：

![git-head](../img/git-head.png)

---

## Branch

创建一个新的分支：

```bash
$ git branch <branch_name>
```

实际上创建了一个新的分支指针，指向当前提交对象：

![git-branch](../img/git-branch.png)

在分支之间切换：

```bash
$ git checkout <branch_name>
```

实际上是将 `HEAD` 指针指向了对应的分支指针：

![git-checkout](../img/git-checkout.png)

之后可以在对应分支上进行 `commit`，对应的分支指针就会向前移动：

![git-branch-commit](../img/git-branch-commit.png)

---

## Merge

Git 的官方网站给出了一个便于理解的实际应用场景：

项目的生产环境服务器上使用的是 `master` 分支的版本

突然，有人提出 `#53 issue` 中的功能需要被实现

因此，从 `master` 分支上派生出 `iss53` 分支用于开发

并将更新 commit 到 `iss53` 分支上：

![git-iss53](../img/git-iss53.png)

此时，突然有人报告，生产环境中的另一个地方出现 BUG 需要被立刻修复

但是 `iss53` 中的需求还没有被实现完

此时，只需要切换回 `master` 分支，Git 将状态恢复到 `C2`

从 `C2` 状态派生出一个新的紧急修补分支 `hotfix`，并进行 BUG 修复：

![git-branch-hotfix](../img/git-branch-hotfix.png)

此时，`hotfix` 分支上的 commit 已经修复了 BUG

因此，需要将生产服务器上的版本更新为修复 BUG 后

即需要合并 `master` 和 `hotfix` 分支

由于从 `master` 分支的 `C2` 状态可以无需回退而直接到达 `C4` 状态

因此这种合并方式称为 __Fast Forward__，即只需要将 `master` 分支指针右移：

![git-fast-forward](../img/git-fast-forward.png)

`hotfix` 分支指针已经完成了使命，可以被删除了

目前生产环境服务器使用的是 `C4` 状态的版本

然后就可以重新转到 `iss53` 分支上，继续新功能的开发~

......

当新功能开发完成后，`iss53` 需要和 `master` 合并时

问题出现了 - 并不能使用 fast-forward 的合并方式

Git 会找到它们的共同祖先，进行三方合并计算：

![git-before-merge](../img/git-before-merge.png)

Git 会将合并后的结果生成为一个新的状态

此时 `iss53` 的使命也完成了，可以被删除：

```bash
$ git branch -d <branch_name>
```

![git-after-merge](../img/git-after-merge.png)

---

## Conflict

合并操作并不一定像上述过程一样顺利

如果两个分支都修改了同一个文件

那么 Git 对 `C6` 状态的生成一定会是矛盾的：

* 到底该使用 `C4` 版本的状态还是 `C5` 版本的状态呢？

因此这时需要人为裁决：

* 二选一
* 亲自整合冲突

命令一大堆，不想记了

尽可能不要修改同一个文件才是正解叭

---

## Reference

<https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%AE%80%E4%BB%8B>

<https://git-scm.com/book/zh/v1/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%9A%84%E6%96%B0%E5%BB%BA%E4%B8%8E%E5%90%88%E5%B9%B6>

---

## Summary

以前一直是一个人在 `master` 分支上玩耍

现在需要和别人协作了

还是学一下 branch 的原理和机制吧

---

