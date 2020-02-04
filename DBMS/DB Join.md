# DB - Join

Created by : Mr Dk.

2020 / 01 / 15 11:14

Nanjing, Jiangsu, China

---

## About Join

突然发现关于数据库的 __连接__ 都已经快忘光了

### Inner Join (Join)

内连接查询出符合查询条件的行

使用比较运算符比较被连接列对应的值

* 等值连接
* 非等值连接

### Natural Join

一种特殊的等值连接

两个关系中比较的分量必须是 __相同的属性组__

在结果中会把重复的属性列去除

### Outer Join

* left (outer) join
  * 左表中的每一行都与右表连接
  * 右表中存在满足连接条件的行，则依次与这些行连接
  * 右表中不存在满足连接条件的行，则依旧连接输出一行，右表中的内容为 NULL
* right (outer) join
  * 右表中的每一行都与左表连接
  * 左表中存在满足连接条件的行，则依次与这些行连接
  * 左表中不存在满足连接条件的行，则依旧连接输出一行，左表中的内容为 NULL
* full (outer) join
  * 左外连接 + 右外连接

__左__ 或 __右__ 的概念来自于 `FROM` 子句中表出现的顺序:

```sql
SELECT employee_id, last_name, first_name
FROM   employees LEFT OUTER JOIN departments
ON     (employees.department_id=departments.departments_id);
```

### Cross Join

两个表的笛卡尔积

左表的每一行依次与右表中的每一行连接

---

