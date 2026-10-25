@echo off
setlocal
cd /d "%~dp0.."
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist C:\Users\HP\Miniconda3\condabin\conda.bat (
    call C:\Users\HP\Miniconda3\condabin\conda.bat activate triageiq
)
python scripts\run_pipeline.py %*
