# Java - Eclipse 镜像

Created by : Mr Dk.

2018 / 10 / 26 23:46

Nanjing, Jiangsu, China

---

### 问题起源

* 每次去 _Eclipse_ 官网下载，速度慢得一批，不能忍 :rage:
* _Eclipse_ 内部的软件更新速度奇慢无比，且日常失败 :rage:

### 原因

_Eclipse_ 默认 _mirror_ 在国外

### 对策

* 使用国内的开源镜像网站
* 推荐使用 [__中国科学技术大学（USTC）__](http://mirrors.ustc.edu.cn/) 的开源镜像网站

### 操作

#### 下载 _Eclipse_

* 在国内开源镜像网站中找到 _Eclipse_，进入主目录
* 进入目录 `/technology/epp/downloads/release/`
* 选择想要下载的 `Release` 版本目录
* 选择想要下载的 _Eclipse_ 的类型 - `java` `javascript` `jee` `cpp` etc.
* 选择对应操作系统与系统架构的 _Eclipse_ 压缩文件

#### 更换 Eclipse 内部更新镜像

* 打开 _Eclipse_ 中的 `Window/Preferences`
* 选择 `Install/Update`
* 选择 `Available Software Sites`
* 更换网址 -  将所有`http://download.eclipse.org/` 替换为 `http://mirrors.ustc.edu.cn/eclipse/`
* 依次将每一个站点进行 _Reload_

### 效果

* 选择 `Help` 下拉框
* 访问
  * `Check for Updates`
  * `Install New Software`
  * `Eclipse Marketplace`
* 简直光速 :stuck_out_tongue_closed_eyes:

---

