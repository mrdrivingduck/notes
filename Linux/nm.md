# nm

Created by : Mr Dk.

2023 / 03 / 21 16:11

Hangzhou, Zhejiang, China

---

## Background

`nm` 用于列出目标文件中的符号以及这些符号的性质。

## Usage

```shell
$ nm --help          
Usage: nm [option(s)] [file(s)]
 List symbols in [file(s)] (a.out by default).
 The options are:
  -a, --debug-syms       Display debugger-only symbols
  -A, --print-file-name  Print name of the input file before every symbol
  -B                     Same as --format=bsd
  -C, --demangle[=STYLE] Decode low-level symbol names into user-level names
                          The STYLE, if specified, can be `auto' (the default),
                          `gnu', `lucid', `arm', `hp', `edg', `gnu-v3', `java'
                          or `gnat'
      --no-demangle      Do not demangle low-level symbol names
      --recurse-limit    Enable a demangling recursion limit.  This is the default.
      --no-recurse-limit Disable a demangling recursion limit.
  -D, --dynamic          Display dynamic symbols instead of normal symbols
      --defined-only     Display only defined symbols
  -e                     (ignored)
  -f, --format=FORMAT    Use the output format FORMAT.  FORMAT can be `bsd',
                           `sysv' or `posix'.  The default is `bsd'
  -g, --extern-only      Display only external symbols
  -l, --line-numbers     Use debugging information to find a filename and
                           line number for each symbol
  -n, --numeric-sort     Sort symbols numerically by address
  -o                     Same as -A
  -p, --no-sort          Do not sort the symbols
  -P, --portability      Same as --format=posix
  -r, --reverse-sort     Reverse the sense of the sort
      --plugin NAME      Load the specified plugin
  -S, --print-size       Print size of defined symbols
  -s, --print-armap      Include index for symbols from archive members
      --size-sort        Sort symbols by size
      --special-syms     Include special symbols in the output
      --synthetic        Display synthetic symbols as well
  -t, --radix=RADIX      Use RADIX for printing symbol values
      --target=BFDNAME   Specify the target object format as BFDNAME
  -u, --undefined-only   Display only undefined symbols
      --with-symbol-versions  Display version strings after symbol names
  -X 32_64               (ignored)
  @FILE                  Read options from FILE
  -h, --help             Display this information
  -V, --version          Display this program's version number

nm: supported targets: elf64-x86-64 elf32-i386 elf32-iamcu elf32-x86-64 pei-i386 pei-x86-64 elf64-l1om elf64-k1om elf64-little elf64-big elf32-little elf32-big pe-x86-64 pe-bigobj-x86-64 pe-i386 elf64-bpfle elf64-bpfbe srec symbolsrec verilog tekhex binary ihex plugin
Report bugs to <http://bugzilla.redhat.com/bugzilla/>.
```

ChatGPT 给出的资料：

> nm is a command-line utility in Linux used for examining binary files, such as executable files, object files, and shared libraries. It is used to display information about the symbols in the binary files, including their names, types, and addresses.
>
> Some of the common options used with the nm command are:
>
> - -a: shows all symbols, including local symbols
> - -g: shows only global symbols
> - -u: shows only undefined symbols
> - -D: shows dynamic symbols
> - -C: shows C++ symbols in a demangled format
> - -f: shows the file name where each symbol is defined
> - -p: shows the symbol's value in hexadecimal format
>
> The nm command is useful for debugging and analyzing binary files, as it can help identify missing or wrong symbols, as well as provide information about the functions and variables used in the code.

## Demo

以 OpenSSL 的 shared object 为例，查看其中的部分符号。其中：

- `-g` 参数表示只查看全局符号
- `-D` 参数表示只查看动态符号
- `-A` 参数表示打印每个符号所属的文件名

```shell
$ nm -g -D -A libssl.so   
libssl.so:                 U ASN1_item_d2i@@OPENSSL_1_1_0
libssl.so:                 U ASN1_item_free@@OPENSSL_1_1_0
libssl.so:                 U ASN1_item_i2d@@OPENSSL_1_1_0
libssl.so:                 U ASN1_OCTET_STRING_it@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_get_current_job@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_start_job@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_WAIT_CTX_free@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_WAIT_CTX_get_all_fds@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_WAIT_CTX_get_changed_fds@@OPENSSL_1_1_0
libssl.so:                 U ASYNC_WAIT_CTX_new@@OPENSSL_1_1_0
libssl.so:                 U BIO_ADDR_clear@@OPENSSL_1_1_0
libssl.so:                 U BIO_ADDR_free@@OPENSSL_1_1_0
libssl.so:                 U BIO_ADDR_new@@OPENSSL_1_1_0
libssl.so:                 U BIO_callback_ctrl@@OPENSSL_1_1_0
libssl.so:                 U BIO_clear_flags@@OPENSSL_1_1_0
libssl.so:                 U BIO_copy_next_retry@@OPENSSL_1_1_0
libssl.so:                 U BIO_ctrl@@OPENSSL_1_1_0
libssl.so:                 U BIO_dump_indent@@OPENSSL_1_1_0
libssl.so:                 U BIO_f_buffer@@OPENSSL_1_1_0
libssl.so:                 U BIO_find_type@@OPENSSL_1_1_0
libssl.so:                 U BIO_free@@OPENSSL_1_1_0
libssl.so:                 U BIO_free_all@@OPENSSL_1_1_0
libssl.so:000000000001e720 T BIO_f_ssl@@OPENSSL_1_1_0
libssl.so:                 U BIO_get_data@@OPENSSL_1_1_0
libssl.so:                 U BIO_get_init@@OPENSSL_1_1_0
libssl.so:                 U BIO_get_retry_reason@@OPENSSL_1_1_0
libssl.so:                 U BIO_get_shutdown@@OPENSSL_1_1_0
libssl.so:                 U BIO_int_ctrl@@OPENSSL_1_1_0
libssl.so:                 U BIO_method_type@@OPENSSL_1_1_0
libssl.so:                 U BIO_new@@OPENSSL_1_1_0
libssl.so:000000000001e830 T BIO_new_buffer_ssl_connect@@OPENSSL_1_1_0
libssl.so:000000000001e730 T BIO_new_ssl@@OPENSSL_1_1_0
libssl.so:000000000001e7b0 T BIO_new_ssl_connect@@OPENSSL_1_1_0
libssl.so:                 U BIO_next@@OPENSSL_1_1_0
libssl.so:                 U BIO_pop@@OPENSSL_1_1_0
libssl.so:                 U BIO_printf@@OPENSSL_1_1_0
libssl.so:                 U BIO_push@@OPENSSL_1_1_0
libssl.so:                 U BIO_puts@@OPENSSL_1_1_0
...
```

- `B` 表示当前符号位于 BSS 数据段，通常包含被 0 初始化或未被初始化过的数据（因平台而异）
- `D` 表示当前符号位于被初始化过的数据段
- `T` 表示当前符号位于代码段
- `U` 代表当前对象内使用过但未定义的符号，通常这个符号位于需要被链接的另一个对象中
- [...](https://man7.org/linux/man-pages/man1/nm.1.html)

## References

[nm(1) — Linux manual page](https://man7.org/linux/man-pages/man1/nm.1.html)
