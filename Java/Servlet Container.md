# Servlet - Container

Created by : Mr Dk.

2020 / 11 / 30 23:04

Nanjing, Jiangsu, China

---

## Servlet 容器是如何工作的

Servlet 容器是一个复杂的系统。要为一个 Servlet 请求提供服务，通常要做三件事：

1. 创建一个 request 对象，并填充其中的信息：
   * 参数
   * 请求头
   * Cookies
   * Query string
   * URI
2. 创建一个 response 对象，Servlet 使用该对象向客户端发送响应
3. 调用 Servlet 的 `service()` 函数，并传入 request 和 response 对象，从 request 中取值，从 response 中写值

## Catalina 架构

Catalina 由两个主要模块组成：

* 连接器 (Connector) - 接收 HTTP 请求，并构造 request 和 response 对象
* 容器 (Container) - 接收 request 和 response 对象，并调用 Servlet 的 `service()` 函数

### 连接器

一个符合 Servlet 2.3 和 2.4 规范的连接器需要创建 `javax.servlet.http.HttpServletRequest` 和 `javax.servlet.http.HttpServletResponse`，并传递给被调用的 `service()` 函数。

连接器是一个可以插入 Servlet 容器的独立模块。一个 Tomcat 连接器必须符合以下条件：

1. 实现接口 `org.apache.catalina.Connector`
2. 创建请求对象，请求对象实现 `org.apache.catalina.Request`
3. 创建响应对象，响应对象实现 `org.apache.catalina.Response`

Tomcat 4 的默认连接器等待 HTTP 请求后，创建 `request` 和 `response` 对象，然后调用容器 (`org.apache.catalina.Container`) 的 `invoke()` 函数来传递这两个对象：

```java
public void invoke(org.apache.catalina.Request request, org.apache.catalina.Response response);
```

连接器必须实现 `org.apache.catalina.Connector` 接口，包含以下重要函数：

* `setContainer()` - 关联连接器和容器
* `getContainer()`
* `createRequest()`
* `createResponse()`

默认连接器运行在一个独立的线程中，且连接器拥有一个处理对象池，从而避免每次重复创建处理对象。每个处理对象也运行在一个独立的线程中，因此实际上每个连接器对应了一个线程池。

### 容器

容器需要实现 `org.apache.catalina.Container` 接口。容器被分为四种类型 (四个接口)，每种容器都有一个默认的标准实现：

* Engine - 整个 Catalina Servlet 引擎
* Host - 包含数个 Context 的虚拟主机
* Context - 一个 Web 应用，包括一个或多个 Wrapper
* Wrapper - 一个独立的 Servlet

一个容器可以有一个或多个更低层次的子容器，Wrapper 是层次最低的子容器类型。每一个容器内部会有一个 **流水线任务** 实例，流水线中包含了容器被唤醒后要处理的所有任务。每个流水线中包含了一个或多个 **阀门**，请求将依次通过阀门，每个阀门都可以操作传递给它的 `request` 和 `response` 实例。处理完毕后，流水线的 **基本阀门** 被调用，负责加载相关的 Servlet 类。

1. 一个容器有一个流水线实例，容器的 `invoke()` 会调用流水线的 `invoke()`
2. 流水线的 `invoke()` 会依次调用每个阀门的 `invoke()`，最终调用基本阀门的 `invoke()`
3. Wrapper 的基本阀门负责加载相关 Servlet 类；Context 的基本阀门复杂查找子容器，并调用子容器的 `invoke()`

## Servlet 接口

所有的 Servlet 必须实现该接口，或继承自实现该接口的类。

