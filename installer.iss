[Setup]
AppName=Som de Fundo
AppVersion=1.1.0
DefaultDirName={commonpf}\Som de Fundo
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
DefaultGroupName=Som de Fundo
OutputDir=dist\installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"

[Files]
Source: "dist\Som_de_fundo\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "icons\*"; DestDir: "{app}\icons"; Flags: recursesubdirs
Source: "playlists\*"; DestDir: "{userappdata}\Som_de_fundo\playlists"; Flags: recursesubdirs uninsneveruninstall

[Icons]
Name: "{group}\Som de Fundo"; Filename: "{app}\Som_de_fundo.exe"
Name: "{commondesktop}\Som de Fundo"; Filename: "{app}\Som_de_fundo.exe"; Tasks: desktopicon
