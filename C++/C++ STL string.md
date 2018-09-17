## C++ STL string

Created by : Mr Dk.

2018 / 09 / 17 20:38

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

* Empty Constructor (Default Constructor)

  * ```C++
    string();
    ```

* Copy Constructor

  * ```C++
    string (const string& str);
    ```

* Substring Constructor
  * `pos` : Beginning of character position

  * `len` : Length that wants to be copied

  * (string is too short) | ( `len` == `string::npos` )  __->__  copy until the end of string

  * ```C++
    string (const string& str, size_t pos, size_t len = npos);
    ```

* From C-String

  * ```C++
    string (const char* s);
    ```

* From C-String, Copy first n characters

  * ```C++
    string (const char* s, size_t n);
    ```

* Fill Constructor

  * Fill the string with n copies of character c

  * ```C++
    string (size_t n, char c);
    ```

* Range Constructor

  * ```C++
    template <class InputIterator> string (InputIterator first, InputIterator last);
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

* 返回指向字符串开头的迭代器

  * ```C++
    string::iterator begin_iter = str.begin();
    ```

* 返回指向字符串结尾的下一个位置的迭代器

  * ```C++
    string::iterator end_iter = str.end();
    ```

* 返回指向字符串结尾的反向迭代器

  * ```C++
    string::reverse_iterator r_begin_iter = str.rbegin();
    ```

* 返回指向字符串开头的前一个位置的反向迭代器

  * ```C++
    string::reverse_iterator r_end_iter = str.rend();
    ```

---

##### 7. Operators Overload

* Operator `=`

  * Return a COPY of object

  * ```C++
    string& operator= (const string& str);  // str = str1;
    string& operator= (const char* s);      // str = "Hello world"
    string& operator= (char c);             // str = '.'
    ```

* Operator `+`

  * Return a newly constructed object after concatenation

  * ```C++
    string operator+ (const string& lhs, const string& rhs);  // str = str1 + str2;
    string operator+ (const string& lhs, const char* rhs);    // str = str1 + "Hello";
    string operator+ (const char* lhs, const string& rhs);    // str = "Hello" + str2;
    string operator+ (const string& lhs, char rhs);           // str = str1 + '.';
    string operator+ (char lhs, const string& rhs);           // str = '.' + str2;
    ```

* Operator `+=`

  * Return the same object after appending value

  * ```C++
    string& operator+= (const string& str);  // str += str1;
    string& operator+= (const char* s);      // str += "Hello world";
    string& operator+= (char c);             // str += '.'
    ```

* Operator `[]`
  * Return a reference to the character at position in the string

   * if (position == string length)  __->__  '\0'

   * Same function : `string::at()`

   * _C++11_
      * `front()`  __->__  Access the first character
      * `back()`  __->__  Access the last character
      * Exception
         * If the string is empty  __->__  _undefined behavior_

  * ```C++
            char& operator[] (size_t pos);
      const char& operator[] (size_t pos) const;
            char& at (size_t pos);
      const char& at (size_t pos) const;
            char& front();
      const char& front() const;
            char& back();
      const char& back() const;
      ```

* Operator >>

  * For input

  * ```C++
    istream& operator>> (istream& is, string& str);
    ```

* Operator <<

  * For output

  * ```C++
    ostream& operator<< (ostream& os, const string& str);
    ```

---

##### 8. Capacity

* Return length of string

  * ```C++
    size_t size() const;
    size_t length() const;
    ```

* Return the maximum length of the string can reach

  * ```C++
    size_t max_size() const;
    ```

* Return size of allocated storage

  * ```C++
    size_t capacity() const;
    ```

* Resizes the string to a length of n characters
  * If `c` is specified, the new elements are initialized as copies of `c`

  * Otherwise, they are value-initialized characters (null characters)

  * If `n` is smaller than current string

  * The current value is shortened to its first `n` character

  * ```C++
    void resize (size_t n);
    void resize (size_t n, char c);
    ```

* Request a change in capacity
  * If `n` is greater than the current string capacity

  * The function causes the container to increase its capacity to `n` characters (or greater)

  * Exception
    * __GUARANTEE__ : If an exception is thrown, there are __NO__ changes in the string
    * If `n` > `max_size`  __->__  `length_error` exception
    * If the function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    void reserve (size_t n = 0);
    ```

* Erases the contents of the string  __->__  Empty string

  * ```C++
    void clear();
    ```

* Returns whether the string is empty

  * ```C++
    bool empty() const;
    ```

---

##### 9. Modifiers

