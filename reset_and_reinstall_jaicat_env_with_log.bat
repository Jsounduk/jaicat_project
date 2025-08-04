@echo off
SETLOCAL ENABLEEXTENSIONS
SET LOGFILE=jaicat_install_log.txt

echo Removing conflicting packages... > %LOGFILE%
pip uninstall -y httpx jsonschema protobuf psutil h11 httpcore >> %LOGFILE% 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to uninstall one or more packages. See %LOGFILE% for details.
    exit /b 1
)

echo Installing from compatible requirements... >> %LOGFILE%
pip install -r jaicat_compatible_requirements.txt >> %LOGFILE% 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install packages. See %LOGFILE% for details.
    exit /b 1
)

echo Installation complete with no errors. >> %LOGFILE%
echo ✅ All done! Log saved to %LOGFILE%
ENDLOCAL
