# ldd

Created by : Mr Dk.

2023 / 01 / 07 14:59

Hangzhou, Zhejiang, China

---

## Background

`ldd` 用于打印程序或共享库的共享库依赖。通常情况下，`ldd` 会调用动态链接器以及环境变量中的 `LD_TRACE_LOADED_OBJECTS`，使其检查程序的动态链接依赖，并寻找和加载这些依赖。最后，显示这些依赖的名称，以及这些共享库加载后的地址。

在安全性上，`ldd` 有可能需要通过直接执行程序的方式来获取依赖，所以不能用它来获取不受信任的程序的依赖，否则将会引发任意代码执行的问题。对于不信任的程序，可以用以下方法获取其依赖：

```shell
$ objdump -p /path/to/program | grep NEEDED
```

## Usage

```shell
$ ldd --help
Usage: ldd [OPTION]... FILE...
      --help              print this help and exit
      --version           print version information and exit
  -d, --data-relocs       process data relocations
  -r, --function-relocs   process data and function relocations
  -u, --unused            print unused direct dependencies
  -v, --verbose           print all information

For bug reporting instructions, please see:
<https://bugs.launchpad.net/ubuntu/+source/glibc/+bugs>.
```

```shell
$ ldd python3.8
        linux-vdso.so.1 (0x00007fff6ab60000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f49681a4000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f4968181000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f496817b000)
        libutil.so.1 => /lib/x86_64-linux-gnu/libutil.so.1 (0x00007f4968176000)
        libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f4968027000)
        libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x00007f4967ff9000)
        libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f4967fdb000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f49683a1000)
```

使用 `-v` 选项可以递归打印每个依赖库的依赖信息和版本信息：

```shell
$ ldd -v ssh
        linux-vdso.so.1 (0x00007fff66f55000)
        libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007f1e6d5a6000)
        libcrypto.so.1.1 => /lib/x86_64-linux-gnu/libcrypto.so.1.1 (0x00007f1e6d2d0000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f1e6d2ca000)
        libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f1e6d2ae000)
        libresolv.so.2 => /lib/x86_64-linux-gnu/libresolv.so.2 (0x00007f1e6d292000)
        libgssapi_krb5.so.2 => /lib/x86_64-linux-gnu/libgssapi_krb5.so.2 (0x00007f1e6d245000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f1e6d051000)
        libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x00007f1e6cfc1000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f1e6d6a2000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f1e6cf9e000)
        libkrb5.so.3 => /lib/x86_64-linux-gnu/libkrb5.so.3 (0x00007f1e6cec1000)
        libk5crypto.so.3 => /lib/x86_64-linux-gnu/libk5crypto.so.3 (0x00007f1e6ce90000)
        libcom_err.so.2 => /lib/x86_64-linux-gnu/libcom_err.so.2 (0x00007f1e6ce89000)
        libkrb5support.so.0 => /lib/x86_64-linux-gnu/libkrb5support.so.0 (0x00007f1e6ce78000)
        libkeyutils.so.1 => /lib/x86_64-linux-gnu/libkeyutils.so.1 (0x00007f1e6ce71000)

        Version information:
        ./ssh:
                libdl.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libdl.so.2
                libresolv.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libresolv.so.2
                libcrypto.so.1.1 (OPENSSL_1_1_0) => /lib/x86_64-linux-gnu/libcrypto.so.1.1
                libgssapi_krb5.so.2 (gssapi_krb5_2_MIT) => /lib/x86_64-linux-gnu/libgssapi_krb5.so.2
                libc.so.6 (GLIBC_2.26) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.8) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.7) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.17) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.25) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libselinux.so.1:
                libdl.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libdl.so.2
                ld-linux-x86-64.so.2 (GLIBC_2.3) => /lib64/ld-linux-x86-64.so.2
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.8) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.7) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.30) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libcrypto.so.1.1:
                libdl.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libdl.so.2
                libpthread.so.0 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libpthread.so.0
                libc.so.6 (GLIBC_2.15) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.25) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.2) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.7) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.17) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.16) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libdl.so.2:
                ld-linux-x86-64.so.2 (GLIBC_PRIVATE) => /lib64/ld-linux-x86-64.so.2
                libc.so.6 (GLIBC_PRIVATE) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libz.so.1:
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libresolv.so.2:
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_PRIVATE) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libgssapi_krb5.so.2:
                libk5crypto.so.3 (k5crypto_3_MIT) => /lib/x86_64-linux-gnu/libk5crypto.so.3
                libkrb5support.so.0 (krb5support_0_MIT) => /lib/x86_64-linux-gnu/libkrb5support.so.0
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.27) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.8) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libkrb5.so.3 (krb5_3_MIT) => /lib/x86_64-linux-gnu/libkrb5.so.3
        /lib/x86_64-linux-gnu/libc.so.6:
                ld-linux-x86-64.so.2 (GLIBC_2.3) => /lib64/ld-linux-x86-64.so.2
                ld-linux-x86-64.so.2 (GLIBC_PRIVATE) => /lib64/ld-linux-x86-64.so.2
        /lib/x86_64-linux-gnu/libpcre2-8.so.0:
                libpthread.so.0 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libpthread.so.0
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libpthread.so.0:
                ld-linux-x86-64.so.2 (GLIBC_2.2.5) => /lib64/ld-linux-x86-64.so.2
                ld-linux-x86-64.so.2 (GLIBC_PRIVATE) => /lib64/ld-linux-x86-64.so.2
                libc.so.6 (GLIBC_2.7) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.2) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_PRIVATE) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libkrb5.so.3:
                libresolv.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libresolv.so.2
                libresolv.so.2 (GLIBC_2.9) => /lib/x86_64-linux-gnu/libresolv.so.2
                libk5crypto.so.3 (k5crypto_3_MIT) => /lib/x86_64-linux-gnu/libk5crypto.so.3
                libkrb5support.so.0 (krb5support_0_MIT) => /lib/x86_64-linux-gnu/libkrb5support.so.0
                libkeyutils.so.1 (KEYUTILS_1.0) => /lib/x86_64-linux-gnu/libkeyutils.so.1
                libkeyutils.so.1 (KEYUTILS_1.5) => /lib/x86_64-linux-gnu/libkeyutils.so.1
                libkeyutils.so.1 (KEYUTILS_0.3) => /lib/x86_64-linux-gnu/libkeyutils.so.1
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.8) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.16) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libk5crypto.so.3:
                libkrb5support.so.0 (krb5support_0_MIT) => /lib/x86_64-linux-gnu/libkrb5support.so.0
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libcom_err.so.2:
                ld-linux-x86-64.so.2 (GLIBC_2.3) => /lib64/ld-linux-x86-64.so.2
                libpthread.so.0 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libpthread.so.0
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.17) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libkrb5support.so.0:
                libdl.so.2 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libdl.so.2
                libc.so.6 (GLIBC_2.3) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.8) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
        /lib/x86_64-linux-gnu/libkeyutils.so.1:
                libc.so.6 (GLIBC_2.3.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.7) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.14) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.4) => /lib/x86_64-linux-gnu/libc.so.6
                libc.so.6 (GLIBC_2.2.5) => /lib/x86_64-linux-gnu/libc.so.6
```

## References

[ldd(1) — Linux manual page](https://man7.org/linux/man-pages/man1/ldd.1.html)
