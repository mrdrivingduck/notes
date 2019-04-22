# Git - Clone

Created by : Mr Dk.

2018 / 10 / 25 14:02

Nanjing, Jiangsu, China

---

## 1. About

__克隆一个现有的远程仓库到本地__

## 2. Format

```bash
$ git clone [url]
```

### 2.1 效果

* 在 __当前目录__ 下建立一个与远程仓库同名的目录
* 在该目录下初始化一个 `.git` 文件夹
* 将远程仓库的所有元数据放入 `.git` 文件夹
* 从远程仓库读取所有文件最新版本的拷贝

### 2.2 自定义本地仓库的名字

```bash
$ git clone [url] [local_repo_name]
```

### 2.3 指定克隆的分支

```bash
$ git clone -b [branch_name] [url]
```

---

