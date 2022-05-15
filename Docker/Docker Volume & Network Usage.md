# Docker - Volume & Network Usage

Created by : Mr Dk.

2020 / 09 / 08 23:04

Nanjing, Jiangsu, China

---

通过一个最简单的例子来了解 Docker 中的 **卷 (volume)** 和网络。例子很简单：在 Docker 中运行一个 Nginx，Nginx 的静态资源目录 (比如网页代码) 位于宿主机上，并以卷的形式挂在到容器中。然后在宿主机上访问容器中的 Nginx 监听的端口。

## 准备工作

首先准备一个能够在容器中启动 Nginx 的镜像：

1. 准备好操作系统 (基础镜像)，并安装 Nginx
2. 将 Nginx 的配置文件在宿主机上提前准备好，使用 `ADD` 指令复制到镜像中
3. 指明从镜像启动的容器暴露自己的 `80` 端口

其余上述思想，实现了一个 Dockerfile。Dockerfile 所在目录的组织方式如下：

```console
$ tree -a
.
├── Dockerfile
├── nginx
│   ├── global.conf
│   └── nginx.conf
└── src
    └── index.html

2 directories, 4 files
```

Dockerfile 具体指令如下：

```dockerfile
FROM ubuntu:20.04
MAINTAINER mrdrivingduck "mrdrivingduck@gmail.com"
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt-get -yqq update && apt-get -yqq install nginx
RUN mkdir -p /var/www/html/website
ADD nginx/global.conf /etc/nginx/conf.d/
ADD nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

首先来看看 Nginx 的两个配置文件吧。首先是 `nginx/global.conf`，会被复制到容器中的 `/etc/nginx/conf.d/` 下。其中指定了：

1. 监听本机 (容器) 的 `80` 端口
2. 静态资源目录位于 `/var/www/html/website/`
3. 日志路径

```nginx
server {
        listen 0.0.0.0:80;
        server_name _;

        root /var/www/html/website;
        index index.html;

        access_log /var/log/nginx/default_access.log;
        error_log /var/log/nginx/default_error.log;
}
```

其次是 `nginx/nginx.conf`，将会被复制到 `/etc/nginx/` 下。可以看到 Nginx 被配置成了一个基本的 HTTP 服务器。注意，配置中的 `daemon off` 使得 Nginx 在容器中以交互模式运行。

```nginx
user www-data;
worker_processes 4;
pid /run/nginx.pid;
daemon off;

events {  }

