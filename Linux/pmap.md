# pmap

Created by : Mr Dk.

2023 / 07 / 03 23:04

Hangzhou, Zhejiang, China

---

## Background

`pmap` 用于打印进程的内存映射情况。其数据来源于 `/proc/PID/smaps`，并被加工为用户友好的阅读形式。

## Usage

```shell
$ pmap --help

Usage:
 pmap [options] PID [PID ...]

Options:
 -x, --extended              show details
 -X                          show even more details
            WARNING: format changes according to /proc/PID/smaps
 -XX                         show everything the kernel provides
 -c, --read-rc               read the default rc
 -C, --read-rc-from=<file>   read the rc from file
 -n, --create-rc             create new default rc
 -N, --create-rc-to=<file>   create new rc to file
            NOTE: pid arguments are not allowed with -n, -N
 -d, --device                show the device format
 -q, --quiet                 do not display header and footer
 -p, --show-path             show path in the mapping
 -A, --range=<low>[,<high>]  limit results to the given range

 -h, --help     display this help and exit
 -V, --version  output version information and exit

For more details see pmap(1).
```

比如观察 `zsh` 进程的内存映射情况：

```shell
$ pmap 10
10:   -zsh
00005575663f0000     92K r---- zsh
0000557566407000    760K r-x-- zsh
00005575664c5000    108K r---- zsh
00005575664e0000      8K r---- zsh
00005575664e2000     24K rw--- zsh
00005575664e8000     80K rw---   [ anon ]
00005575669c1000   2780K rw---   [ anon ]
00007f3a022ee000     12K r---- computil.so
00007f3a022f1000     52K r-x-- computil.so
00007f3a022fe000      8K r---- computil.so
00007f3a02300000      4K r---- computil.so
00007f3a02301000      4K rw--- computil.so
00007f3a02302000   2560K r--s- Unix.zwc
00007f3a0258d000    148K r--s- Zsh.zwc
00007f3a025c9000    100K r--s- Zle.zwc
00007f3a025fc000     12K r---- system.so
00007f3a025ff000      8K r-x-- system.so
00007f3a02601000      4K r---- system.so
00007f3a02602000      4K ----- system.so
00007f3a02603000      4K r---- system.so
00007f3a02604000      4K rw--- system.so
00007f3a0260d000    100K r--s- Misc.zwc
00007f3a02626000    144K r--s- Base.zwc
00007f3a0264a000      4K r---- stat.so
00007f3a0264b000      8K r-x-- stat.so
00007f3a0264d000      4K r---- stat.so
00007f3a0264e000      4K r---- stat.so
00007f3a0264f000      4K rw--- stat.so
00007f3a02651000      4K r---- zleparameter.so
00007f3a02652000      4K r-x-- zleparameter.so
00007f3a02653000      4K r---- zleparameter.so
00007f3a02654000      4K r---- zleparameter.so
00007f3a02655000      4K rw--- zleparameter.so
00007f3a0265a000      4K r---- regex.so
00007f3a0265b000      4K r-x-- regex.so
00007f3a0265c000      4K r---- regex.so
00007f3a0265d000      4K r---- regex.so
00007f3a0265e000      4K rw--- regex.so
00007f3a0265f000      4K r---- langinfo.so
00007f3a02660000      4K r-x-- langinfo.so
00007f3a02661000      4K r---- langinfo.so
00007f3a02662000      4K r---- langinfo.so
00007f3a02663000      4K rw--- langinfo.so
00007f3a02664000     16K r---- complist.so
00007f3a02668000     44K r-x-- complist.so
00007f3a02673000      4K r---- complist.so
00007f3a02674000      4K ----- complist.so
00007f3a02675000      4K r---- complist.so
00007f3a02676000      4K rw--- complist.so
00007f3a02677000      4K r---- datetime.so
00007f3a02678000      4K r-x-- datetime.so
00007f3a02679000      4K r---- datetime.so
00007f3a0267a000      4K r---- datetime.so
00007f3a0267b000      4K rw--- datetime.so
00007f3a0267c000     96K r--s- Completion.zwc
00007f3a02694000     12K r---- parameter.so
00007f3a02697000     24K r-x-- parameter.so
00007f3a0269d000      8K r---- parameter.so
00007f3a0269f000      4K ----- parameter.so
00007f3a026a0000      4K r---- parameter.so
00007f3a026a1000      4K rw--- parameter.so
00007f3a026a2000      8K r---- zutil.so
00007f3a026a4000     20K r-x-- zutil.so
00007f3a026a9000      4K r---- zutil.so
00007f3a026aa000      4K ----- zutil.so
00007f3a026ab000      4K r---- zutil.so
00007f3a026ac000      4K rw--- zutil.so
00007f3a026ad000     32K r---- complete.so
00007f3a026b5000    104K r-x-- complete.so
00007f3a026cf000     12K r---- complete.so
00007f3a026d2000      4K ----- complete.so
00007f3a026d3000      4K r---- complete.so
00007f3a026d4000      4K rw--- complete.so
00007f3a026d5000     88K r---- zle.so
00007f3a026eb000    168K r-x-- zle.so
00007f3a02715000     40K r---- zle.so
00007f3a0271f000      8K r---- zle.so
00007f3a02721000     28K rw--- zle.so
00007f3a02728000      4K rw---   [ anon ]
00007f3a0272d000      4K r---- terminfo.so
00007f3a0272e000      4K r-x-- terminfo.so
00007f3a0272f000      4K r---- terminfo.so
00007f3a02730000      4K r---- terminfo.so
00007f3a02731000      4K rw--- terminfo.so
00007f3a02736000     16K rw---   [ anon ]
00007f3a0273a000    348K r---- LC_CTYPE
00007f3a02791000      4K r---- LC_NUMERIC
00007f3a02792000      4K r---- LC_TIME
00007f3a02793000      4K r---- LC_COLLATE
00007f3a02794000      4K r---- LC_MONETARY
00007f3a02795000     28K r--s- gconv-modules.cache
00007f3a0279c000      8K rw---   [ anon ]
00007f3a0279e000    160K r---- libc.so.6
00007f3a027c6000   1620K r-x-- libc.so.6
00007f3a0295b000    352K r---- libc.so.6
00007f3a029b3000     16K r---- libc.so.6
00007f3a029b7000      8K rw--- libc.so.6
00007f3a029b9000     52K rw---   [ anon ]
00007f3a029c6000     56K r---- libm.so.6
00007f3a029d4000    496K r-x-- libm.so.6
00007f3a02a50000    364K r---- libm.so.6
00007f3a02aab000      4K r---- libm.so.6
00007f3a02aac000      4K rw--- libm.so.6
00007f3a02aad000     56K r---- libtinfo.so.6.3
00007f3a02abb000     68K r-x-- libtinfo.so.6.3
00007f3a02acc000     56K r---- libtinfo.so.6.3
00007f3a02ada000     16K r---- libtinfo.so.6.3
00007f3a02ade000      4K rw--- libtinfo.so.6.3
00007f3a02adf000     12K r---- libcap.so.2.44
00007f3a02ae2000     16K r-x-- libcap.so.2.44
00007f3a02ae6000      8K r---- libcap.so.2.44
00007f3a02ae8000      4K r---- libcap.so.2.44
00007f3a02ae9000      4K rw--- libcap.so.2.44
00007f3a02aea000      4K r---- SYS_LC_MESSAGES
00007f3a02aeb000      4K r---- LC_PAPER
00007f3a02aec000      4K r---- LC_NAME
00007f3a02aed000      4K r---- LC_ADDRESS
00007f3a02aee000      4K r---- LC_TELEPHONE
00007f3a02aef000      4K r---- LC_MEASUREMENT
00007f3a02af0000      8K rw---   [ anon ]
00007f3a02af2000      8K r---- ld-linux-x86-64.so.2
00007f3a02af4000    168K r-x-- ld-linux-x86-64.so.2
00007f3a02b1e000     44K r---- ld-linux-x86-64.so.2
00007f3a02b29000      4K r---- LC_IDENTIFICATION
00007f3a02b2a000      8K r---- ld-linux-x86-64.so.2
00007f3a02b2c000      8K rw--- ld-linux-x86-64.so.2
00007ffc8c720000    308K rw---   [ stack ]
00007ffc8c7f2000     16K r----   [ anon ]
00007ffc8c7f6000      8K r-x--   [ anon ]
 total            12308K
```

