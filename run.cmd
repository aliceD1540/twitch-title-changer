@echo off

@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

cd C:\Users\grimo\OneDrive\repo\twitch-title-changer
python3 .\gui.py
