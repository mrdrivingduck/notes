# Git - Cherry Pick

Created by : Mr Dk.

2021 / 05 / 21 17:36

Nanjing, Jiangsu, China

---

## About

这条命令用于把一个分支中的 **某几次** commit 挑选出来，接到另一个分支的 commit 链表上。如果要将分支中的所有 commit 转移到另一个分支上，那么等效于 `git merge`。

## Usage

### Commit Hash

基本用法很简单：

```bash
git cherry-pick <commit_hash>
```

如下图所示。如果想要把 `Feature` 分支上的 `f` commit 单独挑出来，应用到 `Master` 分支上，那么只需要获得 `Feature` 分支上 `f` 的 commit hash，然后输入上述命令即可。产生的效果如图所示：

```
a - b - c - d   Master
         \
          e - f - g Feature
```

```
a - b - c - d - f   Master
         \
          e - f - g Feature
```

转移后，commit 的 diff 不变，但是 commit hash 将会发生改变。

### Branch Name

当然，也可以直接使用 **分支名**。此时命令的含义是，转移这个分支的最新一次 commit 到当前分支：

```bash
git cherry-pick <branch_name>
```

### Multiple Commit

这条命令支持转移多个独立的提交：

```bash
git cherry-pick <hash_A> <hash_B>
```

如果想要转移几个连续的提交，那么可以这样 (其中 commit A 不包含)：

```bash
git cherry-pick <hash_A>..<hash_B>
```

如果想要连同 commit A 包含在一起：

```bash
git cherry-pick <hash_A>^..<hash_B>
```

## Conflict

如果从其它分支上转移过来的 commit 与本分支之前的 commit 产生了冲突导致合并无法继续进行怎么办？Cherry-pick 会停下来让用户选择怎么办

### Continue

用户手动解决冲突后，继续进行：

```bash
git add .
git cherry-pick --continue
```

### Abort

放弃合并，回滚到合并前的样子：

```bash
git cherry-pick --abort
```

### Quit

保留冲突，不继续合并，也不回滚：

```bash
git cherry-pick --quit
```

## Between Different Repositories

也可以在不同代码库之间的分支上进行转移。首先将另一个库作为远程仓库添加到本地仓库，然后将远程仓库的代码拉到本地。通过 `git log` 查看 commit hash 后，用类似的方法转移 commit。

## References

[阮一峰的网络日志 - git cherry-pick 教程](http://www.ruanyifeng.com/blog/2020/04/git-cherry-pick.html)

[Lydia Hallie - 🌳🚀 CS Visualized: Useful Git Commands](https://dev.to/lydiahallie/cs-visualized-useful-git-commands-37p1)

---