* Assigns a new value to the string
  * Replacing its current contents

  * Exception
    - `s` is not long enough | `range` is not valid  __->__  _undefined behavior_
    - `subpos` __>__ _string length_  __->__  `out_of_range` exception
    - Resulting string length __>__ `max_size`  __->__  `length_error` exception
    - The function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    string& assign (const string& str);                                // String
    string& assign (const string& str, size_t subpos, size_t sublen);  // Substring
    string& assign (const char* s);                                    // C-String
    string& assign (const char* s, size_t n);                          // Buffer
    string& assign (size_t n, char c);                                 // Fill
    template <class InputIterator>
       string& assign (InputIterator first, InputIterator last);       // Range
    ```

* Appending additional characters at the end of its current value
  * Exception
    * `s` is not long enough | `range` is not valid  __->__  _undefined behavior_
    * `subpos` __>__ _string length_  __->__  `out_of_range` exception
    * Resulting string length __>__ `max_size`  __->__  `length_error` exception
    * The function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    string& append (const string& str);                                // String
    string& append (const string& str, size_t subpos, size_t sublen);  // Substring
    string& append (const char* s);                                    // C-String
    string& append (const char* s, size_t n);                          // Buffer
    string& append (size_t n, char c);                                 // Fill
    template <class InputIterator> string&
        append (InputIterator first, InputIterator last);              // Range
    ```

* Insert into string
  * Insert into the string right __before__ the character indicated by `pos` or `p`

  * Exception
    * `s` is not long enough | `range` is not valid  __->__  _undefined behavior_
    * `subpos` __>__ _str's length_  __->__  `out_of_range` exception
    * Resulting string length __>__ `max_size`  __->__  `length_error` exception
    * The function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    string& insert (size_t pos, const string& str);          // String
    string& insert (size_t pos, const string& str, size_t subpos, size_t sublen = npos);
                                                             // Substring
    string& insert (size_t pos, const char* s);              // C-String
    string& insert (size_t pos, const char* s, size_t n);    // Buffer
    string& insert (size_t pos, size_t n, char c);           // Fill
    iterator insert (const_iterator p, size_t n, char c);    // Fill
    iterator insert (const_iterator p, char c);              // Single Character
    template <class InputIterator>
        iterator insert (iterator p, InputIterator first, InputIterator last);  // Range
    ```

* Erase characters from string
  * Exception
    * If `pos` __>__ _string length_  __->__  `out_of_range` exception
    * If _range_ is invalid  __->__  _undefined behavior_

  * ```C++
    string& erase(size_t pos = 0, size_t len = npos);        // Sequence
    iterator erase (iterator p);                             // Character
    iterator erase (iterator first, iterator last);          // Range
    ```

* Replace portion of string
  * Specify a range in old string by
    * `pos` & `len`
    * A pair of _iterators_

  * Specify a new string to replace into the specific range

  * Exception
    * If `s` is not long enough | range is not valid  __->__  _undefined behavior_
    * `pos` or `subpos` is greater than _string's length_  __->__  `out_of_range` exception
    * If the resulting string length __>__ `max_size`  __->__  `length_error` exception
    * If the function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    // String
    string& replace (size_t pos, size_t len, const string& str);
    string& replace (const_iterator i1, const_iterator i2, const string& str);
    // Substring
    string& replace (size_t pos, size_t len,
                     const string& str, size_t subpos, size_t sublen = npos);
    // C-String
    string& replace (size_t pos, size_t len, const char* s);
    string& replace (const_iterator i1, const_iterator i2, const char* s);
    // Buffer
    string& replace (size_t pos, size_t len, const char* s, size_t n);
    string& replace (const_iterator i1, const_iterator i2, const char* s, size_t n);
    // Fill
    string& replace (size_t pos, size_t len, size_t n, char c);
    string& replace (const_iterator i1, const_iterator i2, size_t n, char c);
    // Range
    template <class InputIterator>
        string& replace (const_iterator i1, const_iterator i2,
                         InputIterator first, InputIterator last);
    ```

* Swap string values

  * ```C++
    void swap (string& str);            // Member function -> str1.swap(str2);
    void swap (string& x, string& y);   // Not a member function -> swap(str1, str2);
    ```

