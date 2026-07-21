@echo off
REM ============================================================
REM Midnight Agent Launcher - Set env + start Ollama + run model
REM ============================================================
set OLLAMA_NUM_THREADS=16
set OLLAMA_KEEP_ALIVE=3m

REM Start Ollama serve (hidden) if not running
tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul
if errorlevel 1 (
    start "" /MIN ollama serve
    timeout /t 4 >nul
)

if "%1"=="" (
    echo ========================================
    echo  MIDNIGHT CORE LAUNCHER
    echo ========================================
    echo  [1] midnight-agent-fast  (Red Team AI - default)
    echo  [2] qwen2.5-coder:7b     (Coding)
    echo  [3] llama3.2:3b          (Chat cepat)
    echo ========================================
    set /p CHOICE="Pilih [1/2/3]: "
) else (
    set CHOICE=%1
)

if "%CHOICE%"=="2" set MODEL=qwen2.5-coder:7b
if "%CHOICE%"=="3" set MODEL=llama3.2:3b
if "%CHOICE%"=="1" set MODEL=midnight-agent-fast
if not defined MODEL set MODEL=midnight-agent-fast

echo.
echo >> Menjalankan: %MODEL%
echo.
ollama run %MODEL%
