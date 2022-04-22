# C++ STL string

Created by : Mr Dk.

2018 / 09 / 17 20:38

Nanjing, Jiangsu, China

---

## Template

```cpp
typedef basic_string<char> string;
```

```cpp
#include <string>
using namespace std; // using std::string;
```

## Constructor

```cpp
string();                                                 // Empty constructor (default)
string(const string& str);                                // Copy constructor
string(const string& str, size_t pos, size_t len = npos); // Substring contructor
```

- `pos` : Beginning of character position
- `len` : Length that wants to be copied
- (string is too short) | ( `len` == `string::npos` ) -> copy until the end of string

```cpp
string (const char* s);           // From C-String
string (const char* s, size_t n); // From C-String, copy first n characters
```

```cpp
string (size_t n, char c); // Fill the string with n copies of character c
```

```cpp
// Range constructor
template<class InputIterator> string(InputIterator first, InputIterator last);
```

## Member Constants

```cpp
static const size_t npos = -1;
```

- The greatest possible value for an element of type `size_t`
- When used as the value for a _length_ parameter: means **"Until the end of the string"**
- When used as a return value: indicating **no matches**

## Iterators

```cpp
string::iterator begin_iter = str.begin();            // 指向字符串开头的迭代器
string::iterator end_iter = str.end();                // 指向字符串结尾的下一个位置的迭代器
string::reverse_iterator r_begin_iter = str.rbegin(); // 返回指向字符串结尾的反向迭代器
string::reverse_iterator r_end_iter = str.rend();     // 返回指向字符串开头的前一个位置的反向迭代器
```

## Operators Overload

Operator `=`: return a COPY of object.

```cpp
string& operator= (const string& str);  // str = str1;
string& operator= (const char* s);      // str = "Hello world"
string& operator= (char c);             // str = '.'
```

Operator `+`: return a newly constructed object after concatenation.

```cpp
string operator+ (const string& lhs, const string& rhs);  // str = str1 + str2;
string operator+ (const string& lhs, const char* rhs);    // str = str1 + "Hello";
string operator+ (const char* lhs, const string& rhs);    // str = "Hello" + str2;
string operator+ (const string& lhs, char rhs);           // str = str1 + '.';
string operator+ (char lhs, const string& rhs);           // str = '.' + str2;
```

Operator `+=`: return the same object after appending value.

```cpp
string& operator+= (const string& str);  // str += str1;
string& operator+= (const char* s);      // str += "Hello world";
string& operator+= (char c);             // str += '.'
```

Operator `[]`: return a reference to the character at position in the string. (`string::at()`)

- if (position == string length): `\0`
- _C++11_
  - `front()`: access the first character
  - `back()`: access the last character
  - If the string is empty: _undefined behavior_

```cpp
char& operator[] (size_t pos);

const char& operator[] (size_t pos) const;
      char& at(size_t pos);
const char& at(size_t pos) const;
      char& front();
const char& front() const;
      char& back();
const char& back() const;
```

Operator `>>`: for input.

```cpp
istream& operator>> (istream& is, string& str);
```

Operator `<<`: for output

```cpp
ostream& operator<< (ostream& os, const string& str);
```

## Capacity

Return the length of the string:

```cpp
size_t size() const;
size_t length() const;
```

Return the maximum length of the string can reach:

```cpp
size_t max_size() const;
```

Return size of allocated storage:

```cpp
size_t capacity() const;
```

Resizes the string to a length of n characters

- If `c` is specified, the new elements are initialized as copies of `c`; Otherwise, they are value-initialized characters (null characters)
- If `n` is smaller than current string; the current value is shortened to its first `n` character

```cpp
void resize(size_t n);
void resize(size_t n, char c);
```

Request a change in capacity：

- If `n` is greater than the current string capacity, the function causes the container to increase its capacity to `n` characters (or greater)
- Exception
  - **GUARANTEE**: If an exception is thrown, there are **NO** changes in the string
  - If `n` > `max_size`: `length_error` exception
  - If the function needs to allocate storage and fails: `bad_alloc` exception

```cpp
void reserve(size_t n = 0);
```

Erases the contents of the string: empty string.

```cpp
void clear();
```

Returns whether the string is empty:

```cpp
bool empty() const;
```

## Modifications

Assigns a new value to the string, replacing its current contents. Exception:

- `s` is not long enough | `range` is not valid: undefined behavior
- `subpos` > string length: `out_of_range` exception
- Resulting string length > `max_size`: `length_error` exception
- The function needs to allocate storage and fails: `bad_alloc` exception

```cpp
string& assign(const string& str);                               // String
string& assign(const string& str, size_t subpos, size_t sublen); // Substring
string& assign(const char* s);                                   // C-String
string& assign(const char* s, size_t n);                         // Buffer
string& assign(size_t n, char c);                                // Fill
template <class InputIterator> string& assign(InputIterator first, InputIterator last); // Range
```

