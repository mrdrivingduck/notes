# Solidity - Layout and Structure

Created by : Mr Dk.

2020 / 02 / 25 20:49

Ningbo, Zhejiang, China

---

## Pragmas

编译标记只针对当前源代码文件有效。

### Version Pragma

用于使旧的编译器拒绝编译一些新的特性。常用方法：

```solidity
pragma solidity ^0.5.2;
```

### Experimental Pragma

用于开启一些编译器或语言中默认没有启动的特性。

- ABIEncoderV2
- SMTChecker

---

## Importing other Source Files

### Syntax and Semantics

引入其它源文件，从而获得更好的模块化。

全局模式：

```solidity
import "filename";
```

但是这种模式可能带来的问题就是，在 `filename` 中引入的变量会被自动引入到所有引用它的文件中，可能会带来命名冲突的隐患。可以通过给创建新的全局命名符号来表示 `filename` 中的变量：

```solidity
import * as symbolName from "filename";
// or
import "filename" as symbolName;
// symbolName.synbol
```

如果命名符号存在冲突，或者只想引入某几个变量，可以这样：

```solidity
import {symbol1 as alias, symbol2} from "filename";
```

### Path

除了 `.` 和 `..` 开头的路径以外，所有的路径都会被视为绝对路径。但一般是由编译器决定如何解析路径。

---

## Comments

```solidity
// 单行注释

/*
多行注释
*/
```

另外还支持一种注释，只能标注在 contract 或方法名上，我一看这不就是 Javadoc 嘛......功能也类似，用于标注文档：

```solidity
/** @title Calculator */

/// @dev ...
/// @param w ...
/// @return res ...
```

---

## Structure

Contract 与 OOP 语言的 **类** 类似。另外，一个 contract 可以继承自其它 contract。此外，还有特殊种类的 contract - libraries 和 interfaces。

### State Variables

状态变量的值将会永远被存放在 contract 存储中。

```solidity
pragma solidity >=0.4.0 <0.7.0;

contract SimpleStorage {
    uint storedData; // State variable
    // ...
}
```

### Functions

Contract 内可被执行的单元。

```solidity
pragma solidity >=0.4.0 <0.7.0;

contract SimpleAuction {
    function bid() public payable { // Function
        // ...
    }
}
```

### Function Modifiers

以一种声明式的方式修改函数的语义。

```solidity
pragma solidity >=0.4.22 <0.7.0;

contract Purchase {
    address public seller;

    modifier onlySeller() { // Modifier
        require(
            msg.sender == seller,
            "Only seller can call this."
        );
        _;
    }

    function abort() public view onlySeller { // Modifier usage
        // ...
    }
}
```

### Events

是 EVM 用于进行日志记录的工具。

```solidity
pragma solidity >=0.4.21 <0.7.0;

contract SimpleAuction {
    event HighestBidIncreased(address bidder, uint amount); // Event

    function bid() public payable {
        // ...
        emit HighestBidIncreased(msg.sender, msg.value); // Triggering event
    }
}
```

### Struct Types

结构体用于定义一些变量构成的组。

```solidity
pragma solidity >=0.4.0 <0.7.0;

contract Ballot {
    struct Voter { // Struct
        uint weight;
        bool voted;
        address delegate;
        uint vote;
    }
}
```

### Enum Types

```solidity
pragma solidity >=0.4.0 <0.7.0;

contract Purchase {
    enum State { Created, Locked, Inactive } // Enum
}
```

---
