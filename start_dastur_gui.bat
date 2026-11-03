@echo off
chcp 65001 > nul
title Bioinformatika: Onkologik Tashxislash Dasturi (GUI)
cd /d "%~dp0"
echo ======================================================================
echo    BIOINFORMATIKA: ONKOLOGIK KASALLIKLARNI BASHORATLASH DASTURI
echo    Mualliflar: Ramanov Rustam va Sobirov Elmurod
echo ======================================================================
echo Desktop Dastur (Grafik Oyna) ishga tushirilmoqda...
python app_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Xatolik yuz berdi. Iltimos, Python o'rnatilganligini tekshiring.
    pause
)
exit

