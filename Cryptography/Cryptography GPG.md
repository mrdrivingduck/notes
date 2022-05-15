# Cryptography - GPG

Created by : Mr Dk.

2020 / 12 / 09 12:53

Nanjing, Jiangsu, China

---

## About

GNU Privacy Guard (GnuPG / GPG) 是一个密码学的自由软件，用于加解密、数字签名以及密钥管理。

## Generate

需要的信息包括：

- 加密算法
- 密钥长度
- 有效时间
- 名字 + 邮箱
- 注释

```console
$ gpg --full-generate-key

gpg: key 762A231FF8172D47 marked as ultimately trusted
gpg: revocation certificate stored as '/home/mrdrivingduck/.gnupg/openpgp-revocs.d/8A41********************************2D47.rev'
public and secret key created and signed.

pub   rsa3072 2020-12-09 [SC] [expires: 2022-12-09]
      8A41********************************2D47
uid                      mrdrivingduck <562655624@q.com>
sub   rsa3072 2020-12-09 [E] [expires: 2022-12-09]
```

查看 GPG key：

```console
$ gpg --list-keys
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   2  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 2u
gpg: next trustdb check due at 2022-12-09
/home/mrdrivingduck/.gnupg/pubring.kbx
--------------------------------------
pub   rsa3072 2020-12-09 [SC] [expires: 2022-12-09]
      8A41********************************2D47
uid           [ultimate] mrdrivingduck <562655624@q.com>
sub   rsa3072 2020-12-09 [E] [expires: 2022-12-09]
```

导出并粘贴到 GitHub 上：

```console
$ gpg --armor --export 8A41********************************2D47
-----BEGIN PGP PUBLIC KEY BLOCK-----

...
-----END PGP PUBLIC KEY BLOCK-----
```

## Git Configuration

```console
$ git config --global user.signingkey 8*******7
```

在 commit 中使用 GPG key 来签名只需要加上 `-S` 参数：

```console
$ git commit
--gpg-sign             -S       -- GPG-sign the commit
```

当然也可以直接全局开启 GPG 签名：

```console
$ git config --global commit.gpgsign true
false      -- do not always GPG-sign commits (default)
off    no  -- do not always GPG-sign commits
true       -- always GPG-sign commits (current)
yes    on  -- always GPG-sign commits
```

## Expire

> The expiration time of a key may be updated with the command expire from the key edit menu. If no key is selected the expiration time of the primary key is updated. Otherwise the expiration time of the selected subordinate key is updated.
>
> A key's expiration time is associated with the key's self-signature. The expiration time is updated by deleting the old self-signature and adding a new self-signature. Since correspondents will not have deleted the old self-signature, they will see an additional self-signature on the key when they update their copy of your key. The latest self-signature takes precedence, however, so all correspondents will unambiguously know the expiration times of your keys.

密钥延期：

```console
$ gpg --edit-key 8A41********************************2D47
gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Secret key is available.

sec  rsa3072/762A231FF8172D47
     created: 2020-12-09  expires: 2022-12-09  usage: SC
     trust: ultimate      validity: ultimate
ssb  rsa3072/0E60F78C5F8DBFAE
     created: 2020-12-09  expires: 2022-12-09  usage: E
[ultimate] (1). mrdrivingduck <562655624@q.com>
```

```
gpg> expire
Changing expiration time for the primary key.
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 5y
Key expires at Mon Dec  8 11:19:19 2025 CST
Is this correct? (y/N) y

sec  rsa3072/762A231FF8172D47
     created: 2020-12-09  expires: 2025-12-08  usage: SC
     trust: ultimate      validity: ultimate
ssb  rsa3072/0E60F78C5F8DBFAE
     created: 2020-12-09  expires: 2022-12-09  usage: E
[ultimate] (1). mrdrivingduck <562655624@q.com>
```

```
gpg> key 1

sec  rsa3072/762A231FF8172D47
     created: 2020-12-09  expires: 2025-12-08  usage: SC
     trust: ultimate      validity: ultimate
ssb* rsa3072/0E60F78C5F8DBFAE
     created: 2020-12-09  expires: 2022-12-09  usage: E
[ultimate] (1). mrdrivingduck <562655624@q.com>

gpg> expire
Changing expiration time for a subkey.
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 5y
Key expires at Mon Dec  8 11:19:37 2025 CST
Is this correct? (y/N) y

sec  rsa3072/762A231FF8172D47
     created: 2020-12-09  expires: 2025-12-08  usage: SC
     trust: ultimate      validity: ultimate
ssb* rsa3072/0E60F78C5F8DBFAE
     created: 2020-12-09  expires: 2025-12-08  usage: E
[ultimate] (1). mrdrivingduck <562655624@q.com>
```

最终还要保存修改：

```
gpg> save
```

## Remove

首先删除私钥：(**慎重**)

```console
$ gpg --delete-secret-keys 8A41DCE7DCD03B5F7FA850ED762A231FF8172D47
gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.


sec  rsa3072/762A231FF8172D47 2020-12-09 mrdrivingduck <562655624@q.com>

Delete this key from the keyring? (y/N) y
This is a secret key! - really delete? (y/N) y
```

删除公钥：

```console
$ gpg --delete-keys 8A41DCE7DCD03B5F7FA850ED762A231FF8172D47
gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

pub  rsa3072/762A231FF8172D47 2020-12-09 mrdrivingduck <562655624@q.com>

Delete this key from the keyring? (y/N) y
```

## Transfer

密钥跨系统移动。首先在一台电脑上将密钥导出：

```console
$ gpg --export-secret-keys YOUR_ID_HERE > private.key
```

将 `private.key` 拷贝到新系统上后导入：

```console
$ gpg --import private.key
gpg: key ****************: "mrdrivingduck <562655624@qq.com>" 2 new signatures
gpg: key ****************: secret key imported
gpg: Total number processed: 1
gpg:         new signatures: 2
gpg:       secret keys read: 1
gpg:  secret keys unchanged: 1
```

---

## References

[GPG: Extract private key and import on different machine](https://makandracards.com/makandra-orga/37763-gpg-extract-private-key-and-import-on-different-machine)

[TripleZ's Blog - 让 Git Commit 带上你的 GPG 签名](https://blog.triplez.cn/let-git-commit-brings-with-your-gpg-signature/)

[The GNU Privacy Handbook - Chapter 3. Key Management](https://www.gnupg.org/gph/en/manual/c235.html#AEN328)

[GitHub Docs - Updating an expired GPG key](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/updating-an-expired-gpg-key)

[How to renew a (soon to be) expired GPG key](https://filipe.kiss.ink/renew-expired-gpg-key/)

---
