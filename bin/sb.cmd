@echo off
setlocal
set "SB_ROOT=%~dp0.."
set "PYTHONPATH=%SB_ROOT%\app;%PYTHONPATH%"
if defined SB_PYTHON (
  "%SB_PYTHON%" -m second_brain.cli %*
) else (
  python -m second_brain.cli %*
)
exit /b %errorlevel%
