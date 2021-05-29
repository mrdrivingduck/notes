# Git - Single Commit

Created by : Mr Dk.

2021 / 05 / 29 10:54

Hangzhou, Zhejiang, China

---

## Origin

最近新学习到一条开发规范。从主分支拉出一条分支用于开发 feature 之后，在合入主分支之前，要把 feature 分支上的所有 commit 压缩为一个 commit，再合入。

为什么要这样干？查了查 *ZhiHu*，总结了一下：

1. 很多 commit 只是带有实验性质或暂存性质，并没有必要真正成为一次 commit
2. 将逻辑上相似的多个 commit 压缩到一次 commit 里，可以给它一个描述性很强的 commit message
3. 其它分支上的开发者并没有必要了解你的分支内的 `fix` / `fix again`
4. 好的 commit 应当能够简洁明了地反映一个项目是如何被开发出来的

提问中还给出了 [Vue.js 的 commit 历史](https://www.zhihu.com/question/61283395/answer/186725319) 作为范本。我认为值得学习。我觉得自己以前有着太多的无效 commit 了，特别是有几个反复的 fix。现在想来幸亏是自己一个人的项目，不然让别人看也是够无语的。

## Rebase

合并多次 commit 的直接做法就是 `git rebase` 命令：

```bash
git rebase -i <commit_id>
```

这里的 commit id 为要合并的几个 commit 的再前一个 commit。相当于要对链表中的三个节点进行合并，你必须找到这三个节点的前一个节点。不然如何将合并后的新节点链回去呢？

例子：

```console
$ git log
commit c44d371b4e8fe65ed515b1fe3986b7a5b7eb0a83 (HEAD -> master)
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:52 2021 +0800

    Commit 4

commit 488e75ec020761a176688ed071c2049f3ebf6073
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:40 2021 +0800

    Commit 3

commit ffe162164d4bdeaf1da285852f90860c3c0dc2a2
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:23 2021 +0800

    Commit 2

commit 298e31375c1acab77eccfea320c7646cd2dbddea
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:06 2021 +0800

    Commit 1

```

现在想把最新的三个 commit (2、3、4) 合并。那么首先需要这三个 commit 的之前一次 commit (Commit 1) 的 commit hash。

```bash
git rebase -i 298e31375c1acab77eccfea320c7646cd2dbddea
```

这时，会出来一个文件编辑界面：

```
pick ffe1621 Commit 2
pick 488e75e Commit 3
pick c44d371 Commit 4

# Rebase 298e313..c44d371 onto 298e313 (3 commands)
#
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
#
# These lines can be re-ordered; they are executed from top to bottom.
#
# If you remove a line here THAT COMMIT WILL BE LOST.
#
# However, if you remove everything, the rebase will be aborted.
#
# Note that empty commits are commented out
```

最开头列出了将要操作的 commit，以及操作命令。带 `#` 的是注释，里面详细解释了操作命令。对于合并，我们应该 **pick** 最老的一次 commit，然后将后面的两次 commit **squash** 到前面的 commit 中。因此，编辑这个文件，将后两个 `pick` 改为 `squash` 或 `s`，保存。

保存后，将会进入下一个文件编辑界面：

```
# This is a combination of 3 commits.
# This is the 1st commit message:

Commit 2

# This is the commit message #2:

Commit 3

# This is the commit message #3:

Commit 4

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Sat May 29 10:44:23 2021 +0800
#
# interactive rebase in progress; onto 298e313
# Last commands done (3 commands done):
#    s 488e75e Commit 3
#    s c44d371 Commit 4
# No commands remaining.
# You are currently rebasing branch 'master' on '298e313'.
#
# Changes to be committed:
#       modified:   a.txt
#
```

除去注释外，这里实际上包含了三次 commit 的 commit message。编辑这个文件，删掉原有的 commit message，为合并后的 commit 指定一条 commit message，保存。

完成后，rebase 操作就成功了：

```console
$ git rebase -i 298e31375c1acab77eccfea320c7646cd2dbddea
[detached HEAD 2a81aad] Merged commit!
 Date: Sat May 29 10:44:23 2021 +0800
 1 file changed, 2 insertions(+)
Successfully rebased and updated refs/heads/master.

$ git log
commit 2a81aadb7c1168e8c34af735b1686c617e7d5be3 (HEAD -> master)
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:23 2021 +0800

    Merged commit!

commit 298e31375c1acab77eccfea320c7646cd2dbddea
Author: mrdrivingduck <xxxxxxxxx@qq.com>
Date:   Sat May 29 10:44:06 2021 +0800

    Commit 1

```

## References

[工作中必备 git 技能详解](https://yonghaowu.github.io/2017/06/18/TheGitYouShouldKnow/)

