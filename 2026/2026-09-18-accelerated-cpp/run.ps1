<#
.SYNOPSIS
    Compiles and runs a C++ file using MSVC in C++20 mode.
.EXAMPLE
    .\run.ps1
    .\run.ps1 src\ch00\0-0-hello.cpp
#>
param(
    [string]$Target = "src\ch00\0-0-hello.cpp"
)

Push-Location $PSScriptRoot
try {
    cmd.exe /c "run.bat `"$Target`""
} finally {
    Pop-Location
}
