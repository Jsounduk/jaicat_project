@echo off
mkdir Incubate
echo Moving unused or legacy files into Incubate folder...
if exist backups move backups Incubate\
if exist legacy move legacy Incubate\
if exist deprecated move deprecated Incubate\
if exist temp move temp Incubate\
if exist old_modules move old_modules Incubate\
if exist samples move samples Incubate\
if exist test_data move test_data Incubate\
if exist experimental move experimental Incubate\
:: Move files by extension
for %%f in (*.zip) do move "%%f" Incubate\
for %%f in (*.txt) do move "%%f" Incubate\
for %%f in (*.docx) do move "%%f" Incubate\
for %%f in (*.old) do move "%%f" Incubate\
for %%f in (*.bak) do move "%%f" Incubate\
echo Cleanup complete.
pause