# Syzkaller - Description Syntax

Created by : Mr Dk.

2019 / 07 / 04 14:49

Nanjing, Jiangsu, China

---

## Syscall Descriptions

`syz-fuzzer` 进程产生测试 kernel 系统调用的程序，由 `syz-executor` 进行执行。对应的系统调用接口需要在指定目录下被声明，从而使 syzkaller 能够利用这些系统调用接口生成程序。

系统调用描述文件位于 syzkaller 目录的 `/sys/:OS/:*.txt` 中：比如，`sys/linux/dev_snd_midi.txt` 中包含了 Linux MIDI 接口的描述。

---

## Syscall Descriptions Syntax

### Overview

```
open(file filename, flags flags[open_flags], mode flags[open_mode]) fd
read(fd fd, buf buffer[out], count len[buf]) len[buf]
close(fd fd)
open_mode = S_IRUSR, S_IWUSR, S_IXUSR, S_IRGRP, S_IWGRP, S_IXGRP, S_IROTH, S_IWOTH, S_IXOTH
```

### Entry

```
syscallname "(" [arg ["," arg]*] ")" [type]
```

即，系统调用名，之后带括号，括号内是参数，最后是系统调用的返回值类型，如：

```
open(...) fd
```

* 系统调用名为 `open`，返回值类型为 `fd`

### Arguments

```
arg = argname type
```

每个参数可以分为两部分：

* 参数名
* 参数类型

如：

```
open(file filename, ...) fd
```

* 第一个参数名为 `file`
* 参数类型为 `filename`

### Argument Name

```
argname = identifier
```

### Type

```
type = typename [ "[" type-options "]" ]
```

类型包含两部分：

* `typename` - 类型名
  * `const`
  * `intN`
  * `intptr`
  * `flags`
  * `array`
  * `ptr`
  * `string`
  * `strconst`
  * `filename`
  * `len`
  * `bytesize`
  * `bytesizeN`
  * `bitsize`
  * `vma`
  * `proc`
* `type-options` - 类型选项，在类型名后加 `[]` (可选)

### Ints

* `int8`
* `int16`
* `int32`
* `int64`
* `intptr` - 代表一个指针尺寸的整数，比如 C 中的 `long`

加入 `be` 后缀表示大端 - `int16be`

可以对整数指定范围：`int32[0:100]`，也可以指定位长度：`int64:N`：

```
example_struct {
    f0  int8                  # random 1-byte integer
    f1  const[0x42, int16be]  # const 2-byte integer with value 0x4200 (big-endian 0x42)
    f2  int32[0:100]          # random 4-byte integer with values from 0 to 100 inclusive
    f3  int64:20              # random 20-bit bitfield
}
```

### Structs

```
<structname> {
    fieldname type
    ...
} [ <attribute> ]
```

| Attribute   | Description                      |
| ----------- | -------------------------------- |
| `"packed"`  | No paddings, default alignment 1 |
| `"align_N"` | Alignment N                      |
| `"size"`    | Padded up to the specified size  |

### Unions

```
<unionname> {
    fieldname type
    ...
} [ <attribute> ]
```

| Attribute  | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| `"varlen"` | union size is not maximum of all option but rather length of a particular chosen option |
| `"size"`   | the union is padded up to the specified size                 |

### Resources

代表需要从一个系统调用的输出中传递到另一个系统调用的输入的值：

```
resource <identifier> [<underlying_type>] ...
```

比如：

```
resource fd[int32]: 0xffffffffffffffff, AT_FDCWD, 1000000
resource sock[fd]
resource sock_unix[sock]

socket(...) sock
accept(fd sock, ...) sock
listen(fd sock, backlog int32)
```

* "resource" 声明
* resource 名称
* resource 的类型
  * `int8`、`int16`、`int32`、`int64` 、`intptr` 或另一个 resource (继承)
* 冒号之后可以加其余选项
  * resource 可以使用一些特殊值

### Type Aliases

可以使用低层类型构造新的类型

```
type identifier underlying_type
```

比如：

```
type signalno int32[0:65]
type net_port proc[20000, 4, int16be]
```

一些内置的构造类型：

```
type bool8	int8[0:1]
type bool16	int16[0:1]
type bool32	int32[0:1]
type bool64	int64[0:1]
type boolptr	intptr[0:1]

type filename string[filename]

type buffer[DIR] ptr[DIR, array[int8]]
```

### Type Templates

### Length

### Proc

---

