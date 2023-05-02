# fallocate

Created by : Mr Dk.

2023 / 05 / 02 22:56

Hangzhou, Zhejiang, China

---

## Background

`fallocate` 用于为文件预分配或收回空间。

当我们需要一个指定长度的文件时，最简单的方法是，通过内存缓冲区不断向文件中写入，直到写到指定的长度。或者将文件指针直接修改为指定长度的位移处，并向文件中写入一次，那么文件长度会自动扩展到指定长度。

使用 `fallocate` 可以快速分配指定长度的未初始化数据块，达到同样的效果；另外，对于文件中已有的全 0 页，`fallocate` 也可以回收数据块的物理空间，而上层程序读取这个页中的字节时将直接返回全 0。这样可以实现 [文件打洞](http://blog.jcix.top/2018-09-28/hole_punching/)。

这个 CLI 实际上是由 Linux 上的同名系统调用实现而来。

## Usage

```shell
$ fallocate --help

Usage:
 fallocate [options] <filename>

Preallocate space to, or deallocate space from a file.

Options:
 -c, --collapse-range remove a range from the file
 -d, --dig-holes      detect zeroes and replace with holes
 -i, --insert-range   insert a hole at range, shifting existing data
 -l, --length <num>   length for range operations, in bytes
 -n, --keep-size      maintain the apparent size of the file
 -o, --offset <num>   offset for range operations, in bytes
 -p, --punch-hole     replace a range with a hole (implies -n)
 -z, --zero-range     zero and ensure allocation of a range
 -x, --posix          use posix_fallocate(3) instead of fallocate(2)
 -v, --verbose        verbose mode

 -h, --help           display this help
 -V, --version        display version

Arguments:
 <num> arguments may be followed by the suffixes for
   GiB, TiB, PiB, EiB, ZiB, and YiB (the "iB" is optional)

For more details see fallocate(1).
```

### Preallocate

预分配一个 1MB 的文件：

```shell
$ fallocate -l 1MiB file

$ stat file
  File: file
  Size: 1048576         Blocks: 2048       IO Block: 4096   regular file
Device: 820h/2080d      Inode: 29595       Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/mrdrivingduck)   Gid: ( 1000/mrdrivingduck)
Access: 2023-05-02 23:13:36.445550770 +0800
Modify: 2023-05-02 23:13:36.445550770 +0800
Change: 2023-05-02 23:13:36.445550770 +0800
 Birth: 2023-05-02 23:13:36.445550770 +0800
```

这个文件有 2048 个 512B 的块。由于不需要对这些块进行初始化（写 0），所以 `fallocate` 很快就返回了。但是文件系统需要保证读取这些未初始化的块时需要返回全 0，否则这些块中可能会出现已经被删除掉的其它文件中的信息。

```shell
$ vim file
```

### Deallocate

由于该文件的内容目前全部都是 0，因此这 1MB 的文件数据实际上不需要任何物理块来存储，仅需要在文件的元信息中标记即可。这样在读取全 0 页时，文件系统将直接返回 0。

```shell
$ fallocate -d -v file
file: 1 MiB (1048576 bytes) converted to sparse holes.

$ stat file
  File: file
  Size: 1048576         Blocks: 0          IO Block: 4096   regular file
Device: 820h/2080d      Inode: 29595       Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/mrdrivingduck)   Gid: ( 1000/mrdrivingduck)
Access: 2023-05-02 23:22:56.385558933 +0800
Modify: 2023-05-02 23:23:06.965559107 +0800
Change: 2023-05-02 23:23:06.965559107 +0800
 Birth: 2023-05-02 23:22:49.705557904 +0800
```

### Keep Zero

也可以通过 `-z` 参数指定某个范围内的全 0 页一定要分配物理空间。比如对于刚才的文件，我们可以指定第一个 block 必须分配空间，用 `-o` 和 `-l` 分别指定范围的起始位置和长度：

```shell
$ fallocate -z -o 0 -l 1 file

$ stat file
  File: file
  Size: 1048576         Blocks: 8          IO Block: 4096   regular file
Device: 820h/2080d      Inode: 29595       Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/mrdrivingduck)   Gid: ( 1000/mrdrivingduck)
Access: 2023-05-02 23:24:18.705553660 +0800
Modify: 2023-05-02 23:24:40.725548703 +0800
Change: 2023-05-02 23:24:40.725548703 +0800
 Birth: 2023-05-02 23:24:16.525553837 +0800
```

由于当前文件系统的 I/O 单元大小为 4096 字节（8 个 512B），因此虽然指定的范围只有一个字节，但文件系统将会分配一整个 I/O 单元的物理空间。所以现在文件的前 4096 字节是有物理空间的。

同样，还是可以用刚才的 `-d` 参数检测文件中具有物理空间的全 0 页，并回收其物理空间：

```shell
$ fallocate -d -v file
file: 4 KiB (4096 bytes) converted to sparse holes.

$ stat file
  File: file
  Size: 1048576         Blocks: 0          IO Block: 4096   regular file
Device: 820h/2080d      Inode: 29595       Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/mrdrivingduck)   Gid: ( 1000/mrdrivingduck)
Access: 2023-05-02 23:25:00.975552011 +0800
Modify: 2023-05-02 23:25:10.975551896 +0800
Change: 2023-05-02 23:25:10.975551896 +0800
 Birth: 2023-05-02 23:24:16.525553837 +0800
```

## References

[文件打洞 (Hole Punching) 及其应用](http://blog.jcix.top/2018-09-28/hole_punching/)

[stackoverflow - what is file hole and how can it be used? [closed]](https://stackoverflow.com/questions/13982478/what-is-file-hole-and-how-can-it-be-used)

[fallocate(1) — Linux manual page](https://man7.org/linux/man-pages/man1/fallocate.1.html)

[LWN.net - Punching holes in files](https://lwn.net/Articles/415889/)
