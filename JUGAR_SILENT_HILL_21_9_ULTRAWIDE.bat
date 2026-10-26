@echo off
cd /d "%~dp0"

:: Lanzador dedicado 21:9 Ultra-Panoramico (Ultrawide 2560x1080 / 3440x1440 / 5120x2160)
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_FULLSCREEN=1
set PSX_WS_FORCE_3D=1
set PSX_WS_FORCE_2D=0
set PSX_ASPECT_RATIO=21:9
set PSX_INTERNAL_SCALE=8
set PSX_TEXTURE_FILTER=0

if exist "SilentHill.exe" (
    start "" "SilentHill.exe" -21:9
    exit /b
)
if exist "build-release\SilentHill.exe" (
    start "" "build-release\SilentHill.exe" -21:9
    exit /b
)
if exist "silent-hill-recomp\SilentHill.exe" (
    cd /d "%~dp0silent-hill-recomp"
    start "" "SilentHill.exe" -21:9
    exit /b
)

:: Deteccion de variante por archivos de disco
set TARGET_EXE=Silent_Hill_Recompiled.exe
if exist "Silent Hill (USA).cue" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "Silent Hill (USA).bin" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "build-release\disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "silent-hill-recomp\disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe

if exist "%TARGET_EXE%" (
    start "" "%TARGET_EXE%"
) else if exist "build-release\%TARGET_EXE%" (
    cd /d "%~dp0build-release"
    start "" "%TARGET_EXE%"
) else if exist "silent-hill-recomp\build-release\%TARGET_EXE%" (
    cd /d "%~dp0silent-hill-recomp\build-release"
    start "" "%TARGET_EXE%"
)
exit /b
