# Git - Stash

Created by : Mr Dk.

2021 / 12 / 05 21:38

Nanjing, Jiangsu, China

---

这是一篇拖了很久的更新。Stash 是一个很实用但经常被我忽视的知识点，但之前不知道有这么一个功能，实际上该功能也可以用其它命令组合实现。但是存在即合理，stash 命令既然存在就有它的意义。

Git 中对文件的修改记录包含三个层面。由于并不熟悉 Git 的内部实现，所以就从用户的视角来总结：

- 工作目录：真实文件系统中的文件版本
- 暂存区：已被 Git 纳入追踪，但尚未成为一个正式版本
- 版本库：通过 commit 进入 Git 的版本控制记录中，成为一个正式版本

在特性开发时，绝大部分时间都会在前两步中。而当我们想在版本库的正式版本之间切换时（同一个分支的前进或回退，不同分支版本的切换），Git 不允许工作目录或暂存区中有已被追踪的中间状态文件（已修改，未提交），否则将会在版本切换时引入冲突。所以看起来只有两种做法：

- 将对已追踪文件的修改丢弃（老子辛辛苦苦改半天呢，怎么能丢掉呢？）
- 将已追踪的文件修改做一次 commit，成为一个正式版本（目前已暂存的文件修改并不构成一个版本）

> 未被 Git 追踪的文件（比如新增文件）不会被 stash 命令影响，因为版本进退不会使该文件发生冲突。

这里就体现了 stash 命令的作用：将当前工作目录中的本地修改记录下来，并将工作目录恢复到 HEAD 指针指向版本的干净状态。

```console
$ git status
On branch master
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   a.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        b.txt

no changes added to commit (use "git add" and/or "git commit -a")

```

使用 `git stash save "xxx"` 对这次 stash 添加注释并保存；如果没有 `save "xxx"`，则将会自动生成注释：

```console
$ git stash
Saved working directory and index state WIP on master: fe2f029 Initial commit

$ git status
On branch master
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        b.txt

nothing added to commit but untracked files present (use "git add" to track)

```

可以看到，由于 `b.txt` 还没有被 Git 追踪，所以 stash 对其不起作用。将其纳入 Git 的管理之下即可起作用：

```console
$ git add .

$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   b.txt

$ git stash save "save b"
Saved working directory and index state On master: save b

$ git status
On branch master
nothing to commit, working tree clean
```

现在工作目录已经是干净的了，HEAD 指针可以随意移动以切换版本。通过以下命令可以查看 stash 记录：

```console
$ git stash list
stash@{0}: On master: save b
stash@{1}: WIP on master: fe2f029 Initial commit

$ git stash show stash@{1}
 a.txt | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

$ git stash show stash@{0}
 b.txt | 1 +
 1 file changed, 1 insertion(+)
```

切换版本后把 stash 中的记录恢复到工作目录时，Git 会以栈序（后保存先恢复）依次恢复文件状态。`stash pop` 将会依次恢复文件状态，并从 stash 记录中移除条目；`stash apply` 将会依次恢复文件状态，但不从 stash 记录中移除条目。

```console
$ git stash pop
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   b.txt

Dropped refs/stash@{0} (555468a845a50c6030cf12cb64e4897ca61d21bb)

$ git stash pop
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   b.txt

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   a.txt

Dropped refs/stash@{0} (5ba8b1cf02959f7b9929fced318186faab2615fc)
```

另外，丢弃某次或全部 stash 记录：

```console
$ git stash drop stash@{0}
Dropped stash@{0} (8df2f8dc92fafff3559341c9b6127c1e7462164d)

$ git stash clear
```

## References

[博客园 - git stash 用法总结和注意点](https://www.cnblogs.com/zndxall/archive/2018/09/04/9586088.html)

[Git Docs: git-stash](https://git-scm.com/docs/git-stash)
