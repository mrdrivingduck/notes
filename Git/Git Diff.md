# Git - Commit

Created by : Mr Dk.

2020 / 03 / 26 16:12

Ningbo, Zhejiang, China

---

*Diff* 是一个 Unix 上的很古老的工具，用于比较两个文本文件的差异。在其一路演变的过程中，共产生了三种输出格式：

1. Normal diff
2. Context diff
3. Unified diff

同样，Git 中也有类似的 diff 功能，用于比较两个版本之间的文件差异。虽然很少敲这个命令，但是在 IDE 的 Git 插件中已经通过 `modified` 的形式显示出来了。

## Normal Diff

这是最早期版本的 Unix 中的 diff 的输出格式：

```console
$ diff f1 f2
30,31c30
<             System.out.println(hunk.getToFileRange().getLineStart());
<             System.out.println(hunk.getToFileRange().getLineCount());
---
>             return;
```

输出分为两部分。第一部分是两对数字和中间的字母。中间的字母表示动作，包括：

* `c` - change - 内容改变
* `a` - addition - 内容增加
* `d` - deletion - 内容删除

```console
$ diff f1 f2
31a32
>             return;
```

```console
$ diff f1 f2
30,31d29
<             System.out.println(hunk.getToFileRange().getLineStart());
<             System.out.println(hunk.getToFileRange().getLineCount());
```

两对数字中，左边的部分是修改前版本中的行号，右边的部分是修改后版本中的行号。

第二部分是修改的详细内容。如果是同时有增加有删除的，那么就用 `---` 隔开，`<` 代表删除的行，`>` 代表增加的行。修改后的行号即由第一部分的两组数字所示。

一个文件如果有多处发生了修改，就会有多份这样的两部分的 diff。

## Context Diff

在 *UC Berkeley* 开发的 BSD 推出时，提出 diff 的显示过于简单，最好能显示修改位置的前后信息，即上下文，以便于理解发生的修改。

```console
$ diff -c f1 f2
*** f1  2020-03-26 15:44:46.142999800 +0800
--- f2  2020-03-26 15:44:51.056000000 +0800
***************
*** 27,34 ****
              System.out.println("Hunk***************");
              System.out.println(hunk.getFromFileRange().getLineStart());
              System.out.println(hunk.getFromFileRange().getLineCount());
              System.out.println(hunk.getToFileRange().getLineCount());
-             return;

              System.out.println(hunk.getLines().size());
          }
--- 27,34 ----
              System.out.println("Hunk***************");
              System.out.println(hunk.getFromFileRange().getLineStart());
              System.out.println(hunk.getFromFileRange().getLineCount());
+             System.out.println(hunk.getToFileRange().getLineStart());
              System.out.println(hunk.getToFileRange().getLineCount());
  
              System.out.println(hunk.getLines().size());
          }
```

第一部分表示发生变动的文件，及其修改时间。`***` 表示修改前的文件，`---` 表示修改后的文件。

第二部分和第三部分分别为 **修改前文件版本中的变动** 和 **修改后文件版本的变动**，每个部分内，包含了变动部分的行号，和变动的具体内容。每处变动开始于变动位置的前三行，结束于变动位置的后三行 (如例子所示，显示了第 27 行到第 34 行的信息，变动发生于第 31 行)。

## Unified Diff

如果文件修改前后变动的部分不多，上述方式将会带来大量的重复显示。GNU diff 率先推出了合并格式的 diff，将 f1 和 f2 的上下文合并在一起显示，从而避免了冗余的显示信息：

```console
$ diff -u f1 f2
--- f1  2020-03-26 15:44:46.142999800 +0800
+++ f2  2020-03-26 15:44:51.056000000 +0800
@@ -27,8 +27,8 @@
             System.out.println("Hunk***************");
             System.out.println(hunk.getFromFileRange().getLineStart());
             System.out.println(hunk.getFromFileRange().getLineCount());
+            System.out.println(hunk.getToFileRange().getLineStart());
             System.out.println(hunk.getToFileRange().getLineCount());
-            return;

             System.out.println(hunk.getLines().size());
         }
```

第一部分是变动前的文件和变动后的文件，及其修改时间。`---` 表示修改前文件，`+++` 表示修改后文件。

第二部分由 `@@ @@` 包裹起来的部分是变动的位置。`-` 开头的是修改前的文件，`+` 开头的是修改后的文件。数字的含义是，从第 27 行开始的 8 行。可以看到上下文显示的信息是最上面一处修改位置的前三行，和最后一处修改位置的后三行。

如果相邻两处修改的距离超过了六行 (即前一个修改位置的后三行，后一个修改位置的前三行)，那么改动将会被拆分为两个部分。试想，如果两处修改之间距离成百上千行，那么中间不变的部分就可以不显示了：

```console
$ diff -u f1 f2
--- f1  2020-03-26 15:44:46.142999800 +0800
+++ f2  2020-03-26 15:56:50.124400600 +0800
@@ -22,7 +22,7 @@
         System.out.println(diffFile.getFromFileName());
         System.out.println(diffFile.getToFileName());

-        List<Hunk> hunks = diffFile.getHunks();
+        List<Hunk> hunks = diffFile.getHunks()
         for (Hunk hunk : hunks) {
             System.out.println("Hunk***************");
             System.out.println(hunk.getFromFileRange().getLineStart());
@@ -31,6 +31,7 @@
             return;

             System.out.println(hunk.getLines().size());
+            return;
         }

     }
```

## Git Diff

Git 使用的是 unified diff 的一种变体。比较对象不再是两个文件，而是同一个文件的两个版本：

```console
$ git diff
diff --git a/src/main/java/edu/nuaa/zjt/avatar/App.java b/src/main/java/edu/nuaa/zjt/avatar/App.java
index f7b1066..0419171 100644
--- a/src/main/java/edu/nuaa/zjt/avatar/App.java
+++ b/src/main/java/edu/nuaa/zjt/avatar/App.java
@@ -20,7 +20,7 @@ public final class App {

         Diff diffFile = diffs.get(0);
         System.out.println(diffFile.getFromFileName());
-        System.out.println(diffFile.getToFileName());
+        System.out.println(diffFile.getToFileName())

         List<Hunk> hunks = diffFile.getHunks();
         for (Hunk hunk : hunks) {
@@ -29,6 +29,7 @@ public final class App {
             System.out.println(hunk.getFromFileRange().getLineCount());
             System.out.println(hunk.getToFileRange().getLineStart());
             System.out.println(hunk.getToFileRange().getLineCount());
+            return;

             System.out.println(hunk.getLines().size());
         }
```

其中，第一部分依旧是修改前版本和修改后版本的文件名，`a/` 代表修改前版本，`b/` 代表修改后版本。

第二部分是两个文件版本的 Git hash 值，`100644` 表示对象的模式 (普通文件，权限 `644`)。

之后的部分就与 unified diff 的输出含义一致了。`---` 和 `+++` 分别代表修改前后的文件，之后是发生变动的位置，与发生变动的详情。

---