Appending additional characters at the end of its current value. Exception:

- `s` is not long enough | `range` is not valid: undefined behavior
- `subpos` > string length: `out_of_range` exception
- Resulting string length > `max_size`: `length_error` exception
- The function needs to allocate storage and fails: `bad_alloc` exception

```cpp
string& append(const string& str);                               // String
string& append(const string& str, size_t subpos, size_t sublen); // Substring
string& append(const char* s);                                   // C-String
string& append(const char* s, size_t n);                         // Buffer
string& append(size_t n, char c);                                // Fill
template <class InputIterator> string& append(InputIterator first, InputIterator last); // Range
```

Insert into the string right **before** the character indicated by `pos` or `p`. Exception:

- `s` is not long enough | `range` is not valid: undefined behavior
- `subpos` > str's length: `out_of_range` exception
- Resulting string length > `max_size`: `length_error` exception
- The function needs to allocate storage and fails: `bad_alloc` exception

```cpp
string& insert(size_t pos, const string& str);                                      // String
string& insert(size_t pos, const string& str, size_t subpos, size_t sublen = npos); // Substring
string& insert(size_t pos, const char* s);                                          // C-String
string& insert(size_t pos, const char* s, size_t n);                                // Buffer
string& insert(size_t pos, size_t n, char c);                                       // Fill
iterator insert(const_iterator p, size_t n, char c);                                // Fill
iterator insert(const_iterator p, char c);                                          // Single Character
template <class InputIterator> iterator insert(iterator p, InputIterator first, InputIterator last); // Range
```

Erase characters from string. Exception:

- If `pos` > string length: `out_of_range` exception
- If range is invalid: undefined behavior

```cpp
string& erase(size_t pos = 0, size_t len = npos); // Sequence
iterator erase(iterator p);                       // Character
iterator erase(iterator first, iterator last);    // Range
```

Replace portion of string, specify a range in old string by:

- `pos` & `len`
- A pair of _iterators_

Or specify a new string to replace into the specific range.

Exception:

- If `s` is not long enough | range is not valid: undefined behavior
- `pos` or `subpos` is greater than string's length: `out_of_range` exception
- If the resulting string length > `max_size`: `length_error` exception
- If the function needs to allocate storage and fails: `bad_alloc` exception

```cpp
// String
string& replace(size_t pos, size_t len, const string& str);
string& replace(const_iterator i1, const_iterator i2, const string& str);
// Substring
string& replace(size_t pos, size_t len, const string& str, size_t subpos, size_t sublen = npos);
// C-String
string& replace(size_t pos, size_t len, const char* s);
string& replace(const_iterator i1, const_iterator i2, const char* s);
// Buffer
string& replace(size_t pos, size_t len, const char* s, size_t n);
string& replace(const_iterator i1, const_iterator i2, const char* s, size_t n);
// Fill
string& replace(size_t pos, size_t len, size_t n, char c);
string& replace(const_iterator i1, const_iterator i2, size_t n, char c);
// Range
template <class InputIterator> string& replace(const_iterator i1, const_iterator i2, InputIterator first, InputIterator last);
```

Swap string values:

```cpp
void swap(string& str);            // Member function -> str1.swap(str2);
void swap(string& x, string& y);   // Not a member function -> swap(str1, str2);
```

Append character to the end of the string, increasing its length by **one**. Exception:

- Resulting string length > `max_size`: `length_error` exception
- The function needs to allocate storage and fails: `bad_alloc` exception

```cpp
void push_back(char c);
```

Delete the last character of the string, reducing its length by **one**. Exception:

- If the string is empty: undefined behavior

```cpp
void pop_back();
```

## String Operations

- Get _C_ String with `\0` in the end

```cpp
const char* c_str() const noexcept;
const char* data() const noexcept;
```

Copy sequence of characters **from** string (string -> char[]), returning the number of characters copied to the array. Exception:

- If `s` is not long enough: undefined behavior
- If `pos` > string's length: `out_of_range` exception

```cpp
size_t copy(char* s, size_t len, size_t pos = 0) const;
```

Compare strings - _Compared string_ & _Comparing string_.

| Value | Reason                                                                                                                                                    |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | Compare equal.                                                                                                                                            |
| <0    | Either the value of the first character that does not match is lower in the _compared string_, or all characters match but _compared string_ is shorter.  |
| >0    | Either the value of the first character that does not match is greater in the _compared string_, or all characters match but _compared string_ is longer. |

Exception:

- If `s` is not long enough: undefined behavior
- If `pos` or `subpos` > string's length: `out_of_range` exception

```cpp
// String
int compare(const string& str) const noexcept;
// Substrings
int compare(size_t pos, size_t len, const string& str) const;
int compare(size_t pos, size_t len, const string& str, size_t subpos, size_t sublen) const;
// C-String
int compare(const char* s) const;
int compare(size_t pos, size_t len, const char* s) const;
// Buffer
int compare(size_t pos, size_t len, const char* s, size_t n) const;
```

