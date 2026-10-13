# AgentOS Windows Installer (v0.1 prototype)

The Windows installer is built in GitHub Actions, not shipped as an unverified executable.

1. Open **Actions → Windows Installer**.
2. Open the latest **successful** run.
3. Under **Artifacts**, download **AgentOS-Windows-Installer-v0.1.0**.
4. Extract the ZIP and run **AgentOS-Setup-0.1.0-Windows.exe**.

Requirements: Windows 10/11 x64 and Microsoft Edge WebView2 runtime (usually available on Windows 11). Python and Node.js are not required on the target machine.

The app runs UI and API on a dynamic localhost (127.0.0.1) port. Data stays in %LOCALAPPDATA%\AgentOS\state.sqlite3 and is not removed during uninstall.

To use a model in this early prototype, configure OPENAI_API_KEY and AGENTOS_MODEL in the process environment. There is no in-app provider connection UI yet.

Security: AgentOS v0.1 is local-only, without user authentication. Do not expose it to the internet. The Windows executable is unsigned, so Microsoft SmartScreen may display an Unknown publisher warning. Verify artifacts before running.

Feature status: v0.1 includes Agent Universe, presets, local memories, and tasks. It does NOT yet include Codex/Claude Code sessions, Code Studio, mod marketplace, shell execution, or cloud computers.

## Manual Windows build

From the repository root with Python 3.12+, Node.js 22+ and Inno Setup 6 installed:

    cd apps/web
    $env:NEXT_PUBLIC_AGENTOS_API_URL = ''
    npm install
    npm run build
    cd ../..
    python -m pip install -e './backend[dev]'
    python -m pip install 'pyinstaller>=6,<7' 'pywebview>=5,<7'
    python -m PyInstaller --noconfirm --clean --windowed --onedir --name AgentOS --paths backend --collect-all webview --add-data 'apps/web/out;frontend' desktop/launcher.py
    & (Join-Path ([Environment]::GetFolderPath('ProgramFilesX86')) 'Inno Setup 6\ISCC.exe') 'installer/AgentOS.iss'