```java
/**
 * Defines methods that all servlets must implement.
 *
 * <p>A servlet is a small Java program that runs within a Web server.
 * Servlets receive and respond to requests from Web clients,
 * usually across HTTP, the HyperText Transfer Protocol. 
 *
 * <p>To implement this interface, you can write a generic servlet
 * that extends
 * <code>javax.servlet.GenericServlet</code> or an HTTP servlet that
 * extends <code>javax.servlet.http.HttpServlet</code>.
 *
 * <p>This interface defines methods to initialize a servlet,
 * to service requests, and to remove a servlet from the server.
 * These are known as life-cycle methods and are called in the
 * following sequence:
 * <ol>
 * <li>The servlet is constructed, then initialized with the <code>init</code> method.
 * <li>Any calls from clients to the <code>service</code> method are handled.
 * <li>The servlet is taken out of service, then destroyed with the 
 * <code>destroy</code> method, then garbage collected and finalized.
 * </ol>
 *
 * <p>In addition to the life-cycle methods, this interface
 * provides the <code>getServletConfig</code> method, which the servlet 
 * can use to get any startup information, and the <code>getServletInfo</code>
 * method, which allows the servlet to return basic information about itself,
 * such as author, version, and copyright.
 *
 * @author     Various
 *
 * @see     GenericServlet
 * @see     javax.servlet.http.HttpServlet
 *
 */
public interface Servlet {
    public void init(ServletConfig config) throws ServletException;
    public void service(ServletRequest req, ServletResponse res)
        throws ServletException, IOException;
    public void destroy();
    public String getServletInfo();
    public ServletConfig getServletConfig();
}
```

其中，以下三个函数是 Servlet 的生命周期函数：

* `init()` - 只在 Servlet 类被加载时调用一次，必须在 Servlet 可以接受任何请求之前运行完毕
* `service()` - 在生命周期中会被多次调用，由 Servlet 容器将 request 和 response 对象传递给该函数
* `destroy()` - 在 Servlet 容器移除 Servlet 实例时被调用一次 (比如容器关闭，或容器需要一些空闲内存)

## 一个简单的 Servlet 容器

Servlet 容器会为 Servlet 的每个 HTTP 请求做如下工作：

1. 第一次调用该 Servlet 时，加载该类并调用该类的 `init()` 函数 (仅一次)
2. 对每次请求，构造 `javax.servlet.ServletRequest` 和 `javax.servlet.ServletResponse` 实例
3. 调用 Servlet 的 `service()` 函数，并传递 `ServletRequest` 和 `ServletResponse` 实例
4. 当 Servlet 类被关闭时，调用 Servlet 的 `destroy()` 函数，卸载该类

可以基于最经典的 ServerSocket 程序，实现一个简单的 Servlet 容器。该容器能够根据路由区分 **静态资源** 的调用和 **Servlet** 的调用。对于 Servlet 的调用，通过 *类加载器* 加载 Servlet 类，实例化并调用 `service()` 函数。

### Request && Response

在最原始的 ServerSocket 程序中，每个请求可以通过 `accept()` 函数获得一个 `Socket`。通过这个 `Socket`，可以取得其输入流和输出流。基于输入流，可以构造出一个 Request，并从流中读取 HTTP 协议数据，并 parse 为相应的字段 set 倒 Request 对象的成员变量中，供 `service()` 函数使用；基于输出流，可以构造出一个 Response，并向客户端写回响应内容。

Request 需要继承自 `javax.Servlet.Request`，Response 需要继承自 `javax.Servlet.Response`。

### 静态资源与 Servlet 的路由

指定了一个路径作为静态资源的存放路径。在 parse 出请求的 URI 后，判断 URI 中的路径是否是静态资源路径。如果是，则在该路径下寻找静态资源并返回；否则，使用类加载器寻找 Servlet 类，加载并执行其生命周期函数。由于本章只是一个简单实现，每次 Servlet 被请求时，Servlet 类都会被加载。核心代码：

```java
socket = serverSocket.accept();
input = socket.getInputStream();
output = socket.getOutputStream();

Request request = new Request(input);
Response response = new Response(output);
response.setRequest(request);

request.parse();
if (request.getUri().startsWith("/servlet/")) {
    // Servlet
} else {
    // Static resources
}
```

其中，`parse()` 函数需要解析接收到的 HTTP 请求。HTTP 请求包含三部分：

* 请求行
* 请求头
* 请求体

为了提升性能，具体的实现可以根据需要，选择性地解析一些字段；其它字段可以推迟到需要使用时再解析。

### Servlet 加载

假设 HTTP 请求中通过如下方式调用 Servlet：

