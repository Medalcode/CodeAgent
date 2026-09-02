[Setup]
AppName=CodeAgent
AppVersion=5.0
AppPublisher=Medalcode
DefaultDirName={autopf64}\CodeAgent
DefaultGroupName=CodeAgent
OutputDir=..\..\dist
OutputBaseFilename=CodeAgent_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\launch_codeagent.bat

[Files]
Source: "..\..\dist\CodeAgent\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CodeAgent"; Filename: "{app}\launch_codeagent.bat"
Name: "{autodesktop}\CodeAgent"; Filename: "{app}\launch_codeagent.bat"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
; EXPLICIT NON-DELETION: %APPDATA%\CodeAgent is deliberately preserved to protect user DB and sessions.
