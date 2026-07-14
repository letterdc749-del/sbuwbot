@echo off
cd C:\Users\heart\Downloads\SouthBronxBot
start "Flask Server" cmd /k python server.py
timeout /t 2
start "Discord Bot" cmd /k python bot.py
timeout /t 3
start "ngrok" cmd /k ""C:\Users\heart\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe" http 5000"
exit
