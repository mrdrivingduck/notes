# Tomcat - Class Loader

Created by : Mr Dk.

2020 / 11 / 30 22:10

Nanjing, Jiangsu, China

---

## Servlet 加载器

Tomcat 中的 *标准网络应用加载器 (Standard Web Application Loader)* 用于加载 Servlet 类。Tomcat 需要实现自己的类加载器的原因在于，Servlet 只被允许访问：

* `WEB-INF/` 目录及其子目录下的类
* `WEB-INF/lib` 目录下的类库

从而使得 Tomcat 的类加载器能够 **遵守特定的规则** 来加载类。而使用系统加载器，Servlet 就可以访问 JVM `CLASSPATH` 环境下的任何类和类库，从而带来安全隐患。

另外，Tomcat 的类加载器还需要支持在 `WEB-INF/classes` 或 `WEB-INF/lib` 目录下的文件被修改的时候，自动重新加载类，而不需要重启 Tomcat。在具体实现上，Tomcat 使用一个单独的线程检查类文件的时间戳。总结来说，Tomcat 需要扩展 Java 的类加载器来实现自己的类加载器，原因在于：

1. 需要定义特定的类加载规则
2. 缓存已经加载的类
3. 实现加载类以预备使用

## Java 类加载器

在创建 Java 类实例时，JVM 将会使用类加载器到 Java 核心类库和 `CLASSPATH` 环境变量中查找类；如果需要的类没有找到，那么则会抛出 `java.lang.ClassNotFoundException`。JVM 使用的类加载器包含：

* Bootstrap 类加载器 - 引导 JVM，由 native code 实现，负责加载所有 Java 核心类
* Extension 类加载器 - 负责加载标准扩展目录下的类
* System 类加载器 - 默认加载器，在 `CLASSPATH` 环境变量下查找类

JVM 出于安全原因使用 **委派模型** 来选择加载器。首先 system 类加载器被调用，它会首先向父加载器 extension 委派加载任务，当父加载器无法加载时，再自行尝试加载；extension 类加载器首先也会将加载任务委派给 bootstrap 加载器。因此，bootstrap 总是最先加载类，从而防止 Java 核心类被其它的同名类恶意覆盖。

## Loader 接口

Tomcat 网络应用加载器必须实现的接口。通常一个这样的加载器都是和一个上下文 (容器) 相关联。

```java
/**
 * A <b>Loader</b> represents a Java ClassLoader implementation that can
 * be used by a Container to load class files (within a repository associated
 * with the Loader) that are designed to be reloaded upon request, as well as
 * a mechanism to detect whether changes have occurred in the underlying
 * repository.
 * <p>
 * In order for a <code>Loader</code> implementation to successfully operate
 * with a <code>Context</code> implementation that implements reloading, it
 * must obey the following constraints:
 * <ul>
 * <li>Must implement <code>Lifecycle</code> so that the Context can indicate
 *     that a new class loader is required.
 * <li>The <code>start()</code> method must unconditionally create a new
 *     <code>ClassLoader</code> implementation.
 * <li>The <code>stop()</code> method must throw away its reference to the
 *     <code>ClassLoader</code> previously utilized, so that the class loader,
 *     all classes loaded by it, and all objects of those classes, can be
 *     garbage collected.
 * <li>Must allow a call to <code>stop()</code> to be followed by a call to
 *     <code>start()</code> on the same <code>Loader</code> instance.
 * <li>Based on a policy chosen by the implementation, must call the
 *     <code>Context.reload()</code> method on the owning <code>Context</code>
 *     when a change to one or more of the class files loaded by this class
 *     loader is detected.
 * </ul>
 *
 * @author Craig R. McClanahan
 * @version $Id: Loader.java 939531 2010-04-30 00:54:41Z kkolinko $
 */

public interface Loader {


    // ------------------------------------------------------------- Properties


    /**
     * Execute a periodic task, such as reloading, etc. This method will be
     * invoked inside the classloading context of this container. Unexpected
     * throwables will be caught and logged.
     */
    public void backgroundProcess();


    /**
     * Return the Java class loader to be used by this Container.
     */
    public ClassLoader getClassLoader();


    /**
     * Return the Container with which this Loader has been associated.
     */
    public Container getContainer();


    /**
     * Set the Container with which this Loader has been associated.
     *
     * @param container The associated Container
     */
    public void setContainer(Container container);


    /**
     * Return the "follow standard delegation model" flag used to configure
     * our ClassLoader.
     */
    public boolean getDelegate();


    /**
     * Set the "follow standard delegation model" flag used to configure
     * our ClassLoader.
     *
     * @param delegate The new flag
     */
    public void setDelegate(boolean delegate);


    /**
     * Return descriptive information about this Loader implementation and
     * the corresponding version number, in the format
     * <code>&lt;description&gt;/&lt;version&gt;</code>.
     */
    public String getInfo();


    /**
     * Return the reloadable flag for this Loader.
     */
    public boolean getReloadable();


    /**
     * Set the reloadable flag for this Loader.
     *
     * @param reloadable The new reloadable flag
     */
    public void setReloadable(boolean reloadable);


    // --------------------------------------------------------- Public Methods


    /**
     * Add a property change listener to this component.
     *
     * @param listener The listener to add
     */
    public void addPropertyChangeListener(PropertyChangeListener listener);


    /**
     * Add a new repository to the set of repositories for this class loader.
     *
     * @param repository Repository to be added
     */
    public void addRepository(String repository);


    /**
     * Return the set of repositories defined for this class loader.
     * If none are defined, a zero-length array is returned.
     */
    public String[] findRepositories();


    /**
     * Has the internal repository associated with this Loader been modified,
     * such that the loaded classes should be reloaded?
     */
    public boolean modified();


    /**
     * Remove a property change listener from this component.
     *
     * @param listener The listener to remove
     */
    public void removePropertyChangeListener(PropertyChangeListener listener);


}
```

