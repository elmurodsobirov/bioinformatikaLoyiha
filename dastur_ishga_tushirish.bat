@echo off
chcp 65001 > nul
title Bioinformatika Dasturiy Majmuasi - Ramanov Rustam & Sobirov Elmurod
cls

:MENU
echo ======================================================================
echo    BIOINFORMATIKA FANI BO'YICHA 13-KURS LOYIHASI DASTURI
echo    "Biologik ma'lumotlar asosida kasalliklarni mashinali
echo     o'qitish yordamida bashoratlash (GEO/TCGA, scikit-learn, XGBoost)"
echo.
echo    Mualliflar: Ramanov Rustam va Sobirov Elmurod
echo ======================================================================
echo.
echo    [1] Desktop Dastur (Zamonaviy Tkinter Grafik Interfeys)
echo    [2] Veb-Dashboard Dasturi (Brauzerda Interaktiv Diagnostika)
echo    [3] Konsol Diagnostik Demo (CLI orqali bemorlarni tekshirish)
echo    [4] 21 Slaydli Rasmiy Ilmiy Prezentatsiya (HTML/CSS/JS)
echo    [5] To'liq Ilmiy Pipeline (Ma'lumotlar + O'qitish + Grafiklar)
echo    [0] Chiqish
echo.
echo ======================================================================
set /p choice="Kerakli bo'lim raqamini tanlang (1-5 yoki 0): "

if "%choice%"=="1" goto GUI
if "%choice%"=="2" goto WEB
if "%choice%"=="3" goto CLI
if "%choice%"=="4" goto PRES
if "%choice%"=="5" goto PIPELINE
if "%choice%"=="0" goto EXIT

echo Noto'g'ri tanlov! Iltimos, 1 dan 5 gacha raqam kiriting.
timeout /t 2 > nul
cls
goto MENU

:GUI
cls
echo [*] Desktop GUI dasturi ishga tushirilmoqda...
cd /d "%~dp0"
python app_gui.py
goto MENU

:WEB
cls
echo [*] Veb-Dashboard dasturi brauzerda ochilmoqda...
cd /d "%~dp0"
start "" "%~dp0dastur_web.html"
goto MENU

:CLI
cls
echo [*] Konsol diagnostik dasturi ishga tushirilmoqda...
cd /d "%~dp0"
python app_demo.py
echo.
pause
cls
goto MENU

:PRES
cls
echo [*] 21 slaydli prezentatsiya ochilmoqda...
cd /d "%~dp0"
start "" "%~dp0prezentatsiya.html"
goto MENU

:PIPELINE
cls
echo [*] To'liq pipeline ishga tushirilmoqda (10-15 soniya)...
cd /d "%~dp0"
python run_full_pipeline.py
echo.
pause
cls
goto MENU

:EXIT
exit

