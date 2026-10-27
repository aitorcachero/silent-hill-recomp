@echo off
cd /d "%~dp0"
title Silent Hill - Menu de Configuracion (Mandos, Mods, Graficos)

if exist "SilentHill.exe" (
    start "" "SilentHill.exe" --launcher
    exit /b
)
if exist "silent-hill-recomp\SilentHill.exe" (
    cd /d "%~dp0silent-hill-recomp"
    start "" "SilentHill.exe" --launcher
    exit /b
)
if exist "build-release\Silent_Hill_Recompiled_USA.exe" (
    cd /d "%~dp0build-release"
    start "" "Silent_Hill_Recompiled_USA.exe" --launcher
    exit /b
) else if exist "build-release\Silent_Hill_Recompiled.exe" (
    cd /d "%~dp0build-release"
    start "" "Silent_Hill_Recompiled.exe" --launcher
    exit /b
)
exit /b
