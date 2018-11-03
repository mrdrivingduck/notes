# Java - Maven 项目构建工具

Created by : Mr Dk.

2018 / 11 / 03 15:01

Nanjing, Jiangsu, China

---

### About

_Apache Maven&trade;_ 是一个项目管理和综合工具。提供一个 __项目对象模型文件（POM）__ 的概念来管理项目的构建、相关性和文档。还能够自动下载项目依赖库。

### Installation & Configuration

_Eclipse_ 的最新发布版中已经内嵌了 _Maven_，不需要另外安装

_Maven_ 默认从 __中央存储库__ 自动下载依赖资源 `http://repo1.maven.org/maven2/`

由于国内的网络环境问题，可以修改 _Maven_ 的配置文件，添加国内镜像，从而加快下载速度

官方文档教程：[Apache Maven - Guide to Mirror Settings](http://maven.apache.org/guides/mini/guide-mirror-settings.html )

首先找到 _Maven_ 的 _setting file_ - `${user.home}/.m2/settings.xml` （如果没有需要手动创建）

在配置文件中加入内容，添加国内的阿里云镜像：

```xml
<settings>
    
    <mirrors>
        <mirror>  
	        <id>nexus-aliyun</id>  
	        <name>Nexus aliyun</name>  
	        <url>http://maven.aliyun.com/nexus/content/groups/public</url>    
	        <mirrorOf>central</mirrorOf>  
        </mirror> 
    </mirrors>
    
</settings>
```

### Project

在 _Eclipse_ 中新建一个 _Maven project_，里面有很多个工程模板，根据需求选择（一般选择 `quickstart` 即可）

* 填写 `groupId`、`artifactId`、`version`

* _Maven_ 通过这三个元素唯一确定一个 _project_

* 同时，`groupId` 和 `artifactId` 也会组合为源代码路径 `/src` 下的默认包名

* 根据需要设置 `JRE System Library`

* 如果需要引入依赖

  * 定位到工程根目录的 `pom.xml` 文件中的 `<dependencies>` 定义内
  * 加入依赖的定义组 `<dependency>`，其中包括依赖项目的 `groupId`、`artifactId`、`version`，以及 `scope` （部署阶段，若不加则默认所有阶段）
  * 配置保存后会将依赖的 `.jar` 文件下载到 _Maven_ 默认的本地存储库下 - `${user.home}/.m2/repository/`

  ```xml
  <project>
      <dependencies>
    
          <dependency>
              <groupId>junit</groupId>
              <artifactId>junit</artifactId>
              <version>3.8.1</version>
              <scope>test</scope>
          </dependency>
      
          <dependency>
              <groupId>io.vertx</groupId>
              <artifactId>vertx-core</artifactId>
              <version>3.5.4</version>
          </dependency>
      
      </dependencies>
  </project>
  ```

* `.jar` 文件下载完毕后，会出现在 `Build Path` 的 `Maven Dependencies` 中

* 在 `src/` 目录下进行编码即可，依赖的类可以随时被 `import`

* 与当前工程有关的信息全部都在 `pom.xml` 中，包括各子路径的作用等

* 右键工程，点击 `Maven/Update Project` 可重新构建工程并下载依赖

---

### Summary

其实以前经常碰到 _Maven_

但是没有花心思研究

今天学习 _Vert.x_ 框架的时候

写了一些 _demo_，准备上传到 _GitHub_ 上

突然发现工程目录下 `lib/` 里的文件有 80 MB

包括 _Vert.x_ 的各种 `.jar` 文件以及其依赖文件

传上去既影响速度也没有必要

所以研究了一波 _Maven_

把整个工程构建成 _Maven project_

就不需要上传依赖的库了

---

