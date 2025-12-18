
@echo off
setlocal enabledelayedexpansion

set ARCHIVE_DIR=archive
if not exist %ARCHIVE_DIR% mkdir %ARCHIVE_DIR%

set FILES=main copy.txt main copy 2.txt "main - Master Before Changing my self.txt" conversation_management.py face_concerned.jpeg face_flirty.jpeg face_neutral.jpeg face_sad.jpeg file_handling.py image_processing.py filename.txt

for %%F in (%FILES%) do (
    if exist "%%F" (
        move "%%F" "%ARCHIVE_DIR%\"
        echo Moved: %%F → %ARCHIVE_DIR%\
    ) else (
        echo Not found: %%F
    )
)
