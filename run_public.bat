@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   N1Master - Chay web + Huong dan Public
echo ============================================
echo.
echo [1] Dang khoi chay Flask tren port 8080...
start "N1Master Flask" python app.py
timeout /t 3 >nul
echo.
echo [2] Kiem tra web local...
curl -s -o nul -w "Local 127.0.0.1:8080 -> HTTP %{http_code}\n" http://127.0.0.1:8080/
echo.
echo [3] Lay Public IP cua ban...
for /f %%i in ('curl -s --max-time 8 https://ipinfo.io/ip') do set MYIP=%%i
echo   Public IP: %MYIP%
echo.
echo ============================================
echo   BAN GAI TRUY CAP (sau khi Port Forward):
echo   http://%MYIP%:8080
echo ============================================
echo.
echo HUONG DAN PORT FORWARD (1 lan duy nhat):
echo   1. Mo trinh duyet: http://192.168.0.1  (hoac 192.168.1.1)
echo   2. Dang nhap router (admin/admin hoac in sau router)
echo   3. Tim menu: NAT / Port Forwarding / Virtual Server
echo   4. Them rule: 
echo        - External Port: 8080
echo        - Internal IP: 192.168.0.100
echo        - Internal Port: 8080
echo        - Protocol: TCP
echo   5. Luu / Apply
echo   6. Gui link http://%MYIP%:8080 cho ban gai
echo.
echo Nhan phim bat ky de thoat huong dan...
pause >nul
