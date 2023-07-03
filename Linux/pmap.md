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

可以看出可执行文件或库占用了多少内存地址空间。另外，该工具也可以用于排查内存泄漏：哪些地址空间的使用是只增不减的。

## References

[pmap(1) - Linux man page](https://linux.die.net/man/1/pmap)

[How to analyze a Linux process' memory map with pmap](https://www.redhat.com/sysadmin/pmap-command)
