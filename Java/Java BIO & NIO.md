# Java - BIO & NIO

Created by : Mr Dk.

2020 / 06 / 14 21:42

Nanjing, Jiangsu, China

---

BIO 和 NIO 的概念很早之前就听说过，但没有机会深挖。最近下定决心弄清楚，有机缘巧合买了一节相关的网课听了听，觉得有些收获。把几个常用到的名词和含义搞懂了：

- BIO / NIO / AIO
- SELECT / POLL / EPOLL
- 同步 / 异步
- 阻塞 / 非阻塞

本文大致以服务端网络 I/O 操作的发展演进过程为逻辑。

---

## BIO

BIO 即 blocking I/O，这是操作系统中最简单的 I/O 模型。无论是在网络课还是在操作系统课上，无论是 Java 还是 C/C++，都肯定演示过一个最简单的网络程序 (伪代码)：

- 监听一个服务器端口
- 在一个死循环中，不断接收客户端连接并处理
- 如果不想在处理连接的同时错过新的客户端连接，就把连接的处理交给一个子进程/子线程

```
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket client = server.accept();

    new Thread() {
        // client...
    }
}
```

ServerSocket 的实例化过程有三步：

- 调用 OS 的 `socket()` 系统调用，拿到一个文件描述符 fd
- 调用 OS 的 `bind()` 将这个 fd 关联到服务器要监听的端口上
- 调用 OS 的 `listen()` 开始监听 fd (即监听端口)

```
NAME
       socket - create an endpoint for communication

SYNOPSIS
       #include <sys/types.h>          /* See NOTES */
       #include <sys/socket.h>

       int socket(int domain, int type, int protocol);

DESCRIPTION
       socket()  creates  an  endpoint  for communication and returns a file descriptor that refers to that endpoint.
       The file descriptor returned by a successful call will be the lowest-numbered file  descriptor  not  currently
       open for the process.
```

```
NAME
       bind - bind a name to a socket

SYNOPSIS
       #include <sys/types.h>          /* See NOTES */
       #include <sys/socket.h>

       int bind(int sockfd, const struct sockaddr *addr,
                socklen_t addrlen);

DESCRIPTION
       When  a  socket  is  created  with  socket(2),  it  exists in a name space (address family) but has no address
       assigned to it.  bind() assigns the address specified by addr to the socket referred to by the file descriptor
       sockfd.   addrlen  specifies  the size, in bytes, of the address structure pointed to by addr.  Traditionally,
       this operation is called “assigning a name to a socket”.

       It is normally necessary to assign a local address using bind() before a SOCK_STREAM socket may  receive  con‐
       nections (see accept(2)).
```

```
NAME
       listen - listen for connections on a socket

SYNOPSIS
       #include <sys/types.h>          /* See NOTES */
       #include <sys/socket.h>

       int listen(int sockfd, int backlog);

DESCRIPTION
       listen() marks the socket referred to by sockfd as a passive socket, that is, as a socket that will be used to
       accept incoming connection requests using accept(2).
```

在死循环中，`accept()` 用于接受客户端连接，将会一直阻塞 (即不再向下执行代码，进程处于休眠)，直到有新的连接到来，进程被 OS 唤醒，代码继续向下执行。该系统调用返回了客户端对应的 socket fd。

另外，在子线程处理连接的过程中，如果调用了 `recv()` 读取客户端发来的数据，OS 只有在接收到数据后才会使 `recv()` 返回。因此，`accept()` 和 `recv()` 这两个系统调用都是阻塞的。

```
NAME
       accept, accept4 - accept a connection on a socket

SYNOPSIS
       #include <sys/types.h>          /* See NOTES */
       #include <sys/socket.h>

       int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);

       #define _GNU_SOURCE             /* See feature_test_macros(7) */
       #include <sys/socket.h>

       int accept4(int sockfd, struct sockaddr *addr,
                   socklen_t *addrlen, int flags);

DESCRIPTION
       The  accept()  system  call  is  used  with  connection-based  socket types (SOCK_STREAM, SOCK_SEQPACKET).  It
       extracts the first connection request on the queue of pending connections for the  listening  socket,  sockfd,
       creates a new connected socket, and returns a new file descriptor referring to that socket.  The newly created
       socket is not in the listening state.  The original socket sockfd is unaffected by this call.
```

