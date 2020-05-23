# Git - 版本回退

Created by : Mr Dk.

2018 / 10 / 29 09:28

Nanjing, Jiangsu, China

---

## Local

使用命令 `reset` 加上 **版本号** 的方式，可以实现本地仓库的版本进退：

```bash
$ git reset --hard [commit_id]
```

如果需要回退邻近版本，也可以使用：

```bash
$ git reset --hard HEAD      # 当前版本
$ git reset --hard HEAD^     # 上一个版本
$ git reset --hard HEAD^^    # 上上个版本
                             # ...
```

* 版本回退之前，使用 `git log` 可以查看提交历史，得到 `commit_id`
* 版本前进之前，使用 `git reflog` 可以查看命令历史，得到未来版本的 `commit_id`

## Remote

本地分支回退后，版本将落后于远程分支，必须使用 **强制** (慎用) 覆盖远程分支：

```bash
$ git push -f [origin master]
```

---

