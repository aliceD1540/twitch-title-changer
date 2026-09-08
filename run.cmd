@echo off
REM Twitch Title Changer - Windows Entry Point
REM このスクリプトは Windows 環境で GUI アプリケーションを起動します

REM UTF-8 コードページに設定（日本語文字表示用）
chcp 65001 >nul 2>&1

REM スクリプト自身が最小化ウィンドウで実行されている場合は、新しいウィンドウで再実行
@if not "%~0"=="%~dp0.\%~nx0" (
    start "Twitch Title Changer" cmd /c "%~dp0.\%~nx0" %*
    goto :eof
)

REM 実行ディレクトリをスクリプトのディレクトリに設定
cd /d "%~dp0"

REM Python が存在するか確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo .
        echo ==============================================================
        echo エラー: Python が見つかりません
        echo ==============================================================
        echo.
        echo Python 3.8 以上がインストールされていることを確認してください。
        echo https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

REM 環境変数を設定（UTF-8 エンコーディング）
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo.
echo ==============================================================
echo Twitch Title Changer を起動しています...
echo ==============================================================
echo.

REM メインアプリケーションを実行
%PYTHON% main.py

if %errorlevel% neq 0 (
    echo.
    echo ==============================================================
    echo アプリケーションがエラーで終了しました
    echo ==============================================================
    echo.
    pause
)

exit /b %errorlevel%