```
NAME
       recv, recvfrom, recvmsg - receive a message from a socket

SYNOPSIS
       #include <sys/types.h>
       #include <sys/socket.h>

       ssize_t recv(int sockfd, void *buf, size_t len, int flags);

       ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                        struct sockaddr *src_addr, socklen_t *addrlen);

       ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);

DESCRIPTION
       The  recv(),  recvfrom(), and recvmsg() calls are used to receive messages from a socket.  They may be used to
       receive data on both connectionless and connection-oriented sockets.  This page first  describes  common  fea‐
       tures of all three system calls, and then describes the differences between the calls.
```

因此，BIO 的特性是：**一个线程对应一个连接**，能够解决的问题：

- 可以接收大量的连接

但是弊端在于，OS 中将会同时存在大量的线程：

- 线程内存开销较大
- 大量的 CPU 资源被浪费在线程上下文切换上

造成 BIO 特性的根本原因是，**系统调用的阻塞性**。如果系统调用能够支持非阻塞，那么就能够使用新的 I/O 模型。

## NIO

OS 中的 NIO 指的是 non-blocking I/O，而 Java JDK 中的 `nio` 指的是 new I/O。在 Linux 2.6.27 起对 `socket()` 系统调用的非阻塞提供了支持：

```
Since Linux 2.6.27, the type argument serves a second purpose: in addition to specifying a socket type, it
may include the bitwise OR of any of the following values, to modify the behavior of socket():

       SOCK_NONBLOCK   Set the O_NONBLOCK file status flag on the new open file  description.   Using  this  flag
                       saves extra calls to fcntl(2) to achieve the same result.
```

而较新的 Java 版本使用内核提供的非阻塞系统调用实现了 JDK 中的 NIO。可以看一个用 Java NIO API 实现的例子：

```java
ServerSocketChannel server = ServerSocketChannel.open();
server.bind(new InetSocketAddress(9090));
server.configureBlocking(false);

// 所有客户端连接
LinkedList<SocketChannel> clients = new LinkedList<>();

while (true) {
    SocketChannel client = server.accept();

    if (client == null) {
        // ..
    } else {
        client.configureBlocking(false);
        clients.add(client); // 维护客户端
    }

    ByteBuffer buffer = ByteBuffer.allocateDirect(4096);
    for (SocketChannel c : clients) {
        int num = c.read(buffer);
        if (num > 0) {
            // ...
        }
    }
}
```

每一轮循环中，`accept()` 不会阻塞，立刻返回：

- 如果有连接，就返回连接
- 如果没有连接，就返回 `null`

另外，在每轮循环中，对于已经建立的每一个连接调用一次 `read()` 来接收数据，`read()` 的调用也是非阻塞的，如果有数据，就返回一个大于 0 的字节数。这样一来，**只使用了一个线程**，就实现了 BIO 模型中的功能。在并发量较大时 (C10K)，相比 BIO 有优势。

它的局限性在于，假设 `clients` 中维护着大量的客户端连接。在每一轮循环中，都要对整个 `clients` 链表中的每一个客户端调用一次 `read()`，但只有极个别的客户端有数据可以被读取。那么相当于绝大部分 `read()` 的调用是无意义的。这一过程中，由于进行了大量的系统调用，大量的 CPU 时间被浪费在内核态-用户态切换上。

这个问题的实质是，用户空间程序用一个 for 循环来遍历内核中的数据结构 (fd)，大量系统调用带来了大量堆栈切换的开销。如果用户空间程序可以通过 **一次** 系统调用，一次性把所有要查询的 fd 告诉内核，由内核来进行循环遍历，那么就可以节省堆栈切换的开销。这种通过一次系统调用同时查询多个 fd 的 I/O 状态的方式被称为 **多路复用**。

---

## SELECT and POLL

这两个系统调用是 POSIX 标准中定义的多路复用功能，Linux 很早就实现了它们。用户空间程序告诉内核自己想要查询哪些 fd 的 I/O 已经处于就绪状态，内核代为查询之后，返回给用户空间。

关于 SELECT 在 Linux 0.12 中的实现可以参考 [这里](../../linux-kernel-comments-notes/Chapter 12 - 文件系统/Chapter 12.19 - select.c 程序.md)。用户空间程序可以以 bitmap 的形式，将想要查询 I/O 状态的 fd 对应的 bit 置为 1。其中的限制在于 bitmap 的长度是确定的，因此查询的 fd 范围受到了限制。而 POLL 的参数是链表，从而突破了这个局限。

