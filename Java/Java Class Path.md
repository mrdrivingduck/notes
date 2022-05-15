# Java - Class Path

Created by : Mr Dk.

2020 / 05 / 16 0:10

Nanjing, Jiangsu, China

---

## Class Path

什么是 class path？它是用来干什么用的？

`classpath` 是一个被 JVM 使用的环境变量，用于指示 JVM 在加载一个类时，到哪个路径下搜索对应的字节码文件，即 `.class` 文件。因此，[class path](<https://en.wikipedia.org/wiki/Classpath_(Java)>) 实际上是一个目录的集合 - 根据操作系统的不同，目录之间的分隔符也不同。如果 JVM 在其中一个路径下找到了字节码文件，就不再往后搜索；如果在所有路径下都没有找到文件，则报错。

Class path 可以通过系统环境变量的方式设置 (现已过时)，也可以在每次 JVM 启动时通过 `-classpath` 或 `-cp` 参数来设置。在早期的 Java 环境配置教程 (1.5 之前) 中，要求将 `dt.jar` 和 `tools.jar` 加入到系统环境变量的 class path 中：

- `dt.jar` 主要用于 Swing
- `tools.jar` 主要用于编译和运行一个类

这些核心类库在 1.5 版本之后已经能够自动被 JVM 搜索到了，因此不再需要配置系统环境变量中的 class path。IDE 通常会自动对 `-cp` 参数传入当前工程的编译目标目录，以及引入的 jar 包目录。

## Java ARchive

当 `.class` 文件过多时，在 class path 指定很多目录是个挺麻烦的事。[JAR](<https://en.wikipedia.org/wiki/JAR_(file_format)>) 文件能够将 package 下的所有文件打成一个 `.jar` 包 (相当于 ZIP 格式的压缩文件)，使得 JVM 能够直接在这个包中搜索类的字节码。

JAR 包中可以包含一个特殊的 `/META-INF/MANIFEST.MF` 文件，指定包中主类的信息。这类 JAR 包可以通过 `java -jar xxx.jar` 命令直接运行，而无需显式指定主类。

Maven 等工具能够方便地自动生成 JAR 包。

## References

[廖雪峰的官方网站 - Java 教程 - Class Path 和 JAR](https://www.liaoxuefeng.com/wiki/1252599548343744/1260466914339296)

[Java 开发环境不再需要配置 classpath！](https://juejin.im/post/5ce67fa1f265da1b6a346d16)

[Java Documentation - Setting the Class Path](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/classpath.html)

[Java Documentation - PATH and CLASSPATH](https://docs.oracle.com/javase/tutorial/essential/environment/paths.html)

---
