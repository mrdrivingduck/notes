# Node.js - NPM

Created by : Mr Dk.

2019 / 02 / 21 13:28

Nanjing, Jiangsu, China

---

### About

> npm 为你和你的团队打开了连接整个 JavaScript 天才世界的一扇大门。它是世界上最大的软件注册表，每星期大约有 30 亿次的下载量，包含超过 600000 个 _包（package）_ （即，代码模块）。来自各大洲的开源软件开发者使用 npm 互相分享和借鉴。包的结构使您能够轻松跟踪依赖项和版本。

npm 包含三个独立的部分：

* 网站
  * 用于查找包、设置参数、管理 npm
* 注册表（registry）
  * 大型数据库，保存了每个包的信息
* 命令行工具（CLI）
  * 与开发者交互

---

### Manage NPM

查看 npm 当前版本：

```bash
$ npm -v
```

更新 npm：

```bash
$ npm install npm@latest -g
```

---

### Install Packages

* 本地安装
  * 自己的模块依赖于某个包，并通过 Node.js 的 `require` 加载时使用
  * `npm install <package_name>` 的默认行为
  * 执行后会在当前目录下创建 `node_modules` 目录，存在下载的包
* 全局安装
  * 将包作为命令行工具
  * `npm install -g <package_name>`

---

### Update Packages

* 本地包更新
  * 在 `package.json` 文件所在的目录执行 `npm update`
  * 执行 `npm outdated` 命令不应该有任何输出
* 全局包更新
  * `npm update -g <package_name>`
  * 查看哪些包需要被更新 - `npm outdated -g --depth=0`
  * 更新所有的全局包 - `npm update -g`

---

### Uninstall Packages

* 卸载本地包
  * `npm uninstall <package_name>`
  * 卸载，同时从 `package.json` 文件中删除依赖 - 在 `uninstall` 后添加 `--save`
* 卸载全局包
  * `npm uninstall -g <package_name>`

---

### package.json

The best way to manage locally installed npm packages is to create a `package.json` file.

一个 `package.json` 文件至少要有：

* `"name"`
* `"version"`

#### How to create?

* 创建一个个人的 `package.json`

  ```bash
  $ npm init
  ```

  * 会在命令行中产生一个问卷，用于填写对应的信息

* 创建一个默认的 `package.json`

  ```bash
  $ npm init --yes
  ```

  * 会使用从当前目录下提取的信息创建默认的文件

也可以进行修改：

```bash
$ npm set init.author.name "mrdrivingduck"
```

__NOTE:__

>If there is no description field in the `package.json`, npm uses the first line of the `README.md` or README instead. The description helps people find your package when searching npm, so it's definitely useful to make a custom description in the `package.json` to make your package easier to find.

#### Dependencies

To add an entry to your `package.json`'s `dependencies`:

```bash
$ npm install <package_name> --save
```

To add an entry to your `package.json`'s `devDependencies`:

```bash
$ npm install <package_name> --save-dev
```

> If you have a `package.json` file in your directory and you run `npm install`, npm will look at the dependencies that are listed in that file and download the latest versions, using semantic versioning.

---

### Source

#### Setting

```bash
$ npm config set registry https://registry.npm.taobao.org
```

#### Check

```bash
$ npm config get registry
$ npm info express
```

---

### Reference

NPM 官方网站- [https://www.npmjs.com/](https://www.npmjs.com/)

NPM 中文文档 - [https://www.npmjs.cn/](https://www.npmjs.cn/)

---

### Summary

学 Vue.js 之前的预备知识

---

