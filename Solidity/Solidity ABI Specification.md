# Solidity - ABI Specification

Created by : Mr Dk.

2020 / 03 / 05 15:27

Ningbo, Zhejiang, China

---

## About

_Application Binary Interface (ABI)_ 是与 contract 进行交互的标准方式，不管是在区块链之外，还是 contract-contract 的交互。数据会根据其数据类型被编码。

总体来说，对一个函数 `f` 的调用，并带有 `a_1, ..., a_n` 的参数，会被编码为：`function_selector(f) enc((a_1, ..., a_n))`，即函数 `f` 的选择符，以及所有参数组合为 tuple 后进行编码的形式。返回值也是 `enc((v_1, ..., v_k))` 的形式。

## Function Selector

函数选择符用于定位特定地址的 contract 中的一个唯一的函数。其计算方法是 __函数签名__ 的 _Keccak-256 (SHA-3)_ hash 的前四个字节。

其中，__函数签名__ 被定义为函数名 + 函数参数的类型列表。其中，参数类型用逗号隔开，函数签名中没有任何空格。注意函数的返回值不是签名的一部分。

```solidity
pragma solidity >=0.4.16 <0.7.0;

contract Foo {
    function bar(bytes3[2] memory) public pure {}
    function baz(uint32 x, bool y) public pure returns (bool r) { r = x > 32 || y; }
    function sam(bytes memory, bool, uint[] memory) public pure {}
}
```

比如，对于函数 `baz()`，其函数签名是：`baz(uint32,bool)`。然后计算这个签名的 SHA-3，并取前四个字节，就成为函数的 function selector。给定这个 function selector，就相当于确定了要调用的函数。

## Argument Encoding

在调用函数时，除了唯一确定要调用的那个函数，还需要将函数参数进行传递。函数参数也需要被编码为特定的格式进行传递。

可被编码的数据类型：

* `uint<M>` - 其中 `0 < M <= 256`，`M % 8 == 0`
* `int<M>`
* `address` - 等价于 `uint160` (20 Bytes)
* `uint` / `int` - 等价于 256-bit 的对应形式
* `bool` - 等价于 `uint8`
* `fixed<M>x<N>` - 带符号的定点数，`v = v / (10 ** n)`
* `ufixed<M>x<N>` - 无符号的定点数
* `fixed` / `ufixed` - 等价于 `fixed128x18` / `ufixed128x18`
* `bytes<M>` - M 个字节的二进制数据 (32 Bytes 以下)
* `function` - 20 Bytes 的地址 + 4 Bytes 的 function selector

定长数组：

* `<type>[M]`

不定长类型:

* `bytes`
* `string`
* `<type>[]`

所有的类型都可以被组合为 tuple - `(T1,T2,...,Tn)`。

以上所有类型，都会被按照特定的格式进行编码。比如，以参数 `(69, true)` 调用上述 `baz()` 时，会被编码为：

* `0xcdcd77c0` - `sha3("baz(uint32,bool)")`
* `0x0000000000000000000000000000000000000000000000000000000000000045` - 69
* `0x0000000000000000000000000000000000000000000000000000000000000001` - true

然后拼接起来。

## JSON

上述编码形式用于 contract-contract 之间的交互。对于 contract 与区块链以外 (比如应用程序) 的交互，contract 提供了接口的 JSON 格式描述，实际上一个 contract 对应了一个 JSON Array。其中，每个 JSON 对象描述一个函数或 event。JSON 对象中包含的域：

* `type` - 函数类型：`"function"` / `"constructor"` / `"receive"` / `"fallback"`
* `name` - 函数名
* `inputs` - 函数输入 (参数)
    * `name` - 参数名
    * `type` - 参数类型
    * `components` (给结构体使用)
* `outputs` - 函数输出
* `stateMutability` - 函数描述：`pure` / `view` / `nonpayable` / `payable`

```json
[
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "donate",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "get",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
```

---

