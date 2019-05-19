# Compiler - Intermediate Representation

Created by : Mr Dk.

2019 / 05 / 19 16:25

Nanjing, Jiangsu, China

---

## Significance

中间代码（IR）抽象并简化了程序结构

## Advantages

* 将各类分析需要的信息进行统一编码
* 使编译器的前端、优化器、后端能够分离
* 使优化器、后端处理提供统一的接口
  * 提升效率
  * 减少错误

## Disadvantages

* 需要在编译器上添加额外的 analysis pass
* 对于非优化的编译器来说，多此一举

## Basic Blocks

一条接一条执行的代码块

Group operations that always happen together

## Control-flow Graph

Nodes - basic blocks

Edges - 

* Labelled - conditional jumps
  * `true` / `false`
* Unlabeled - unconditional jumps

Loops - back edges

* 可简化为，对判断条件进行判断 &rarr; Labelled

---

