# Java - Thread Pool

Created by : Mr Dk.

2020 / 11 / 02 16:17

Nanjing, Jiangsu, China

---

线程池技术预先创建了若干数量的线程，用户不能直接对线程的创建进行控制。在这一前提下，重复使用固定或较为固定数目的线程来完成任务的执行。合理使用线程池能够带来的好处如下：

1. 重复利用已创建的线程，降低了线程 **创建** 和 **销毁** 造成的开销
2. 任务到达时，无需等到线程创建就能立刻执行，提高了响应速度
3. 对线程统一分配、调优、监控，提高了线程的客观理性

## Theory

线程池的工作原理如下：

1. 线程池中的线程数还没有达到设定值，则创建新线程处理任务 (预热)
2. 线程池中的线程数达到设定值，则将要处理的任务添加到工作队列中
3. 线程执行完一个任务后，从工作队列中取出下一个任务继续运行
4. 如果工作队列已满，则由 **饱和策略** 来处理任务

也可以通过选项一次性创建线程池中的所有线程。

## Parameters

- `corePoolSize` - 线程池基本大小，当需要执行的任务数超过线程池基本大小时，不再创建新的线程
- `runnableTaskQueue` - 阻塞队列，用于保存等待被执行的任务
  - `ArrayBlockingQueue` - 基于数组的有界阻塞队列
  - `LinkedBlockingQueue` - 基于链表的阻塞队列
  - `SynchronousQueue` - 阻塞队列，插入操作与移除操作必须一一匹配
  - `PriorityBlockingQueue` - 具有优先级的无界阻塞队列
- `maximumPoolSize` - 线程池允许创建的最大线程数，在阻塞队列已满时继续创建线程的阈值 (如果阻塞队列无界，那么该参数就没有什么效果)
- `RejectExecutionHandler` - 饱和策略，当队列和线程池都满时，对新任务的策略
  - `AbortPolicy` - 直接抛出异常
  - `CallerRunsPolicy` - 由调用者所在线程运行任务
  - `DiscardOldestPolicy` - 丢掉队列里最老的任务，并试图添加新的任务
  - `DiscardPolicy` - 不处理新任务
  - 实现 `RejectedExecutionHandler` 接口自行定义策略
- 时间参数
  - `keepAliveTime` - 超出线程池 `corePoolSize` 的工作线程空闲后保持存活的时间
  - `TimeUnit` - 线程活动保持时间的单位

## Submission

`execute()` 函数用于提交不需要返回值的任务，输入参数是一个 `Runnable` 类的实例。因此无法判断任务是否被线程池执行成功。`submit()` 函数用于提交需要返回值的任务，线程池会返回一个 `Future` 类型的对象，通过该对象判断任务是否被执行成功，并获取返回值。

## Shut Down

关闭线程池的原理是通过遍历线程池中的每个线程，逐个调用线程的 `interrupt()` 函数来中断线程 - 因此无法响应中断的任务可能永远无法终止。`shutdownNow()` 将线程池的状态设置为 `STOP`，并尝试停止所有线程；`shutdown()` 则只是将线程池的状态设置为 `SHUTDOWN`，并中断所有空闲线程。

调用以上两个函数中的任意一个，`isShutdown` 就会返回 `true`；当所有任务都关闭后，`isTerminated` 返回 `true`，线程池才算关闭成功。

## Configuration

合理配置先线程池所需要考虑的要素：

- 任务性质 - CPU 密集 / I/O 密集 / 混合型
- 任务优先级 - 高 / 中 / 低
- 任务的执行时间 - 长 / 中 / 短
- 任务的依赖性 - 是否依赖其它系统资源

CPU 密集型任务应当配置尽可能少的线程 (接近处理器个数)，以便减少上下文切换开销；I/O 密集型任务应配置尽可能多的线程。

有界的阻塞队列能够增强系统的稳定性和预警能力。无界队列可能会使线程池队列越来越长，撑满内存，导致整个系统不可用。

## Executor Framework

HotSpot 虚拟机将 Java 线程一对一映射为本地 OS 的线程。在上层，Java 多线程程序使用用户空间的调度器 Executor 框架将任务映射到固定数量的线程。

### Tasks

Executor 框架中的任务需要实现 `Runnable` 接口或 `Callable` 接口。

### Executors

`ThreadPoolExecutor` 是线程池的核心实现类，用于执行被提交的任务。根据使用场景分别实现了：

- `FixedThreadPool` - 固定线程数的线程池，以 `LinkedBlockingQueue` 作为工作队列，可以无限延长，因此线程池也永远不会拒绝新任务，并且线程池中的线程数不会超出 `corePoolSize`，另外 `maximumPoolSize` 和 `keepAliveTime` 参数无效
- `SingleThreadExecutor` - 单工作线程的线程池，也使用 `LinkedBlockingQueue` 作为工作队列，`corePoolSize` 参数被设置为 `1`，只有一个工作线程不断从工作队列中获取任务执行
- `CachedThreadPool` - 根据需要创建新线程的线程池，`corePoolSize` 被设置为 `0`，`maximumPoolSize` 被设置为 `Integer.MAX_VALUE`，即线程池无界；`keepAliveTime` 被设置为 `60L`，表示一个线程在空闲 60s 后将会被终止；内部使用 `SynchronousQueue` 作为线程池的工作队列

`ScheduledThreadPoolExecutor` 继承自 `ThreadPoolExecutor`，用于在给定的延迟之后运行任务，或者定期执行任务。其内部维护了一个 `DelayQueue`，内部实际上是一个以时间为优先级的优先队列，而 JDK 优先队列的实现是自增长的，所以 `maximumPoolSize` 参数并没有实际意义。任务在被封装为 `ScheduledThreadPoolExecutor` 后加入延时队列，包含参数：

- `time` - 任务要被执行的具体时间
- `ssequenceNumber` - 任务被添加到调度器中的序号
- `period` - 任务被执行的间隔周期

线程会从延时队列中取出最早到期的 `ScheduledFutureTask`，执行并修改 `time` 为下次要被执行的时间后，再放回延时队列中。

---