```http
GET /servlet/servletName
```

其中，`servletName` 是 Servlet 的类名。在 Servlet 容器中，类加载器可以找到 Servlet 类的地方称为 *资源库 (repository)*，因此需要指定一个资源库路径。这里，使用 `java.net.URLClassLoader` 类加载器，它接收一个 `URL` 对象数组。核心代码：

```java
String uri = request.getUri();
String servletName = uri.substring(uri.lastIndexOf("/") + 1);
URLClassLoader loader = null;

try {
    URL[] urls = new URL[1]; // one URL for Servlet only
    URLStreamHandler streamHandler = null;
    String repo = (new URL(
        			"file",
        			null, 
                     new File("WEB_ROOT").getCanonicalPath() + File.saparator)
                  ).toString();
    urls[0] = new URL(null, repo, streamHandler);
    loader = new URLClassLoader(urls);
} catch (IOException e) {
    // ...
}

Class myClass = null;
try {
    myClass = loader.loadClass(servletName);
} catch (ClassNotFoundException e) {
    // ...
}

Servlet servlet = null;
try {
    servlet = (Servlet) myClass.newInstance();
    servlet.service((ServletRequest) request, (ServletResponse) response);
} catch (Exception e) {
    // ...
} catch (Throable e) {
    // ...
}
```

可以看到，这里通过类加载器获得了 Servlet 类的 Class 对象，然后通过反射机制实例化了一个 Servlet 实例，并调用其 `service()` 函数。

### 增强安全性

上述程序的最后有一点不安全的地方。假设我是一个 Servlet 程序员，可以自行实现 Servlet 中的逻辑。如果我知道 Servlet 容器中的实现是上述的代码，那么我就可以在 `service()` 函数中将 `request` 强制转换为我自己的 `Request` 类，并调用该类中的公共函数。从容器的角度来看，不允许发生这种事情。一种优雅的解决方式：

```java
public class RequestFacade implements ServletRequest {
    private ServletRequest request = null;
    
    public RequestFacade(Request request) {
        this.request = request;
    }
    
    // 实现 ServletRequest 接口的所有函数
    // 直接调用传入的 request 的实现函数
    public Object getAttribute(String attribute) {
        return request.getAttribute();
    }
}
```

这样，相当于将自定义的 Request 类封装到了 `RequestFacade` 类的私有域中，该类只暴露 ServletRequest 类中允许被调用的公共函数，其它公共函数被屏蔽。

```java
RequestFacade requestFacade = new RequestFacade(request);
ResponseFacade responseFacade = new ResponseFacade(response);
try {
    servlet = (Servlet) myClass.newInstance();
    servlet.service((ServletRequest) requestFacade, (ServletResponse) responseFacade);
}
```

## 标准容器实现

### StandardWrapper

主要职责：加载其表示的 Servlet (Class) 并建立一个实例。`StandardWrapper` 容器流水线中的基本阀门 `StandardWrapperValve` 负责调用 `StandarWrapper` 的 `allocate()` 获得 Servlet 实例，然后调用 Servlet 实例的 `service()` 函数。

其中重要的区别在于，Servlet 是否实现了 `SingleThreadModel` 接口。实现该接口的目的在于保证一个 Servlet 实例的 `service()` 函数不会被两个线程同时调用。那么，为了提高 Servlet 容器的响应性能，通常会为实现 STM 的 Servlet 类创建多个实例，这样同时可以有多个线程分别调用每个实例的 `service()`。

由此，如果 Servlet 容器发现请求的 Servlet 没有实现 STM 接口，那么容器只加载并实例化该容器一次，对于之后的每次请求，返回同一个实例即可 (容器假定 `service()` 线程安全)，并调用 `service()` 函数；对于实现了 STM 接口的 Servlet 请求，容器需要从 **实例池** 中取出一个没有被使用的 Servlet 实例，再调用其 `service()` 函数。

可以看到，在类成员变量定义中，分别定义了可以被重复使用的 `instance` 实例，以及 `Stack` 实现的实例池：

