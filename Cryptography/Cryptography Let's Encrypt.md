# Cryptography - Let's Encrypt

Created by : Mr Dk.

2020 / 04 / 04 0:43

Ningbo, Zhejiang, China

---

最近在开发一个微信小程序的后端，服务器需要支持 HTTPS 并备案。既要支持 HTTPS，那么就一定要有一个被签发的证书。找正规的 CA 机构签发证书是要时间要钱的。而 [Let's Encrypt](https://letsencrypt.org/) 是一个非盈利性组织提供的免费、开放的证书颁发机构 (CA)，可以用它来免费签发证书。

## *Certbot*

目前，官方推荐的签发工具是 [certbot](https://certbot.eff.org/)，在其 [GitHub](https://github.com/certbot/certbot) 仓库上也有代码。关于这个工具的原理我没有研究，只能根据运行过程大致猜测。

想要运行 certbot，要满足几个条件：

* 一台服务器，并能够 SSH 连接到它上面进行操作
* 一个已经在开放的 **80** 端口上运行的 HTTP 网站

![certbot-requirement](../img/certbot-requirement.png)

然后，根据你使用的 **OS** 和 **Web Server** ，*certbot* 分别提供了相应的步骤和自动化工具。根据步骤，可以一步一步地产生证书，并自动将证书添加到 Web server 的配置文件中。比如想为一台 *Ubuntu 16.04* 服务器签发证书，这个证书由 *nginx* 使用，就按如下方式选择：

![certbot-environment](../img/certbot-environment.png)

然后该网站会告诉你接下来的步骤：

1. 将 *certbot* 加入到 PPA 中
2. 用 `apt` 从 PPA 中安装 *certbot*
3. 以 `--nginx` 选项运行 *certbot*，签发证书并自动配置到 *nginx* 上
4. 证书有效期为 90 天，*certbot* 会产生一个 *cron* 任务 (定时任务) 自动刷新证书

## *Nginx* Configuration

证书生成完毕后，*cerbot* 自动修改了我的 nginx 配置文件 (作为前提条件的 HTTP 网站已经运行在 nginx 上)。其中 `<hostname>` 为自己申请的域名，并需要将该域名通过 DNS 解析到这台服务器上。

```nginx
server {
    server_name www.<hostname>.cn <hostname>.cn;
    listen 80;
	rewrite ^(.*)$ https://${server_name}$1 permanent; # 将 80 端口的访问转移到 443
}

server {
	server_name www.<hostname>.cn <hostname>.cn;
	location / {
		root /root/homepage;
		index index.html;
	}

	listen 443 ssl; # managed by Certbot
	ssl_certificate /etc/letsencrypt/live/<hostname>.cn/fullchain.pem; # managed by Certbot
	ssl_certificate_key /etc/letsencrypt/live/<hostname>.cn/privkey.pem; # managed by Certbot
	include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
	ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

## Certificates

证书被生成在一个特定位置 (`/etc/letsencrypt/live/<hostname>/`)，包含以下四个文件：

* `cert1.pem`
* `chain1.pem`
* `fullchain1.pem`
* `privkey1.pem`

其中，`privkey1.pem` 保存了私钥；`cert1.pem` 是签发的最终证书，保存了公钥。可以使用 `openssl` 查看证书：

```bash
$ openssl x509 -in cert1.pem -noout -text 
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            03:3f:c7:88:2e:7f:ad:cd:17:28:c7:e2:c2:81:bb:cd:ce:94
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = US, O = Let's Encrypt, CN = Let's Encrypt Authority X3
        Validity
            Not Before: Mar 19 16:02:23 2020 GMT
            Not After : Jun 17 16:02:23 2020 GMT
        Subject: CN = api.smartcommunity.mrdrivingduck.cn
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                RSA Public-Key: (2048 bit)
                Modulus:
                    00:9f:33:28:bd:79:4d:c6:34:3b:d9:4a:8b:ed:d5:
                    55:22:84:00:fa:bd:84:00:2c:0d:3d:4e:10:61:82:
                    a3:07:7a:87:0d:01:11:09:bc:78:0f:37:d6:85:bb:
                    90:10:8e:e9:7f:fd:55:46:33:be:94:99:ea:4e:90:
                    87:05:1a:c2:04:90:95:47:13:1f:88:b0:da:46:7a:
                    92:8d:13:9a:bb:6f:2f:9c:7c:c5:6f:7b:c3:0b:2c:
                    ee:5e:e7:48:5a:f1:fe:ee:b2:7b:3a:51:6c:1f:55:
                    5a:fe:10:3c:dc:f9:75:87:31:e1:83:a8:71:97:1b:
                    0a:71:a1:04:83:eb:3e:c5:c3:09:a2:6b:c9:08:77:
                    bd:92:86:a2:4b:2b:b7:4c:6a:1e:d6:b8:3c:79:ca:
                    6c:99:65:20:7a:e7:68:5b:cd:1d:a8:b9:d1:44:b8:
                    e1:51:53:b9:7f:df:9f:cf:8f:04:d9:bc:da:bb:c7:
                    81:da:d9:d8:bd:7a:7e:79:a1:f9:99:1f:8d:8c:d3:
                    a9:e6:16:e2:d0:e5:0f:8a:e8:dc:65:36:05:fa:d9:
                    f7:c7:f5:ef:cd:be:d0:ae:01:e0:bd:be:94:f3:84:
                    be:62:2f:a6:4d:2a:2e:96:1c:7b:90:29:95:0c:7a:
                    13:0c:63:db:c5:c8:aa:51:cb:ef:ba:5a:35:e8:de:
                    ee:25
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Key Usage: critical
                Digital Signature, Key Encipherment
            X509v3 Extended Key Usage: 
                TLS Web Server Authentication, TLS Web Client Authentication
            X509v3 Basic Constraints: critical
                CA:FALSE
            X509v3 Subject Key Identifier: 
                B3:FD:D0:6E:AB:3E:42:27:2A:36:C8:23:49:8A:54:E3:93:9B:F9:0C
            X509v3 Authority Key Identifier: 
                keyid:A8:4A:6A:63:04:7D:DD:BA:E6:D1:39:B7:A6:45:65:EF:F3:A8:EC:A1

            Authority Information Access: 
                OCSP - URI:http://ocsp.int-x3.letsencrypt.org
                CA Issuers - URI:http://cert.int-x3.letsencrypt.org/

            X509v3 Subject Alternative Name: 
                DNS:api.smartcommunity.mrdrivingduck.cn
            X509v3 Certificate Policies: 
                Policy: 2.23.140.1.2.1
                Policy: 1.3.6.1.4.1.44947.1.1.1
                  CPS: http://cps.letsencrypt.org

            CT Precertificate SCTs: 
                Signed Certificate Timestamp:
                    Version   : v1 (0x0)
                    Log ID    : 5E:A7:73:F9:DF:56:C0:E7:B5:36:48:7D:D0:49:E0:32:
                                7A:91:9A:0C:84:A1:12:12:84:18:75:96:81:71:45:58
                    Timestamp : Mar 19 17:02:23.379 2020 GMT
                    Extensions: none
                    Signature : ecdsa-with-SHA256
                                30:45:02:21:00:EF:16:97:A2:E7:FF:7D:D9:C0:D8:84:
                                2F:9F:FC:92:89:27:77:83:5A:63:8C:12:5B:44:20:A2:
                                BC:F9:C1:E1:50:02:20:51:8D:59:BE:0E:E9:93:81:B8:
                                09:98:08:39:BA:F6:07:14:EF:58:A0:09:E0:6D:24:D3:
                                B9:64:F3:83:78:22:E7
                Signed Certificate Timestamp:
                    Version   : v1 (0x0)
                    Log ID    : 07:B7:5C:1B:E5:7D:68:FF:F1:B0:C6:1D:23:15:C7:BA:
                                E6:57:7C:57:94:B7:6A:EE:BC:61:3A:1A:69:D3:A2:1C
                    Timestamp : Mar 19 17:02:23.455 2020 GMT
                    Extensions: none
                    Signature : ecdsa-with-SHA256
                                30:44:02:20:1C:0E:27:DB:10:96:46:78:D2:DD:B3:21:
                                E9:B8:64:FB:44:16:E8:11:6A:28:FC:96:A8:4E:2C:3C:
                                5E:FE:05:AC:02:20:3A:49:60:25:C6:26:44:C8:72:11:
                                B4:3B:8D:4E:D4:E7:AE:60:44:B8:90:B8:3B:60:9D:31:
                                30:69:25:0C:79:5A
    Signature Algorithm: sha256WithRSAEncryption
         7a:a5:56:d7:18:9f:0c:39:70:df:91:d2:ca:aa:43:8a:b1:33:
         f7:df:72:4d:f1:aa:1f:ee:32:ca:51:89:e7:37:e1:66:a6:f1:
         2a:14:4f:52:32:05:78:8b:89:49:65:bf:b9:a6:9c:ac:ce:79:
         6c:2b:07:8f:b7:85:62:a4:50:43:db:a6:42:a5:92:e0:1a:c5:
         59:f7:21:f5:db:97:8b:85:f0:96:c1:fe:57:7a:8e:f0:25:87:
         1f:8a:c3:b9:4a:72:51:2a:d8:5b:71:c2:fb:fc:64:6c:70:a6:
         a5:41:44:e1:85:52:8e:1b:d2:04:9d:89:9e:30:47:72:98:55:
         b9:da:ec:86:63:9f:cb:87:6b:e4:6c:8c:06:b5:5f:23:e2:b8:
         31:aa:dc:22:04:b3:46:ad:42:79:67:2f:be:4c:5f:4e:fb:95:
         83:7c:e0:ea:7b:2b:28:57:5e:e4:64:e8:8e:8e:dd:4c:0b:e5:
         9a:f9:cc:52:b7:a3:f6:e8:96:58:62:17:aa:63:05:bf:7c:63:
         ab:1c:fa:ef:c8:a8:79:9c:28:61:0d:96:b0:c7:12:81:b7:05:
         26:b9:76:19:4c:80:4d:2e:a7:71:33:03:df:4e:be:61:0e:ea:
         24:07:95:f7:53:10:b7:b3:c0:71:55:e7:37:62:54:3f:83:1b:
         37:5d:a7:f3
```

而 `chain1.pem` 应当是签发证书 `cert1.pem` 到 CA 根证书中间的证书链条；`fullchain.pem` 是包含了 **签发证书** 和 **中间证书链** 在内的 **完整证书链条**。

## **记坑**

这次试用 Vert.x HTTPS Server 作为后端。Server 初始化代码是这样写的：

```java
public void init(final Vertx vertx) {
	server = vertx.createHttpServer(new HttpServerOptions()
		.setSsl(true)
		.setPemKeyCertOptions(new PemKeyCertOptions()
			.setKeyPath(Config.getConfig().get("tls", "keyPath"))
			.setCertPath(Config.getConfig().get("tls", "certPath"))
		)
	);
}
```

关于 `keyPath`，很显然是使用私钥 `privkey1.pem`；而证书路径，我一开始使用的是 `cert1.pem`，即只有签发证书不包含证书链的那个 keystore。

然后微信小程序前端就出了问题：测试时都是 OK 的，真机调试时，iOS OK，Android 的请求无法发出去。虽然用了一些在线测试网站都正常，但还是没解决问题。Baidu 上搜索没有一个有效答案 (顺便真心吐槽一下国内的技术氛围)，反正大致意思都是说证书有问题。

后来从上面的 *nginx* 配置文件中受到启发。在 *nginx* 的配置中，私钥用的是 `privkey.pem`，证书用的是 `fullchain.pem`。看来，如果缺少了中间的证书链，HTTPS 的认证不一定能成功。另外还在 [StackOverflow](https://stackoverflow.com/questions/54305577/lets-encrypt-with-vert-x) 上找到了一个相关的具体问题。于是按照答案，将证书的路径由 `cert.pem` 换为 `fullchain.pem`。一开始 Android 前端好像说还是不行，我还正郁闷着呢 😓，突然就看到屏幕上打出来日志，访问来源是 *MI 6*，成功啦！😆

## References

[简书 - Let's Encrypt 证书申请及配置](https://www.jianshu.com/p/1a792f87b6fe)

[Certbot](https://certbot.eff.org/)

---

