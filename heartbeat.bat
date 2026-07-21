@REM Heartbeat auto-commit harian (biar contribution graph hijau)
@REM Jalankan via Windows Task Scheduler setiap hari
@echo off
cd /d C:\midnight_agent
set OLLAMA_KEEP_ALIVE=3m

REM Timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
set DATE_STAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%
set TIME_STAMP=%dt:~8,2%:%dt:~10,2%

REM Update heartbeat file
echo %DATE_STAMP% %TIME_STAMP% - Midnight Core active >> heartbeat.txt

REM Commit & push
git add heartbeat.txt
git commit -m "heartbeat: daily activity [%DATE_STAMP%]"
git push origin master
