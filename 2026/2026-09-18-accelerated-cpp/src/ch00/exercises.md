# Accelerated C++ — Chapter 0 Exercises

Reference: *Accelerated C++: Practical Programming by Example*, Chapter 0 ("Getting started").

---

### Exercise 0-0
Compile and run the `"Hello, world!"` program.
* Source: [`0-0-hello.cpp`](0-0-hello.cpp)

### Exercise 0-1
What does the following statement do?
```cpp
3 + 4;
```
*(Hint: It is a valid expression statement that evaluates the sum, but discards the result. Modern compilers with `/W4` may warn about an expression with no effect.)*

### Exercise 0-2
Write a program that, when run, writes the following text to standard output:
```text
This (") is a quote, and this (\) is a backslash.
```
*(Tests understanding of escape sequences: `\"` and `\\`.)*

### Exercise 0-3
The string literal `"\t"` represents a tab character; different platforms and display programs display tabs using different numbers of columns. Experiment with tabs to see how your system behaves.

### Exercise 0-4
Write a program that, when run, writes the exact C++ source code of the `"Hello, world!"` program as its output.

### Exercise 0-5
Is this a valid program? Why or why not?
```cpp
#include <iostream>

int main() std::cout << "Hello, world!" << std::endl;
```
*(Tests understanding of function bodies and curly brace requirements in C++.)*

### Exercise 0-6
Is this a valid program? Why or why not?
```cpp
#include <iostream>

int main() {{{{{{ std::cout << "Hello, world!" << std::endl; }}}}}}
```
*(Tests compound statements / nested block scopes.)*

### Exercise 0-7
What does this program do?
```cpp
#include <iostream>

int main()
{
    /* This is a comment that extends over several lines
       because it uses /* and */ as its starting and ending delimiters */
    std::cout << "Does this work?" << std::endl;
    return 0;
}
```
*(Tests block comment nesting rules: `/* ... */` comments do NOT nest in C++.)*

### Exercise 0-8
What about this comment?
```cpp
// This is a comment that extends over several lines
// by using // at the beginning of each line instead of using /*
// or */ to delimit comments.
```

### Exercise 0-9
What is the shortest valid C++ program?

### Exercise 0-10
Rewrite the `"Hello, world!"` program using `\n` instead of `std::endl`. Does it behave identically? What is the technical difference?
*(Hint: `std::endl` writes `\n` and then flushes the buffer via `std::flush`.)*
