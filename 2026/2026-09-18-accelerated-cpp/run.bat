@echo off
setlocal enabledelayedexpansion
pushd "%~dp0"

:: Check if cl is already in PATH
where cl >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :HAVE_CL

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
    goto :HAVE_CL
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
    goto :HAVE_CL
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" >nul
    goto :HAVE_CL
)

echo [ERROR] MSVC C++ compiler (cl.exe) not found in PATH and vcvars64.bat not found.
popd
exit /b 1

:HAVE_CL

:: Select target file
set TARGET=%~1
if "%TARGET%"=="" (
    set TARGET=src\ch00\0-0-hello.cpp
)

if not exist "%TARGET%" (
    echo [ERROR] Target file not found: %TARGET%
    exit /b 1
)

:: Ensure output directory exists
if not exist bin mkdir bin

echo [Compiling] %TARGET% (C++20 /W4)...
cl /nologo /std:c++20 /EHsc /W4 /Fe:bin\program.exe /Fo:bin\program.obj "%TARGET%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo -------------------- Execution Output --------------------
    bin\program.exe
    set RUN_EXIT=%ERRORLEVEL%
    echo ----------------------------------------------------------
    echo [Program exited with code !RUN_EXIT!]
    popd
) else (
    echo.
    echo [BUILD FAILED]
    popd
    exit /b %ERRORLEVEL%
)