Generating substring. Exception

- If `pos` > string's length: `out_of_range` exception
- If the function needs to allocate storage and fails: `bad_alloc` exception

```cpp
string substr(size_t pos = 0, size_t len = npos) const;
```

Find content in string - **matching the entire string**. Exception:

- If `s` is not long enough: undefined behavior
- `pos` is used to specify the first character to start searching
- `n` is used to specify the length of `s`
- If there is no match, return `string::npos`

```cpp
// Find the first occurrence
size_t find(const string& str, size_t pos = 0) const noexcept;     // String
size_t find(const char* s, size_t pos = 0) const;                  // C-String
size_t find(const char* s, size_t pos, size_type n) const;         // Buffer
size_t find(char c, size_t pos = 0) const noexcept;                // Character

// Find the last occurrence
size_t rfind(const string& str, size_t pos = npos) const noexcept; // String
size_t rfind(const char* s, size_t pos = npos) const;              // C-String
size_t rfind(const char* s, size_t pos, size_t n) const;           // Buffer
size_t rfind(char c, size_t pos = npos) const noexcept;            // Character
```

Find character in string - **matching any of the characters specified in arguments**. Exception:

- If `s` is not long enough: undefined behavior
- `pos` is used to specify the first character to start searching
- `n` is used to specify the length of `s`
- If there is no match, return `string::npos`

```cpp
// The first character matched
size_t find_first_of(const string& str, size_t pos = 0) const noexcept;  // String
size_t find_first_of(const char* s, size_t pos = 0) const;               // C-String
size_t find_first_of(const char* s, size_t pos, size_t n) const;         // Buffer
size_t find_first_of(char c, size_t pos = 0) const noexcept;             // Character

// The first character absent
size_t find_first_not_of(const string& str, size_t pos = 0) const noexcept; // String
size_t find_first_not_of(const char* s, size_t pos = 0) const;              // C-String
size_t find_first_not_of(const char* s, size_t pos, size_t n) const;        // Buffer
size_t find_first_not_of(char c, size_t pos = 0) const noexcept;            // Character

// The last character matched
size_t find_last_of(const string& str, size_t pos = npos) const noexcept; // String
size_t find_last_of(const char* s, size_t pos = npos) const;              // C-String
size_t find_last_of(const char* s, size_t pos, size_t n) const;           // Buffer
size_t find_last_of(char c, size_t pos = npos) const noexcept;            // Character

// The last character absent
size_t find_last_not_of(const string& str, size_t pos = npos) const noexcept; // String
size_t find_last_not_of(const char* s, size_t pos = npos) const;              // C-String
size_t find_last_not_of(const char* s, size_t pos, size_t n) const;           // Buffer
size_t find_last_not_of(char c, size_t pos = npos) const noexcept;            // Character
```

## Input

作为基本数据类型，可以直接使用 `cin` & `>>`。另外，还可以使用 `getline()`：

- default delimitation character: `\n`

```cpp
istream& getline(istream&  is, string& str, char delim);
istream& getline(istream&& is, string& str, char delim);
istream& getline(istream&  is, string& str);
istream& getline(istream&& is, string& str);
```

## Conversion

将数据类型转换为字符串：

```cpp
#include <string>
using std::to_string

string to_string (int val);
string to_string (long val);
string to_string (long long val);
string to_string (unsigned val);
string to_string (unsigned long val);
string to_string (unsigned long long val);
string to_string (float val);
string to_string (double val);
string to_string (long double val);
```

将字符串转换为数据类型：

```cpp
#include <string>
using std::stoi;
using std::stol;
using std::stoul;
using std::stoll;
using std::stoull;
using std::stof;
using std::stod;
using std::stold;

int stoi (const string&  str, size_t* idx = 0, int base = 10);
int stoi (const wstring& str, size_t* idx = 0, int base = 10);
long stol (const string&  str, size_t* idx = 0, int base = 10);
long stol (const wstring& str, size_t* idx = 0, int base = 10);
unsigned long stoul (const string&  str, size_t* idx = 0, int base = 10);
unsigned long stoul (const wstring& str, size_t* idx = 0, int base = 10);
long long stoll (const string&  str, size_t* idx = 0, int base = 10);
long long stoll (const wstring& str, size_t* idx = 0, int base = 10);
unsigned long long stoull (const string&  str, size_t* idx = 0, int base = 10);
unsigned long long stoull (const wstring& str, size_t* idx = 0, int base = 10);
float stof (const string&  str, size_t* idx = 0);
float stof (const wstring& str, size_t* idx = 0);
double stod (const string&  str, size_t* idx = 0);
double stod (const wstring& str, size_t* idx = 0);
long double stold (const string&  str, size_t* idx = 0);
long double stold (const wstring& str, size_t* idx = 0);
```

---

## Summary

Useful & important.
