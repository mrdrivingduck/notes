# Linux - Mutex & Condition

Created by : Mr Dk.

2021 / 03 / 02 20:25

Nanjing, Jiangsu, China

---

## Semaphore

信号量用于进程 (或线程) 之间的同步：一个线程完成后，通知另一个线程。信号量自身带有 **数值**，数值决定了共享资源的数量。如果共享资源的数量为 1，那么就可以完成资源的互斥访问。

* 有名信号量 - 适用于不同进程间
* 无名信号量 - 适用于进程内部的线程之间

具体操作：

* 初始化，并指定共享资源数量：`int sem_init (sem_t* sem, int pshared, unsigned int value)`
* 信号量 P 操作
    * `int sem_wait(sem_t* sem)`
    * `int sem_trywait(sem_t* sem)`
* 信号量 V 操作：`int sem_post(sem_t* sem)` (唯一一个能在信号处理程序中安全调用的函数)
* 取得信号量的值：`int sem_getvalue (sem_t* sem)`
* 销毁信号量：`int sem_destroy(sem_t* sem)`

## Mutex

线程互斥锁，用于锁住线程间的共享资源。相当于共享资源数量为 1 的信号量。具体操作：

* 初始化：`int pthread_mutex_init(pthread_mutex_t *restrict mutex, const pthread_mutexattr_t *restric attr)`
* 销毁：`int pthread_mutex_destroy(pthread_mutex_t *mutex)`
* 上锁
    * 阻塞加锁：`int pthread_mutex_lock(pthread_mutex_t *mutex)`
    * 非阻塞试图加锁：`int pthread_mutex_trylock(pthread_mutex_t *mutex)`
* 解锁：`int pthread_mutex_unlock(pthread_mutex_t *mutex)`

由一个线程上锁后，只能由那个线程解锁。

## Condition Variable

条件变量需要与 *互斥锁* 同时使用。互斥锁用于原子地计算条件。主要的操作是 wait 和 signal。在进行操作前，总是需要先获得互斥锁。

* 对于 wait 操作，线程进入等待队列，然后释放锁；被唤醒后返回前，线程重新获得锁并返回
* 对于 signal 操作，线程唤醒一个或多个等待线程后，释放锁；所有被唤醒的线程 **重新竞争互斥锁**，竞争成功的那个线程以持有互斥锁的方式从 wait 操作返回

发出 wait 和 signal 操作的线程不是同一个。具体操作：

* 初始化条件变量：`int pthread_cond_init(pthread_cond_t *restrict cond, pthread_condattr_t *restrict attr)`
* 销毁条件变量：`int pthread_cond_destroy(pthread_cond_t *cond)`
* 等待
    * 阻塞等待：`int pthread_cond_wait(pthread_cond_t *restrict cond, pthread_mutex_t *restric mutex)`
    * 超时等待：`int pthread_cond_timedwait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex, const struct timespec *restrict timeout)`
* 通知
    * 通知一个线程 (按入队顺序)：`int pthread_cond_signal(pthread_cond_t *cond)`
    * 通知所有线程：`int pthread_cond_broadcast(pthread_cond_t *cond)`

使用方式：在 signal 激活等待线程后，当前线程需要释放互斥锁。

```c
// thread 1
pthread_mutex_lock(&mutex);
if (condition) {
    pthread_cond_signal(&cond);
}　　
pthread_mutex_unlock(&mutex);
```

当等待线程被唤醒后，重新对互斥锁进行竞争；竞争成功的线程从 wait 函数返回。从 wait 操作返回后，需要重新对条件进行判断：有可能在这段时间内，条件已经被改变了。

```c
// thread 2
pthread_mutex_lock(&mutex);
while (condition) {
    pthread_cond_wait(&cond, &mutex);
}
pthread_mutex_unlock(&mutex);
```

---

## References

[博客园 - Linux 互斥锁、条件变量和信号量](https://www.cnblogs.com/li-daphne/p/5558435.html)

[ChinaUnix - 信号量、互斥锁、读写锁和条件变量的区别](http://blog.chinaunix.net/uid-20671208-id-4935154.html)

---

