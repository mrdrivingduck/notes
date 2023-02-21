# hexdump

Created by : Mr Dk.

2023 / 02 / 21 22:51

Hangzhou, Zhejiang, China

---

## Background

`hexdump` 被用于 ASCII、八进制、十进制、十六进制互相转换。

## Usage

```shell
$ hexdump --help
hexdump: invalid option -- '-'
usage: hexdump [-bcCdovx] [-e fmt] [-f fmt_file] [-n length]
               [-s skip] [file ...]
       hd      [-bcdovx]  [-e fmt] [-f fmt_file] [-n length]
               [-s skip] [file ...]
```

## 八进制

使用 `-b` 打印单字节八进制；使用 `-o` 打印双字节八进制：

```shell
$ hexdump -b a.txt
0000000 061 062 063 064 065 066 067 070 012 061 062 063 064 065 066 067
0000010 070 012 061 062 063 064 065 066 067 070 012 061 062 063 064 065
0000020 066 067 070 012 012
0000025

$ hexdump -o a.txt
0000000  031061  032063  033065  034067  030412  031462  032464  033466
0000010  005070  031061  032063  033065  034067  030412  031462  032464
0000020  033466  005070  000012
0000025
```

## 十进制

使用 `-d` 打印双字节的十进制：

```shell
$ hexdump -d a.txt
0000000   12849   13363   13877   14391   12554   13106   13620   14134
0000010   02616   12849   13363   13877   14391   12554   13106   13620
0000020   14134   02616   00010
0000025
```

## 十六进制

使用 `-x` 打印双字节十六进制；使用 `-C` 打印单字节十六进制：

```shell
$ hexdump -x a.txt
0000000    3231    3433    3635    3837    310a    3332    3534    3736
0000010    0a38    3231    3433    3635    3837    310a    3332    3534
0000020    3736    0a38    000a
0000025

$ hexdump -C a.txt
00000000  31 32 33 34 35 36 37 38  0a 31 32 33 34 35 36 37  |12345678.1234567|
00000010  38 0a 31 32 33 34 35 36  37 38 0a 31 32 33 34 35  |8.12345678.12345|
00000020  36 37 38 0a 0a                                    |678..|
00000025
```

## ASCII 字符

使用 `-c` 打印 ASCII 字符：

```shell
$ hexdump -c a.txt
0000000   1   2   3   4   5   6   7   8  \n   1   2   3   4   5   6   7
0000010   8  \n   1   2   3   4   5   6   7   8  \n   1   2   3   4   5
0000020   6   7   8  \n  \n
0000025
```

## References

[hexdump command in Linux with examples](https://www.geeksforgeeks.org/hexdump-command-in-linux-with-examples/)

[hexdump(1) - Linux man page](https://linux.die.net/man/1/hexdump)
