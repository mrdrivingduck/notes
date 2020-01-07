# Python - Multi-Process

Created by : Mr Dk.

2020 / 01 / 07 11:33

Nanjing, Jiangsu, China

---

## The Problem

为什么突然研究起了 Python 的多进程？

问题来自于昨天做 _Machine Learning_ 的 project 时

嫌 Python 跑得太慢，于是写了个多线程版本

运行起来以后，打开任务管理器发现还是只占了一个 CPU core (25%)

问了一下学长，他说他不太清楚原理

但是根据经验，开多个命令行窗口同时执行脚本才能充分利用 CPU

我心想那不就是多进程吗 😅

那么为什么多线程就不行呢？

---

## About _GIL_

__GIL (Global Interpreter Lock)__ 被翻译为 __全局解释器锁__

在 Python 的主流实现 _CPython_ 中，是一个全局线程锁

* 解释器在执行任何 Python 代码时，都需要获得这把锁
* 遇到 I/O 操作时，释放这把锁
* 纯计算操作，解释器每隔 100 次操作就释放这把锁，让别的线程有机会执行

那么在一个解释器进程中，只有占有 GIL 的那个线程可以被 CPU 执行

。。。这就很僵硬了 😥

根据资料，GIL 的存在可能是一个历史遗留问题

在 Python 出现时，还没有多核 CPU

因此用一个全局锁来实现线程安全是最简单经济的设计了

### 对多计算程序的分析

假设有一个纯计算程序，被实现为多线程版本

每个线程的任务就是不停地计算

而由于 GIL 的存在，它们等价于运行在一个 core 上

并且效率还不如单线程版本 😒

因为线程切换、释放锁、获得锁也是需要一点点 CPU 资源的

### 对多 I/O 程序的分析

对于这种程序来说，实现为多线程还是有一定好处的

当一个线程需要 I/O 时，单线程程序就只能被阻塞并等待 I/O 了

而多线程程序可以调度另一个不需要 I/O 的线程运行

---

## Multi-Processing

就算再被人诟病，GIL 这个实现已经板上钉钉

是否弃用 GIL 就由 Python 的设计人员决定吧 (至少在目前是不太可能)

既然绕不过 GIL，就用别的方法来解决 CPU 利用的问题

Python 是可以调用 C/C++ 的扩展的 - 在 C/C++ 扩展中将逻辑实现为多线程，那就是真的多线程了

当然，为了简单，有没有只用 Python 就能利用多核 CPU 的方法呢？

那就同时启动多个解释器吧 (这也就是学长所谓的开多个 terminal 同时执行的意思)

一个 GIL 吞吐率太低，我就整很多个 GIL 呗

Python 内置了支持 __跨平台__ 的多进程模块 `multiprocessing`

其中提供了 `Process` 类来代表进程对象

```python
from multiprocessing import Process

def func(arg1, arg2):
    # TO DO ...

if __name__ == "__main__":
    p = Process(target=func, args=(arg1, arg2))
    p.start()
    p.join()
```

给定新进程的入口函数地址，及其参数

然后启动该进程

等待该进程结束

---

## References

[知乎 - 为什么多线程Python程序无法充分利用多个CPU核心带来的优势？](https://www.zhihu.com/question/322492039)

[多进程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/1016959663602400/1017628290184064)

[CSDN - python多线程为什么不能利用多核cpu](https://blog.csdn.net/qq_16059847/article/details/82660620)

---

## Summary

高级用法 (池化、进程间通信等) 暂时不谈

主要是明白 Python 对 CPU 利用的原理

之后我编了一个多进程版本的程序

CPU 的利用率果然就上去了诶嘿嘿嘿 😎

---

