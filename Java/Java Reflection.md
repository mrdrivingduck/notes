# Java - Reflection Mechanism

Created by : Mr Dk.

2018 / 09 / 22 21:15

Nanjing, Jiangsu, China

---

## About

_Reflection - 反射_
* 通过 _.class_ 文件动态加载类
* 不用通过类对象，就能获取类的所有信息
  * _Field_、_Method_、_Constructor_ 等
* 不用通过类对象，就能调用类的函数
* 在运行时判断任意一个对象所属的类

---

## Procedure

1. 获取 _Class_ 对象
2. 利用 _Class_ 对象获取类的信息（_Field_、_Method_、_Constructor_）
3. 使用构造函数实例化对象 - 访问属性 - 调用函数

---

## 类装载过程

* 加载某个类的 _.class_ 文件
* _JVM_ 在磁盘上寻找对应的 _.class_ 文件，并载入 _JVM_ 内存
* _JVM_ 自动创建一个 _Class_ 对象
  * 一个类只产生一个 _Class_ 对象
  * _Class_ 对象中存储与类有关的各种信息

---

## 获取 _Class_ 对象

```java
class Base {
    
    // Fields
    private int a;
    private String b;
    
    // Getters & Setters for fields
    public void setA(int a) {
        this.a = a;
    }
    public int getA() {
        return a;
    }
    public void setB(String b) {
        this.b = b;
    }
    public String getB() {
        return b;
    }
    
    // Constructors
    public Base() {}
    public Base(int a) {this.a = a;}
    public Base(String b) {this.b = b;}
    public Base(int a, String b) {
        this.a = a;
        this.b = b;
    }
    
    // Methods
    public void Print(String msg) {
        System.out.println(msg);
    }
}
```

```java
/**
 * 通过类获得 Class 对象
 */
Class clazz = Base.class;

/**
 * 通过类对象获得 Class 对象
 */
Base base = new Base();
Class clazz = base.getClass();

/**
 * 通过类全名（字符串）获得 Class 对象 - 最常用
 */
Class clazz = Class.forName("package.Base");
```

---

## 获取类信息

* 只能获取到当前类的信息，不能获取到父类的信息

* 获取 _Constructors_

  ```java
  /**
   * 获取所有的 public Constructor
   */
  Constructor[] constructors = clazz.getConstructors();
  
  /**
   * 获取所有的 Constructor （包括 private、protected）
   */
  Constructor[] constructors = clazz.getConstructors();
  
  /**
   * 获取某个特定的 public Constructor
   * 参数为对应的 Class 对象
   */
  Constructor constructor = clazz.getConstructor(int.class, String.class);
  
  /**
   * 获取某个特定的 Constructor
   * 参数为对应的 Class 对象
   */
  Constructor constructor = clazz.getDeclaredConstructor(int.class, String.class);
  ```

* 获取 _fields_

  ```java
  /**
   * 获取所有 field
   */
  Field[] fields = clazz.getDeclaredFields();
  
  /**
   * 获取所有的 public field
   */
  Field[] fields = clazz.getFields();
  
  /**
   * 获取某个特定 field
   */
  Field field = clazz.getDeclaredField("a");
  
  /**
   * 获取某个特定的 public field
   */
  Field field = clazz.getField("a");
  ```

* 获取 _Methods_

  ```java
  /**
   * 获取所有的 public method
   */
  Method[] methods = clazz.getMethods();
  
  /**
   * 获取所有的 method
   */
  Method[] methods = clazz.getDeclaredMethods();
  
  /**
   * 获取某个特定的 public method
   * 第一个参数为函数名，之后的参数为对应的参数列表的 class 对象
   */
  Method method = clazz.getMethod("Print", String.class);
  
  /**
   * 获取某个特定的 method
   * 第一个参数为函数名，之后的参数为对应的参数列表的 class 对象“
   */
  Method method = clazz.getDeclaredMethod("Print", String.class);
  ```

---

## 对类的一些操作

* 实例化

  ```java
  /**
   * 返回类型为 Object
   * 调用无参数的 Constructor（必须定义并实现！！！）
   */
  Object obj = clazz.newInstance();
  
  /**
   * 返回类型为 Object
   * 可以指定使用不同的构造函数
   */
  Constructor constructor = clazz.getConstructor(int.class, String.class);
  Object obj = constructor.newInstance(50, "Mr Dk.");
  ```

* 访问属性

  ```java
  Field field = clazz.getDeclaredField("a");
  field.setAccessible(true);    // 用于访问 private 变量，但不建议使用
  int a = field.getInt(obj);
  ```

* 获取父类属性

  ```java
  for (; !clazz.equals(Object.class); clazz = clazz.getSuperclass()) {
      // ...
      Field[] allFields = clazz.getDeclaredFields();
      // ...
  }
  ```

* 调用函数

  ```java
  Method method = clazz.getDeclaredMethod("Print", String.class);
  method.invoke(obj, "HelloWorld");
  ```

---

## Pros

应用在那些需要 __在运行时检测或修改程序行为__ 的程序中

---

## Cons

* 反射的效率比非反射低得多
  * 避免在经常执行的代码中使用
  * 避免在对性能要求较高的代码中使用
* 使用反射要求程序必须在一个没有安全限制的环境内运行
* 内部暴露
  * 反射允许一些正常情况下不被允许的操作
    * 访问 _private_ 属性
    * 访问 _private_ 函数
  * 反射可能导致一些副作用
    * 代码功能上的错误
    * 降低可移植性
    * 破坏代码的抽象性
    * 不同运行平台上的行为差异

---

