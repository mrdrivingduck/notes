# Android Development - Adapter for ListView

Created by : Mr Dk.

2018 / 05 / 05 14:48

Nanjing, Jiangsu, China

---

## 功能

* ListView 适配器


* 为 ListView 中的每一项制定布局和格式

## Override 方法

* 创建一个 MyAdapter 类，继承自 BaseAdapter 类

* Constructor Parameters：

  ```java
  // 上下文参数
  private Context context;
  // 所有要放入 ListView 的数据集合
  private List <Map <String, Object> > AllValues;
  ```

  

* Override 4个函数

  ```Java
  @Override
  public int getCount() {
      return AllValues.size();
  }
  
  @Override
  public Object getItem(int position) {
      return AllValues.get(position);
  }
  
  @Override
  public long getItemId(int position) {
      return position;
  }
  
  @Override
  public View getView(
      int position, 
      View convertView, 
      ViewGroup parent) {
  
      if (convertView == null) {
          // Create an item
          
          // add a layout file
          convertView = LayoutInflater
              .from(context)
              .inflate(R.layout.listview_menu, null);
          // set size
          convertView.setLayoutParams(
              new AbsListView.LayoutParams(
                  ViewGroup.LayoutParams.MATCH_PARENT,
                  GetScreenSize.GetScreenHeight(context) / 8
              )
          );
      }
  
      // Find views by ID
  
      // Get data for one item
      Map<String, Object> map = AllValues.get(position);
      
      // Data deployment
  
      return convertView;
  }
  ```

## 在 Activity 中的使用

```Java
List <Map <String, Object> > AllValues = new ArrayList<>();
MyAdapter myAdapter = new MyAdapter (getContext(), AllValues);
listView.setAdapter (myAdapter);
```

