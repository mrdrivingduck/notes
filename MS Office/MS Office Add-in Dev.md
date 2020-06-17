# MS Office - Add-in Dev

Created by : Mr Dk.

2019 / 08 / 28 0:56

Ningbo, Zhejiang, China

---

## About

这个东西的中文名称叫做 **外接程序**，也可以叫做 **加载项**，可以用于扩展 Office 应用程序，并与 Office 文档中的内容进行交互。换句话说就是可以自己写程序操作 Office 文档叭 😶。

Office 提供了套件通用的 API，也有适用于程序个体 (Excel, Word...) 的专用 API。

---

## Office VBA

Office Visual Basic for Applications (VBA) 是一种事件驱动编程语言。几乎所有可以使用鼠标、键盘或对话框执行的操作也可以通过使用 VBA 自动进行。若某个操作可以使用 VBA 执行一次，则可以同样轻松地执行该操作一百次。除了可通过编写 VBA 脚本来加速执行日常任务外，还可以使用 VBA 为 Office 应用程序添加新功能，或以特定于业务需要的方式来提示文档用户并与之交互。

但是..技术似乎比较老，😅 不优雅。我不喜欢。

---

## VSTO

Visual Studio Tools for Office (VSTO) 是 VBA 的替代。VSTO 外接程序包含与 Microsoft Office 应用程序相关联的程序集，使用 `C#` + `.NET` 扩展 Office 的功能。

这种技术方便在，使用较为高级的编程语言，再加上宇宙第一 IDE 的集成，使得开发较为方便。[文档在这里](https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.tools?view=vsto-2017)。

考虑用这一套技术写一些简单的 Office 工具，比如自动化解锁密码。之前手动解密码让我觉得太累了。

---

## JavaScript API + Web

这是目前最新的加载项开发方式，通过 Web 技术来扩展 Office。这一技术不涉及 **用户设备** 或 **Office 客户端** 中运行的代码，主机应用程序 (如 Excel) 读取 **加载项清单**

* 挂钩 UI 中的加载项自定义功能区按钮和菜单命令
* 在应用程序中加载加载项的 HTML 和 JavaScript 代码
* 这些代码在沙盒中的浏览器上下文范围内执行，操作 Office 功能

优势：

1. 跨平台支持 - 不需要 VB 或者 .NET 支持
2. 集中部署和分发
3. 可以通过 AppSource 供广大受众使用
4. 以标准的 Web 技术为依据

### Components

Office 加载项 = 加载项清单 (XML) + 网页 (HTML + JavaScript)

#### 清单

是一个 XML 文件，指定外接程序的设置和功能：

* 外接程序在应用程序 (如 Excel) 中的显示名称、说明、ID、版本
* 如何将外接程序与 Office 集成
* 外接程序的权限级别和数据访问要求

#### Web 应用

在 Office 应用中显示的静态 HTML 页面。此页面并不与 Office 文档或其他任何 Internet 资源交互。若要与 Office 客户端和文档交互，可以使用 Office.js JavaScript API。

大致上来说，就是这个 Web 应用运行起来，在 Office 应用程序内，运行一个类似浏览器的东西。根据清单文件里面的配置信息，访问 Web 服务。可能还涉及 Office 应用程序中状态信息的传递，作为访问 Web 的参数。Web 服务触发调用 Office.js 的 API，实现相应的功能。

### Demo

![office-js-api](../img/office-js-api.png)

根据清单文件，Office 应用程序上可以显示出对应的外接程序。点击外接程序，右边出现一个类似浏览器界面，访问对应的 Web 页面。在左侧的 Excel 表格中选中一定尺寸的单元格，点击右侧 Web 页面中的一个按钮 (比如 - 设置背景颜色)。Office 应用程序相当于访问了 Web 应用中的服务，触发了 Web 服务调用 Office JavaScript API，修改选中所有单元格的背景颜色。

### Supporting

在各种 Web 技术下都适用

- [x] 原生 JavaScript + ajax
- [x] Angular / React / Vue
- [x] Visual Studio - ASP .NET

不过各自有各自的配置，官网的文档中都有。

---

## References

https://docs.microsoft.com/en-us/office/dev/add-ins/

https://docs.microsoft.com/zh-cn/visualstudio/vsto/create-vsto-add-ins-for-office-by-using-visual-studio?view=vs-2017

---

## Summary

虽说基于 Web 的技术是官方最为推崇的，但我还是喜欢 VSTO 的 😂，觉着写起来舒服些。原则上来说，只要是点击鼠标或者键盘能做到的事，应当都有对应的 API，并且能帮助干一些重复的活。接下来准备做两个小型的批处理外接程序试试看：

1. 将多个 Excel 文件合并为一个 Excel 文件中的多个表
2. 将多个 Excel 文件的保护密码移除

---

