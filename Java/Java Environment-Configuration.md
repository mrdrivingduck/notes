# Java - 运行环境配置

Created by : Mr Dk.

2018 / 10 / 19 10:14

Nanjing, Jiangsu, China

---

## Concept

* _JDK (Java Development kit | Java SE | J2SE)_ - _Java_ 编译、调试工具 
* _JRE (Java Runtime Environment)_ - _Java_ 运行环境

---

## Steps

### 1. Download JDK

* 在 _Oracle_ 官网上[下载 _JDK_](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
* 选择对应操作系统的 _JDK_ - _Windows | Linux | Mac OS_
* 选择适用 _PC_ 架构的 _JDK_ - _x86 | x64_

### 2. Install JDK & JRE

* _Windows_
  * 运行安装程序 安装 _JDK_
  * 中途会自动跳出 _JRE_ 安装界面
* _Linux_
  * 直接将下载的免安装压缩包解压即可
* _Mac OS_
  * 下载 `.dmg` 格式的安装包

### 3. Environment variables configuration

* _Windows_

  * 打开 `编辑系统环境变量`
  * 新建一个系统变量
    * 变量名为 `JAVA_HOME`
    * 变量值为 _JDK_ 安装根目录，如 `C:\Program Files\Java\jdk1.8.0_172`
  * 编辑系统环境变量 `Path`
    * 加入 `%JAVA_HOME%\bin` 和 `%JAVA_HOME%\jre\bin`
  * 编辑系统环境变量 `CLASSPATH`
    * 加入 `.;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar`
  * 确定 保存
  * 进入 _Windows cmd_
    * 输入 `java -version` - 查看 _JDK_ 是否配置成功
    * 输入 `javac -version` - 查看 _JRE_ 是否配置成功

* _Linux_

  * 编辑环境变量文件

    * ```bash
      $ vim /etc/profile
      ```

  * 在文件中加入如下代码

    * ```bash
      export JAVA_HOME=/usr/local/jdk1.8.0_172  # 压缩包解压路径
      export PATH=.:$JAVA_HOME/bin:$PATH
      export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
      ```

  * 刷新环境变量配置（最好 `reboot` 重启电脑）

    * ```bash
      $ source /etc/profile
      ```

* _Mac OS_

  * 似乎不需要配置环境变量？？？

---

## Testing

### 1. 用文本编辑工具创建一个 `.java` 文件

* _Windows_
  * 记事本 / 写字板
  * 保存为 `Test.java` 文件（注意后缀名）
* _Linux_
  * _vi / vim / gedit_ `Test.java`
* _Mac OS_
  * 没用过不知道 😅 ...

```java
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello world!");
    }
}
```

### 2. 进入命令行进行测试

* _Windows_
  * `win` + `R` 弹出运行框
  * 输入 `cmd` 进入命令行
* _Linux_
  * `Ctrl` + `Alt` + `T` 进入 _Terminal_
* _Mac OS_
  * 进入 _Terminal_

```bash
# 进入保存 .java 文件的目录
$ javac Test.java  # 编译 .java 文件生成 .class 文件
$ java Test        # 从主类 Test 进入程序
```

* 若运行结果为 `Hello world!`，则配置成功！

---