http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;
        gzip on;
        gzip_disable "msie6";
        include /etc/nginx/conf.d/*.conf;
}
```

## 构建镜像

接下来，使用 Dockerfile 构建镜像。

```console
$ sudo docker build -t mrdrivingduck/website .
Sending build context to Docker daemon  6.144kB
Step 1/8 : FROM ubuntu:20.04
 ---> 4e2eef94cd6b
Step 2/8 : MAINTAINER mrdrivingduck "mrdrivingduck@gmail.com"
 ---> Running in 88369a6f9503
Removing intermediate container 88369a6f9503
 ---> 2e6504b82ad7
Step 3/8 : RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
 ---> Running in 66de419b4a0b
Removing intermediate container 66de419b4a0b
 ---> 8705db5025d4
Step 4/8 : RUN apt-get -yqq update && apt-get -yqq install nginx
 ---> Running in 5397334a1984
Removing intermediate container 5397334a1984
 ---> bc3ec63ef95e
Step 5/8 : RUN mkdir -p /var/www/html/website
 ---> Running in be3b9e8b57af
Removing intermediate container be3b9e8b57af
 ---> 1d854b54248b
Step 6/8 : ADD nginx/global.conf /etc/nginx/conf.d/
 ---> 108f1e4a78cb
Step 7/8 : ADD nginx/nginx.conf /etc/nginx/nginx.conf
 ---> 4b1099f18e8d
Step 8/8 : EXPOSE 80
 ---> Running in 188934c22f2d
Removing intermediate container 188934c22f2d
 ---> ea637a98908b
Successfully built ea637a98908b
Successfully tagged mrdrivingduck/website:latest
```

镜像构建完毕后，查看：

```console
$ sudo docker image list
REPOSITORY              TAG                 IMAGE ID            CREATED             SIZE
mrdrivingduck/website   latest              ea637a98908b        22 minutes ago      156MB
```

## 启动容器 & 卷

接下来启动容器：

1. 容器以后台模式而非交互模型运行，所以使用 `-d` 选项
2. Dockerfile 的 `EXPOSE` 指令指定容器将暴露 `80` 端口，因此这里使用 `-p 80` 选项打开 `80` 端口
3. 这个容器被我自行命名 `--name website`
4. 通过 `-v` 属性将宿主机下的 `$PWD/src` 目录作为卷挂载到容器中的 `/var/www/html/website` 目录
5. 容器的启动命令为 `nginx`

```console
$ sudo docker run -d -p 80 --name website -v $PWD/src:/var/www/html/website mrdrivingduck/website nginx
7302af622f9810b14b2107111346bb56ea95f14d5ba8b7d4a00e0f96dbd1c816
```

容器以后台模式运行，因此命令返回一个容器 ID 后就结束了。可以看到容器正在运行：

```console
$ sudo docker ps -a
CONTAINER ID        IMAGE                   COMMAND             CREATED             STATUS                      PORTS                   NAMES
7302af622f98        mrdrivingduck/website   "nginx"             7 seconds ago       Up 6 seconds                0.0.0.0:32770->80/tcp   website
```

在上面的信息中可以看到，容器的 `80` 端口被映射到了宿主机的 `32770` 端口上。因此，通过 `宿主机 IP:32770` 或 `容器 IP:80` 都可以访问容器中的 Nginx。这里我们用宿主机 IP 进行尝试。命令得到的 HTML 就是宿主机目录 `src/index.html` 中的内容。

```console
$ curl localhost:32770
<h1>Hello Docker!</h1>
$ curl localhost:32770
<h1>Hello Docker!</h1>
<p>Edited On Host!</p>
```

为什么两次命令的结果不一样呢？因为在两条命令中间，我直接对宿主机上的 `src/index.html` 进行了编辑。这里就体现了 **卷** 的特性。卷是一个宿主机目录，它可以被一个或多个容器选定，绕过 Docker 的联合文件系统，直接 mount 到容器内的某个目录上。卷用于为 Docker 提供 **持久数据** 或 **共享数据**，对卷的修改会立刻生效。当提交或创建镜像时，卷不包含在其中。在我的理解中，卷有点像一个能同时插在多台电脑上的移动硬盘。

如果不想把应用或者代码构建到镜像中时 (比如只想在镜像中营造一个生产环境，但是开发中的代码位于宿主机上)，就体现出了卷的价值：

- 同时对代码开发和测试
- 代码改动频繁，不想在开发过程中反复构建镜像
- 在多个容器之间共享代码

在 `docker run` 命令中，通过 `-v source:target:ro` 指定卷的映射。如果容器内目录 `target` 不存在，Docker 会自动创建一个。在最后加上 `rw` 或 `ro` 来指定 **容器内目录** (`target`) 的读写权限。

## Docker 的网络连接

上述的例子中，通过搭建了一个生产环境容器，成功地在开发的同时测试了代码在生产环境中的使用情况。而其中包含了一个细节：我们有多少种访问容器内 Nginx `80` 端口的方式？

1. 宿主机上的进程作为客户端访问
2. 在容器内的其它进程作为客户端访问
3. **其它容器内的进程作为客户端访问**

这里就涉及到了 Docker 的网络连接是如何实现的。Docker 中有三种网络连接方式：

1. Docker 内部网络 (不太灵活)
2. Docker Networking (After Docker 1.9，推荐)
3. Docker 链接

### Docker 内部网络

在默认情况下，Docker 容器都是公开端口并绑定到宿主机的网络接口上，这样可以把 Docker 内提供的服务放到宿主机所在的外部网络上公开。在安装 Docker 时，会创建一个新的网络接口 `docker0`。每个 Docker 容器都会在这个接口上被分配 IP 地址：

```console
$ ifconfig
docker0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        inet6 fe80::42:6ff:feae:e946  prefixlen 64  scopeid 0x20<link>
        ether 02:42:06:ae:e9:46  txqueuelen 0  (Ethernet)
        RX packets 21599  bytes 1191336 (1.1 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 42554  bytes 63422188 (63.4 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

veth0f97e6d: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::6ca3:8bff:fe50:3210  prefixlen 64  scopeid 0x20<link>
        ether 6e:a3:8b:50:32:10  txqueuelen 0  (Ethernet)
        RX packets 28  bytes 2858 (2.8 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 70  bytes 7060 (7.0 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Docker 会使用一个 `172.17.x.x` 的子网作为 Docker 内部网络，`docker0` 对应的 IP 地址也就是这个网络的网关。`docker0` 是一个虚拟的以太网桥。Docker 每创建一个容器，就会创建一组互相连接的网络接口，与 **管道** 类似。管道的一端连接容器内的虚拟网卡 (如 `eth0`，IP 地址也在子网中)，管道的另一端以 `veth*` 的名称连接到宿主机的 `docker0` 上。由此，Docker 将维护一个虚拟子网，由宿主机和所有 Docker 容器共享。

Docker 内部网络的互连还受宿主机的 **防火墙规则** 与 **NAT 配置** 的影响。在默认情况下，宿主机无法访问容器；只有明确指定了打开的端口，宿主机与容器才能够通信。以上面的应用场景为例，可以在路由表中看到容器的 `80` 端口与宿主机 `32770` 端口的通信规则：

```console
$ sudo iptables -t nat -L -n
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination
DOCKER     all  --  0.0.0.0/0            0.0.0.0/0            ADDRTYPE match dst-type LOCAL

Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
DOCKER     all  --  0.0.0.0/0           !127.0.0.0/8          ADDRTYPE match dst-type LOCAL

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination
MASQUERADE  all  --  172.17.0.0/16        0.0.0.0/0
MASQUERADE  tcp  --  172.17.0.2           172.17.0.2           tcp dpt:80

Chain DOCKER (2 references)
target     prot opt source               destination
RETURN     all  --  0.0.0.0/0            0.0.0.0/0
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:32770 to:172.17.0.2:80
```

通过以下命令，可以查看容器的网络详情：

```console
$ sudo docker inspect website
[
    {
        "Id": "7302af622f9810b14b2107111346bb56ea95f14d5ba8b7d4a00e0f96dbd1c816",
        ...
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "bb4af0908c0eb3663ab86175bbc4cab01d11e5547390348b9d963fa5e951ba22",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {
                "80/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "32770"
                    }
                ]
            },
            "SandboxKey": "/var/run/docker/netns/bb4af0908c0e",
            "SecondaryIPAddresses": null,
            "SecondaryIPv6Addresses": null,
            "EndpointID": "9bd094ac1d2e4bc247fa843a5db32e921d995d357a4c57be8035db9e7eef960d",
            "Gateway": "172.17.0.1",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "172.17.0.2",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "MacAddress": "02:42:ac:11:00:02",
            "Networks": {
                "bridge": {
                    "IPAMConfig": null,
                    "Links": null,
                    "Aliases": null,
                    "NetworkID": "062db7d45781261af12df968dc9c139df61ba129ed8f5b356c5f90851e0ae361",
                    "EndpointID": "9bd094ac1d2e4bc247fa843a5db32e921d995d357a4c57be8035db9e7eef960d",
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:02",
                    "DriverOpts": null
                }
            }
        }
    }
]
```

从上面的信息中可以看到，容器的 IP 地址为 `172.17.0.2`，与宿主机网关 `172.17.0.1` 在同一个子网中。因此，不仅通过宿主机 IP 地址可以访问到容器的的 Nginx (`172.17.0.1:32770`)，还可以通过容器 IP 地址访问 Nginx (`172.17.0.2:80`)。

这种容器局域网网络看似简单，但很不灵活：

1. 需要根据容器的 IP 地址进行硬编码
2. 重启容器后，Docker 会给容器分配新的 IP 地址

### Docker Networking

Docker Networking 允许用户自行创建网络，甚至支持跨不同宿主机的容器间通信，网络配置也可以更加灵活地定制。想要使用这一套机制，首先需要 **创建一个网络**，然后在这个网络下启动容器。首先建立一个名为 `mynet` 的网络：

```console
$ sudo docker network create mynet
08e97c3f58b9b128c5958b36e96c769b3c242ea55ab21af175b12cb40ffcadf7

$ sudo docker network inspect mynet
[
    {
        "Name": "mynet",
        "Id": "08e97c3f58b9b128c5958b36e96c769b3c242ea55ab21af175b12cb40ffcadf7",
        "Created": "2020-09-08T22:27:32.178555856+08:00",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {},
        "Options": {},
        "Labels": {}
    }
]

$ sudo docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
062db7d45781        bridge              bridge              local
f88e74985810        host                host                local
08e97c3f58b9        mynet               bridge              local
abdf15c3754d        none                null                local
```

可以看到这个网络的网关为 `172.18.0.1`，这是一个新的子网，且暂时没有任何容器在其中。再重新启动容器时，需要在 `docker run` 命令中启用 `--net=mynet` 显式将容器启动在新的网络中。然后再重新查看以下网络：

```console
$ sudo docker rm website
website

$ sudo docker run -d -p 80 --name website --net=mynet -v $PWD/src:/var/www/html/website mrdrivingduck/website nginx
f550227293ff831255b76972011ee88120a7d44fadf29e2cd92161e9d5704d7b

$ sudo docker network inspect mynet
[
    {
        "Name": "mynet",
        ...
        "Containers": {
            "f550227293ff831255b76972011ee88120a7d44fadf29e2cd92161e9d5704d7b": {
                "Name": "website",
                "EndpointID": "61a412d1bc738020e606800e74fac45ff9dc85a45d2463b9cac0866b3691d377",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]
```

可以看到运行 Nginx 的容器已经被加入到网络中。这与之前的内部网络相比，到底灵活在哪呢？Docker 将会自动感知所有在这个网络下运行的容器，并将容器的网络信息保存到 `/etc/hosts` 中。在该文件中，除了该容器本身的 IP 地址，还会保存网络内其它容器的 IP 地址，并映射到 `<container_name>.<network_name>` 形式的域名上。重要的是，当任意一个容器重启时，其 IP 地址信息会自动在网络内所有容器的 `/etc/hosts` 中更新。如果容器内的上层应用全部使用 **域名** 而不是 IP 地址，那么容器的重启不会对应用程序产生影响。

通过 `docker network connect <network_name> <container_name>` 命令，可以将一个正在运行的容器添加到特定网络中。同理，`docker network disconnect` 就不多说。另外，一个容器还可以 **同时隶属多个网络**，从而构建复杂的网络模型。

### Docker 链接

在 Docker 1.9 之前推荐这种方式。让一个容器链接到另一个容器是个简单的过程，只需要引用两个容器的名字就好了。先启动第一个容器，然后启动第二个容器时，在 `docker run` 命令中附加 `--link <target_container>:<link_alias>`。其中，第二个容器是 **客户容器**，要链接到的目标容器是 **服务容器**。容器启动后，会将 `--link` 中的参数添加到 `/etc/hosts` 中。在这样的链接后，只有客户容器可以直接访问服务容器的公开端口，而其它容器不行；服务容器的端口也不需要对宿主机公开。由此，这个模型非常安全，可以限制容器化应用程序的被攻击面，减少容器暴露的端口。

可以将多个客户容器链接到一个服务容器上。容器链接目前只能工作于同一台 Docker 宿主机中。

Docker 在建立容器间的链接时，会在自动创建一些以 **链接别名** 命名的环境变量，包含了丰富的链接信息。

### 灵活性

所谓的灵活性，就是避免在应用程序进行容器间通信时使用硬编码的 IP 地址。根据上述三种网络连接方式，灵活性通过以下两种方法保证：

1. 利用环境变量中的连接信息
2. 利用 `/etc/hosts` 中的 DNS 映射信息

---
