# Solidity - Types

Created by : Mr Dk.

2020 / 02 / 25 22:20

Ningbo, Zhejiang, China

---

## Value Types

### Booleans

`bool` - `true` / `false`，运算符同 C 语言。

### Integers

- `uint8` / `int8`
- ...
- `uint256` (`uint`) / `int156` (`int`)

数据宽度以 8 位为单位增长。比较运算符、位运算符、移位运算符、数学运算符同 C 语言。

幂运算符 `**` - `2**32`

### Fixed Point Numbers

暂未被 Solidity 完全支持，略了。

### Address

有两种类型的地址，基本上是相同的：

- `address` - 20 Bytes 的 Ethereum 地址，无法向这类地址发送 Ether
- `address payable` - 是一个可以发送 Ether 的地址，具有两个额外的成员 `transfer` 和 `send`

`address payable` 是在 Solidity 0.5.0 后才加入的。

### Members of Addresses

快速查询某个地址的余额 / 以 wei 为单位发送 Ether：

- `balance`
- `transfer`

```solidity
address payable x = address(0x123);
address myAddress = address(this);
if (x.balance < 10 && myAddress.balance >= 10) x.transfer(10);
```

如果余额不足，或 Ether 转账被对方拒绝，`transfer` 将会回滚。

在调用 `transfer` 时，对应 contract 的 fallback function 将会一起执行。如果在 fallback function 执行过程中 out-of-gas 或发生了其它错误，本次交易中已经被转账的 Ether 将会被回滚，当前 contract 将会抛出异常停止执行。

- `send`

是 `transfer` 的一种低级表示。如果执行失败，`transfer` 将会使当前 contract 抛出异常停止执行，而 `send` 将会返回 `false`。为了安全起见，要么使用 `transfer`，要么就对 `send` 的返回值进行 check。

- `call`
- `delegatecall`
- `staticcall`

低层调用，接收的参数为一些编码后的字节。需要小心使用，因为可能会将当前 contract 的控制权交给任意位置的恶意 contract，这些 contract 会通过调用返回当前 contract，并对状态变量作出修改。

通常，与其它合约的交互使用的是 contract 对象 - `x.f()`

```solidity
address(nameReg).call{gas: 1000000, value: 1 ether}(abi.encodeWithSignature("register(string)", "MyName"));
```

而 `delegatecall` 的区别在于，除了使用给定地址上的代码，其它 (balance、storage) 都使用的是当前 contract。主要是用于调用存储在其它 contract 中的库代码。

`staticcall` 基本上与 `call` 相同，但是会在函数修改状态时发生回滚。

这三种低级函数破坏了 Solidity 的类型安全性，因此只能在万不得已的情况下使用。`gas` 选项对于这三种函数都可用，`value` 选项对于 `delegatecall` 不能使用。

### Contract Types

每一个 contract 定义其自己的类型 (和 Class 类似，每个类都是一个类型)。可以与地址类型进行显式转换。对于 `address payable` 的转换，只有当 contract 有接收转账的函数或可支付的 fallback 函数才能完成。如果没有这两种函数，就只能通过 `payable(address(x))` 来完成转换。

如果定义了某个 contract 的局部变量，就可以通过该变量直接调用 contract 中的被声明为 `external` 的函数和被声明为 `public` 的状态变量。

### Fixed-size Byte Arrays

`byte1` (`byte`), `byte2`, `byte3`, ..., `byte32` 用于存放字节。

成员：`.length` (只读)

### Dynamically-sized Byte Array

- `bytes`
- `string`

### Function Types

```solidity
function (<parameter types>) {internal|external} [pure|view|payable] [returns (<return types>)]
```

Internal 函数只能在当前 contract 内被调用，不能在当前 contract 的上下文以外被执行 - 调用这种类型的函数是由跳转到某个 label 实现的。默认情况下，函数类型都是 internal 的。

External 函数包含了地址和函数签名，可以在 contract 外部被使用。

其中，`external` 函数有如下成员：

- `.address` - 返回函数所在的 contract 地址
- `.selector` - 返回 ABI function selector
- `.gas(uint)` - 已过时，使用 `{gas: ...}` 指定向目标函数发送的 gas
- `.value(uint)` - 已过时，使用 `{value: ...}` 指定向目标函数发送的 wei

---

## Reference Types

引用类型在处理时需要比值类型更加小心。在使用引用类型时，需要显式指定数据被存储的位置：

- `memory` - 生命周期为一次 external 函数调用
- `storage` - 存储状态变量的位置，生命周期为整个 contract 的生命周期
- `calldata` - 存放函数参数，类似 `memory`，但不可修改

这三种类型在互相赋值时，可能是复制引用，可能是复制值。

---

## Mapping Types

声明方式 - `mapping(_KeyType => _ValueType) _VariableName`

- Key 的类型可以是任意内置类型、contract 类型、枚举等
- Value 可以是任意类型 (包括 mapping、array、struct)

数据位置只能为 `storage`，因此只能作为状态变量。

---
