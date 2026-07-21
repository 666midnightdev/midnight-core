@REM Heartbeat auto-commit harian (biar contribution graph hijau)
@REM Jalankan via Windows Task Scheduler setiap hari
@echo off
cd /d C:\midnight_agent
set OLLAMA_KEEP_ALIVE=3m

REM Timestamp via PowerShell (reliable)
for /f %%I in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"') do set TIMESTAMP=%%I
set DATE_STAMP=%TIMESTAMP:~0,10%
set TIME_STAMP=%TIMESTAMP:~11,8%

REM Update heartbeat file (UTF-8 tanpa BOM via PowerShell)
powershell -Command "$u=[System.Text.UTF8Encoding]::new($false); $p='C:\midnight_agent\heartbeat.txt'; $o=[System.IO.File]::ReadAllText($p,$u) + ('%DATE_STAMP% %TIME_STAMP% - Midnight Core active' + [char]13 + [char]10); [System.IO.File]::WriteAllText($p,$o,$u)"

REM Commit & push
git add heartbeat.txt
git commit -m "heartbeat: daily activity [%DATE_STAMP%]"
git push origin master
