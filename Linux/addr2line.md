# addr2line

Created by : Mr Dk.

2023 / 01 / 15 17:25

Hangzhou, Zhejiang, China

---

## Background

`addr2line` 用于将程序地址翻译为代码中的源文件名和行号。

## Usage

```shell
$ addr2line --help
Usage: addr2line [option(s)] [addr(s)]
 Convert addresses into line number/file name pairs.
 If no addresses are specified on the command line, they will be read from stdin
 The options are:
  @<file>                Read options from <file>
  -a --addresses         Show addresses
  -b --target=<bfdname>  Set the binary file format
  -e --exe=<executable>  Set the input file name (default is a.out)
  -i --inlines           Unwind inlined functions
  -j --section=<name>    Read section-relative offsets instead of addresses
  -p --pretty-print      Make the output easier to read for humans
  -s --basenames         Strip directory names
  -f --functions         Show function names
  -C --demangle[=style]  Demangle function names
  -R --recurse-limit     Enable a limit on recursion whilst demangling.  [Default]
  -r --no-recurse-limit  Disable a limit on recursion whilst demangling
  -h --help              Display this information
  -v --version           Display the program's version

addr2line: supported targets: elf64-x86-64 elf32-i386 elf32-iamcu elf32-x86-64 pei-i386 pei-x86-64 elf64-l1om elf64-k1om elf64-little elf64-big elf32-little elf32-big pe-x86-64 pe-bigobj-x86-64 pe-i386 plugin srec symbolsrec verilog tekhex binary ihex
Report bugs to <http://www.sourceware.org/bugzilla/>
```

## Demo

PolarDB for PostgreSQL 内核代码中的 Assert 条件测试失败后，会在内核错误日志中打印堆栈的 trace：

```
2023-01-13 03:25:24.506 UTC [67861] [67861] LOG:
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT() [0x989e1b]
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT(polar_exceptional_condition+0x9) [0x989f09]
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT() [0x70d9c1]
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT(ExecScan+0x359) [0x6ee499]
        /home/postgres/tmp_basedir_polardb_pg_1100_bld/lib/polar_sql_plan_monitor.so(+0x2bcb) [0x7f5a3e658bcb]
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT() [0x6e4716]
        postgres(5432): postgres postgres 127.0.0.1(40586)SELECT(standard_ExecutorRun+0x17a) [0x6e4c7a]
        /home/postgres/tmp_basedir_polardb_pg_1100_bld/lib/polar_stat_plans.so(+0x429d) [0x7f5a4c09d29d]
        /home/postgres/tmp_basedir_polardb_pg_1100_bld/lib/pg_stat_statements.so(+0x40da) [0x7f5a3e6f60da]
        /home/postgres/tmp_basedir_polardb_pg_1100_bld/lib/polar_stat_sql.so(+0x2eda) [0x7f5a3e6eaeda]
        /home/postgres/tmp_basedir_polardb_pg_1100_bld/lib/auto_explain.so(+0x274a) [0x7f5a3e6a074a]
```

其中，每行最后的十六进制数即为代码中的地址。想要看这个堆栈在代码中的对应位置，就可以使用 `addr2line`。

使用 `-e` 参数指定对应的可执行文件：

```shell
$ addr2line -e postgres 0x989e1b
/home/postgres/polardb_pg/src/backend/utils/error/assert.c:90

$ addr2line -e postgres 0x6ee499
/home/postgres/polardb_pg/src/backend/executor/execScan.c:98
```

如果加上 `-f` 参数，还可以打印代码所在的函数名：

```shell
$ addr2line -e ~/tmp_basedir_polardb_pg_1100_bld/bin/postgres -f 0x70d9c1
SeqNext
/home/postgres/polardb_pg/src/backend/executor/nodeSeqscan.c:100 (discriminator 3)
```

`-i` 参数用于打印被内联函数的原始位置。

## References

[addr2line(1) - Linux man page](https://linux.die.net/man/1/addr2line)