```
NAME
       select, pselect, FD_CLR, FD_ISSET, FD_SET, FD_ZERO - synchronous I/O multiplexing

SYNOPSIS
       /* According to POSIX.1-2001, POSIX.1-2008 */
       #include <sys/select.h>

       /* According to earlier standards */
       #include <sys/time.h>
       #include <sys/types.h>
       #include <unistd.h>

       int select(int nfds, fd_set *readfds, fd_set *writefds,
                  fd_set *exceptfds, struct timeval *timeout);

       void FD_CLR(int fd, fd_set *set);
       int  FD_ISSET(int fd, fd_set *set);
       void FD_SET(int fd, fd_set *set);
       void FD_ZERO(fd_set *set);

       #include <sys/select.h>

       int pselect(int nfds, fd_set *readfds, fd_set *writefds,
                   fd_set *exceptfds, const struct timespec *timeout,
                   const sigset_t *sigmask);
   Feature Test Macro Requirements for glibc (see feature_test_macros(7)):

       pselect(): _POSIX_C_SOURCE >= 200112L

DESCRIPTION
       select()  and pselect() allow a program to monitor multiple file descriptors, waiting until one or more of
       the file descriptors become "ready" for some class of  I/O  operation  (e.g.,  input  possible).   A  file
       descriptor  is  considered ready if it is possible to perform a corresponding I/O operation (e.g., read(2)
       without blocking, or a sufficiently small write(2)).

       select() can monitor only file descriptors numbers that are less than FD_SETSIZE; poll(2)  does  not  have
       this limitation.  See BUGS.
```

```
NAME
       poll, ppoll - wait for some event on a file descriptor

SYNOPSIS
       #include <poll.h>

       int poll(struct pollfd *fds, nfds_t nfds, int timeout);

       #define _GNU_SOURCE         /* See feature_test_macros(7) */
       #include <signal.h>
       #include <poll.h>

       int ppoll(struct pollfd *fds, nfds_t nfds,
               const struct timespec *tmo_p, const sigset_t *sigmask);

DESCRIPTION
       poll()  performs a similar task to select(2): it waits for one of a set of file descriptors to become ready
       to perform I/O.
```

这种多路复用显著减少了系统调用的调用次数，但是还存在一个问题：

- 每次调用都要传递大量重复的 fd (用户空间向内核空间复制参数是需要开销的)
- 内核每次都要遍历内核中所有的 fd 来确定哪些 fd 就绪 (类似轮询，需要通过中断解决)

如果能够在内核中维护用户空间要查询的所有 fd 的状态，那么就能够消除这种参数复制开销。这就是 EPOLL 多路复用器出现的意义。

---

## EPOLL

EPOLL 如何实现高效查询多个 fd 的状态呢？

EPOLL 包含三个系统调用：

```c
int epoll_create(int size);
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
int epoll_wait(int epfd, struct epoll_event *events,
                      int maxevents, int timeout);
```

这三个系统调用的使用方式：

首先使用 `epoll_create()`，内核会开辟一块内存，然后返回一个代表这个内存区的 epoll fd。这块内存用于保存所有要监视的 fd。

然后，用户空间通过调用 `epoll_ctl()`，将 想要监视的 **fd** 以及 **事件** 注册到 epoll fd 对应的内存中。注意，对于某一个被监视的 fd，一般只需要调用一次 `epoll_ctl()` 即可。`epoll_ctl()` 支持的注册事件包括：

- `EPOLL_CTL_ADD` - 注册 fd
- `EPOLL_CTL_MOD` - 修改已注册 fd 的事件
- `EPOLL_CTL_DEL` - 解除注册 fd

支持监视的事件很多，比如：

- `EPOLLIN` - fd 可被调用 `read()`
- `EPOLLOUT` - fd 可被调用 `write()`
- ...

用户空间程序只需要调用 `epoll_wait()` (并可指定一个超时参数)，内核就会返回目前已经就绪的 fd。

可以看到，上述步骤解决了 SELECT 与 POLL 中需要反复向内核传递 fd 集合的问题，内核已经在 epoll fd 对应的内存中维护了所有已注册的被监控 fd。另外，EPOLL 中具体做了哪些工作来提高性能呢？

