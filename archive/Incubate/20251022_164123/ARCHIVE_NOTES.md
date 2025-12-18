# Incubate Archive (20251022_164123)

The following files were moved here to consolidate duplicates and standardise imports:

- Core\controller.py (replaced by app\controller.py)
- command\processor.py (replace with Core\command_router + command\builtin)
- command\handler_table.py (same as above)
- services\weather_api.py (use services\weather_service.py)
- services\calendar_api.py, services\google_calendar_api.py (use services\calendar_service.py)
- utils\encryption_utils.py (use security\encryption_utils.py)
- utils\enrollment.py (use services\user_enrollment.py)
- services\spotify_integration 1.txt (notes merged; file removed)

If -MigrateOneDrive was used:
- computer_vision\oneDrive.py -> services\one_drive.py (imports updated)

A backup of modified source files lives at:
C:\Users\josh_\Desktop\jaicat_project\archive\RefactorBackups\20251022_164123

See change log:
C:\Users\josh_\Desktop\jaicat_project\archive\RefactorLog_20251022_164123.txt
