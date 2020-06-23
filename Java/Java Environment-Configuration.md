# Java - 运行环境配置

Created by : Mr Dk.

2018 / 10 / 19 10:14

Nanjing, Jiangsu, China

---

## Concept

*JDK (Java Development kit | Java SE | J2SE)*：Java 编译、调试工具

*JRE (Java Runtime Environment)*： Java 运行环境

---

## Steps

### 1. Download JDK

* 在 *Oracle* 官网上 [下载 JDK](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
* 选择适合的操作系统 - Windows / Linux / Mac OS
* 选择适合的 PC 架构 - x86 / x64

### 2. Install JDK & JRE

Windows 下，运行安装程序安装 JDK，中途会自动跳出 JRE 安装界面。

Linux 下，直接将下载的免安装压缩包解压即可。

Mac OS 下，下载 `.dmg` 格式的安装包。

### 3. Environment Variables Configuration

Windows 下：

* 打开 `编辑系统环境变量`
* 新建一个系统变量
  * 变量名为 `JAVA_HOME`
  * 变量值为 JDK 安装根目录，如 `C:\Program Files\Java\jdk1.8.0_172`
* 编辑系统环境变量 `Path`
  * 加入 `%JAVA_HOME%\bin` 和 `%JAVA_HOME%\jre\bin`
* 确定，保存
* 进入 Windows cmd 进行测试：
  * 输入 `java -version` - 查看 JDK 是否配置成功

Linux 下：

* 编辑环境变量文件
  ```bash
  $ vim /etc/profile
  ```
* 在文件中加入如下代码
  ```bash
  export JAVA_HOME=/usr/local/jdk1.8.0_172  # 压缩包解压路径
  export PATH=.:$JAVA_HOME/bin:$PATH
  ```
* 刷新环境变量配置 (重启 bash 即可)

Mac OS 下似乎不需要配置环境变量？？？

---

