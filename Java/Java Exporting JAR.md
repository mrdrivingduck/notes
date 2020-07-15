# Java - Exporting JAR

Created by : Mr Dk.

2019 / 05 / 13 09:57

Nanjing, Jiangsu, China

---

## Library JAR

不可执行，可被其它程序依赖

可以直接用 Eclipse 导出 - 选择 JAR file

* 选择打包进 JAR 中的类
* 选择导出的 JAR 路径与名称
* 使用自动生成的配置文件 `manifest.mf`

直接可以获得 `xxx.jar`

---

## Runnable JAR

可以直接被执行的 JAR 文件：

```console
$ java -jar xxx.jar
```

可能依赖了其它 JAR

需要指定一个可被执行的主类

### 自定义 `manifest.mf`，并用 Eclipse 导出

在项目根目录创建一个 `manifest.mf`

```
Manifest-Version: 1.0 
Main-Class: iot.zjt.protector.FileProtector 
Class-Path: lib/encryption-machine-1.1.jar 
```

Attention

* 每行最多 `72` 个字符
* 多个 `.jar` 要用空格隔开
* 换行时，行首需要有一个空格，行尾也要有空格
* 行尾如果没有空格，则与下一行是连起来的
* 最后一行为空行

使用 Eclipse 的导出工具，选择 JAR file

* 选择打包进 JAR 中的类
* 选择导出的 JAR 路径与名称
* 选择自定义的配置文件 `manifest.mf`
* 选择执行的主类

导出完成后，`xxx.jar` 会在同目录下的 `lib/` 中寻找依赖的其余 JAR

* 总觉得不太爽 😤

### 直接用 Eclipse 导出

在 Eclipse 的 Export 中直接选择 Runnable JAR file

#### Launch Configuration

相当于选定了执行主类

#### Export Destination

导出路径与名称

#### Library Handling

* Extract required libraries into generated JAR
  * 将其余 JAR 解压为 `.class` 并打包进生成的 JAR 中
* Package required libraries into generated JAR
  * 不对其余的 JAR 进行解压，直接打包进生成的 JAR 中
* Copy required libraries into a sub-folder next to the generated JAR
  * 将依赖的 JAR 放在生成 JAR 的同级目录的某个子文件夹下（与上面类似）

其中，前两种选项最终可以只输出一个 `.jar`

后一种选项除了 `.jar` 以外，还有一个文件夹，里面是所有依赖的 JAR

---

## Summary

被导出 JAR 这个问题困扰好几次了

主要出现的还是找不到依赖的问题

今天把它整明白了 ☹️

希望下次遇到类似的问题能快速解决

---

