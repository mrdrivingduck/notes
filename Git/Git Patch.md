# Git - Patch

Created by : Mr Dk.

2022 / 01 / 12 22:29

Nanjing, Jiangsu, China

---

试水 Git 的补丁导出和补丁应用功能：

- 从代码库中导出文本形式的补丁文件以便分发
- 将文本形式的补丁应用到另一个代码库中，并解决潜在的冲突

该功能可以解决跨代码库的代码变更移植问题，甚至可以解决跨代码库重命名源文件的移植问题。

## Background

某个项目 A 的目录结构如图所示：

```console
$ tree A
A
└── src
    └── backend
        └── foo.c

2 directories, 1 file
```

在另一个项目 B 中，也使用了项目 A `src/backend/` 中的 `foo.c` 源代码，但是放到了另一个目录 `src/another/` 下：

```console
$ tree B
B
└── src
    └── another
        └── foo.c

2 directories, 1 file
```

随着项目 A 中 `foo.c` 文件的不断演变，想要使项目 B 的 `foo.c` 也能够及时追踪这些变动。由于这两个文件属于不同的代码库，且文件所在的目录也发生了变化，因此不能直接使用 `cherry-pick` 解决这个问题。

拟解决的方法是：

1. 从项目 A 的 commit 记录中导出文本形式的补丁，补丁中包含了 commit 信息
2. 编辑文本形式的补丁，将 diff 里项目 A 的文件路径改为项目 B 的文件路径
3. 将补丁应用到项目 B 当中

## Format Patch

Git 的 `format-patch` 命令可以将一次 commit 的 diff 导出为文本格式。在导出的文件中，包含了：

- 补丁作者信息
- 补丁 commit 时间
- 补丁 commit message
- 补丁具体的 diff
- Git 版本号

```console
$ git format-patch -1 82058795ae3b65276004bdbaf965dc6568af1408
0001-Project-A-add-sth.patch

$ cat 0001-Project-A-add-sth.patch
From 82058795ae3b65276004bdbaf965dc6568af1408 Mon Sep 17 00:00:00 2001
From: mrdrivingduck <562655624@qq.com>
Date: Wed, 12 Jan 2022 21:47:13 +0800
Subject: [PATCH] Project A add sth.

---
 src/backend/foo.c | 3 +++
 1 file changed, 3 insertions(+)

diff --git a/src/backend/foo.c b/src/backend/foo.c
index 263cf7e..480f9e7 100644
--- a/src/backend/foo.c
+++ b/src/backend/foo.c
@@ -2,6 +2,9 @@

 int main()
 {
+    // Project A add sth. start
+    //
+    // Project A add sth. end
     return 0;
 }

--
2.25.1
```

也可以直接导出某次 commit 之后所有 commit 的补丁，会自动按照从 `0001` 开始的编号来排列。

```console
$ git log

commit 0917a83586ec8eb89a62dab616ee634fc2f9ad79 (HEAD -> master)
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:48:01 2022 +0800

    Project A add sth. again

commit 82058795ae3b65276004bdbaf965dc6568af1408
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:47:13 2022 +0800

    Project A add sth.

commit 28188a533e874eae1160e71be339922b0a9655aa
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:46:45 2022 +0800

    Initial commit

$ git format-patch 28188a533e874eae1160e71be339922b0a9655aa
0001-Project-A-add-sth.patch
0002-Project-A-add-sth.-again.patch
```

## Am

从项目 A 中导出的两个补丁分别对 `foo.c` 进行了如下更改：

```diff
diff --git a/src/backend/foo.c b/src/backend/foo.c
index 263cf7e..480f9e7 100644
--- a/src/backend/foo.c
+++ b/src/backend/foo.c
@@ -2,6 +2,9 @@

 int main()
 {
+    // Project A add sth. start
+    //
+    // Project A add sth. end
     return 0;
 }
```

```diff
diff --git a/src/backend/foo.c b/src/backend/foo.c
index 480f9e7..68071af 100644
--- a/src/backend/foo.c
+++ b/src/backend/foo.c
@@ -5,6 +5,8 @@ int main()
     // Project A add sth. start
     //
     // Project A add sth. end
+
+    // Project A add sth. again
     return 0;
 }
```

使用 Git 的 `am` 命令可以将补丁应用到代码库中。但是项目 B 的文件路径为 `src/another/foo.c`，不同于项目 A 及其 patch 中的 `src/backend/foo.c`。这怎么办呢？

那就直接编辑 `.patch` 文件中的 diff，将 `src/backend/foo.c` 改为 `src/another/foo.c`，然后应用补丁：

```console
$ git am ../A/0001-Project-A-add-sth.patch
Applying: Project A add sth.

$ git am ../A/0002-Project-A-add-sth.-again.patch
Applying: Project A add sth. again
```

此时，项目 B 的 commit 记录与项目 A 如出一辙：

