# Solidity - Expressions and Control Structures

Created by : Mr Dk.

2020 / 02 / 26 11:57

Ningbo, Zhejiang, China

---

## Input Parameters and Output Parameters

输入参数如果不被使用，可以忽略变量名

```solidity
pragma solidity ^0.4.0;

contract Simple {
    function taker(uint _a, uint _b) {
        // do something with _a and _b.
    }
}
```

输出参数在 `returns` 关键字后被声明。参数的数据类型是必须声明的，而参数名可以忽略。如果显式指定了参数名，那么这些参数将被初始化为 0；如果不指定参数名，则在函数的最后通过 `return` 关键字返回被作为输出值的变量。

`return` 支持同时返回多个值 - `return (v0, v1, .., vn);`

```solidity
pragma solidity ^0.4.0;

contract Simple {
    function arithmetics(uint _a, uint _b) returns (uint o_sum, uint o_product) {
        o_sum = _a + _b;
        o_product = _a * _b;
    }
}
```

---

## Function Calls

### Internal Function Calls

通过简单的跳转实现。

```solidity
pragma solidity ^0.4.0;

contract C {
    function g(uint a) returns (uint ret) { return f(); }
    function f() returns (uint ret) { return g(7) + f(); }
}
```

### External Function Calls

通过 `this.g(8);` 和 `c.g(2);` (`c` 是一个实例对象) 进行的调用称为外部调用。实现方式是通过一个 message call，而不是通过跳转。`this` 不能在构造函数中使用，因为 contract 还没有被创建完成。

其它 contract 中的函数只能通过外部调用完成。当调用其它 contract 的函数时，需要指定带有的 `value()` 和 `gas()`：

```solidity
pragma solidity ^0.4.0;

contract InfoFeed {
    function info() payable returns (uint ret) { return 42; }
}

contract Consumer {
    InfoFeed feed;
    function setFeed(address addr) { feed = InfoFeed(addr); }
    function callFeed() { feed.info.value(10).gas(800)(); }
}
```

使用 `{ }` 以任意顺序传递参数：

```solidity
pragma solidity ^0.4.0;

contract C {
    function f(uint key, uint value) {
        // ...
    }

    function g() {
        // named arguments
        f({value: 2, key: 3});
    }
}
```

---

## Creating Contracts via `new`

通过构造函数实例化 contract：

```solidity
pragma solidity ^0.4.0;

contract D {
    uint x;
    function D(uint a) payable {
        x = a;
    }
}

contract C {
    D d = new D(4); // will be executed as part of C's constructor

    function createD(uint arg) {
        D newD = new D(arg);
    }

    function createAndEndowD(uint arg, uint amount) {
        // Send ether along with the creation
        D newD = (new D).value(amount)(arg);
    }
}
```

---

## Error Handling

Solidity 使用状态回退来处理异常。异常将会导致当前调用及其子调用中的所有状态变化回滚，并给调用者一个错误标志。

使用 `assert` 和 `require` 来对条件进行检验，并抛出相应的异常。`assert` 用于测试内部错误，检查一些常量；`require` 用于检验输入或者 contract 的状态变量。

如果在一个子调用中发生了异常，则遵循 _bubble up_ 原则 - 即自动向上抛出。例外情况就是 `send` 和低层调用函数 `call` `delegatecall` 和 `callnode` - 这些函数在发生异常时会返回 `false`。

---

