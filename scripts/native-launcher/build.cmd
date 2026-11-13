@echo off
rem Build the native Windows launchers for the two local dashboards.
rem Output: one .exe in each project folder, no console window, custom icon.
rem Uses the C# compiler that ships with .NET Framework, so no Visual Studio,
rem no NuGet, no extra install.
setlocal

set "HERE=%~dp0"
set "ROOT=%HERE%..\.."

set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
if not exist "%CSC%" (
  echo csc.exe tidak ditemukan. Pasang .NET Framework 4.x dulu.
  exit /b 1
)

set "FLAGS=/nologo /target:winexe /platform:anycpu /optimize+ /warn:2"

echo [1/2] Free Model Radar ...
"%CSC%" %FLAGS% /define:RADAR ^
  /win32icon:"%HERE%icons\free-model-radar.ico" ^
  /out:"%ROOT%\projects\free-model-radar\Free Model Radar.exe" ^
  "%HERE%Launcher.cs" || exit /b 1

echo [2/2] Dark Fiber Core Manager ...
"%CSC%" %FLAGS% /define:DARKFIBER ^
  /win32icon:"%HERE%icons\dark-fiber-core-manager.ico" ^
  /out:"%ROOT%\projects\dark-fiber-core-manager\Dark Fiber Manager.exe" ^
  "%HERE%Launcher.cs" || exit /b 1

echo.
echo Selesai. Klik dua kali file .exe di folder proyek untuk menjalankan.
