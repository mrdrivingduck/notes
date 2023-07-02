# iostat

Created by : Mr Dk.

2023 / 07 / 02 23:30

Hangzhou, Zhejiang, China

---

## Background

`iostst` 能够显示 CPU 和 I/O 设备的统计信息。其数据主要来源于 `/proc`、`/sys`、`/dev` 等。

## Usage

```shell
$ iostat --help
Usage: iostat [ options ] [ <interval> [ <count> ] ]
Options are:
[ -c ] [ -d ] [ -h ] [ -k | -m ] [ -N ] [ -s ] [ -t ] [ -V ] [ -x ] [ -y ] [ -z ]
[ { -f | +f } <directory> ] [ -j { ID | LABEL | PATH | UUID | ... } ]
[ --dec={ 0 | 1 | 2 } ] [ --human ] [ --pretty ] [ -o JSON ]
[ [ -H ] -g <group_name> ] [ -p [ <device> [,...] | ALL ] ]
[ <device> [...] | ALL ]
```

### Information

默认打印 CPU 和所有 I/O 设备的简单统计信息。`-c` 参数只显示 CPU（上面部分），`-d` 参数只显示磁盘（下面部分）。

```shell
$ iostat
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    07/02/23        _x86_64_        (8 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           2.09    0.00    0.92    0.36    0.00   96.63

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
sda               1.76       114.08         0.00         0.00      69977          0          0
sdb               0.09         2.14         0.01         0.00       1312          4          0
sdc              23.91       730.77       982.04       297.89     448270     602400     182732
```

使用 `-x` 参数可以显示详细信息：

```shell
$ iostat -x
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    07/02/23        _x86_64_        (8 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           1.90    0.00    0.85    0.33    0.00   96.92

Device            r/s     rkB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wkB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dkB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
sda              1.54     99.97     0.62  28.81    0.94    64.79    0.00      0.00     0.00   0.00    0.00     0.00    0.00      0.00     0.00   0.00    0.00     0.00    0.00    0.00    0.00   0.18
sdb              0.07      1.87     0.00   0.00    0.13    25.23    0.00      0.01     0.00   0.00    4.50     2.00    0.00      0.00     0.00   0.00    0.00     0.00    0.00    6.00    0.00   0.01
sdc             15.57    640.39     8.74  35.94    1.28    41.13    4.54    861.94    11.92  72.41   34.16   189.73    1.02    261.12     0.01   0.83    0.48   255.64    0.94    3.05    0.18   3.60
```

### Unit

使用 `-k` 和 `-m` 表示分别以 KB 或 MB 为单位显示统计信息：

```shell
$ iostat -m
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    07/02/23        _x86_64_        (8 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           1.82    0.00    0.81    0.32    0.00   97.05

Device             tps    MB_read/s    MB_wrtn/s    MB_dscd/s    MB_read    MB_wrtn    MB_dscd
sda               1.46         0.09         0.00         0.00         68          0          0
sdb               0.07         0.00         0.00         0.00          1          0          0
sdc              20.00         0.59         0.79         0.24        437        589        178
```

### Periodically

加入两个数字作为参数，可以以指定时间间隔打印三次：

```shell
$ iostat 2 4
Linux 5.15.90.1-microsoft-standard-WSL2 (zjt-laptop)    07/02/23        _x86_64_        (8 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           1.67    0.00    0.75    0.29    0.00   97.29

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
sda               1.29        83.87         0.00         0.00      69977          0          0
sdb               0.06         1.57         0.00         0.00       1312          4          0
sdc              17.89       537.25       724.35       219.11     448270     604380     182820


avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.00    0.00    0.00    0.13    0.00   99.87

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
sda               0.00         0.00         0.00         0.00          0          0          0
sdb               0.00         0.00         0.00         0.00          0          0          0
sdc               1.00         0.00        20.00         0.00          0         40          0


avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.00    0.00    0.13    0.00    0.00   99.87

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
sda               0.00         0.00         0.00         0.00          0          0          0
sdb               0.00         0.00         0.00         0.00          0          0          0
sdc               0.00         0.00         0.00         0.00          0          0          0


avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.06    0.00    0.00    0.00    0.00   99.94

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
sda               0.00         0.00         0.00         0.00          0          0          0
sdb               0.00         0.00         0.00         0.00          0          0          0
sdc               0.00         0.00         0.00         0.00          0          0          0
```

### Device Partitions

加入 `-p` 参数可以打印设备每个分区上的统计信息：

```shell
$ iostat -m -p
Linux 5.10.134-007.ali5000.al8.x86_64 (k39a07236.sqa.eu95)      07/02/2023      _x86_64_       (104 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           1.27    0.00    1.54    0.01    0.00   97.19

Device             tps    MB_read/s    MB_wrtn/s    MB_read    MB_wrtn
nvme1n1           1.60         0.00         0.02      31500     165672
nvme1n1p1         1.60         0.00         0.02      31495     165672
nvme0n1           2.05         0.00         0.02      30416     187276
nvme0n1p1         2.05         0.00         0.02      30411     187276
nvme10n1        127.31         0.07        12.00     728935  120740654
nvme10n1p1      127.31         0.07        12.00     728932  120740654
nvme6n1         129.18         0.07        12.18     726532  122508797
nvme6n1p1       129.18         0.07        12.18     726528  122508797
nvme2n1         130.45         0.07        12.39     743078  124676636
nvme2n1p1       130.45         0.07        12.39     743074  124676636
nvme5n1         129.03         0.07        12.32     735269  123958529
nvme5n1p1       129.03         0.07        12.32     735265  123958529
nvme3n1         130.37         0.07        12.35     725545  124301518
nvme3n1p1       130.37         0.07        12.35     725541  124301518
nvme7n1         126.96         0.07        12.18     722887  122517772
nvme7n1p1       126.96         0.07        12.18     722883  122517772
nvme12n1        125.60         0.07        11.94     722299  120133296
nvme12n1p1      125.60         0.07        11.94     722295  120133296
nvme9n1         125.97         0.07        12.08     729875  121594725
nvme9n1p1       125.97         0.07        12.08     729872  121594725
nvme8n1         126.90         0.07        12.14     743049  122178102
nvme8n1p1       126.90         0.07        12.14     743045  122178102
nvme11n1        125.40         0.07        11.94     722724  120163025
nvme11n1p1      125.40         0.07        11.94     722720  120163025
nvme13n1        125.15         0.07        11.90     730468  119785017
nvme13n1p1      125.15         0.07        11.90     730464  119785017
nvme4n1         128.15         0.07        12.34     732513  124123440
nvme4n1p1       128.15         0.07        12.34     732510  124123440
sda              25.03         0.08         0.14     810028    1409423
sda1              0.00         0.00         0.00          7          0
sda2              0.00         0.00         0.00         66        382
sda3             25.02         0.08         0.14     809939    1409041
md0               6.66         0.01         0.04      65485     356833
md1            1584.99         0.87       145.76    8763116 1466681517
loop0             0.00         0.00         0.00          0          0
loop1             0.00         0.00         0.00          3          0
```

## References

[iostat command in Linux with examples](https://www.geeksforgeeks.org/iostat-command-in-linux-with-examples/)

[iostat(1) - Linux man page](https://linux.die.net/man/1/iostat)
