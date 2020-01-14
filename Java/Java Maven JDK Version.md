# Java - Maven JDK Version

Created by : Mr Dk.

2019 / 01 / 01 05:01

Nanjing, Jiangsu, China

---

## Issue

* 创建 _Maven_ 项目后，项目默认 JDK 版本是 1.5，而我电脑上的是 1.8，导致代码编译出错
* 每次 _update project_ 后，项目 JDK 版本退回 1.5，导致代码编译出错

---

## Solution

在 `pom.xml` 中指定 JDK 版本

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <source>8</source>
                <target>8</target>
            </configuration>
        </plugin>
    </plugins>
</build>
```

---

