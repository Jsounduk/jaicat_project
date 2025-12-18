@echo off
setlocal ENABLEDELAYEDEXPANSION

:: === CONFIGURATION ===
set "TARGET_FOLDER=%~1"
if "%TARGET_FOLDER%"=="" set /p TARGET_FOLDER="Enter folder path to scan: "

set "OUTPUT_WORD=Folder_Structure_Report.docx"

:: === START ===
echo Generating folder structure and content...
powershell -ExecutionPolicy Bypass -File "%~dp0\generate_word_report.ps1" "%TARGET_FOLDER%" "%OUTPUT_WORD%"

echo Done. Output file: %OUTPUT_WORD%
pause
