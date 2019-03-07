# MongoDB - Data Import

Created by : Mr Dk.

2019 / 03 / 07 15:15

Nanjing, Jiangsu, China

---

### About

已有数据库的导出文件，存放在同一目录下：

* 元数据为 `xxx.metadata.json`
* 数据为 `xxx.bson`

---

### Import

```bash
$ mongorestore -d <db_name> /dir/...
```

---

