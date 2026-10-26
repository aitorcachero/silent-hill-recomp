@echo off
cd /d "%~dp0"

:: 1. Lanzar el ejecutable nativo silencioso con autodeteccion de region (PAL / USA Doblaje)
if exist "SilentHill.exe" (
    start "" "SilentHill.exe"
    exit /b
)
if exist "build-release\SilentHill.exe" (
    start "" "build-release\SilentHill.exe"
    exit /b
)
if exist "silent-hill-recomp\SilentHill.exe" (
    cd /d "%~dp0silent-hill-recomp"
    start "" "SilentHill.exe"
    exit /b
)

:: 2. Deteccion de variante por archivos de disco
set TARGET_EXE=Silent_Hill_Recompiled.exe
if exist "Silent Hill (USA).cue" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "Silent Hill (USA).bin" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "build-release\disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe
if exist "silent-hill-recomp\disc\SLUS_007.07" set TARGET_EXE=Silent_Hill_Recompiled_USA.exe

:: 3. Lanzar runtime directo si aplica
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_FULLSCREEN=1
set PSX_WS_FORCE_3D=1
set PSX_WS_FORCE_2D=0
set PSX_ASPECT_RATIO=16:9
set PSX_INTERNAL_SCALE=8
set PSX_TEXTURE_FILTER=0

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
