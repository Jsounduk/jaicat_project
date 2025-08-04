@echo off
REM ===============================
REM Jaicat Repo Safe Rebuild Script
REM ===============================

REM === CONFIGURATION ===
set PROJECT_FOLDER=jaicat_project
set CLEAN_FOLDER=jaicat_clean

echo [1/5] Checking path...
if not exist %PROJECT_FOLDER% (
    echo ERROR: '%PROJECT_FOLDER%' folder not found. Please run this script from the parent directory.
    pause
    exit /b
)

rmdir /S /Q %CLEAN_FOLDER% >nul 2>&1
mkdir %CLEAN_FOLDER%

echo [2/5] Copying '%PROJECT_FOLDER%' into '%CLEAN_FOLDER%'...
robocopy %PROJECT_FOLDER% %CLEAN_FOLDER% /E /XD .git

cd %CLEAN_FOLDER%

echo [3/5] Initializing fresh Git repo...
rmdir /S /Q .git >nul 2>&1
git init
git lfs install

echo [4/5] Tracking LFS files and committing...
git lfs track "*.weights"
echo yolov7.weights>> .gitignore
git add .gitattributes
git add .gitignore
git add .
git commit -m "Clean rebuild: repo reset with LFS for yolov7.weights"
git branch -M main

echo [5/5] Pushing to GitHub with force...
git remote add origin https://github.com/Jsounduk/jaicat_project
git push --force origin main

echo All done Sir. Only '%PROJECT_FOLDER%' was pushed. Safe, clean, and ready 💋
pause
