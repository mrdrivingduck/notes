# Solidity - Contracts

Created by : Mr Dk.

2020 / 02 / 26 12:56

Ningbo, Zhejiang, China

---

## Creating Contracts

Contract 可以在 Solidity 外部或内部内创建。当创建时，contract 的构造函数将会被调用一次。Solidity 中只允许有一个构造函数 - 重载是不允许的。

## Visibility and Getters

Solidity 识别两种类型的函数调用 - 一种使用 EVM call (message call)，一种不使用。

函数可被声明为 `external` `public` `internal` `private` - 默认的是 `public`；而状态变量中 `external` 是不可能的，默认的是 `internal`。

* `external` - 函数只能在外部被调用，不能在内部被调用 (但是 `this.f()` 可以，因为这是外部调用)
* `public` - 函数可以在外部或内部被调用；对于变量，一个 getter 函数将会自动生成
* `internal` - 函数或变量只能在当前 contract 中或从当前 contract 中衍生的 contract 中访问
* `private` - 只能从当前 contract 中访问

### Getter Functions

编译器自动为所有 `public` 状态变量生成一个 getter 函数。该函数不接收任何参数，只会将当前的状态变量值返回。Getter 函数的可见性为 `external`。

---

## Function Modifiers

用于改变函数的行为，并且可以被继承和重写。用 `_` 来代替程序原本的行为。

```solidity
pragma solidity ^0.4.11;

contract owned {
    function owned() { owner = msg.sender; }
    address owner;

    // This contract only defines a modifier but does not use
    // it - it will be used in derived contracts.
    // The function body is inserted where the special symbol
    // "_;" in the definition of a modifier appears.
    // This means that if the owner calls this function, the
    // function is executed and otherwise, an exception is
    // thrown.
    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
}


contract mortal is owned {
    // This contract inherits the "onlyOwner"-modifier from
    // "owned" and applies it to the "close"-function, which
    // causes that calls to "close" only have an effect if
    // they are made by the stored owner.
    function close() onlyOwner {
        selfdestruct(owner);
    }
}


contract priced {
    // Modifiers can receive arguments:
    modifier costs(uint price) {
        if (msg.value >= price) {
            _;
        }
    }
}


contract Register is priced, owned {
    mapping (address => bool) registeredAddresses;
    uint price;

    function Register(uint initialPrice) { price = initialPrice; }

    // It is important to also provide the
    // "payable" keyword here, otherwise the function will
    // automatically reject all Ether sent to it.
    function register() payable costs(price) {
        registeredAddresses[msg.sender] = true;
    }

    function changePrice(uint _price) onlyOwner {
        price = _price;
    }
}

contract Mutex {
    bool locked;
    modifier noReentrancy() {
        require(!locked);
        locked = true;
        _;
        locked = false;
    }

    /// This function is protected by a mutex, which means that
    /// reentrant calls from within msg.sender.call cannot call f again.
    /// The `return 7` statement assigns 7 to the return value but still
    /// executes the statement `locked = false` in the modifier.
    function f() noReentrancy returns (uint) {
        require(msg.sender.call());
        return 7;
    }
}
```

---

## Constant State Variables

必须被一个在编译时就是常量的表达式赋值。

```solidity
pragma solidity ^0.4.0;

contract C {
    uint constant x = 32**22 + 8;
    string constant text = "abc";
    bytes32 constant myHash = keccak256("abc");
}
```

---

## View Functions

被声明为 `view` 的函数将不会修改状态 - 比如 getter。

会修改状态的函数包含：

* 对状态变量进行写操作
* 创建其它 contract
* 转账
* 调用其它不是 `view` 或 `pure` 函数
* ......

```solidity
pragma solidity ^0.4.16;

contract C {
    function f(uint a, uint b) view returns (uint) {
        return a * (b + 42) + now;
    }
}
```

---

## Pure Functions

声明为 `pure` 的函数不会对状态变量进行读取或修改。

```solidity
pragma solidity ^0.4.16;

contract C {
    function f(uint a, uint b) pure returns (uint) {
        return a * (b + 42);
    }
}
```

---

## Fallback Functions

一个合约只能有一个未命名的函数，这个函数不能有参数，也不能有返回值。如果没有任何一个函数与给定的 function identifier 匹配，就会调用这个函数。

另外，当 contract 收到了裸的 Ether (没有数据) 时，这个函数也会被调用。为了能够获得 Ether，fallback function 需要被声明为 `payable`。否则 contract 就无法通过普通的转账接收 Ether。

通常只有 2300 gas 会被用于执行 fallback function。因此需要使该函数的执行尽可能便宜。

---

## Events

使用了 EVM 的日志功能。被调用时，将会把参数保存到交易日志中，并保存在区块里。

```solidity
pragma solidity ^0.4.0;

contract ClientReceipt {
    event Deposit(
        address indexed _from,
        bytes32 indexed _id,
        uint _value
    );

    function deposit(bytes32 _id) payable {
        // Any call to this function (even deeply nested) can
        // be detected from the JavaScript API by filtering
        // for `Deposit` to be called.
        Deposit(msg.sender, _id, msg.value);
    }
}
```

---

## Inheritance

## Abstract Contracts

## Interfaces

---

## Libraries

库与 contract 类似，但它们部署在一个特定地址，仅被用于 `delegatecall`。也就是说，如果一个库的代码被调用，代码的执行环境将会位于调用该库的 contract 的上下文中。

在 EVM 实现中，库中所有被调用的函数将会被 pull 到调用库的 contract 中，然后就开始使用 `JUMP` 指令对这些代码进行访问。

---