加上 `-x` 参数可以显示更详细的信息：

```shell
$ pmap -x 1245
1245:   -zsh
Address           Kbytes     RSS   Dirty Mode  Mapping
00005649bd87d000      92      92       0 r---- zsh
00005649bd894000     760     760       0 r-x-- zsh
00005649bd952000     108      64       0 r---- zsh
00005649bd96d000       8       8       8 r---- zsh
00005649bd96f000      24      24      24 rw--- zsh
00005649bd975000      80      40      40 rw---   [ anon ]
00005649be532000    2692    2644    2644 rw---   [ anon ]
00007f1d18034000     100      96       0 r--s- Zle.zwc
00007f1d18067000      12      12       0 r---- system.so
00007f1d1806a000       8       8       0 r-x-- system.so
00007f1d1806c000       4       4       0 r---- system.so
00007f1d1806d000       4       0       0 ----- system.so
00007f1d1806e000       4       4       4 r---- system.so
00007f1d1806f000       4       4       4 rw--- system.so
00007f1d18078000     100     100       0 r--s- Misc.zwc
00007f1d18091000     144      60       0 r--s- Base.zwc
00007f1d180b5000       4       4       0 r---- stat.so
00007f1d180b6000       8       8       0 r-x-- stat.so
00007f1d180b8000       4       4       0 r---- stat.so
00007f1d180b9000       4       4       4 r---- stat.so
00007f1d180ba000       4       4       4 rw--- stat.so
00007f1d180bc000       4       4       0 r---- zleparameter.so
00007f1d180bd000       4       4       0 r-x-- zleparameter.so
00007f1d180be000       4       4       0 r---- zleparameter.so
00007f1d180bf000       4       4       4 r---- zleparameter.so
00007f1d180c0000       4       4       4 rw--- zleparameter.so
00007f1d180c5000       4       4       0 r---- regex.so
00007f1d180c6000       4       4       0 r-x-- regex.so
00007f1d180c7000       4       4       0 r---- regex.so
00007f1d180c8000       4       4       4 r---- regex.so
00007f1d180c9000       4       4       4 rw--- regex.so
00007f1d180ca000       4       4       0 r---- langinfo.so
00007f1d180cb000       4       4       0 r-x-- langinfo.so
00007f1d180cc000       4       4       0 r---- langinfo.so
00007f1d180cd000       4       4       4 r---- langinfo.so
00007f1d180ce000       4       4       4 rw--- langinfo.so
00007f1d180cf000      16      16       0 r---- complist.so
00007f1d180d3000      44      44       0 r-x-- complist.so
00007f1d180de000       4       4       0 r---- complist.so
00007f1d180df000       4       0       0 ----- complist.so
00007f1d180e0000       4       4       4 r---- complist.so
00007f1d180e1000       4       4       4 rw--- complist.so
00007f1d180e2000       4       4       0 r---- datetime.so
00007f1d180e3000       4       4       0 r-x-- datetime.so
00007f1d180e4000       4       4       0 r---- datetime.so
00007f1d180e5000       4       4       4 r---- datetime.so
00007f1d180e6000       4       4       4 rw--- datetime.so
00007f1d180e7000      96      60       0 r--s- Completion.zwc
00007f1d180ff000      12      12       0 r---- parameter.so
00007f1d18102000      24      24       0 r-x-- parameter.so
00007f1d18108000       8       8       0 r---- parameter.so
00007f1d1810a000       4       0       0 ----- parameter.so
00007f1d1810b000       4       4       4 r---- parameter.so
00007f1d1810c000       4       4       4 rw--- parameter.so
00007f1d1810d000       8       8       0 r---- zutil.so
00007f1d1810f000      20      20       0 r-x-- zutil.so
00007f1d18114000       4       4       0 r---- zutil.so
00007f1d18115000       4       0       0 ----- zutil.so
00007f1d18116000       4       4       4 r---- zutil.so
00007f1d18117000       4       4       4 rw--- zutil.so
00007f1d18118000      32      32       0 r---- complete.so
00007f1d18120000     104     104       0 r-x-- complete.so
00007f1d1813a000      12      12       0 r---- complete.so
00007f1d1813d000       4       0       0 ----- complete.so
00007f1d1813e000       4       4       4 r---- complete.so
00007f1d1813f000       4       4       4 rw--- complete.so
00007f1d18140000      88      88       0 r---- zle.so
00007f1d18156000     168     168       0 r-x-- zle.so
00007f1d18180000      40      40       0 r---- zle.so
00007f1d1818a000       8       8       8 r---- zle.so
00007f1d1818c000      28      28      28 rw--- zle.so
00007f1d18193000       4       4       4 rw---   [ anon ]
00007f1d18198000       4       4       0 r---- terminfo.so
00007f1d18199000       4       4       0 r-x-- terminfo.so
00007f1d1819a000       4       4       0 r---- terminfo.so
00007f1d1819b000       4       4       4 r---- terminfo.so
00007f1d1819c000       4       4       4 rw--- terminfo.so
00007f1d181a1000      16      16      16 rw---   [ anon ]
00007f1d181a5000     348     128       0 r---- LC_CTYPE
00007f1d181fc000       4       4       0 r---- LC_NUMERIC
00007f1d181fd000       4       4       0 r---- LC_TIME
00007f1d181fe000       4       4       0 r---- LC_COLLATE
00007f1d181ff000       4       4       0 r---- LC_MONETARY
00007f1d18200000       4       4       0 r---- SYS_LC_MESSAGES
00007f1d18201000       4       4       0 r---- LC_PAPER
00007f1d18202000       4       4       0 r---- LC_NAME
00007f1d18203000       4       4       0 r---- LC_ADDRESS
00007f1d18204000       4       4       0 r---- LC_TELEPHONE
00007f1d18205000       8       8       8 rw---   [ anon ]
00007f1d18207000     160     160       0 r---- libc.so.6
00007f1d1822f000    1620    1372       0 r-x-- libc.so.6
00007f1d183c4000     352     172       0 r---- libc.so.6
00007f1d1841c000      16      16      16 r---- libc.so.6
00007f1d18420000       8       8       8 rw--- libc.so.6
00007f1d18422000      52      24      24 rw---   [ anon ]
00007f1d1842f000      56      56       0 r---- libm.so.6
00007f1d1843d000     496     244       0 r-x-- libm.so.6
00007f1d184b9000     364       0       0 r---- libm.so.6
00007f1d18514000       4       4       4 r---- libm.so.6
00007f1d18515000       4       4       4 rw--- libm.so.6
00007f1d18516000      56      56       0 r---- libtinfo.so.6.3
00007f1d18524000      68      68       0 r-x-- libtinfo.so.6.3
00007f1d18535000      56      52       0 r---- libtinfo.so.6.3
00007f1d18543000      16      16      16 r---- libtinfo.so.6.3
00007f1d18547000       4       4       4 rw--- libtinfo.so.6.3
00007f1d18548000      12      12       0 r---- libcap.so.2.44
00007f1d1854b000      16      16       0 r-x-- libcap.so.2.44
00007f1d1854f000       8       0       0 r---- libcap.so.2.44
00007f1d18551000       4       4       4 r---- libcap.so.2.44
00007f1d18552000       4       4       4 rw--- libcap.so.2.44
00007f1d18553000       4       4       0 r---- LC_MEASUREMENT
00007f1d18554000      28      28       0 r--s- gconv-modules.cache
00007f1d1855b000       8       8       8 rw---   [ anon ]
00007f1d1855d000       8       8       0 r---- ld-linux-x86-64.so.2
00007f1d1855f000     168     168       0 r-x-- ld-linux-x86-64.so.2
00007f1d18589000      44      40       0 r---- ld-linux-x86-64.so.2
00007f1d18594000       4       4       0 r---- LC_IDENTIFICATION
00007f1d18595000       8       8       8 r---- ld-linux-x86-64.so.2
00007f1d18597000       8       8       8 rw--- ld-linux-x86-64.so.2
00007fff651d2000     272     272     272 rw---   [ stack ]
00007fff6537c000      16       0       0 r----   [ anon ]
00007fff65380000       8       4       0 r-x--   [ anon ]
---------------- ------- ------- -------
total kB            9396    7792    3248
```

可以看出可执行文件或库占用了多少内存地址空间。另外，该工具也可以用于排查内存泄漏：哪些地址空间的使用是只增不减的。

## References

[pmap(1) - Linux man page](https://linux.die.net/man/1/pmap)

[How to analyze a Linux process' memory map with pmap](https://www.redhat.com/sysadmin/pmap-command)
