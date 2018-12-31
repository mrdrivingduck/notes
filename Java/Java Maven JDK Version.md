# Java - Maven JDK Version

Created by : Mr Dk.

2019 / 01 / 01 05:01

Nanjing, Jiangsu, China

---

### Issue

* 创建 _Maven_ 项目后，项目默认 _JDK_ 版本是 _1.5_，而我电脑上的是 _1.8_，导致代码编译出错
* 每次 _update project_ 后，项目 _JDK_ 版本退回 _1.5_，导致代码编译出错

### Solution

在 `pom.xml` 中指定 _JDK_ 版本

```xml
<build>  
    <plugins>  
        <plugin>  
            <groupId>org.apache.maven.plugins</groupId>  
            <artifactId>maven-compiler-plugin</artifactId>  
            <version>3.1</version>  
            <configuration>  
                <source>1.8</source>  
                <target>1.8</target>  
            </configuration>  
         </plugin>  
    </plugins>  
</build>  
```

---