```java
/**
 * Standard implementation of the <b>Wrapper</b> interface that represents
 * an individual servlet definition.  No child Containers are allowed, and
 * the parent Container must be a Context.
 *
 * @author Craig R. McClanahan
 * @author Remy Maucherat
 * @version $Id: StandardWrapper.java 939525 2010-04-30 00:36:35Z kkolinko $
 */
public class StandardWrapper
    extends ContainerBase
    implements ServletConfig, Wrapper, NotificationEmitter {
 
    // ...
    
    /**
     * The (single) initialized instance of this servlet.
     */
    private Servlet instance = null;
    
    /**
     * Stack containing the STM instances.
     */
    private Stack instancePool = null;
    
    // ...
}
```

其中，类内部的 `allocate()` 根据 Servlet 是否实现了 STM 来决定如何对上述两个变量进行赋值：

* 要么将 `instance` 赋值为一个 Servlet 实例
* 要么将 `instancePool` 初始化并放入实例

```java
/**
 * Allocate an initialized instance of this Servlet that is ready to have
 * its <code>service()</code> method called.  If the servlet class does
 * not implement <code>SingleThreadModel</code>, the (only) initialized
 * instance may be returned immediately.  If the servlet class implements
 * <code>SingleThreadModel</code>, the Wrapper implementation must ensure
 * that this instance is not allocated again until it is deallocated by a
 * call to <code>deallocate()</code>.
 *
 * @exception ServletException if the servlet init() method threw
 *  an exception
 * @exception ServletException if a loading error occurs
 */
public Servlet allocate() throws ServletException {

    // If we are currently unloading this servlet, throw an exception
    if (unloading)
        throw new ServletException
        (sm.getString("standardWrapper.unloading", getName()));

    // If not SingleThreadedModel, return the same instance every time
    if (!singleThreadModel) {

        // Load and initialize our instance if necessary
        if (instance == null) {
            synchronized (this) {
                if (instance == null) {
                    try {
                        if (log.isDebugEnabled())
                            log.debug("Allocating non-STM instance");

                        instance = loadServlet();
                    } catch (ServletException e) {
                        throw e;
                    } catch (Throwable e) {
                        throw new ServletException
                            (sm.getString("standardWrapper.allocate"), e);
                    }
                }
            }
        }

        if (!singleThreadModel) {
            if (log.isTraceEnabled())
                log.trace("  Returning non-STM instance");
            countAllocated++;
            return (instance);
        }

    }

    synchronized (instancePool) {

        while (countAllocated >= nInstances) {
            // Allocate a new instance if possible, or else wait
            if (nInstances < maxInstances) {
                try {
                    instancePool.push(loadServlet());
                    nInstances++;
                } catch (ServletException e) {
                    throw e;
                } catch (Throwable e) {
                    throw new ServletException
                        (sm.getString("standardWrapper.allocate"), e);
                }
            } else {
                try {
                    instancePool.wait();
                } catch (InterruptedException e) {
                    ;
                }
            }
        }
        if (log.isTraceEnabled())
            log.trace("  Returning allocated STM instance");
        countAllocated++;
        return (Servlet) instancePool.pop();

    }

}
```

两种赋值方式都会用到真正获取到 Servlet 实例的 `loadServlet()`，加载实例后，还会调用 Servlet 实例的 `init()` 函数：

