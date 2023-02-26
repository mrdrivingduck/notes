# fio

Created by : Mr Dk.

2023 / 02 / 25 22:55

Hangzhou, Zhejiang, China

---

## Background

`fio` 是它的作者因厌烦了为测试不同的 I/O 负载的性能数据而需要写不同的测试而开发的。它无需写任何 test case 就可以模拟出不同的 I/O 负载。它的作者希望 `fio` 足够灵活，以便能够面对各种各样的 I/O 场景。从大体上，`fio` 会使用一些线程 / 进程来模拟用户指定的 I/O pattern。

## Usage

```shell
$ fio -h
fio-3.28
fio [options] [job options] <job file(s)>
  --debug=options       Enable debug logging. May be one/more of:
                        process,file,io,mem,blktrace,verify,random,parse,
                        diskutil,job,mutex,profile,time,net,rate,compress,
                        steadystate,helperthread,zbd
  --parse-only          Parse options only, don't start any IO
  --merge-blktrace-only Merge blktraces only, don't start any IO
  --output              Write output to file
  --bandwidth-log       Generate aggregate bandwidth logs
  --minimal             Minimal (terse) output
  --output-format=type  Output format (terse,json,json+,normal)
  --terse-version=type  Set terse version output format (default 3, or 2 or 4)
  --version             Print version info and exit
  --help                Print this page
  --cpuclock-test       Perform test/validation of CPU clock
  --crctest=[type]      Test speed of checksum functions
  --cmdhelp=cmd         Print command help, "all" for all of them
  --enghelp=engine      Print ioengine help, or list available ioengines
  --enghelp=engine,cmd  Print help for an ioengine cmd
  --showcmd             Turn a job file into command line options
  --eta=when            When ETA estimate should be printed
                        May be "always", "never" or "auto"
  --eta-newline=t       Force a new line for every 't' period passed
  --status-interval=t   Force full status dump every 't' period passed
  --readonly            Turn on safety read-only checks, preventing writes
  --section=name        Only run specified section in job file, multiple sections can be specified
  --alloc-size=kb       Set smalloc pool to this size in kb (def 16384)
  --warnings-fatal      Fio parser warnings are fatal
  --max-jobs=nr         Maximum number of threads/processes to support
  --server=args         Start a backend fio server
  --daemonize=pidfile   Background fio server, write pid to file
  --client=hostname     Talk to remote backend(s) fio server at hostname
  --remote-config=file  Tell fio server to load this local job file
  --idle-prof=option    Report cpu idleness on a system or percpu basis
                        (option=system,percpu) or run unit work
                        calibration only (option=calibrate)
  --inflate-log=log     Inflate and output compressed log
  --trigger-file=file   Execute trigger cmd when file exists
  --trigger-timeout=t   Execute trigger at this time
  --trigger=cmd         Set this command as local trigger
  --trigger-remote=cmd  Set this command as remote trigger
  --aux-path=path       Use this path for fio state generated files

Fio was written by Jens Axboe <axboe@kernel.dk>
```

### Device / File

I/O 测试的对象可以是块设备或者是文件。如果是文件，还支持对一系列文件进行测试。使用 `--filename` 参数来指定。

### Read / Write Pattern

使用 `--rw` 参数指定不同的 I/O pattern：

- `read`：顺序读
- `write`：顺序写
- `randread`：随机读
- `randwrite`：随机写
- `rw`：混合顺序读写
- `randrw`：混合随机读写

默认的混合百分比是 1:1。读写混合比例可调整。

### Block Size

使用 `--blocksize` 来指定 I/O 的单位，默认为 4kB。

使用 `--nrfiles` 来指定每个并发单位使用的文件数量，默认为 1。

使用 `--openfiles` 来指定同时打开的文件数量，默认与 `--nrfiles` 保持一致。

使用 `--lockmem` 来限定使用的内存量。

### Parallelism

使用 `--numjobs` 指定有多少个相同的进程 / 线程同时工作，默认为 1。

使用 `--thread` 来指定使用 `pthread_create` 创建出的线程，而不是 `fork` 产生的进程。

使用 `--group_reporting` 来指定输出整个并行组的汇总统计数据，而不是单个进程 / 线程的。

### I/O Engine

使用 `--ioengine` 参数指定每个工作进程 / 线程如何发出 I/O：

- `sync`：使用 `read` / `write` 来进行 I/O，`fseek` 被用于修改 I/O 位置
- `psync`：使用 `pread` / `pwrite`
- `vsync`：使用 `readv` / `writev`
- `libaio`
- `posixaio`
- ...

### Direct / Buffer

使用 `--direct` 使用 direct I/O；使用 `--buffered` 使用 buffered I/O。默认使用 buffered I/O。

### Initialization

