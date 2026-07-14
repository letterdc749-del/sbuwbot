@echo off
REM Run this file as Administrator
schtasks /create /tn "SouthBronxBot" /tr "C:\Users\heart\Downloads\SouthBronxBot\start_bot.bat" /sc onstart /rl highest /f
echo ✅ Task created! Bot will auto-start at boot.
pause
