# rpm2cpio / rpm2archive

Created by : Mr Dk.

2023 / 07 / 16 22:45

Hangzhou, Zhejiang, China

---

## Background

`rpm2cpio` / `rpm2archive` 分别用于从 RPM 包解出 cpio / tar 归档格式的文件。[**cpio**](https://en.wikipedia.org/wiki/Cpio) 和 [**tar**](<https://en.wikipedia.org/wiki/Tar_(computing)>) 都是类 UNIX 系统上较为常见的归档格式。**归档** 的作用是将多个分离的文件拼接到同一个流中，而并不进行压缩。

从 RPM 中解出归档格式的数据后，输入到相应的归档解析程序中，就可以在文件系统中恢复出 RPM 包内的目录结构。

## Usage

```shell
$ rpm2cpio --help
Usage: rpm2cpio file.rpm

$ rpm2archive --help
Usage: rpm2archive [file.rpm ...]
```

## Cpio

将 RPM 中的文件目录通过 cpio 恢复到当前目录：

```shell
rpm2cpio xxx.rpm | cpio -dimv
```

## Tar

将 RPM 中的文件归档并压缩到 `.tgz` 文件中，然后使用 `tar` 解开：

```shell
rpm2archive xxx.rpm
tar -xzvf xxx.rpm.tgz
```

## References

[rpm2cpio(8) — Linux manual page](https://man7.org/linux/man-pages/man8/rpm2cpio.8.html)

[rpm2archive(8) — Linux manual page](https://man7.org/linux/man-pages/man8/rpm2archive.8.html)

[superuser - What is the difference between TAR vs CPIO archive file formats?](https://superuser.com/questions/343915/what-is-the-difference-between-tar-vs-cpio-archive-file-formats)