默认情况下，只会在初始化阶段用随机数据填充 buffer。使用 `--zero_buffers` 可以把 buffer 初始化为全 0；使用 `--refill_buffers` 将会在每次进行 I/O 前重新填充 buffer。

### Stop Condition

使用 `--size` 来指定需要进行的 I/O 总量。当 I/O 传输达到这个总量的字节数时停止。

使用 `--runtime` 来指定运行时间。

## Results

模拟一个数据库的 I/O pattern：

- I/O pattern 为随机读写（比如说 OLTP 点查）
- 读写比例为 3:1（瞎定的）
- 固定内存（数据库 Buffer Pool）
- Direct I/O
- 并发数为 50（数据库连接数量）
- Block Size 为 8kB（PostgreSQL 默认值）
- 每个进程打开 8 个文件

对我的笔记本上的 SSD 和 HDD 做一个测试。不知道是不是因为对块设备的测试会随意写入块设备上的任何地址，测试完毕后两个磁盘上的系统全部都启动不了了 😧。

### SSD

```shell
$ sudo fio \
--filename=/dev/nvme0n1 --direct=1 \
--rw=randrw --rwmixread=75 \
--ioengine=psync --bs=8k --lockmem=4mb \
--numjobs=50 --nrfiles=8 \
--runtime=180 --group_reporting --name=TEST

TEST: (g=0): rw=randrw, bs=(R) 8192B-8192B, (W) 8192B-8192B, (T) 8192B-8192B, ioengine=psync, iodepth=1
...
fio-3.28
Starting 50 processes
Jobs: 50 (f=50): [m(50)][100.0%][r=77.7MiB/s,w=25.7MiB/s][r=9942,w=3289 IOPS][eta 00m:00s]
TEST: (groupid=0, jobs=50): err= 0: pid=35801: Sun Feb 26 00:00:00 2023
  read: IOPS=49.5k, BW=387MiB/s (406MB/s)(68.0GiB/180061msec)
    clat (usec): min=30, max=538011, avg=909.71, stdev=5033.14
     lat (usec): min=30, max=538012, avg=909.86, stdev=5033.15
    clat percentiles (usec):
     |  1.00th=[   180],  5.00th=[   231], 10.00th=[   265], 20.00th=[   297],
     | 30.00th=[   322], 40.00th=[   355], 50.00th=[   424], 60.00th=[   494],
     | 70.00th=[   545], 80.00th=[   685], 90.00th=[  1188], 95.00th=[  1450],
     | 99.00th=[ 21365], 99.50th=[ 25560], 99.90th=[ 49546], 99.95th=[ 56886],
     | 99.99th=[227541]
   bw (  KiB/s): min= 2560, max=741643, per=100.00%, avg=397456.34, stdev=5721.71, samples=17944
   iops        : min=  320, max=92704, avg=49680.10, stdev=715.20, samples=17944
  write: IOPS=16.5k, BW=129MiB/s (135MB/s)(22.7GiB/180061msec); 0 zone resets
    clat (usec): min=16, max=301913, avg=286.71, stdev=1422.05
     lat (usec): min=16, max=301913, avg=287.16, stdev=1422.06
    clat percentiles (usec):
     |  1.00th=[   31],  5.00th=[   60], 10.00th=[   88], 20.00th=[  147],
     | 30.00th=[  188], 40.00th=[  210], 50.00th=[  225], 60.00th=[  239],
     | 70.00th=[  269], 80.00th=[  359], 90.00th=[  400], 95.00th=[  424],
     | 99.00th=[  668], 99.50th=[  701], 99.90th=[31327], 99.95th=[38536],
     | 99.99th=[44827]
   bw (  KiB/s): min=  800, max=272308, per=100.00%, avg=133434.13, stdev=1912.32, samples=17824
   iops        : min=  100, max=34036, avg=16677.77, stdev=239.03, samples=17824
  lat (usec)   : 20=0.03%, 50=0.88%, 100=2.14%, 250=19.06%, 500=48.57%
  lat (usec)   : 750=15.33%, 1000=2.71%
  lat (msec)   : 2=10.16%, 4=0.11%, 10=0.07%, 20=0.08%, 50=0.80%
  lat (msec)   : 100=0.06%, 250=0.01%, 500=0.01%, 750=0.01%
  cpu          : usr=0.86%, sys=1.62%, ctx=11923220, majf=0, minf=950
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=8919086,2974324,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
   READ: bw=387MiB/s (406MB/s), 387MiB/s-387MiB/s (406MB/s-406MB/s), io=68.0GiB (73.1GB), run=180061-180061msec
  WRITE: bw=129MiB/s (135MB/s), 129MiB/s-129MiB/s (135MB/s-135MB/s), io=22.7GiB (24.4GB), run=180061-180061msec

Disk stats (read/write):
  nvme0n1: ios=8919334/2974725, merge=0/234, ticks=7912550/807409, in_queue=8720940, util=99.92%
```