Tomcat 提供了 `WebappLoader` 作为 Loader 接口的实现。该类实现了 `Lifecycle` 接口，所以可以由相关联的容器来进行启动或停止。在启动时，它需要完成如下工作：

1. 创建对象内部维护的真正的类加载器 `WebappClassLoader` (如果想要创建自己的，那么也要继承 `WebappClassLoader`)
2. 设置类加载器的类库 (`WEB-INF/classes` 目录会被传递给 `addRepository()`)
3. 设置类路径
4. 设置访问权限 (如果启动安全管理器，就给必要的目录增加访问权限)
5. 开启自动重加载线程，并定时调用内部维护的类加载器的 `modified()` 函数以判断是否需要重加载

```java
/**
 * Classloader implementation which is specialized for handling web
 * applications in the most efficient way, while being Catalina aware (all
 * accesses to resources are made through the DirContext interface).
 * This class loader supports detection of modified
 * Java classes, which can be used to implement auto-reload support.
 * <p>
 * This class loader is configured by adding the pathnames of directories,
 * JAR files, and ZIP files with the <code>addRepository()</code> method,
 * prior to calling <code>start()</code>.  When a new class is required,
 * these repositories will be consulted first to locate the class.  If it
 * is not present, the system class loader will be used instead.
 *
 * @author Craig R. McClanahan
 * @author Remy Maucherat
 * @version $Id: WebappLoader.java 939527 2010-04-30 00:43:48Z kkolinko $
 */

public class WebappLoader
    implements Lifecycle, Loader, PropertyChangeListener, MBeanRegistration  {
    
    // ...
    
    /**
     * The class loader being managed by this Loader component.
     */
    private WebappClassLoader classLoader = null;
    
    // ...
}
```

类内维护了一个 `WebappClassLoader` 对象，该类继承自 Java 的 `URLClassLoader`，并扩展了一些功能，比如缓存了以前加载的类以改进性能。