```c
/*
 * This structure is stored inside the "private_data" member of the file
 * structure and represents the main data structure for the eventpoll
 * interface.
 */
struct eventpoll {
	/* Protect the access to this structure */
	spinlock_t lock;

	/*
	 * This mutex is used to ensure that files are not removed
	 * while epoll is using them. This is held during the event
	 * collection loop, the file cleanup path, the epoll file exit
	 * code and the ctl operations.
	 */
	struct mutex mtx;

	/* Wait queue used by sys_epoll_wait() */
	wait_queue_head_t wq;

	/* Wait queue used by file->poll() */
	wait_queue_head_t poll_wait;

	/* List of ready file descriptors */
	struct list_head rdllist;

	/* RB tree root used to store monitored fd structs */
	struct rb_root_cached rbr;

	/*
	 * This is a single linked list that chains all the "struct epitem" that
	 * happened while transferring ready events to userspace w/out
	 * holding ->lock.
	 */
	struct epitem *ovflist;

	/* wakeup_source used when ep_scan_ready_list is running */
	struct wakeup_source *ws;

	/* The user that created the eventpoll descriptor */
	struct user_struct *user;

	struct file *file;

	/* used to optimize loop detection check */
	int visited;
	struct list_head visited_list_link;

#ifdef CONFIG_NET_RX_BUSY_POLL
	/* used to track busy poll napi_id */
	unsigned int napi_id;
#endif
};
```

以上是 Linux 4.15 内核中的 epoll 结构体。内核在 `struct rb_root_cached rbr` 中将所有被监控的 fd 维护成一颗红黑树，对这棵树进行增删改查的时间复杂度为 O(log(n))。另外，`struct list_head rdllist` 维护了所有已经就绪的被监控 fd。

当被监控的 fd 加入红黑树时，内核会为中断处理程序注册一个回调函数。当这个 fd 对应的中断到达时，在中断处理程序的回调函数中，将 fd 自身放入就绪链表。当用户空间程序调用 `epoll_wait()` 时，直接返回这个链表中的数据即可。

EPOLL 是一个适用于多 CPU core 场景的多路复用器。对于 SELECT 或 POLL 来说，假设一个 CPU 正在运行用户空间的服务器进程，当服务器进程调用 SELECT 或 POLL 时，另一个 CPU 运行内核态代码，而运行服务器进程的 CPU 只能干等，或上下文切换。对于 EPOLL 来说，一个 CPU 可以专门运行服务器进程，一个 CPU 可以专门运行内核中的中断处理代码，两者可以并行。能够并行的根本原因是，内核中维护了 fd 的状态，两个 CPU core 能够共同访问这些状态。

EPOLL 有两种触发方式：

- Level-triggered (水平触发) (也是 SELECT、POLL 的触发方式)
- Edge-triggered (边沿触发) (也是 _信号驱动 I/O_ 的触发方式)

顾名思义，水平触发就是，只要 fd 已经就绪，每次调用 `epoll_wait()` 都能返回该 fd；而边沿触发只会在某个 fd 第一次就绪时通过 `epoll_wait()` 返回，假设用户代码没有对一个已经就绪的 fd 调用 `recv()`，那么之后调用 `epoll_wait()` 时内核将不会返回这个 fd，直到这个 fd 第二次就绪。

---

## 同步 & 异步？

这是一个纠缠了很久的问题，但是随着上述知识点的学习，似乎突然就明朗了。

可以看到，上述的 BIO 过程，或是 NIO + 多路复用器的过程，程序都需要主动调用 `recv()` / `accept()` 等系统调用读取数据或建立连接。即使使用了 **多路复用器**，其系统调用也只不过是向内核 **查询了 I/O 的状态**，对于状态为 ready 的 fd，程序还是需要主动调用 `recv()` 接收数据。这种 I/O 模型全部被称为 **同步 I/O 模型**。

而所谓的异步 I/O，是有专门的内核线程负责将 socket 接收到的数据自动拷贝到程序的用户空间缓冲区中，再发送信号通知进程。程序自己不需要主动调用 `recv()` 从内核拷贝数据了。这种模型被称为 **异步 I/O (AIO) 模型**。

---

## References

腾讯课堂 马士兵教育公开课：BIO NIO Netty

[CSDN - epoll 为什么这么快，epoll 的实现原理](https://blog.csdn.net/wangfeng2500/article/details/9127421)

[Julia Evans - Async IO on Linux: select, poll, and epoll](https://jvns.ca/blog/2017/06/03/async-io-on-linux--select--poll--and-epoll/)

[Mr Dk.'s blog - Linux 0.12 内核完全注释 - select.c 程序](../../linux-kernel-comments-notes/Chapter 12 - 文件系统/Chapter 12.19 - select.c 程序.md)
