@echo off
REM === CONFIGURATION ===
set REPO_URL=https://github.com/Jsounduk/jaicat_project
set REPO_NAME=jaicat_project
set FILE_TO_DELETE=yolov7.weights
set BFG_JAR=bfg-1.14.0.jar

REM === STEP 1: Clone mirror repo ===
echo Cloning mirror of %REPO_URL%
git clone --mirror %REPO_URL%
cd %REPO_NAME%.git

REM === STEP 2: Run BFG to delete large file ===
echo Running BFG Repo-Cleaner...
java -jar ..\%BFG_JAR% --delete-files %FILE_TO_DELETE%

REM === STEP 3: Cleanup and prune history ===
git reflog expire --expire=now --all
git gc --prune=now --aggressive

REM === STEP 4: Force-push clean repo to GitHub ===
echo Force pushing cleaned history to GitHub...
git push --force

cd ..
echo All done Sir. Your repo is now purged of that naughty %FILE_TO_DELETE% 💋
pause
