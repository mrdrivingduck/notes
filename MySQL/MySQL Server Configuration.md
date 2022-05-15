# MySQL - Server Configuration

Created by : Mr Dk.

2020 / 10 / 28 22:17

Nanjing, Jiangsu, China

---

在远程机器上新装了 Linux server 并安装了 MySQL，在开发机器上使用 [_MySQL Workbench_](https://www.mysql.com/products/workbench/) 来进行数据库的管理，所以要在 workbench 中配置数据库的信息。Linux server 上新安装的 MySQL 需要进行一定的配置后才能够被 MySQL Workbench 连接。

## Binding

首先，MySQL 默认 bind 了 `127.0.0.1` 作为监听地址，也就是说只有本机上的应用才能够通过 `localhost` 访问 MySQL。到 `/etc/mysql/mysql.conf.d` 中 (MySQL 5.7) 设置 `mysqld.cnf` 文件：

```conf
#
# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address            = 127.0.0.1
```

设置为：

```conf
#
# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address            = 0.0.0.0
```

这样，MySQL server 将监听设备地址而不是本地 loop back，从而能够被远程机器连接。

## User

MySQL 默认已经有了一个名为 `root` 的用户。对于一个应用来说，我们可以为这个应用创建一个用户并授予权限。另外，MySQL 中还对每个用户连接的源 IP 地址作出了限制，保证只有特定的 IP 地址能够通过该用户连接到 MySQL。

创建用户的方式如下。登录 MySQL 的命令行，输入：

```bash
mysql> use mysql;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
```

```mysql
CREATE USER 'username'@'host' IDENTIFIED BY 'password';
```

其中，`username` 表示用户名；`host` 表示可以通过该用户名连接到 MySQL 的域名，如果允许这个用户通过所有的 IP 地址访问 MySQL server，那么可以使用 `'%'`；`password` 用于表示该用户对应的密码。

可以在 `mysql` 数据库的 `user` 表中查看所有的用户和对应的 `host`：

```bash
mysql> select user,host from user;
+------------------+-----------+
| user             | host      |
+------------------+-----------+
| ccdetect         | %         |
| root             | %         |
| debian-sys-maint | localhost |
| mysql.session    | localhost |
| mysql.sys        | localhost |
| root             | localhost |
+------------------+-----------+
6 rows in set (0.00 sec)
```

之后，新创建的用户需要被赋予访问特定的数据库 / 表的权限：

```mysql
GRANT SELECT, INSERT ON database.table TO 'username'@'host';
```

当然，也可以直接赋予该用户对 **所有** 数据库表的 **所有** 权限：

```mysql
GRANT ALL ON *.* TO 'username'@'host';
```

之后，就可以使用用户名 + 密码通过 MySQL Workbench 进行登录了。

---
