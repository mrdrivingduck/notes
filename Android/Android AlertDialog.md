# Android Development - AlertDialog

Created by : Mr Dk.

2018 / 05 / 21 19:10

Nanjing, Jiangsu, China

------

##### 1. 介绍

* Android 中的基本控件 —— 警告框
* 动态触发显示
* 可显示标题、信息、单选框、复选框
* 可设置按钮

---

##### 2. 创建方式

* 由于是触发显示，所以不能使用构造函数进行创建

```java
AlertDialog.Builder builder = new AlertDialog.Builder(context);
// builder.set...
AlertDialog dialog = builder.create();

/*    Another way    */
AlertDialog dialog = new AlertDialog.Builder(context).create();
// dialog.set...
```

---

##### 3. 显示方式

```Java
dialog.show();
if (dialog.isShowing()) {
    dialog.dismiss();
}
```

---

##### 4. 设置内部信息

```java
// 设置标题
dialog.setTitle("...")；
// 设置文字信息
dialog.setMessage("...");
// 设置按钮
dialog.setButton(BUTTON_TYPE, BUTTON_TEXT, onClickListener);
// 设置图标
dialog.setIcon();

// 设置标题
builder.setTitle();
// 设置文字信息
builder.setMessage();
// 设置图标
builder.setIcon();
// 设置单选选项
builder.setSingleChoiceItems();
// 设置多选选项
builder.setMultiChoiceItems();
// 设置中立按钮
builder.setNeutralButton();
// 设置消极按钮
builder.setNegativeButton();
// 设置积极按钮
builder.setPositiveButton();
// ......
```

---

##### 5. 修改标题、内容、按钮颜色，字体大小等

- 参考 CSDN

- 修改按钮样式

  ```Java
  dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(Color.BLUE);
      
  dialog.getButton(DialogInterface.BUTTON_NEGATIVE).setTextColor(Color.BLACK);
  ```

- 修改标题样式

  ```Java
  dialog.show();
  try {
  	Field mAlert = AlertDialog
          .class
  		.getDeclaredField("mAlert");
      mAlert.setAccessible(true);
      Object mAlertController = mAlert.get(dialog);
      Field mMessage = mAlertController
   		.getClass()
   		.getDeclaredField("mMessageView");
      // OR "mTitleView"
      mMessage.setAccessible(true);
      TextView mMessageView = (TextView) mMessage.get(mAlertController);
      mMessageView.setTextColor(Color.BLUE);
  } catch (IllegalAccessException e) {
  	e.printStackTrace();
  } catch (NoSuchFieldException e) {
  	e.printStackTrace();
  }
  ```

------

