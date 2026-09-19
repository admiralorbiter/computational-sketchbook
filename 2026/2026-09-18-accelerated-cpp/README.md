# Accelerated C++ — Deliberate Practice Workbench

> **Status:** `ACTIVE` — Started: 2026-09-18  
> **Type:** Deliberate practice workspace / textbook study  
> **Textbook:** *Accelerated C++: Practical Programming by Example* (Andrew Koenig & Barbara E. Moo)  
> **Compiler:** MSVC 2022 (x64) with `/std:c++20 /W4 /EHsc`  
> **Related BBT notes:** [`intervention-competence-practice.md`](../../../bigbraintime/projects/intervention-competence-practice.md), [`cognitive-modes-and-protected-inefficiency.md`](../../../bigbraintime/notes/cognitive-modes-and-protected-inefficiency.md)

---

## 1. Purpose & Practice Rules

This repository folder serves as a distraction-free, unassisted coding workbench for working through Koenig & Moo’s *Accelerated C++*. The goal is to build muscle memory, idiomatic C++ mental models, and algorithmic confidence without generative AI scaffolding.

### The Practice Contract:
1. **Hand-typed code only:** Type every program and exercise from an empty file. No pasting generated solutions.
2. **Strict compiler discipline:** Compiled with `/W4` (high warning level) and modern `/std:c++20`. Treat warnings as actionable feedback.
3. **Reason before running:** Predict output, state invariants, and trace edge cases before executing.
4. **Reference materials allowed:** Language standard docs ([cppreference.com](https://en.cppreference.com/w/)), debugger, and compiler diagnostics.

---

## 2. Quick Start: Build & Run

A unified runner script is provided for both CMD and PowerShell. It automatically discovers the MSVC 64-bit environment and compiles in C++20 mode.

### From Terminal:
```powershell
# Using the Batch runner:
.\run.bat src\ch00\0-0-hello.cpp

# Or using the PowerShell runner:
.\run.ps1 src\ch00\0-0-hello.cpp

# Omit arguments to run the default target:
.\run.bat
```

### In VS Code:
1. Open any `.cpp` file in `src/`.
2. Press `Ctrl+Shift+B` (the default build task).
3. The file compiles with warnings displayed in the terminal and runs immediately.

---

## 3. Directory Layout

```text
2026-09-18-accelerated-cpp/
├── README.md               # This guide and progress tracker
├── run.bat                 # One-click Windows CMD build & run script
├── run.ps1                 # One-click PowerShell build & run script
├── .vscode/
│   └── tasks.json          # Ctrl+Shift+B build task for active file
├── bin/                    # Output binaries and object files (gitignored)
└── src/
    ├── ch00/               # Chapter 0: Getting Started
    │   ├── 0-0-hello.cpp
    │   └── exercises.md
    ├── ch01/               # Chapter 1: Working with Strings
    │   └── 1-0-greeting.cpp
    └── ch02/ ...           # Subsequent chapters & exercises
```

---

## 4. Chapter Roadmap & Exercise Log

| Chapter | Topic | Key C++ Concepts | Status |
|---|---|---|---|
| **0** | Getting started | `#include <iostream>`, `std::cout`, expressions, return codes, comments | `READY` |
| **1** | Working with strings | `std::string`, `std::cin`, `const`, string construction `(n, c)` | `READY` |
| **2** | Looping and counting | Invariants, `while`, `for`, loop bounds, coordinates | `QUEUED` |
| **3** | Batches of data | `std::vector`, sorting (`std::sort`), medians, floating point precision | `QUEUED` |
| **4** | Organizing computations | Functions, references (`const &`), pass-by-value vs reference, header files | `QUEUED` |
| **5** | Sequential containers | Iterators, `std::vector` vs `std::list`, erasing elements, string analysis | `QUEUED` |
| **6** | Library algorithms | `<algorithm>`, predicates, two-pointer algorithms, copy/transform | `QUEUED` |
| **7** | Associative containers | `std::map`, key-value lookup, word count histograms, cross-reference tables | `QUEUED` |
| **8** | Writing generic functions | Template functions, iterator categories, generic algorithms | `QUEUED` |
| **9–12** | Defining types & classes | Encapsulation, constructors, memory management, copy constructors | `QUEUED` |
| **13–14**| Polymorphism & handles | Virtual functions, dynamic binding, inheritance, smart handle classes | `QUEUED` |
| **15–16**| Character pictures | Designing practical extensible data structures | `QUEUED` |
