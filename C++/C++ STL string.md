## C++ STL string

Created by : Mr Dk.

2018 / 09 / 16 23:38

Nanjing, Jiangsu, China

---

##### 1. 原型

```C++
typedef basic_string<char> string;
```

---

##### 2. 依赖

```C++
#include <string>
using namespace std;    // using std::string;
```

---

##### 3. Constructor

```C++
/*
 * Empty Constructor (Default Constructor)
 */
string();

/*
 * Copy Constructor
 */
string(const string& str);

/*
 * Substring Constructor
 */
string(const string& str, size_t pos, size_t len = npos);
// pos : Beginning of character position
// len : Length that wants to be copied
// (string is too short) | (len == string::npos) -> copy until the end of string

/*
 * From C-String
 */
string(const char* s);

/*
 * From C-String
 * Copy first n characters
 */
string(const char* s, size_t n);

/*
 * Fill Constructor
 */
string(size_t n, char c);
// Fill the string with n copies of character c

/*
 * Range Constructor
 */
template <class InputIterator> string(InputIterator first, InputIterator last);
```

---

##### 4. Destructor

---

##### 5. Member Constants

```C++
static const size_t npos = -1;
```

* The greatest possible value for an element of type _size_t_
* When used as the value for a _length_ parameter  __->__  Means __"Until the end of the string"__
* When used as a return value  __->__  Indicate __no matches__

---

##### 6. Iterators

```C++
#include <string>
using std::string;

int main()
{
    string str("Hello world");
    
    // 返回指向字符串开头的迭代器
    string::iterator begin_iter = str.begin();
    // 返回指向字符串结尾的下一个位置的迭代器
    string::iterator end_iter = str.end();
    // 返回指向字符串结尾的反向迭代器
    string::reverse_iterator r_begin_iter = str.rbegin();
    // 返回指向字符串开头的前一个位置的反向迭代器
    string::reverse_iterator r_end_iter = str.rend();
    
    return 0;
}
```

---

##### 7. Operators Overload

```C++
/*
 * Operator =
 *     Return a COPY of object
 */
string& operator= (const string& str);  // str = str1;
string& operator= (const char* s);      // str = "Hello world"
string& operator= (char c);             // str = '.'

/*
 * Operator +
 *     Return a newly consturcted obj after concatenation
 */
string operator+ (const string& lhs, const string& rhs);  // str = str1 + str2;
string operator+ (const string& lhs, const char* rhs);    // str = str1 + "Hello";
string operator+ (const char* lhs, const string& rhs);    // str = "Hello" + str2;
string operator+ (const string& lhs, char rhs);           // str = str1 + '.';
string operator+ (char lhs, const string& rhs);           // str = '.' + str2;

/*
 * Operator +=
 *     Return the same obj after appending value
 */
string& operator+= (const string& str);  // str += str1;
string& operator+= (const char* s);      // str += "Hello world";
string& operator+= (char c);             // str += '.'

/*
 * Operator []
 *     Return a reference to the character at position in the string
 *     if (position == string length) -> '\0'
 * 
 * --> Same function : string::at()
 */
      char& operator[] (size_t pos);
const char& operator[] (size_t pos) const;
      char& at (size_t pos);
const char& at (size_t pos) const;

/*
 * Operator >>
 *     For input
 */
istream& operator>> (istream& is, string& str);

/*
 * Operator <<
 *     For output
 */
ostream& operator<< (ostream& os, const string& str);
```

---

##### 8. Capacity

```C++
/*
 * Return length of string
 */
size_t size() const;
size_t length() const;

/*
 * Return the maximum length of the string can reach
 */
size_t max_size() const;

/*
 * Return size of allocated storage
 */
size_t capacity() const;

/*
 * Resizes the string to a length of n characters
 *     If c is specified, the new elements are initialized as copies of c,
 *     otherwise, they are value-initialized characters (null characters).
 *     If n is smaller than current string,
 *     the current value is shortened to its first n character.
 */
void resize (size_t n);
void resize (size_t n, char c);

/*
 * Request a change in capacity
 *     If n is greater than the current string capacity,
 *     the function causes the container to increase its capacity
 *     to n characters (or greater).
 *
 * Exception
 *     GUARANTEE : If an exception is thrown, there are no changes in the string.
 *     if n > max_size  ->  length_error exception
 *     if the function needs to allocate storage and fails  ->  bad_alloc exception
 */
void reserve (size_t n = 0);

/*
 * Erases the contents of the string  ->  Empty string
 */
void clear();

/*
 * Returns whether the string is empty
 */
bool empty() const;
```

---

##### 9. Modifiers

