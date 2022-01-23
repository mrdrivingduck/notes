# Vue.js - Environment Variable

Created by : Mr Dk.

2020 / 06 / 16 13:45

Nanjing, Jiangsu, China

---

## Why We Need Environment Variable?

在开发应用时，一些 APP key 或 token 不能硬编码在源代码中 push 到仓库里。相应的解决方式是将这些 key 保存到环境变量中，在程序构建/运行时，环境变量中的值才会替代代码中的引用。这样只需要在本地存储 key，不需要将 key push 到仓库内。

## Vue.js Environment Variable

在 [Vue CLI](https://cli.vuejs.org/) 创建的 Vue.js 工程的 **根目录** 下，可以有好几种环境变量文件。其中，带 `.local` 后缀的文件会被 `.gitignore` 忽略而不被传入仓库。另外，环境变量支持三种 **模式**：

- `development` - 开发环境模式，对应于 `serve` 命令
- `production` - 生产环境模式，对应于 `build` 命令
- `test` - 测试环境模式，对应于 `test` 命令

由此，在工程根目录下可以有以下几类环境变量文件：

```
.env                # 在所有的环境中被载入
.env.local          # 在所有的环境中被载入，但会被 git 忽略
.env.[mode]         # 只在指定的模式中被载入
.env.[mode].local   # 只在指定的模式中被载入，但会被 git 忽略
```

其中，带有 `mode` 的环境变量文件比一般的环境变量文件 (比如 `.env`) 有更高的优先级。

```
VUE_APP_SECRET=HHHHHHHH
```

**只有以 `VUE_APP_` 开头的环境变量才会被嵌入到客户端中！** 在代码中可以通过如下方式访问：

```javascript
console.log(process.env.VUE_APP_SECRET);
```

另外，还有两个特殊的环境变量：

- `NODE_ENV` - 应用运行的模式，也就是 `development` / `production` / `test` 中的一个
- `BASE_URL` - 与 `vue.config.js` 中的 `publicPath` 相符，也就是应用会部署到的基础路径

## Public Path

一个关于 `vue.config.js` 配置的小细节。如果打算将项目部署到 `https://<USERNAME>.github.io/`，那么 `publicPath` 需要被设置为默认的 `/`。如果部署到 `https://github.com/<USERNAME>/<REPO>`，那么 `publicPath` 就需要被设置为 `/<REPO>/`。因此，`vue.config.js` 中可以这样写：

```javascript
module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "/my-project/" : "/",
};
```

这里就使用了上面提到的 `NODE_ENV` 环境变量来判断应用运行的模式是否为生产环境。

另外，如果仓库还集成了 Travis CI，那么还可以将环境变量添加到 Travis CI 的 setting 中。这样在 Travis CI 自动构建时，会将程序中的引用值替换为环境变量中的值。

> 好吧我其实就是想在环境变量中放一个 GitHub Pernonal Access Token (PAT)，这样我的网页可以直接调用 GitHub API。但是无论是硬编码，还是环境变量，在构建完成后，token 的完整字符串都会出现在仓库中而被 GitHub 识别，GitHub 会自动删除这个 token。
>
> 如果想要避免这个问题，还得搞点小操作。

---

## References

[How to Use Environment Variables in Vue.js](https://medium.com/js-dojo/how-to-use-environment-variables-in-vue-js-273eba0102b0)

[Vue CLI - 环境变量和模式](https://cli.vuejs.org/zh/guide/mode-and-env.html#%E6%A8%A1%E5%BC%8F)

[Vue CLI - 部署](https://cli.vuejs.org/zh/guide/deployment.html#github-pages)
