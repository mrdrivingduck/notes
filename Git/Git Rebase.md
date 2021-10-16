# Git - Rebase

Created by : Mr Dk.

2021 / 10 / 17 0:15

Nanjing, Jiangsu, China

---

## About

`git rebase` 命令有着两种不同的效果：

- 分支变基
- 重写分支历史

可以说是 Git 中最魔法的命令了。

## Rebase for a Branch

场景：一个子分支从主分支的某一次 commit 上分叉，子分支和主分支都分别有独立的 commit：

![git-rebase-basic](../img/git-rebase-basic.png)

`git merge` 的操作是将两个分支的最新一次 commit 和两个分支的公共祖先进行一次 **三方合并**，并生成一次新的 commit：

![git-rebase-merge](../img/git-rebase-merge.png)

`git rebase` 的做法：找到主分支和子分支的分叉 commit，将子分支基于这次 commit 的修改保存为临时文件。然后将分支的 base 指向主分支的最新一次 commit，并对这次 commit 应用之前保存的修改。结果如下：

![git-rebase-after](../img/git-rebase-after.png)

之后从主分支 merge 子分支就是一次 fast forward 的合并了。

变基是有风险的。由于被 rebase 分支的祖先 commit 变了，那么该分支内的每一次 commit 的 SHA 都会发生改变。在多人协作时，可不能瞎 rebase。

> 目前遇到的比较多的变基用途是，将自己的独立开发分支与被保护的主分支 rebase，以便对齐团队里所有人 merge 到主分支上的工作。

## Rewriting History

对于一个没有分叉的分支，也可以通过 `git rebase -i <SHA>` 命令 (`i` 表示 interactive，交互式) 来重写任意的 commit 历史。此时输入的参数不再是一个分支名了，而是想要从当前分支历史中开始改写历史的起始 commit 的前一次 commit (想象对链表中的某个节点开始操作则需要先找到它的前驱节点)。如果是希望从分支的第一次 commit 开始改写 (没有前驱节点)，则需要使用特殊的命令：

```bash
git rebase -i --root
```

在交互式的 rebase 中，Git 会将从参数指定 commit 开始的每一次 commit 信息载入，并让用户选择如何处理每一次 commit。默认的处理是 `pick`，即保留这次 commit。

```
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup <commit> = like "squash", but discard this commit's log message
# x, exec <command> = run command (the rest of the line) using shell
# b, break = stop here (continue rebase later with 'git rebase --continue')
# d, drop <commit> = remove commit
# l, label <label> = label current HEAD with a name
# t, reset <label> = reset HEAD to a label
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# .       create a merge commit using the original merge commit's
# .       message (or the oneline, if no original merge commit was
# .       specified). Use -c <commit> to reword the commit message.
```

以上为所有可选的命令：

- pick (p) 表示保留这次 commit
- reword (r) 表示保留这次 commit，但是编辑 commit 信息
- edit (e) 表示使用这次 commit，但重新修订它 (编辑 commit 信息 / 添加或移除 commit 的文件)，可被用于拆分提交
- squash (s) 表示使用这次 commit，但是把这次 commit 合并到前一次 commit 中
- fixup (f) 与 squash 类似，但是丢弃掉 commit log
- exec (x) 在这次 commit 上执行 shell 命令
- break (b) 表示停在这次 commit 上 (使用 `git rebase --continue` 继续)
- drop (d) 表示移除这次 commit
- label (l) 表示给当前 commit 打上标签
- reset (t) 表示将当前 commit 恢复标签
- merge (m) 表示创建一个 merge commit

通过在交互式命令行中编辑每次 commit 之前的命令，就可以对每一次 commit 实现相应的动作。包括但不限于：

- 合并几次 commit 为一次
- 拆分一次 commit 为多次
- 编辑某次 commit 的 commit message
- 在每次 commit 上修改 commit 邮箱地址
- ...

Rebase 可以干很多事情。

## References

[3.6 Git 分支 - 变基](https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%8F%98%E5%9F%BA)

[7.6 Git 工具 - 重写历史](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E9%87%8D%E5%86%99%E5%8E%86%E5%8F%B2)

