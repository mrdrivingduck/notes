# Compiler - LLVM

Created by : Mr Dk.

2019 / 05 / 19 14:06

Nanjing, Jiangsu, China

---

## About

LLVM 是一个模块化、可重用的编译器和工具链技术的集合

> The LLVM Project is a collection of modular and reusable compiler and toolchain technologies.
>
> Despite its name, LLVM has little to do with traditional virtual machines.
>
> The name "LLVM" itself is not an acronym; it is the full name of the project.

_"For designing and implementing LLVM"_, the ACM presented Vikram Adve, Chris Lattner, and Evan Cheng with the 2012 ACM Software System Award.

---

## Architecture

引用自：<https://www.jianshu.com/p/1367dad95445>

### 传统的编译器架构

![compiler-traditional](../img/compiler-traditional.png)

* Frontend - 前端

  词法分析、语法分析、语义分析、生成中间代码

* Optimizer - 优化器

  中间代码优化

* Backend - 后端

  生成机器码

### LLVM 架构

![compiler-llvm](../img/compiler-llvm.png)

* __不同的前后端使用相同的中间代码 - LLVM Intermediate Representation (LLVM IR)__
* 如果需要支持一种新的编程语言，只需要实现一个新的前端
* 如果需要支持一种新的硬件平台，只需要实现一个新的后端
* 优化阶段通用，只针对 LLVM IR，与前端后端无关

### Evaluation

GCC 的前后端耦合严重

* 支持新的编程语言
* 支持新的硬件平台

会变得非常困难

---

## Sub-projects of LLVM

### LLVM Core

广义上的 LLVM 指的是以上的整个架构

狭义上的 LLVM 指 LLVM 核心后端

* 优化器
* 机器码生成器

_[LLVM Official](http://llvm.org/)_:

> The __LLVM Core__ libraries provide a modern source- and target-independent __optimizer__, along with __code generation__ support for many popular CPUs (as well as some less common ones!) 
>
> These libraries are built around a well specified code representation known as the __LLVM intermediate representation ("LLVM IR")__.
>
> The LLVM Core libraries are well documented, and it is particularly easy to invent your own language (or port an existing compiler) to use LLVM as an optimizer and code generator.

借助这一后端，开发者可以很方便地实现某个编程语言的前端

从而实现该编程语言的编译器

### Clang

> "LLVM native" C/C++/Objective-C compiler

Clang 是 LLVM 的一个子项目，是 C/C++/Objective-C 的编译器前端

* 编译速度快（3x faster than GCC when compiling Objective-C code in a debug configuration）
* Useful error and warning messages
* Provide a platform for building great source level tools

> The __Clang Static Analyzer__ is a tool that automatically finds bugs in your code, and is a great example of the sort of tool that can be built using the Clang frontend as a library to parse C/C++ code.

![clang](../img/clang.png)

IR 由 Clang 生成

并由 __Pass__ 进行优化，通过 LLVM Core 生成对应的机器码

### LLDB

基于 LLVM Core 和 Clang 的调试工具

比 GDB 的更省内存

### libc++ & libc++ ABI

C++ 标准库的实现，包括对 C++11 和 C++14 的支持

### ...

---

## Summary

关于 LLVM 和 Clang 其实在一年前就已经听说过了

当时刚开始用 VS Code

安装了一个 C/C++ 的编译运行插件

里面的代码提示就依赖于 Clang

安装 Clang 的时候好像控制面板里就多了 LLVM

今天学习后发现 - 从架构上来看

LLVM 真的非常科学合理呢 🤙

前后端解耦实现了最大程度上的模块重用

---

