# PL/SQL - (+)

Created by : Mr Dk.

2020 / 01 / 07 21:24

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

## (+)

### Syntax

* 只能出现在 `WHERE` 子句中，不能与 `OUTER JOIN` 同时使用
* 若 `WHERE` 中包含多个条件，则必须在所有条件上包含 `(+)`
* 只能适用于列，而不是表达式
* 不能与 `OR` 或 `IN` 一起使用
* 只能用于实现左外连接或右外连接，不能实现 full outer join

### Example

* `(+)` 出现在右表上，则左表将全部显示，是左连接
* `(+)` 出现在左表上，则右表将全部显示，是右连接

```plsql
select * from t_A a, t_B b where a.id=b.id(+);
select * from t_A a, t_B b where a.id(+)=b.id;
```

---

## References

https://www.cnblogs.com/hehaiyang/p/4745897.html

https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/joins.html#GUID-2174C4BA-C852-4050-9269-353A3B40B355

---

