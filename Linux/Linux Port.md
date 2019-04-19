# Linux - 端口占用

Created by : Mr Dk.

2019 / 03 / 14 17:36

Nanjing, Jiangsu, China

---

### 查看端口占用情况

```bash
$ lsof -i
```

### 查看某一端口的占用情况

```bash
$ lsof -i:8090
```

### 结束占用端口的进程

```bash
$ killall 进程名
$ kill -9 pid
```

---
