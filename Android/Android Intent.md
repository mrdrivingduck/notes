## Android Development - Intent

Created by : Mr Dk.

2018 / 05 / 05 14:48

Nanjing, Jiangsu, China

---

##### 1. 功能 

* Activity之间的跳转与数据传递

---

##### 2. 构造函数

```Java
Intent intent = new Intent (Context packageContext, Class <?> cls);

// packageContext : 上下文参数
// 可以传入 Activity.this
// 可以传入 getContext()
// 可以传入 getApplicationContext()

// cls : 跳转到的 Activity 的类名
// 使用反射机制 : LogInActivity.class

// e.g.
Intent intent = new Intent(LogInActivity.this, MainActivity.class);
```

---

##### 3. 数据传递

```java
intent.putExtra (String key, Type value);
// value 支持所有数据类型

//在跳转到的 Activity 中取得数据
Intent intent = getIntent();
intent.getTypeExtra(String key, Type defaultValue);
// Type 支持所有数据类型
```

---

##### 4. 自定义数据类型的传递

```Java
// 首先对于自定义的类，必须实现 Serializable 接口
// 对 class 中的每个属性，必须实现 get & set 方法
public class User implements Serializable {
	// Getters
    // Setters
}

// 发送数据
intent.putExtra (String key, Serializable value);

// 接收数据
user = (User) getIntent().getSerializableExtra(key);

// e.g.
// LogInActivity
intent.putExtra ("USER", user);
startActivity(intent);
// MainActivity
user = (User) getIntent().getSerializableExtra("USER");
```

---

##### 5. 跳转界面的两种方式

```Java
// 当跳转的界面返回时，不需要返回结果
startActivity (Intent intent);
startActivity (Intent intent, Bundle options);

// 当跳转的界面返回时，需要返回结果
startActivityForResult (Intent intent, int requestCode);
startActivityForResult (Intent intent, int requestCode, Bundle options);

// e.g.
// MainActivity
public void StartActivity () {
    Intent intent = new Intent(MainActivity.this, UpdateActivity.class);
	// intent.putExtra();
	startActivityForResult (intent);
}

@Override
protected void onActivityResult(
    int requestCode, int resultCode, Intent data) {
    if (requestCode == A && resultCode == B) {
        // data.getTypeExtra();
    }
}

// UpdateActivity
getIntent().putExtra();
setResult (resultCode, getIntent());
```

---

##### 6. 关于 FragmentActivity 和 Fragment 的 Intent

* FragmentActivity 和 子Fragment 都可以通过 Intent 启动 Activity

  ```java
  class TestFragment extends Fragment {
      public void OnCreateView (args) {
          // 通过 Fragment 启动
          startActivity(intent);
          
          // 通过 FragmentActivity 启动
          getActivity().startActivity(intent);
      }
  }
  ```

* 若 FragmentActivity 中 Override 了 OnActivityResult 函数

  那么 Fragment 中的 OnActivityResult 将不会收到结果

  除非在 FragmentActivity 的 OnActivityResult 函数中

  获取到 Fragment，并显示调用它们的 OnActivityResult 函数

  并在 Fragment 中的 OnActivity 函数中调用 super.OnActivityResult

  ```Java
  class MainActivity extends FragmentActivity {
      @Override
  	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
          getFragment().OnActivityResult (requestCode, resultCode, data);
  	}
  }
  
  class TestFragment extends Fragment {
      @Override
  	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
          super.OnActivityResult (requestCode, resultCode, data);
          
          // Service
  	}
  }
  ```

* 通过 Activity 启动的 Activity，可以通过 Activity 的 OnActivityResult，

  将返回的数据传递到所有的 Fragment 中

  通过 Fragment 启动的 Activity，在 Activity 的 OnActivityResult 中，

  只有启动 Activity 的 Fragment 才能接收到数据

  ```Java
  class MainActivity extends FragmentActivity {
      @Override
  	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
          // testFragment 将收到数据
          testFragment.OnActivityResult (requestCode, resultCode, data);
          // anotherFragment 将不会收到数据
          anotherFragment.OnActivityResult (requestCode, resultCode, data);
  	}
  }
  
  class TestFragment extends Fragment {
      
      public void StartActivity () {
          // 从 Fragment 中启动 Activity
          startActivityForResult (intent);
          // 从 Activity 中启动 Activity
          // getActivity()
          //    .startActivityForResult (intent);
      }
      
      @Override
  	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
          
          super.OnActivityResult (requestCode, resultCode, data);
          
          // Service
  	}
  }
  ```

  ​