```java
/**
 * Specialized web application class loader.
 * <p>
 * This class loader is a full reimplementation of the 
 * <code>URLClassLoader</code> from the JDK. It is designed to be fully
 * compatible with a normal <code>URLClassLoader</code>, although its internal
 * behavior may be completely different.
 * <p>
 * <strong>IMPLEMENTATION NOTE</strong> - This class loader faithfully follows 
 * the delegation model recommended in the specification. The system class 
 * loader will be queried first, then the local repositories, and only then 
 * delegation to the parent class loader will occur. This allows the web 
 * application to override any shared class except the classes from J2SE.
 * Special handling is provided from the JAXP XML parser interfaces, the JNDI
 * interfaces, and the classes from the servlet API, which are never loaded 
 * from the webapp repository.
 * <p>
 * <strong>IMPLEMENTATION NOTE</strong> - Due to limitations in Jasper 
 * compilation technology, any repository which contains classes from 
 * the servlet API will be ignored by the class loader.
 * <p>
 * <strong>IMPLEMENTATION NOTE</strong> - The class loader generates source
 * URLs which include the full JAR URL when a class is loaded from a JAR file,
 * which allows setting security permission at the class level, even when a
 * class is contained inside a JAR.
 * <p>
 * <strong>IMPLEMENTATION NOTE</strong> - Local repositories are searched in
 * the order they are added via the initial constructor and/or any subsequent
 * calls to <code>addRepository()</code> or <code>addJar()</code>.
 * <p>
 * <strong>IMPLEMENTATION NOTE</strong> - No check for sealing violations or
 * security is made unless a security manager is present.
 *
 * @author Remy Maucherat
 * @author Craig R. McClanahan
 * @version $Id: WebappClassLoader.java 992240 2010-09-03 09:00:10Z rjung $
 */
public class WebappClassLoader
    extends URLClassLoader
    implements Reloader, Lifecycle
 {
    // ...
    
    /**
     * The cache of ResourceEntry for classes and resources we have loaded,
     * keyed by resource name.
     */
    protected HashMap resourceEntries = new HashMap();
    
    /**
     * The list of not found resources.
     */
    protected HashMap notFoundResources = new LinkedHashMap() {
        private static final long serialVersionUID = 1L;
        protected boolean removeEldestEntry(
                Map.Entry eldest) {
            return size() > 1000;
        }
    };
    
    // ...
}
```

每个被加载过的类会被缓存在类加载器的 `resourceEntries` 中，没有被找到的类全部会被存放在 `notFoundResources` 中。类加载器首先在缓存中寻找类；如果找不到，再使用系统的类加载器来加载类；如果还找不到，则从当前的源中加载类；如果还没有，则抛出 `ClassNotFoundException` 异常。

```java
/**
 * Resource entry.
 *
 * @author Remy Maucherat
 * @version $Id: ResourceEntry.java 939527 2010-04-30 00:43:48Z kkolinko $
 */
public class ResourceEntry {


    /**
     * The "last modified" time of the origin file at the time this class
     * was loaded, in milliseconds since the epoch.
     */
    public long lastModified = -1;


    /**
     * Binary content of the resource.
     */
    public byte[] binaryContent = null;


    /**
     * Loaded class.
     */
    public volatile Class loadedClass = null;


    /**
     * URL source from where the object was loaded.
     */
    public URL source = null;


    /**
     * URL of the codebase from where the object was loaded.
     */
    public URL codeBase = null;


    /**
     * Manifest (if the resource was loaded from a JAR).
     */
    public Manifest manifest = null;


    /**
     * Certificates (if the resource was loaded from a JAR).
     */
    public Certificate[] certificates = null;


}
```

## Reloader 接口

如果加载器想要支持自动重新加载，就需要实现 `Reloader` 接口。其中，当 Servlet 的任何支持类被修改的时候，`modified()` 函数需要返回 `true`。

```java
public interface Reloader {


    /**
     * Add a new repository to the set of places this ClassLoader can look for
     * classes to be loaded.
     *
     * @param repository Name of a source of classes to be loaded, such as a
     *  directory pathname, a JAR file pathname, or a ZIP file pathname
     *
     * @exception IllegalArgumentException if the specified repository is
     *  invalid or does not exist
     */
    public void addRepository(String repository);


    /**
     * Return a String array of the current repositories for this class
     * loader.  If there are no repositories, a zero-length array is
     * returned.
     */
    public String[] findRepositories();


    /**
     * Have one or more classes or resources been modified so that a reload
     * is appropriate?
     */
    public boolean modified();


}
```

`WebappLoader` 中会启用一个后台线程来判断与它通过 `setContainer()` 相关联的上下文容器是否需要重新加载：

