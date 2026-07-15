@echo off
REM ==============================
REM  TECH SUPPORT TOOLS
REM  Simple everyday tasks for
REM  beginners. Just pick a number.
REM ==============================

REM Set the window title so they know what this is
title Tech Support Tools

REM Make text green on black (easier to read)
color 0A

REM Clear the screen
cls


REM ==============================
REM  CHECK IF RUNNING AS ADMIN
REM  Some options need admin rights.
REM  If not admin, we show a warning.
REM ==============================

REM Check if we are running as Administrator.
REM We try to create a file in C:\Windows\System32
REM (only admins can write there).
REM If it fails, we are NOT admin.
NET SESSION >nul 2>&1
if %errorlevel% neq 0 (
    set "is_admin=NO"
) else (
    set "is_admin=YES"
)


REM ==============================
REM  MENU - show options and ask
REM  the user to pick one
REM ==============================
:menu
cls
echo ==============================
echo    TECH SUPPORT TOOLS
echo    Simple everyday tasks
echo ==============================
echo.

REM Show a message if not running as admin
if "%is_admin%"=="NO" (
    echo  [!] NOT running as Administrator
    echo  [!] Options 4 and 5 work best with Admin rights
    echo  [!] Right-click this file -^> "Run as administrator"
    echo.
)

echo  1 - Show my IP address
echo  2 - Ping Google (test internet)
echo  3 - Check disk space
echo  4 - Clear temp files     (needs Admin)
echo  5 - Show system info     (needs Admin)
echo  6 - Exit
echo.

REM "set /p" asks the user to type something
REM The input is stored in a variable called "choice"
set /p "choice=Pick a number: "

REM Check what the user typed and jump to that section
REM If none match, go back to the menu
if "%choice%"=="1" goto ip
if "%choice%"=="2" goto ping
if "%choice%"=="3" goto disk
if "%choice%"=="4" goto clean
if "%choice%"=="5" goto info
if "%choice%"=="6" exit
goto menu


REM ==============================
REM  OPTION 1 - Show IP address
REM ==============================
:ip
cls
echo [Your IP Address]
echo.

REM "ipconfig" shows network info
REM "findstr" filters to only show the IPv4 line
ipconfig | findstr "IPv4"
echo.
pause
goto menu


REM ==============================
REM  OPTION 2 - Ping Google
REM ==============================
:ping
cls
echo [Testing internet connection...]
echo.

REM Pings Google 4 times to see if we get a reply
REM If you see "Reply from" = internet works
REM If you see "Request timed out" = no internet
ping google.com -n 4
echo.
pause
goto menu


REM ==============================
REM  OPTION 3 - Check disk space
REM ==============================
:disk
cls
echo [Disk Space]
echo.

REM Shows each drive letter, how much space it has,
REM and how much is free
wmic logicaldisk get size,freespace,caption
echo.
pause
goto menu


REM ==============================
REM  OPTION 4 - Clear temp files
REM ==============================
:clean
cls
echo [Clear Temp Files]
echo.

REM If not admin, tell the user it may not work fully
if "%is_admin%"=="NO" (
    echo  [!] You are NOT running as Administrator.
    echo  [!] This may not delete all temp files.
    echo  [!] Close this and right-click -^> "Run as administrator"
    echo.
)

echo WARNING: This will delete temporary files from:
echo   - Your user temp folder
echo   - Windows temp folder
echo.
echo These are safe to delete, but if you are unsure,
echo you can type N to cancel.
echo.

REM Ask the user to confirm before deleting
set /p "confirm=Are you sure you want to delete temp files? (Y/N): "

REM If they typed N (or n), cancel
if /i "%confirm%"=="N" (
    echo.
    echo Cancelled. Nothing was deleted.
    echo.
    pause
    goto menu
)

REM If they typed anything besides Y, also cancel
if /i not "%confirm%"=="Y" (
    echo.
    echo Cancelled. Nothing was deleted.
    echo.
    pause
    goto menu
)

REM User said Yes - go ahead and delete
echo.
echo Deleting temp files... please wait.

REM Delete user temp files (like from your browser, etc.)
REM "del" = delete, "/q" = quiet (don't ask), "/s" = subfolders
REM ">nul 2>nul" = hide success and error messages
del /q /s "%temp%\*.*" >nul 2>nul

REM Delete Windows temp files - this needs Admin rights
REM If not admin, this line will just fail silently
del /q /s "C:\Windows\Temp\*.*" >nul 2>nul

echo Done! Temp files have been deleted.
echo.
pause
goto menu


REM ==============================
REM  OPTION 5 - Show system info
REM ==============================
:info
cls
echo [System Information]
echo.

REM If not admin, warn that info may be limited
if "%is_admin%"=="NO" (
    echo  [!] Running without Admin rights.
    echo  [!] Some info may be hidden.
    echo.
)

REM Shows basic info about the computer
REM "/c" means search for multiple patterns
systeminfo | findstr /c:"OS Name" /c:"OS Version" /c:"System Manufacturer" /c:"Total Physical Memory"
echo.
pause
goto menu