* Append character to the end of the string
  * Increasing its length by __one__

  * Exception
    - Resulting string length __>__ `max_size`  __->__  `length_error` exception
    - The function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    void push_back (char c);
    ```

* Delete the last character of the string
  * Reducing its length by __one__

  * Exception

    * If the string is empty  __->__  _undefined behavior_

  * ```C++
    void pop_back();
    ```

---

##### 10. String Operations

* Get _C_ String

  * With `\0` in the end

  * ```C++
    const char* c_str() const noexcept;
    const char* data() const noexcept;
    ```

* Copy sequence of characters __from__ string
  * string -> char[]

  * Return the number of characters copied to the array

  * Exception
    * If `s` is not long enough  __->__  _undefined behavior_
    * If `pos` __>__ _string's length_  __->__  `out_of_range` exception

  * ```C++
    size_t copy (char* s, size_t len, size_t pos = 0) const;
    ```

* Compare strings

  * _Compared string_ & _Comparing string_

  * | Value | Reason                                                       |
    | ----- | ------------------------------------------------------------ |
    | 0     | Compare equal.                                               |
    | <0    | Either the value of the first character that does not match is lower in the _compared string_, or all characters match but _compared string_ is shorter. |
    | >0    | Either the value of the first character that does not match is greater in the _compared string_, or all characters match but _compared string_ is longer. |

  * Exception

    * If `s` is not long enough  __->__  _undefined behavior_
    * If `pos` or `subpos`  __>__ _string's length_  __->__  `out_of_range` exception

  * ```C++
    // String
    int compare (const string& str) const noexcept;
    // Substrings
    int compare (size_t pos, size_t len, const string& str) const;
    int compare (size_t pos, size_t len,
                 const string& str, size_t subpos, size_t sublen) const;
    // C-String
    int compare (const char* s) const;
    int compare (size_t pos, size_t len, const char* s) const;
    // Buffer
    int compare (size_t pos, size_t len, const char* s, size_t n) const;
    ```

* Generate substring
  * Exception
    * If `pos` __>__ _string's length_  __->__  `out_of_range` exception
    * If the function needs to allocate storage and fails  __->__  `bad_alloc` exception

  * ```C++
    string substr (size_t pos = 0, size_t len = npos) const;
    ```

* Find content in string
  * __Match the entire string__

  * Exception

    * If `s` is not long enough  __->__  _undefined behavior_

  * `pos` is used to specify the first character to start searching

  * `n` is used to specify the length of `s`

  * If there is no match, return `string::npos`

  * ```C++
    // Find the first occurrence
    size_t find (const string& str, size_t pos = 0) const noexcept;      // String
    size_t find (const char* s, size_t pos = 0) const;                   // C-String
    size_t find (const char* s, size_t pos, size_type n) const;          // Buffer
    size_t find (char c, size_t pos = 0) const noexcept;                 // Character
    
    // Find the last occurrence
    size_t rfind (const string& str, size_t pos = npos) const noexcept;  // String
    size_t rfind (const char* s, size_t pos = npos) const;               // C-String
    size_t rfind (const char* s, size_t pos, size_t n) const;            // Buffer
    size_t rfind (char c, size_t pos = npos) const noexcept;             // Character
    ```

* Find character in string
  * __Match any of the characters specified in arguments__

  * Exception

    * If `s` is not long enough  __->__  _undefined behavior_

  * `pos` is used to specify the first character to start searching

  * `n` is used to specify the length of `s`

  * If there is no match, return `string::npos`

  * ```C++
    // The first character matched
    size_t find_first_of (const string& str, size_t pos = 0) const noexcept;  // String
    size_t find_first_of (const char* s, size_t pos = 0) const;               // C-String
    size_t find_first_of (const char* s, size_t pos, size_t n) const;         // Buffer
    size_t find_first_of (char c, size_t pos = 0) const noexcept;             // Character
    
    // The first character absent
    size_t find_first_not_of (const string& str, size_t pos = 0) const noexcept; // String
    size_t find_first_not_of (const char* s, size_t pos = 0) const;        // C-String
    size_t find_first_not_of (const char* s, size_t pos, size_t n) const;  // Buffer
    size_t find_first_not_of (char c, size_t pos = 0) const noexcept;      // Character
    
    // The last character matched
    size_t find_last_of (const string& str, size_t pos = npos) const noexcept; // String
    size_t find_last_of (const char* s, size_t pos = npos) const;              // C-String
    size_t find_last_of (const char* s, size_t pos, size_t n) const;           // Buffer
    size_t find_last_of (char c, size_t pos = npos) const noexcept;            // Character
    
    // The last character absent
    size_t find_last_not_of (const string& str, size_t pos = npos) const noexcept;// String
    size_t find_last_not_of (const char* s, size_t pos = npos) const;          // C-String
    size_t find_last_not_of (const char* s, size_t pos, size_t n) const;       // Buffer
    size_t find_last_not_of (char c, size_t pos = npos) const noexcept;        // Character
    ```

---

##### 11. Input

* `cin` & `>>`
* _getline_

  * default delimitation character - `\n`

  * ```C++
    istream& getline (istream&  is, string& str, char delim);
    istream& getline (istream&& is, string& str, char delim);
    istream& getline (istream&  is, string& str);
    istream& getline (istream&& is, string& str);
    ```

---

##### 12. Summary

Useful & important

---

