## Java Web - Tomcat and Servlet : Thread safety

Created by : Mr Dk.

2018 / 05 / 10 10:51

Nanjing, Jiangsu, China

---

##### 1. 问题的提出

* 将 Servlet 部署至 Tomcat 服务器上
* 当多个用户并发地访问该 Servlet 时，Tomcat 该如何处理？

---

##### 2. Servlet 的生命周期

* Servlet 运行在 Servlet 容器中
* Tomcat 就是一种 Servlet 容器
* 生命周期四大阶段：
  1. 加载并实例化
  2. 初始化
  3. 处理请求
  4. 销毁

~~~Java
package cn.Test.servlet;

import java.io.IOException;
import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class TestServlet
 */
@WebServlet("/TestServlet")
public class TestServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
       
    public TestServlet() {
        super();
        // TO DO ...
    }

    public void init(ServletConfig config) throws ServletException {
        // TO DO ...
    }

    public void destroy() {
        // TO DO ...
    }

    protected void service(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
	// TO DO ...
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
    throws ServletException, IOException {
	// TO DO ...
    }
    
    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
    throws ServletException, IOException {
	// TO DO ...
    }
}

~~~

1. Servlet 的加载并实例化
   * Tomcat 截获请求，将请求封装为 HttpRequest 对象，进行处理
   * Tomcat 查询 web.xml 文件，找到对应 Servlet 的 Java 类
     （现已不需要在 web.xml 中配置 Servlet）
     （如果是第一次，则 Tomcat 会将 Servlet 编译成 .class 文件）
   * Tomcat 实例化查询到的 Servlet 类
     **注意：单例模式 只实例化一个 Servlet 类**
2. Servlet 的初始化
   * 调用 init() 函数进行初始化
   * 可执行一些一次性的活动
   * 在整个生命周期中，init() 函数只会被调用一次
3. Servlet 的请求处理 （多线程调用）
   * 并行调用 service() 函数
   * 多个 service() 函数运行在独立的线程中
   * 通过 HttpServletRequest 获取请求
   * 通过 HttpServletResponse 发送响应
   * 如果不对 service() 函数进行 override，
     则根据提交的方式执行 doPost() 或 doGet()
4. Servlet 的销毁
   * 调用 destroy() 函数进行对象销毁、资源回收

---

##### 3. Servlet 的线程安全

* 由 Servlet 的生命周期可以看出
  多个 service 线程共用同一个 Servlet 实例
* 单实例多线程
* 降低系统资源需求
* 提高系统并发量以及响应时间
* 无状态的 Servlet 是绝对线程安全的
* 控制 Servlet 的线程安全性：
  1. 避免在 Servlet 类中定义变量并使用 （多线程共享该变量）
  2. 避免使用非线程安全的集合
  3. 使用 _Synchronized_ 进行互斥访问

---

##### 4. Tomcat 线程管理

* Tomcat 会维护一个线程池
* Tomcat 线程池参数
  * `maxThreads` ：Tomcat 能创建的用于处理请求的最大线程数
  * `maxSpareTHreads` ：最大空闲线程数
    处于活跃状态的、正在等待的空闲线程的最大数量
    若超过这个数量，则回收部分活跃空闲线程
  * `minSpareTHreads` ：最小空闲线程数
    处于活跃状态的、正在等待的空闲线程的最小数量
    若低于这个数量，则创建部分活跃空闲线程等待被调度
  * `acceptCount` ：最大等待队列长度
    若并发请求超过了线程池的处理能力
    则放入等待队列中等待被处理
  * `maxIdleTime` ：最大空闲时间
    若超过最大空闲时间，且线程数大于最小空闲线程数
    则线程将被回收，以节省资源
* Tomcat 处理请求
  * Tomcat 截获请求，并封装
  * 从线程池中取一个活跃空闲线程，将请求传入线程进行处理
  * 处理结束后，将线程资源返还给线程池

---

