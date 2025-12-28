@echo off
title Dayi Runner - Final Paketleyici (V6)
color 0B
cls

echo ======================================================
echo    DAYI RUNNER - GARANTI DOSYA YOLU ONARICI
echo ======================================================
echo.

:: 1. TAM TEMIZLIK
echo [+] Eski build dosyalari temizleniyor...
rd /s /q "build" 2>nul
rd /s /q "dist" 2>nul
del /q *.spec 2>nul

:: 2. KUTUPHANE GUNCELLEME
echo [+] Gereksinimler kontrol ediliyor...
python -m pip install --upgrade pygame pyinstaller --quiet

:: 3. PAKETLEME (EN STABIL AYARLARLA)
echo.
echo [+] PAKETLEME BASLADI...
:: --onedir: Klasör yapısı hata payını düşürür.
python -m PyInstaller --noconsole --onedir --clean ^
--add-data "assets;assets" ^
--hidden-import=pygame ^
--collect-all pygame ^
--name="DayiRunner_Final" main.py

:: 4. ASSET KOPYALAMA (YOL HATALARINA KARSI GARANTI)
echo [+] Dosya yollari dogrulanıyor...
if exist "assets" (
xcopy /E /I /Y "assets" "dist\DayiRunner_Final\assets"
)

:: 5. KONTROL VE CALISTIRMA
if not exist "dist\DayiRunner_Final\DayiRunner_Final.exe" (
color 0C
echo.
echo [!!!] HATA: Dosya olusturulamadi! Lutfen Python yuklu mu kontrol et.
pause
exit
)

echo.
echo ======================================================
echo [+] ISLEM TAMAMLANDI!
echo [+] 'dist\DayiRunner_Final' klasoru hazir.
echo [+] Klasorun icindeki 'DayiRunner_Final.exe'ye sag tikla:
echo [+] 'Yonetici Olarak Calistir' de.
echo ======================================================
echo.
pause

:: Windows hata vermesin diye yolu tırnak içinde ve tam adresle çağırıyoruz
start "" "%cd%\dist\DayiRunner_Final\DayiRunner_Final.exe"
exit