```java
/**
 * Has the internal repository associated with this Loader been modified,
 * such that the loaded classes should be reloaded?
 */
public boolean modified() {
    return (classLoader.modified()); // WebappClassLoader::modified
}

/**
 * Execute a periodic task, such as reloading, etc. This method will be
 * invoked inside the classloading context of this container. Unexpected
 * throwables will be caught and logged.
 */
public void backgroundProcess() {
    if (reloadable && modified()) { // modified !!!
        try {
            Thread.currentThread().setContextClassLoader
                (WebappLoader.class.getClassLoader());
            if (container instanceof StandardContext) {
                ((StandardContext) container).reload(); // reload
            }
        } finally {
            if (container.getLoader() != null) {
                Thread.currentThread().setContextClassLoader
                    (container.getLoader().getClassLoader());
            }
        }
    } else {
        closeJARs(false);
    }
}
```

在与 Tomcat 加载器关联的标准上下文容器中，实现了具体的 `reload()` 函数：

```java
/**
 * Reload this web application, if reloading is supported.
 * <p>
 * <b>IMPLEMENTATION NOTE</b>:  This method is designed to deal with
 * reloads required by changes to classes in the underlying repositories
 * of our class loader.  It does not handle changes to the web application
 * deployment descriptor.  If that has occurred, you should stop this
 * Context and create (and start) a new Context instance instead.
 *
 * @exception IllegalStateException if the <code>reloadable</code>
 *  property is set to <code>false</code>.
 */
public synchronized void reload() {

    // Validate our current component state
    if (!started)
        throw new IllegalStateException
        (sm.getString("containerBase.notStarted", logName()));

    // Make sure reloading is enabled
    //      if (!reloadable)
    //          throw new IllegalStateException
    //              (sm.getString("standardContext.notReloadable"));
    if(log.isInfoEnabled())
        log.info(sm.getString("standardContext.reloadingStarted"));

    // Stop accepting requests temporarily
    setPaused(true);

    try {
        stop();
    } catch (LifecycleException e) {
        log.error(sm.getString("standardContext.stoppingContext"), e);
    }

    try {
        start();
    } catch (LifecycleException e) {
        log.error(sm.getString("standardContext.startingContext"), e);
    }

    setPaused(false);

}
```

其中的 `stop()` 会将容器原先关联的加载器对象解除关联，`start()` 函数会给容器重新实例化一个加载器，从而抛弃了原加载器 (及其缓存的 Servlet Class 对象？)

> 感觉有些粗暴，不知道是不是我理解有偏差...

```java
/**
 * Stop this Context component.
 *
 * @exception LifecycleException if a shutdown error occurs
 */
public synchronized void stop() throws LifecycleException {
    // ...
    
    // Binding thread
    ClassLoader oldCCL = bindThread();

    try {
        // Stop our child containers, if any

    } finally {

        // Unbinding thread
        unbindThread(oldCCL);

    }
    
    // ...
}

/**
 * Bind current thread, both for CL purposes and for JNDI ENC support
 * during : startup, shutdown and realoading of the context.
 *
 * @return the previous context class loader
 */
private ClassLoader bindThread() {

    ClassLoader oldContextClassLoader =
        Thread.currentThread().getContextClassLoader();

    if (getResources() == null)
        return oldContextClassLoader;

    if (getLoader().getClassLoader() != null) {
        Thread.currentThread().setContextClassLoader
            (getLoader().getClassLoader());
    }

    DirContextURLStreamHandler.bind(getResources());

    if (isUseNaming()) {
        try {
            ContextBindings.bindThread(this, this);
        } catch (NamingException e) {
            // Silent catch, as this is a normal case during the early
            // startup stages
        }
    }

    return oldContextClassLoader;

}

/**
 * Unbind thread.
 */
private void unbindThread(ClassLoader oldContextClassLoader) {

    Thread.currentThread().setContextClassLoader(oldContextClassLoader);

    oldContextClassLoader = null;

    if (isUseNaming()) {
        ContextBindings.unbindThread(this, this);
    }

    DirContextURLStreamHandler.unbind();

}
```

```java
/**
 * Start this Context component.
 *
 * @exception LifecycleException if a startup error occurs
 */
public synchronized void start() throws LifecycleException {
    // ...

    if (getLoader() == null) {
        WebappLoader webappLoader = new WebappLoader(getParentClassLoader());
        webappLoader.setDelegate(getDelegate());
        setLoader(webappLoader);
    }

    // ...
}
```

---

