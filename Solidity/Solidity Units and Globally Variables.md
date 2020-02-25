# Solidity - Units and Globally Available Variables

Created by : Mr Dk.

2020 / 02 / 25 22:42

Ningbo, Zhejiang, China

---

## Ether Units

最小单位 - `wei`

* `wei` - 最小单位，也是单位缺省时的默认单位
* `szabo` - `10^12 wei`
* `finney` - `10^3 szabo`
* `ether` - `10^3 finney`

## Time Units

* `seconds`
* `minutes`
* `hours`
* `days`
* `weeks`
* `years`

## Special Variables and Functions

### Block and Transaction Properties

* `block.blockhash(uint blockNumber) returns (bytes32)` - 256 个最近的区块 hash
* `address block.coinbase` - 目前区块矿工地址
* `unit block.difficulty` - 目前区块的难度
* `uint block.gaslimit` - 目前区块的 gaslimit
* `uint block.number` - 目前区块的 number
* `uint block.timestamp` - 目前区块的 Unix 时间戳
* `bytes msg.data` - 完整的 calldata
* `uint msg.gas` - 剩余的 gas
* `address msg.sender` - 目前调用的发送者
* `bytes4 msg.sig` - Calldata 的前四个字节 (函数标识符)
* `uint msg.value` - 随着 message 发送的 wei
* `uint now` - 目前区块的 Unix 时间戳
* `uint tx.gasprice` - 交易的 gas price
* `address tx.origin` - 交易的发起方

`msg` 在每次 external function call 中可能都是不一样的。

处于安全性的考虑，不要使用区块的时间戳或者 hash 等作为随机数的生成源 - 因为这些数据可以被矿工操控。

### Error Handling

* `assert(bool condition)` - 如果条件不满足，就抛出；用于内部错误
* `require(bool condition)` - 如果条件不满足，就抛出；用于外部输入错误
* `revert()` - 中止执行，回滚状态改变

## Mathematical and Cryptographic Functions

## Address Related

* `<address>.balance (uint256)` - 地址中的余额 (wei 为单位)
* `<address>.transfer(uint256 amount)` - 向指定地址转账，如果失败就抛出异常
* `<address>.send(uint256 amount) returns (bool)` - 向指定地址转账，如果失败则返回 `false`
* `<address>.call(...) returns (bool)`
* `<address>.callcode(...) returns (bool)`
* `<address>.delegatecall(...) returns (bool)`

## Contract Related

* `this` - 当前 contract
* `selfdestruct(address recipient)` - 自毁，将资金转向指定地址
* `suicide(address recipient)` - 同上

---

