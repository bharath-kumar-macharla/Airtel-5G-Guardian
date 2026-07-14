; Airtel 5G Guardian — Inno Setup 6 Installer Script
; ===================================================
;
; Prerequisites:
;   1. Build the EXE first: pyinstaller Airtel-5G-Guardian.spec --clean
;   2. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
;   3. Compile this script with Inno Setup Compiler.
;
; Output: installer\Output\Airtel5GGuardian-Setup-1.0.0.exe

#define AppName       "Airtel 5G Guardian"
#define AppVersion    "1.0.0"
#define AppPublisher  "Macharla Bharath Kumar"
#define AppURL        "https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian"
#define AppExeName    "Airtel-5G-Guardian.exe"
#define SourceDir     "..\dist"

[Setup]
; Basic identity
AppId                   = {{A3F9E2D1-7B4C-4E8A-9F1D-2C6B5E3A0D7F}}
AppName                 = {#AppName}
AppVersion              = {#AppVersion}
AppPublisherURL         = {#AppURL}
AppSupportURL           = {#AppURL}/issues
AppUpdatesURL           = {#AppURL}/releases

; Install destination
DefaultDirName          = {autopf}\{#AppName}
DefaultGroupName        = {#AppName}
DisableProgramGroupPage = no

; Output
OutputDir               = Output
OutputBaseFilename      = Airtel5GGuardian-Setup-{#AppVersion}
Compression             = lzma/ultra64
SolidCompression        = yes
WizardStyle             = modern

; Permissions — per-user install, no admin required
PrivilegesRequired      = lowest
PrivilegesRequiredOverridesAllowed = dialog

; Visual
SetupIconFile           = ..\assets\guardian.ico
UninstallDisplayIcon    = {app}\{#AppExeName}
UninstallDisplayName    = {#AppName}

; Minimum Windows version (Windows 10)
MinVersion              = 10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupentry";   Description: "Launch {#AppName} when Windows starts (minimized to tray)"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Main executable (built by PyInstaller)
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Default config (only installed if config.json doesn't already exist)
Source: "..\config\config.json"; DestDir: "{app}\config"; Flags: onlyifdoesntexist

; Assets and sounds
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\sounds\*"; DestDir: "{app}\sounds";  Flags: recursesubdirs createallsubdirs ignoreversion

[Dirs]
; Create writable user-data directories
Name: "{app}\data"
Name: "{app}\exports"
Name: "{app}\logs"

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}"

; Desktop shortcut (optional, selected via task)
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Windows startup entry (optional, selected via task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "AirtelGuardian5G"; \
    ValueData: """{app}\{#AppExeName}"" --minimized"; \
    Flags: uninsdeletevalue; Tasks: startupentry

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Make sure the app is closed before uninstalling
Filename: "taskkill.exe"; Parameters: "/f /im {#AppExeName}"; Flags: runhidden waituntilterminated

[Code]
// Remove user-data directories on uninstall only if user confirms
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Msg: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    Msg := 'Do you want to remove your monitoring data, logs, and exports?' + #13#10 +
           '(config.json, data/, logs/, exports/)' + #13#10 + #13#10 +
           'Click Yes to delete everything, No to keep your data.';
    if MsgBox(Msg, mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\data'),    True, True, True);
      DelTree(ExpandConstant('{app}\logs'),    True, True, True);
      DelTree(ExpandConstant('{app}\exports'), True, True, True);
      DeleteFile(ExpandConstant('{app}\config\config.json'));
    end;
  end;
end;
