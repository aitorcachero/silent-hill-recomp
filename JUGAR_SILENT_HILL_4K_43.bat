@echo off
cd /d "%~dp0"
set PSX_RENDER_THREAD=1
set PSX_PRESENT_THREAD=1
set PSX_FRAME_GEN=0
set PSX_FRAME_INTERPOLATION=0
set PSX_VSYNC=0
set PSX_FPS_TELEMETRY=0
set PSX_WS_FORCE_FULLSCREEN=0
set PSX_WS_FORCE_3D=0
set PSX_WS_FORCE_2D=0
set PSX_ASPECT_RATIO=4:3
set PSX_INTERNAL_SCALE=8
set PSX_TEXTURE_FILTER=0

if exist "Silent_Hill_Recompiled.exe" (
    start "" "Silent_Hill_Recompiled.exe"
) else if exist "build-release\Silent_Hill_Recompiled.exe" (
    cd /d "%~dp0build-release"
    start "" "Silent_Hill_Recompiled.exe"
)
exit /b
