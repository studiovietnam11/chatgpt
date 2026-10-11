#define MyAppName "FoxProfile Studio"
#define MyAppVersion "2.5.1"
[Setup]
AppId={{D71D8461-D09D-4F6F-BA09-775E624F2EBB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=FoxProfile Studio
DefaultDirName={localappdata}\Programs\FoxProfileStudio
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\release
OutputBaseFilename=FoxProfileStudio-Setup-2.5.1-Win64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
CloseApplications=yes
SetupIconFile=..\..\work\src\assets\icon.ico
UninstallDisplayIcon={app}\FoxProfileStudio.exe
[Files]
Source: "..\..\dist\FoxProfileStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\work\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\FoxProfile Studio"; Filename: "{app}\FoxProfileStudio.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\FoxProfile Studio"; Filename: "{app}\FoxProfileStudio.exe"; WorkingDir: "{app}"
Name: "{autoprograms}\Uninstall FoxProfile Studio"; Filename: "{uninstallexe}"
[Run]
Filename: "{app}\FoxProfileStudio.exe"; Description: "Launch FoxProfile Studio"; Flags: nowait postinstall skipifsilent
