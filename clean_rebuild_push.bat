@echo off
REM ===============================
REM Clean Jaicat Repo Bootstrapper
REM ===============================

echo [1/5] Creating clean folder...
mkdir jaicat_clean
xcopy * jaicat_clean\ /E /I /Y
cd jaicat_clean

echo [2/5] Initializing fresh Git repo...
rmdir /S /Q .git
git init
git lfs install

echo [3/5] Tracking LFS files...
git lfs track "*.weights"
echo yolov7.weights >> .gitignore
git add .gitattributes
git add .gitignore

echo [4/5] Adding files...
git add .
git commit -m "Clean rebuild: repo reset with LFS for yolov7.weights"

echo [5/5] Pushing to GitHub with force...
git remote add origin https://github.com/Jsounduk/jaicat_project
git push --force origin main

echo Done! Your repo is clean, tracked with LFS, and fully pushed 💋
pause