```console
$ git log

commit caa028bb5e0341cf551d95908d3380eb7230fb57 (HEAD -> master)
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:48:01 2022 +0800

    Project A add sth. again

commit 3abadbc2da7dccd54c9f0910a87c714938626ee2
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:47:13 2022 +0800

    Project A add sth.

commit b3a2dec42fd0e569cf5dbedaea67bcf86624615c
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 22:02:50 2022 +0800

    Initial commit for B
```

## Conflict

应用补丁时遇到冲突了怎么办？假设项目 B 的 `foo.c` 文件在应用补丁之前已经进行了如下修改：

```console
$ git show b945780884fc69e526789ce29a1c078a6573d9d0

commit b945780884fc69e526789ce29a1c078a6573d9d0 (HEAD -> master)
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 22:06:15 2022 +0800

    Project B add sth.

diff --git a/src/another/foo.c b/src/another/foo.c
index 263cf7e..01d45db 100644
--- a/src/another/foo.c
+++ b/src/another/foo.c
@@ -2,6 +2,7 @@

 int main()
 {
+    // Project B add sth.
     return 0;
 }
```

显然，这与项目 A 导出的两个补丁将会冲突。`git am` 命令提供了类似 `git merge` 的冲突处理方式来解决冲突。其中，`-3` 的含义为使用 **三方合并** 算法：

```
-3, --3way, --no-3way
    When the patch does not apply cleanly, fall back on 3-way merge if the patch records the
    identity of blobs it is supposed to apply to and we have those blobs available locally.
    --no-3way can be used to override am.threeWay configuration variable. For more information, see
    am.threeWay in git-config(1).
```

```console
$ git am -3 ../A/0001-Project-A-add-sth.patch
Applying: Project A add sth.
Using index info to reconstruct a base tree...
M       src/another/foo.c
Falling back to patching base and 3-way merge...
Auto-merging src/another/foo.c
CONFLICT (content): Merge conflict in src/another/foo.c
error: Failed to merge in the changes.
Patch failed at 0001 Project A add sth.
hint: Use 'git am --show-current-patch' to see the failed patch
When you have resolved this problem, run "git am --continue".
If you prefer to skip this patch, run "git am --skip" instead.
To restore the original branch and stop patching, run "git am --abort".
```

此时，在 `foo.c` 中，已经出现了待解决的冲突标志：

```c
#include <stdio.h>

int main()
{
<<<<<<< HEAD
    // Project B add sth.
=======
    // Project A add sth. start
    //
    // Project A add sth. end
>>>>>>> Project A add sth.
    return 0;
}
```

解决冲突后，保存文件：

```console
$ git status
On branch master
You are in the middle of an am session.
  (fix conflicts and then run "git am --continue")
  (use "git am --skip" to skip this patch)
  (use "git am --abort" to restore the original branch)

Unmerged paths:
  (use "git restore --staged <file>..." to unstage)
  (use "git add <file>..." to mark resolution)
        both modified:   src/another/foo.c

no changes added to commit (use "git add" and/or "git commit -a")

$ git add src/another/foo.c

$ git status
On branch master
You are in the middle of an am session.
  (fix conflicts and then run "git am --continue")
  (use "git am --skip" to skip this patch)
  (use "git am --abort" to restore the original branch)

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   src/another/foo.c

$ git am --continue
Applying: Project A add sth.
```

这样就成功在项目 B 中应用了项目 A 导出的补丁：

```console
$ git log

commit 6dc46e2199bc53eb28a7b6ccb79fb383a5e9ad3c (HEAD -> master)
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 21:47:13 2022 +0800

    Project A add sth.

commit b945780884fc69e526789ce29a1c078a6573d9d0
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 22:06:15 2022 +0800

    Project B add sth.

commit b3a2dec42fd0e569cf5dbedaea67bcf86624615c
Author: mrdrivingduck <562655624@qq.com>
Date:   Wed Jan 12 22:02:50 2022 +0800

    Initial commit for B
```

## AM Three-Way Issue

在 `git am -3` 的时候出现以下错误：

```
fatal: sha1 information is lacking or useless (xxx/xxx).
```

在 [这个回答](https://stackoverflow.com/questions/16572024/get-error-message-fatal-sha1-information-is-lacking-or-useless-when-apply-a) 中，答者指出在带有与 patch 不相关历史的 Git 仓库内进行 `git am -3` 会出现这个问题，因为与 patch 中改动相关的文件 hash 不在当前代码库中。解决方式是把 patch 的来源代码库作为 remote 来源添加到当前代码库中，并且 `git fetch`。

## References

[Git Documentations - format-patch](https://git-scm.com/docs/git-format-patch)

[Git Documentations - am](https://git-scm.com/docs/git-am)

[Stackoverflow - What is the difference between git am and git apply?](https://stackoverflow.com/questions/12240154/what-is-the-difference-between-git-am-and-git-apply)

[Stackoverflow - How can I generate a Git patch for a specific commit?](https://stackoverflow.com/questions/6658313/how-can-i-generate-a-git-patch-for-a-specific-commit)
