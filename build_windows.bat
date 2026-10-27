@echo off
REM ===========================================================
REM  IDM Lite - one-click Windows build
REM  Produces: dist\IDM Lite.exe
REM ===========================================================
setlocal
cd /d "%~dp0"

echo.
echo  ==============================================
echo   IDM Lite - building the Windows executable
echo  ==============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo  [ERROR] Python 3.10+ was not found on PATH.
    echo          Install it from https://python.org/downloads/
    echo          and tick "Add python.exe to PATH" during setup.
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo  [ERROR] Python 3.10 or newer is required.
    pause
    exit /b 1
)

echo  [1/4] Installing PyInstaller...
python -m pip install --upgrade pip --quiet
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo  [ERROR] Could not install PyInstaller.
    pause
    exit /b 1
)

echo  [2/4] Regenerating the icon...
python tools\make_icon.py

echo  [3/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo  [4/4] Building IDM Lite.exe ...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "IDM Lite" ^
    --icon "assets\icon.ico" ^
    --add-data "browser_extension;browser_extension" ^
    --hidden-import "idmlite.engine" ^
    --hidden-import "idmlite.gui" ^
    --hidden-import "idmlite.dialogs" ^
    main.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo  ==============================================
echo   DONE: dist\IDM Lite.exe
echo  ==============================================
echo.
echo  The browser extension is bundled next to the
echo  executable in dist\browser_extension\
echo.
pause
