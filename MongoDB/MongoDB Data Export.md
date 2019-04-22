# MongoDB - Data Export

Created by : Mr Dk.

2019 / 04 / 22 09:40

Nanjing, Jiangsu, China

---

## About

__mongoexport__ tool - 将 Collection 导出为 JSON 或 CSV 格式

* 可通过参数指定导出的数据项
* 可根据指定的条件导出数据

__mongodump__ tool - 导出整个数据库备份

* 元数据为 `xxx.metadata.json`
* 数据为 `xxx.bson`

---

## Export

```bash
$ mongoexport -d <db_name> -c <collection_name> -o <export_file> --type json/csv -f "_id, user_id, ..."
```

```bash
$ mongodump -h <db_host> -d <db_name> -o <export_dir>
```

---

