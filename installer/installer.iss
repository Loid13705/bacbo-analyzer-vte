[Setup]
AppName=VT BacBo Analyzer
AppVersion=1.0
DefaultDirName={pf}\VT BacBo Analyzer
OutputDir=dist_installer
OutputBaseFilename=VT_BacBo_Analyzer_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\bacbo_gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.ini"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VT BacBo Analyzer"; Filename: "{app}\bacbo_gui.exe"
Name: "{commondesktop}\VT BacBo Analyzer"; Filename: "{app}\bacbo_gui.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais:";
