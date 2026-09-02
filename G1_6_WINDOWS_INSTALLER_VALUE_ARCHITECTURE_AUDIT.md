# CODEAGENT — PHASE G1.6: WINDOWS INSTALLER VALUE & ARCHITECTURE AUDIT

## 1. Executive Summary
This audit evaluated the concrete product value of introducing a traditional Windows Installer over the existing Certified Portable ZIP. Analysis confirms that an installer resolves real UX constraints regarding UAC privilege escalation during installation, start menu discovery, and deterministic updates/uninstallations, without threatening the established architectural isolation between application binaries and user data. The recommendation is to proceed with an installer wrapper that natively consumes the G1.5 portable payload.

## 2. Objective
Determine, using objective evidence, if CodeAgent genuinely requires a Windows installer traditional distribution, or if the portable ZIP distribution certified in Phase G1.5 is already the optimal product solution.

## 3. Scope
A read-only architectural evaluation of installer lifecycles, user experience boundaries, UAC integration, and security risks. No code modifications or installer scripts were generated during this phase.

## 4. Baseline
- **Tests**: 223 collected, 222 passed, 1 failed (`test_workspace_tree_endpoint` - PRE_EXISTING_CONFIRMED/ENVIRONMENTAL socket timeout). 0 collection errors.
- **SDD**: PASS.
- **Artifact**: `CodeAgent-5.0-windows-x64.zip` (Certified in G1.5).

## 5. Evidence
The G1.5 ZIP artifact functions flawlessly outside the repository context. 
- **Application Directory** is effectively read-only.
- **Data Boundary** (`%APPDATA%\CodeAgent`) correctly segregates SQLite DB and user sessions.
- **Embedded Python** properly orchestrates subprocess testing without global dependencies.

## 6. ZIP vs Installer Comparison
- **ZIP**: Requires manual extraction. If the user extracts to `C:\Program Files\`, Windows UAC blocks extraction unless elevated. If extracted to `C:\Users\...\Desktop`, it clutters the desktop. Upgrades require manually deleting old folders.
- **Installer**: Handles UAC prompts for `Program Files`, creates deterministic Desktop/Start Menu shortcuts, and provides a clear uninstallation path via Windows Settings.

## 7. User Value Analysis
- **Benefit**: Resolves UAC extraction blocks.
  - **Evidence**: Windows enforces read-only access to `Program Files`. Manual extraction there by standard users fails.
  - **Requires Installer**: Yes.
- **Benefit**: Start Menu Discovery & Shortcuts.
  - **Evidence**: A batch script (`launch_codeagent.bat`) is functionally capable but visually unappealing and hard to pin to the taskbar gracefully compared to a proper shortcut pointing to a `.bat` or wrapper with an `.ico`.
  - **Requires Installer**: Yes.

## 8. Installation Lifecycle
- **Initial Install**: Copies payload to `Program Files` using Admin privileges.
- **Update**: Replaces files deterministically. Overcomes the "folder locked" issues common in manual ZIP replacements.
- **Uninstall**: Wipes `Program Files\CodeAgent` and Start Menu shortcuts.
- **Rule Enforced**: The installer MUST NOT touch or delete `%APPDATA%\CodeAgent` during uninstallation to protect user configurations and databases.

## 9. APPDATA Boundary
The application logic verified in G1.2 cleanly decouples the application from data. An installer operates strictly on the application directory. Upgrading or removing the application via a traditional Windows uninstaller will inherently preserve the user data in `%APPDATA%`.

## 10. Windows/UAC Analysis
Because CodeAgent doesn't write to its own execution directory, it is 100% compliant with standard `C:\Program Files` restrictions. However, to *put* it there requires a one-time UAC elevation—which an installer automatically provides via standard Windows APIs.

## 11. Shell Integration Analysis
- **Start Menu & Desktop Shortcuts**: High benefit, low risk, necessary for standard desktop applications.
- **Context Menus / File Associations**: Unnecessary. CodeAgent currently manages active workspaces via an internal UI picker, not by double-clicking files.
- **PATH Integration**: Unnecessary. The IDE is a localized desktop product, not a global CLI tool.

## 12. Update Model
- **Portable ZIP Update**: Highly error-prone (users drag-and-drop merging folders, leaving orphaned `.py` files from previous versions that can crash Python).
- **Installer Update**: Atomic replacement of the directory, wiping orphaned files efficiently and ensuring a 1:1 match with the released manifest.

## 13. Installer Technology Comparison
- **Inno Setup**: Extremely lightweight, highly customizable, directly consumes folder trees, requires no dependencies, and creates standard uninstaller binaries.
- **NSIS**: Similar to Inno Setup but uses a slightly more complex scripting paradigm.
- **MSIX**: Strict sandboxing limits subprocess interactions and `sys.executable` behavior severely. Not recommended.
- **Selection**: **Inno Setup** is the most architecturally congruent option. It can consume the G1.5 ZIP payload natively without touching Python orchestration.

## 14. Packaging Boundary
**CERTIFIED PORTABLE PACKAGE → INSTALLER WRAPPER → WINDOWS USER**
The installer will simply be a deployment wrapper that consumes the artifact proven in G1.5. It will NOT rebuild the application, preserving ONE PACKAGING AUTHORITY.

## 15. Security Analysis
- The installer must only run standard file-copy operations. 
- Auto-updating components should not be built into the application layer to avoid DLL hijacking risks; updates should be handled by running a new installer.
- User data remains outside the installation scope, mitigating accidental data loss.

## 16. Rollback Analysis
If the installer fails or is deemed unnecessary, the project can instantly roll back to shipping the `CodeAgent-5.0-windows-x64.zip`. The installer logic operates strictly in an isolated `/installer` script and affects nothing else.

## 17. Architectural Impact
**A) No cambia arquitectura.** 
The installer adds strictly external infrastructure. It acts only on the filesystem layer to copy the pre-compiled portable payload to the target machine.

## 18. Risks
- If the uninstall script inadvertently targets `%APPDATA%`, it could cause critical user data loss. This must be explicitly disabled in the installer configuration.
- The Start Menu shortcut must correctly launch the `.bat` (or a VBS wrapper to hide the console) without disrupting `sys.executable` semantics.

## 19. Decision
**DECISION: A — INSTALLER JUSTIFIED**
Evidence proves an installer solves genuine Windows OS constraints (UAC elevation for `Program Files`, orphaned file merging during updates, and Start Menu discovery). It will be implemented purely as an external wrapper around the G1.5 payload using Inno Setup.

## 20. Recommended Next Step
**Phase G1.7: INNO SETUP WRAPPER IMPLEMENTATION**
Create an `Inno Setup` script (`.iss`) that consumes the G1.5 `dist/CodeAgent` payload, packages it into a single `CodeAgent_Setup.exe`, creates shortcuts, and manages uninstallation, explicitly preserving `%APPDATA%`.

## 21. Explicit Non-Changes
- `agent_pipeline.py` and `cognitive_directives.py` were NOT modified.
- Database and APPDATA architectures were NOT modified.
- No `TaskContract` or `SDD` specifications were altered.
- No installer scripts were actually implemented during this phase.
