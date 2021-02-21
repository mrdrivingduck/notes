# Algorithm - Sliding Window

Created by : Mr Dk.

2021 / 02 / 21 11:41

Ningbo, Zhejiang, China

---

2021 年 2 月的 *LeetCode* 题目全都是 **滑动窗口** 相关。记录一下该类型题目的编程范式。以 C++ 为例：

```c++
// vector<int> nums;

int left = 0;
int right = 0;
int window_len = 0

while (right < (int) nums.size()) {
    // 将滑动窗口右端点纳入窗口统计值
    // nums[right]...

    // 根据题目限制，从窗口左端点开始缩短窗口
    // nums[left]...
    // while (condition) { left++; }

    // 统计窗口长度
    // window_len = min / max (window_len, right - left + 1);

    right++; // 滑动窗口向右扩展
}
```

---

