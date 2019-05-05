# Python - Thread

Created by : Mr Dk.

2018 / 12 / 25 20:59

Nanjing, Jiangsu, China

---

## Usage

使用 _Python_ 的 `threading` 模块

启动线程：

* 用一个入口函数和线程名创建一个线程实例
* 调用 `start()` 开始执行
* 调用 `join()` 使主线程等待子线程结束

```python
import time, threading

def work():
    print("Thread %s is running" % threading.current_thread().name)
    for i in range(5):
        print("Thread %s >>> %s" % (threading.current_thread().name, i))
        time.sleep(1)
    print("Thread %s ended" % threading.current_thread().name)

print("Thread %s is running" % threading.current_thread().name)
t = threading.Thread(target=work, name="LoopThread")
t.start()
t.join()
print("Thread %s ended" % threading.current_thread().name)
```

---

## Lock

使用 `threading.Lock()` 定义一个锁

使用 `lock.acquire()` 获得锁 - 只有一个线程能成功获得该锁

使用 `lock.release()` 释放锁

* 为了防止 __死锁__，使用 `try ... finally` 来确保锁一定会被释放

```python
lock = threading.Lock()

def work():
    lock.acquire()
    try:
        # ...
    finally:
        lock.release()
```

---

## ThreadLocal

可以看做是一个全局变量

但是其中的属性对于每个线程而言是独立的，是线程中的局部变量

* 线程间对 `ThreadLocal` 中的局部变量读写不干扰

```python
import threading

local = threading.local()

def process_children():
    print("%s >>> %s" % (threading.current_thread().name, local.name))

def process_parent(name):
    local.name = name
    process_children()

t1 = threading.Thread(target=process_parent, args=("Tim", ), name="Thread 1")
t2 = threading.Thread(target=process_parent, args=("Tom", ), name="Thread 2")
t1.start()
t2.start()
t1.join()
t2.join()
```

---

## Summary

和 _Java_ 的多线程不太一样吧

反而和当年写操作系统作业时

_C_ 里面的 _libpthread_ 库的用法有点像

再写一个类似 _Java_ 的网络程序时

多线程肯定是要用到的

---

