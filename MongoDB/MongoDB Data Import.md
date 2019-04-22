# MongoDB - Data Import

Created by : Mr Dk.

2019 / 03 / 07 15:15

Nanjing, Jiangsu, China

---

## About

__mongorestore__ tool - 导入已有数据库的导出备份：

* 元数据为 `xxx.metadata.json`
* 数据为 `xxx.bson`

__mongoimport__ tool - 导入单独的 Collection 的 JSON 导出文件

---

## Import

```bash
$ mongorestore -d <db_name> /dir/...
```

```bash
$ mongoimport --db <db_name> --collection <cl_name> --file data.json
```

---

