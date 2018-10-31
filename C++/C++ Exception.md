# C++ - Exception

Created by : Mr Dk.

2018 / 09 / 13 13:49

Nanjing, Jiangsu, China

---

### 1. Exception Mechanism

* Place the code in which may cause exception in a __try__ block
* If exception happens, use __throw__ to raise a specific exception
* the exception is caught in the __catch__ block under __try__ block to do specific operation

```C++
#include <iostream>
using std::cout;
using std::endl;

void ThrowException()
{
    throw "Exception Test";
}

int main()
{
    try
    {
        ThrowException();
    }
    catch(const char* s)
    {
        cout << s << endl;
    }
    catch(...)	// Other Exception
    {
        cout << "other exception" << endl;
    }
    
    return 0;
}
```

---

### 2. Exception Class

* Basic class : `std::exception`

```C++
class exception
{
public:
    exception () noexcept;
    exception (const exception&) noexcept;
    exception& operator= (const exception&) noexcept;
    virtual ~exception();
    virtual const char* what() const noexcept;
}
```

* `exception () noexcept;`
  * Constructor
  * No exception will be thrown
* `exception (const exception&) noexcept;`
  * Copy constructor
  * No exception will be thrown
* `exception& operator= (const exception&) noexcept;`
  * Overload operator for assigning
  * No exception will be thrown
* `virtual ~exception();`
  * Destructor
  * May throw exception
  * Can be __override__
* `virtual const char* what() const noexcept;`
  * Exception message
  * No exception will be thrown
  * Can be __override__

---

### 3. My Own Exception Class

* Extend from `std::exception`

```C++
#include <iostream>
using std::cout;
using std::endl;
using std::exception;

class MyException : public exception
{
public:
    const char* what() {return "My Exception";}
};

void ThrowException()
{
    throw MyException();
}

int main()
{
    try
    {
        ThrowException();
    }
    catch(MyException &me)
    {
        cout << me.what() << endl;
    }
    catch(...)
    {
        cout << "Other Exceptions" << endl;
    }
    
    return 0;
}
```

---



