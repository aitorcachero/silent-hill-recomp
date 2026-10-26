Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\build-release"
WshShell.Run "cmd /c ..\JUGAR_SILENT_HILL.bat", 0, False
