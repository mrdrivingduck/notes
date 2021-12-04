# C++ File I/O

Created by : Mr Dk.

2018 / 09 / 10 16:05

Nanjing, Jiangsu, China

---

## 1. 输入/输出流

### `ifstream` - 输入流

```c++
template < class charT, class traits = char_traits<charT> >
class basic_ifstream;
```

### `ofstream` - 输出流

```c++
template < class charT, class traits = char_traits<charT> >
class basic_ofstream;
```

### `fstream` - 输入/输出流

## 2. 文件打开方式

* `ios::in` - 读取文件
* `ios::out` - 写入文件
* `ios::binary` - 二进制模式 (若不使用，则默认为字符模式)
* `ios::app` - 追加模式 (一般与输出流配合)
* `ios::ate` - 转到文件尾部 (一般与输入流配合)
* `ios::trunc` - 如果文件存在，则清除文件内容
* `ios::nocreate` - 若文件不存在，则不创建文件
* `ios::noreplace` - 若文件存在，则打开失败

## 3. 文件打开/关闭

### 打开

* `ifstream` 默认打开方式 - `ios::in`
* `ofstream` 默认打开方式 - `ios::out`
* `fstream` 默认打开方式 - `ios::in | ios::out`

```c++
#include <fstream>
using namespace std;

// Two step
ifstream fin;
fin.open("read.txt", ios::in);
// One step
ofstream fout("write.txt", ios::out | ios::app);

if(!fin.is_open()) {
    exit(0);
}
if (fout.fail()) {
    exit(0);
}

// ...
```
  
### 关闭

```c++
// ...

fin.close();
fout.close();
```

## 4. 字符流文件读写

除非指定以 **二进制方式 (字节流)** 打开文件，否则默认以 **文本方式 (字符流)** 打开文件。使用 `<<` 和 `>>` 来读写

```c++
// ...
// File opend

// Input
int temp;
fin >> temp;
// Output
fout << "hello" << endl;

// ...
// File closed
```

## 5. 格式化输出

```c++
#include <iomanip>	// NECESSARY !!!

// 设置实数精度
fout.precision(4);
fout << 3.1415926535 << endl;	// 仅一次有效
// OR
// fout << setprecision(4) << 3.1415926535 << endl;

// 设置字段宽度和填充字符
fout.fill('0');
fout.width(10);
fout << "hello" << endl;	// 仅一次有效
// OR
// fout << setfill('0') << setw(10) << "hello" << endl;

// 进制转换
fout << setbase(8) << 32 << endl;
fout << setbase(16) << 32 << endl;

// 设置/终止设置输出格式
fout.setf(ios::left);
fout << 5 << endl;
fout.unsetf(ios::left);
// OR : fout << setiosflags(ios::left) << 5 << endl;
```

| 格式              | 作用                                               |
| ----------------- | -------------------------------------------------- |
| `ios::left`       | 域宽范围内左对齐                                     |
| `ios::right`      | 域宽范围内右对齐                                     |
| `ios::internal`   | 符号位在域宽内左对齐 数值右对齐 中间由填充字符填充        |
| `ios::dec`        | 设置基数为 10                                       |
| `ios::oct`        | 设置基数为 8                                        |
| `ios::hex`        | 设置基数为 16                                       |
| `ios::showbase`   | 强制输出整数的基数                                   |
| `ios::showpoint`  | 强制输出浮点数的小数点和尾数 0                        |
| `ios::uppercase`  | 十六进制字母大写                                     |
| `ios::showpos`    | 显示正数的 **+** 号                                 |
| `ios::scientific` | 以科学计数法格式输出                                 |
| `ios::fixed`      | 以定点小数格式输出                                   |
| `ios::unitbuf`    | 每次输出后刷新所有的流                                |
| `ios::stdio`      | 每次输出后清除 *stdout* *stderr*                     |

## 6. 二进制文件读写

* 文件打开方式必须包含 `ios::binary`
* 使用 `read` 和 `write` 函数进行读写
  * `ostream& write (const char* s, streamsize n);`
  * `istream& read (char* s, streamsize n);`
  * `s` 为起始地址，`n` 为字节数
* 读写结构体

```c++
struct Buffer {
	// ...
};

Buffer buffer;
fout.write((char *) &buffer, sizeof(Buffer));
fin.read((char *) &buffer, sizeof(Buffer));
```
