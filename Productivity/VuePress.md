# VuePress

Created by : Mr Dk.

2021 / 12 / 11 15:30

Nanjing, Jiangsu, China

---

几个月来一直以暂未离职的实习生身份帮忙负责某司某产品的开源工作。最近一周的任务是，基于全开源的镜像一步一步配置好该产品的开发环境，以便社区中的用户上手开发调试。踩了一周的坑，终于把环境配置的完整步骤摸出来了，于是准备把详细步骤更新到 README 文档。默默看了一眼 README，负责各部分的人东一笔西一画，整个 README 文件变得极长。其中包含了该产品在各种环境下的详细部署步骤、架构解读说明等。我觉得这不是一个 README 该有的样子，会让人没有兴趣看下去。

或许应当把各部分文档用一套漂亮的文档管理系统管理起来，配合导航栏、大纲，让不同需求的人能够快速找到他们想要找到的信息。比如，想学习设计架构和关键技术的朋友，可以只看这部分；想要快速搭建开发环境并上手开发的，可以只看另一部分；对于不同的开发环境，也可以看不同的部分。

一直有听说过一些静态网页生成器。出于对 [Vue.js](https://cn.vuejs.org/) 的熟悉，我选择对同属一套全家桶的 [VuePress](https://vuepress.vuejs.org/zh/) 进行了调研。随着 Vue.js 已经在向 3.0 版本过渡，VuePress 基于 Vue.js 3.0 也进入了 2.0 版本。用新不用旧，所以调研就基于 [VuePress 2](https://v2.vuepress.vuejs.org/zh/) 进行啦~

## Features

以下为官方宣传语：

- 简洁至上，以 Markdown 为中心的项目结构，以最少的配置专注于写作（就是需要这样的 😁）
- Vue 驱动，可以在 Markdown 中使用 Vue 组件，也可以用 Vue 开发自定义主题（高端玩法）
- 高性能，为每个页面渲染生成静态 HTML
- 提供开箱即用的默认主题，或使用社区主题或自行开发（一般来说默认也够用）
- 灵活的插件 API（暂时用不着）
- 打包工具（暂时用不着）

该项目本质上是一个由 Vue 和 Vue Router 驱动的单页面应用（SPA）。理念是一切从简，专注于写好 Markdown，再加上少量的配置即可。至于样式上，我觉得基本上可以无脑相信这些前端开发者提供的默认主题，最多加上少量的定制——因为他们的审美真的挺棒的。

## Start Up

推荐使用方式是在目录下初始化一个 Node.js 工程，并本地安装依赖。工程根目录下产生 `package.json` 后，在其中添加用于运行的脚本：

```json
{
  "scripts": {
    "docs:dev": "vuepress dev docs",
    "docs:build": "vuepress build docs"
  }
}
```

从工程根目录开始，所有的目录和文件将被组织为如下形式：

```
├─ docs
│  ├─ .vuepress
│  │  └─ config.js
│  └─ README.md
├─ .gitignore
└─ package.json
```

其中，根目录下的 `package.json` 保存了工程相关的基本信息，所有将要被渲染为页面的 Markdown 文档全部放置在 `docs/` 目录下。

## Configuration

`docs/.vuepress/config.js` 是文档站点的核心配置文件（也可以是一个 TypeScript 文件），它应该导出一个配置对象。该配置文件内包含两个部分：

```javascript
module.exports = {
  lang: "zh-CN",
  title: "你好， VuePress ！",
  description: "这是我的第一个 VuePress 站点",
  sidebar: false,

  themeConfig: {
    logo: "https://vuejs.org/images/logo.png",
    repo: "mrdrivingduck/blog",
    navbar: [
      // NavbarItem
      {
        text: 'Contributing',
        link: '/contributing/',
      },
      // Page file
      '/README.md',
    ],
  },
};
```

其中，`themeConfig` 对象以外的部分被称为 **站点配置**，即无论使用什么主题都可以生效的配置；`themeConfig` 内部的配置属于 **主题配置**。在 `themeConfig` 对象内，可以配置在顶部导航（navbar）、侧面导航（sidebar）中显示的控件和目录结构，以及每个目录对应的 Markdown 文件。顶部导航可配置的控件包括：

- 多语言切换
- GitHub（或其它 Git 托管站点）的链接
- 亮色 / 暗色主题切换
- 搜索框

顶部导航和侧面导航中显示了 Markdown 文档中一级标题和二级标题的汇总，显示标题的深度也是可以配置的。

## Markdown

VuePress 内对 Markdown 的相关支持都是由 [markdown-it](https://github.com/markdown-it/markdown-it) 支持的。除了 Markdown 的基本特性以外，还带有一些不错的扩展功能：

- GFM（GitHub Flavored Markdown）风格的表格和删除线
- 标题锚点：通过 `#` 直接跳转到相应章节
- 通过相对路径在不同的 Markdown 文档之间跳转
- Emoji
- 目录：`[[toc]]`
- 代码块中的行高亮、行号支持

## Frontmatter

Frontmatter 是一个包含在 Markdown 文件顶部的 YAML 信息，可以作为 Markdown 页面级作用域的配置项，覆盖当前全局的站点配置。其应用场景包含三个类型：

- 在所有类型页面中生效
- 在首页类型页面中生效
- 在普通类型页面中生效

例子：将当前页面设定为首页。

```markdown
---
home: true
---

# XXX
```

## Languages

VuePress 原生支持多语言文档的管理，这对国人开源到 GitHub 上的项目来说简直是刚需：一方面符合世界级开源社区的规范，需要有一套默认的英文文档；而为了迎合占据绝大多数使用者数量的国人，又可以有一套中文文档。

为使用多语言支持，需要将目录结构组织为如下形式：

```
docs
├─ README.md
├─ foo.md
├─ nested
│  └─ README.md
└─ zh
   ├─ README.md
   ├─ foo.md
   └─ nested
      └─ README.md
```

在上述结构中，默认语言支持为英语。而 `zh` 文件夹下的文件就是英语版文档结构的一个翻版，显然，里面的内容全部都是与英文版文档相对应的中文版文档。这样，不同语言类型可以以相同的方式导航到相应的文档。在 `docs/.vuepress/config.js` 的 **站点配置** 中，需要设置 `locales` 选项：

```javascript
module.exports = {
  locales: {
    // 键名是该语言所属的子路径
    // 作为特例，默认语言可以使用 '/' 作为其路径。
    '/': {
      lang: 'en-US',
      title: 'VuePress',
      description: 'Vue-powered Static Site Generator',
    },
    '/zh/': {
      lang: 'zh-CN',
      title: 'VuePress',
      description: 'Vue 驱动的静态网站生成器',
    },
  },

  themeConfig: {
    locales: {
      '/': {
        selectLanguageName: 'English',
        // navbar
        navbar: navbar.en,
        // sidebar
        sidebar: sidebar.en,
        // page meta
        editLinkText: 'Edit this page on GitHub',
      },
      '/zh/': {
        selectLanguageName: '简体中文',
        // navbar
        navbar: navbar.zh,
        selectLanguageName: '简体中文',
        selectLanguageText: '选择语言',
        selectLanguageAriaLabel: '选择语言',

        // sidebar
        sidebar: sidebar.zh,

        // page meta
        editLinkText: '在 GitHub 上编辑此页',
        lastUpdatedText: '上次更新',
        contributorsText: '贡献者',

        // custom containers
        tip: '提示',
        warning: '注意',
        danger: '警告',
      },
    },
  },
}
```

如果使用默认主题，那么在 **主题配置** 中提供多语言支持的方式与站点配置一致，可以使用一种新语言覆盖控件上出现的文字，如上述主题配置所示。

## Deploy

不必多说，因为文档生成器被设计出来自然就是为了便于线上部署。从 GitHub Pages 到 GitLab Pages，各种 CI 部署方式一应俱全。

## Theme

除默认主题以外，NPM 上也有很多社区人员自行开发的主题，VuePress 也支持直接本地使用自行开发的主题。以我个人来看，默认主题已经足够完美了，最多需要加以定制——比如把 Vue 全家桶默认的绿色换位某司的主题色橙色。

VuePress 的默认主题使用 [SASS](https://sass-lang.com/) 作为 CSS 预处理器。用户可以通过 palette 文件（我不会）或 style 文件来自定义样式变量或添加额外的样式。如，在 `docs/.vuepress/styles/index.scss` 文件中，覆盖默认样式：

```scss
:root {
  scroll-behavior: smooth;

  // brand colors
  --c-brand: #3eaf7c;
  --c-brand-light: #4abf8a;
}
```

## References

[VuePress: Vue 驱动的静态网站生成器](https://v2.vuepress.vuejs.org/zh/)

[GitHub: vuepress-next](https://github.com/vuepress/vuepress-next)
