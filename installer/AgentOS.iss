#define MyAppName "AgentOS"
#define MyAppVersion "0.1.0"
#define MyAppExeName "AgentOS.exe"

[Setup]
AppId={{7E8B2142-3FB2-4503-A4AB-3CD2E5414C79}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=AgentOS Contributors
DefaultDirName={localappdata}\Programs\AgentOS
DefaultGroupName=AgentOS
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=AgentOS-Setup-0.1.0-Windows
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\AgentOS.exe
WizardStyle=modern

[Files]
Source: "..\dist\AgentOS\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\AgentOS"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\AgentOS"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch AgentOS"; Flags: nowait postinstall skipifsilent