```java
/**
 * Load and initialize an instance of this servlet, if there is not already
 * at least one initialized instance.  This can be used, for example, to
 * load servlets that are marked in the deployment descriptor to be loaded
 * at server startup time.
 */
public synchronized Servlet loadServlet() throws ServletException {

    // Nothing to do if we already have an instance or an instance pool
    if (!singleThreadModel && (instance != null))
        return instance;

    PrintStream out = System.out;
    if (swallowOutput) {
        SystemLogHandler.startCapture();
    }

    Servlet servlet;
    try {
        // ...

        // Instantiate and initialize an instance of the servlet class itself
        try {
            servlet = (Servlet) classClass.newInstance();
        } catch (ClassCastException e) {
            unavailable(null);
            // Restore the context ClassLoader
            throw new ServletException
                (sm.getString("standardWrapper.notServlet", actualClass), e);
        } catch (Throwable e) {
            unavailable(null);

            // Added extra log statement for Bugzilla 36630:
            // http://issues.apache.org/bugzilla/show_bug.cgi?id=36630
            if(log.isDebugEnabled()) {
                log.debug(sm.getString("standardWrapper.instantiate", actualClass), e);
            }

            // Restore the context ClassLoader
            throw new ServletException
                (sm.getString("standardWrapper.instantiate", actualClass), e);
        }

        // Check if loading the servlet in this web application should be
        // allowed
        if (!isServletAllowed(servlet)) {
            throw new SecurityException
                (sm.getString("standardWrapper.privilegedServlet",
                              actualClass));
        }

        // Special handling for ContainerServlet instances
        if ((servlet instanceof ContainerServlet) &&
            (isContainerProvidedServlet(actualClass) ||
             ((Context)getParent()).getPrivileged() )) {
            ((ContainerServlet) servlet).setWrapper(this);
        }

        classLoadTime=(int) (System.currentTimeMillis() -t1);
        // Call the initialization method of this servlet
        try {
            instanceSupport.fireInstanceEvent(InstanceEvent.BEFORE_INIT_EVENT,
                                              servlet);

            if( System.getSecurityManager() != null) {

                Object[] args = new Object[]{((ServletConfig)facade)};
                SecurityUtil.doAsPrivilege("init",
                                           servlet,
                                           classType,
                                           args);
                args = null;
            } else {
                servlet.init(facade);
            }

            // Invoke jspInit on JSP pages
            if ((loadOnStartup >= 0) && (jspFile != null)) {
                // Invoking jspInit
                DummyRequest req = new DummyRequest();
                req.setServletPath(jspFile);
                req.setQueryString("jsp_precompile=true");
                DummyResponse res = new DummyResponse();

                if( System.getSecurityManager() != null) {
                    Object[] args = new Object[]{req, res};
                    SecurityUtil.doAsPrivilege("service",
                                               servlet,
                                               classTypeUsedInService,
                                               args);
                    args = null;
                } else {
                    servlet.service(req, res);
                }
            }
            instanceSupport.fireInstanceEvent(InstanceEvent.AFTER_INIT_EVENT,
                                              servlet);
        } catch (UnavailableException f) {
            instanceSupport.fireInstanceEvent(InstanceEvent.AFTER_INIT_EVENT,
                                              servlet, f);
            unavailable(f);
            throw f;
        } catch (ServletException f) {
            instanceSupport.fireInstanceEvent(InstanceEvent.AFTER_INIT_EVENT,
                                              servlet, f);
            // If the servlet wanted to be unavailable it would have
            // said so, so do not call unavailable(null).
            throw f;
        } catch (Throwable f) {
            getServletContext().log("StandardWrapper.Throwable", f );
            instanceSupport.fireInstanceEvent(InstanceEvent.AFTER_INIT_EVENT,
                                              servlet, f);
            // If the servlet wanted to be unavailable it would have
            // said so, so do not call unavailable(null).
            throw new ServletException
                (sm.getString("standardWrapper.initException", getName()), f);
        }

        // Register our newly initialized instance
        singleThreadModel = servlet instanceof SingleThreadModel;
        if (singleThreadModel) {
            if (instancePool == null)
                instancePool = new Stack();
        }
        fireContainerEvent("load", this);

        loadTime=System.currentTimeMillis() -t1;
    } finally {
        if (swallowOutput) {
            String log = SystemLogHandler.stopCapture();
            if (log != null && log.length() > 0) {
                if (getServletContext() != null) {
                    getServletContext().log(log);
                } else {
                    out.println(log);
                }
            }
        }
    }
    return servlet;

}
```

### StandardContext

一个上下文容器代表一个 Web 应用，包含一个或多个 wrapper，每个 wrapper 代表一个 Servlet。上下文容器内部维护了请求 URI 与每个 wrapper (即每个 Servlet) 的映射。对于每个请求，上下文容器内流水线的基本阀门 `StandardContextValve` 会查找容器内维护的所有 wrapper，并选择一个与要处理的请求匹配的 wrapper，调用其 `invoke()` 函数。

---