可以看到读 IOPS 约为 49.5k，读带宽约为 387MiB/s (406MB/s)；写 IOPS 约为 16.5k，写带宽约为 129MiB/s (135MB/s)。

### HDD

```shell
$ sudo fio \
--filename=/dev/sda --direct=1 \
--rw=randrw --rwmixread=75 \
--ioengine=psync --bs=8k --lockmem=4mb \
--numjobs=50 --nrfiles=8 \
--runtime=180 --group_reporting --name=TEST

TEST: (g=0): rw=randrw, bs=(R) 8192B-8192B, (W) 8192B-8192B, (T) 8192B-8192B, ioengine=psync, iodepth=1
...
fio-3.28
Starting 50 processes
Jobs: 50 (f=50): [m(50)][100.0%][r=792KiB/s,w=256KiB/s][r=99,w=32 IOPS][eta 00m:00s]
TEST: (groupid=0, jobs=50): err= 0: pid=39682: Sun Feb 26 00:12:59 2023
  read: IOPS=93, BW=750KiB/s (768kB/s)(132MiB/180761msec)
    clat (msec): min=17, max=2528, avg=462.65, stdev=347.01
     lat (msec): min=17, max=2528, avg=462.65, stdev=347.01
    clat percentiles (msec):
     |  1.00th=[   56],  5.00th=[   99], 10.00th=[  136], 20.00th=[  192],
     | 30.00th=[  243], 40.00th=[  300], 50.00th=[  368], 60.00th=[  447],
     | 70.00th=[  550], 80.00th=[  684], 90.00th=[  911], 95.00th=[ 1150],
     | 99.00th=[ 1737], 99.50th=[ 1989], 99.90th=[ 2232], 99.95th=[ 2265],
     | 99.99th=[ 2433]
   bw (  KiB/s): min=  749, max= 2750, per=100.00%, avg=1074.83, stdev= 8.92, samples=12554
   iops        : min=   50, max=  342, avg=132.58, stdev= 1.13, samples=12554
  write: IOPS=31, BW=253KiB/s (259kB/s)(44.6MiB/180761msec); 0 zone resets
    clat (usec): min=131, max=1963.7k, avg=205394.16, stdev=184952.85
     lat (usec): min=133, max=1963.7k, avg=205395.00, stdev=184952.86
    clat percentiles (msec):
     |  1.00th=[    5],  5.00th=[   26], 10.00th=[   38], 20.00th=[   66],
     | 30.00th=[   95], 40.00th=[  129], 50.00th=[  165], 60.00th=[  203],
     | 70.00th=[  239], 80.00th=[  288], 90.00th=[  418], 95.00th=[  584],
     | 99.00th=[  902], 99.50th=[ 1070], 99.90th=[ 1485], 99.95th=[ 1519],
     | 99.99th=[ 1972]
   bw (  KiB/s): min=  752, max= 2368, per=100.00%, avg=968.86, stdev= 7.28, samples=4698
   iops        : min=   54, max=  296, avg=119.45, stdev= 0.93, samples=4698
  lat (usec)   : 250=0.02%, 500=0.05%, 750=0.03%, 1000=0.05%
  lat (msec)   : 2=0.08%, 4=0.02%, 10=0.11%, 20=0.48%, 50=3.41%
  lat (msec)   : 100=7.69%, 250=29.87%, 500=30.70%, 750=14.58%, 1000=6.99%
  lat (msec)   : 2000=5.57%, >=2000=0.35%
  cpu          : usr=0.01%, sys=0.01%, ctx=22832, majf=0, minf=812
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=16952,5706,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
   READ: bw=750KiB/s (768kB/s), 750KiB/s-750KiB/s (768kB/s-768kB/s), io=132MiB (139MB), run=180761-180761msec
  WRITE: bw=253KiB/s (259kB/s), 253KiB/s-253KiB/s (259kB/s-259kB/s), io=44.6MiB (46.7MB), run=180761-180761msec

Disk stats (read/write):
  sda: ios=17132/5708, merge=0/0, ticks=7940082/1173972, in_queue=9116371, util=100.00%
```

可以看到读 IOPS 约为 93，读带宽约为 750KiB/s (768kB/s)；写 IOPS 约为 31，写带宽约为 253KiB/s (259kB/s)。简直和 SSD 不在一个数量级。

## References

[fio(1) - Linux man page](https://linux.die.net/man/1/fio)

[墨天轮 - 服务器 I/O 测试工具 - fio 介绍及示例](https://www.modb.pro/db/337456)

[GitHub - fio](https://github.com/axboe/fio)
