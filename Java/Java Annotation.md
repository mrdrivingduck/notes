# Java - Annotation 注解

Created by : Mr Dk.

2018 / 10 / 13 14:43

Nanjing, Jiangsu, China

---

### 1. About

__Annotation（注解）__ 是 _Java_ 提供的为程序中的元素关联 _元数据 （metadata）_ 的一种方法，在 _JDK 5.0_ 及以后被支持。程序可利用 __反射机制__ 来访问注解，并根据不同的注解，完成不同的功能。注解可以标记在 __包、类、成员变量、成员方法、方法参数以及局部变量__ 上。注解能够使代码更加精简、灵活。

* 元数据
  * __“描述数据的数据“__
  * 以标签的形式存在于 _Java_ 代码中
  * 不影响代码的编译和执行
  * 作用大致包括
    * 编写文档 - 通过代码中的标签生成 _Javadoc_
    * 代码分析
    * 编译检查

### 2. Type

* _Java_ 内置注解
  * `@Override` - 添加在重写父类的方法上，可用于检测重写的函数名是否与父类一致
  * `@Deprecated ` - 修饰已过时不再推荐使用的方法
  * `@SuppressWarnings` - 关闭编译器警告
* 元注解
  * `@Target` - 表示注解修饰的元素类型，可选参数如下：
    * `ElementType.CONSTRUCTOR` - 用于 _Constructor_ 的声明
    * `ElementType.PACKAGE` - 用于包声明
    * `ElementType.TYPE` - 用于类或接口的声明
    * `ElementType.FIELD` - 用于域声明
    * `ElementType.METHOD` - 用于方法声明
    * `ElementType.PARAMETER` - 用于参数声明
    * `ElementType.LOCAL_VARIABLE` - 用于局部变量声明
  * `@Retention` - 表示保存该注解信息的级别，可选参数如下：
    * `RetentionPolicy.SOURCE`  - 保存在源码中，编译时被编译器丢弃
    * `RetentionPolicy.CLASS` - 保存在字节码文件中，但被 _JVM_ 丢弃
    * `RetentionPolicy.RUNTIME` - 保留在 _JVM_ 运行期间（__因此可通过 Reflection 读取注解信息__）
  * `@Document` - 注解包含在 _Javadoc_ 中
  * `@Inherited` - 允许子类继承父类的注解
* 自定义注解
  * 一种可能的设计模式：注解 + 注解解释器
    * __注解__ - 使被标记元素之间的差异性独立于代码层之上。必要时，只需修改注解而不需修改代码
    * __注解解释器__ - 利用反射机制拿到注解信息，并根据不同的注解，完成对应的功能

### 3. Declaration

* Attention : Annotation can be declared __public__ only in its own file

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@interface MethodAnnotation {
    String value() default "METHOD";
}

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@interface TypeAnnotation {
    String value() default "TYPE";
}

/*

public @interface SomeAnnotation {
    // Some value...
}

*/

@TypeAnnotation("ClassAnnotation")
public class MyClass {
    
    private String text;

    public String getText() {
        return text;
    }

    @MethodAnnotation("TextAnnotation")
    public void setText(String text) {
        this.text = text;
    }
}
```

### 4. Using Annotation In Code

* The `RetentionPolicy` of annotation must be declared as `RUNTIME`
* Consider an __annotation__ just as a __class__
* Using annotation with __Reflection Mechanism__

```java
/**
 * Annotation of class
 */
TypeAnnotation typeAnnotation = MyClass.class.getAnnotation(TypeAnnotation.class);
System.out.println(typeAnnotation.value());

/**
 * Annotation of method
 */
Method[] methods = MyClass.class.getMethods();
for (Method method : methods) {
    MethodAnnotation methodAnnotation = method.getAnnotation(MethodAnnotation.class);

    // Some method may not have annotation
    if (methodAnnotation != null) {
        System.out.println(methodAnnotation.value());
    }
}
```

---

