# Git - Basic Configuration

Created by : Mr Dk.

2018 / 10 / 19 13:29

Nanjing, Jiangsu, China

---

## 1. Get an account on Version Control website

* GitHub
* GitLab
* Coding.net
* Gitee
* ...

## 2. Generate SSH-key locally

```console
$ ssh-keygen -t rsa -C "your_email@youremail.com"
```

* 按下 `Enter` 后会提示保存密钥的路径 - 可直接 `Enter` 使用默认路径
* 提示输入一个密码 - 用于保护产生的密钥（可以不设置密码）
* SSH key 生成完成
  * 在设定的保存密钥路径中可以找到公钥 *id_rsa.pub*
  * 默认位于 `~/.ssh/` 路径下

## 3. Add Public Key to your account

* 查看 `id_rsa.pub`
* 将 **除了邮箱以外的部分** 复制，粘贴到版本控制网站个人账号的 *SSH 公钥* 中

比如，复制如下部分：

```console
$ cat .ssh/id_rsa.pub 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6oNrhO0KoK9IcvXCg30oaDKLI95ucOFloikfjMXU1S3cfmkOuUgtZ+e+UYaQQQjsGnyqynf4LqVE459Sit0qDEyiEUtLbYdaoIAC95puK4fZDJbM8/f1RnnMuzzVAmhr6viSfFGZ+Ck4tyMYSDQXE+Da3B5JeQe0T9yGqtoMPcXFWixrWqG/vKX9lN8tFhKMAZB5/1n/NBZUMkpqPfUjcvTfLzDeUCn2ZtsXA6G0TtcILM06NMMCZIzd0yyaZkIVAp4zNSGoOLLISiLjAxNZb1DyBs+KzFSrPVxb30KZZrCKT0LTp0Tw52FKnGCpxaUs8AkCQ7Nz9Rla07NIg5xRJ 562655624@qq.com
```

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6oNrhO0KoK9IcvXCg30oaDKLI95ucOFloikfjMXU1S3cfmkOuUgtZ+e+UYaQQQjsGnyqynf4LqVE459Sit0qDEyiEUtLbYdaoIAC95puK4fZDJbM8/f1RnnMuzzVAmhr6viSfFGZ+Ck4tyMYSDQXE+Da3B5JeQe0T9yGqtoMPcXFWixrWqG/vKX9lN8tFhKMAZB5/1n/NBZUMkpqPfUjcvTfLzDeUCn2ZtsXA6G0TtcILM06NMMCZIzd0yyaZkIVAp4zNSGoOLLISiLjAxNZb1DyBs+KzFSrPVxb30KZZrCKT0LTp0Tw52FKnGCpxaUs8AkCQ7Nz9Rla07NIg5xRJ
```

## 4. Git local configuration

After creating a repository on the website and `clone` it to local:

```console
$ git clone xxxxxxxx.git
```

Get into Command-Line (Git Bash):

```console
$ cd ./xxxxxxxx
$ git config --list
```

Check all configurations, configure `name` & `email`:

```console
$ git config --global user.name "mrdrivingduck"
$ git config --global user.email "562655624@qq.com"
```

---

