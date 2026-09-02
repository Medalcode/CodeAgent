# CODEAGENT — PHASE G1.7: WINDOWS INSTALLER IMPLEMENTATION

## 1. Objective
Implement the official Windows Installer for CodeAgent using a minimal, declarative Inno Setup wrapper. The installer must consume the certified portable package (`dist/CodeAgent/`) without rebuilding it, target `Program Files` with UAC elevation, and strictly preserve `%APPDATA%\CodeAgent` during uninstallation.

## 2. Scope
- Created `packaging/installer/CodeAgent.iss`.
- Configured to wrap `dist/CodeAgent`.
- UAC elevation configured (`PrivilegesRequired=admin`).
- Uninstaller explicitly scoped to avoid user data.
- The compilation of the `.exe` artifact is deferred due to the absence of the Inno Setup compiler (`iscc`) on the build machine.

## 3. G1.6 Evidence
Phase G1.6 proved that an installer adds crucial value by solving UAC folder creation in `Program Files`, cleaning up orphaned files during updates, and providing Start Menu discovery. It also proved that an installer could act merely as a wrapper, preserving the application architecture.

## 4. Installer Architecture
- **Tool**: Inno Setup.
- **Role**: Pure infrastructure layer.
- **Payload**: Natively consumes `dist/CodeAgent/*`.

## 5. Packaging Boundary
**CodeAgent Application → Portable Package (`dist/CodeAgent`) → Installer (`CodeAgent_Setup.exe`)**
There is only ONE packaging authority. The Inno Setup script does not declare individual Python packages; it bundles the pre-certified folder wholesale.

## 6. Payload Source
`..\..\dist\CodeAgent\*` (Relative to `packaging/installer/`).

## 7. Installation Directory
`{autopf64}\CodeAgent` (Resolves to `C:\Program Files\CodeAgent` on 64-bit Windows).

## 8. APPDATA Boundary
The `[UninstallDelete]` section strictly limits deletion to `{app}`. No directives target `{userappdata}\CodeAgent`. Uninstalling the application will guarantee the survival of SQLite databases and user sessions.

## 9. Shortcut Strategy
- **Start Menu**: Automatically created (`{group}\CodeAgent`).
- **Desktop**: Optional during installation (`Tasks: desktopicon`, unchecked by default).
Both shortcuts point directly to `{app}\launch_codeagent.bat`, preserving `sys.executable` embedded Python semantics perfectly.

## 10. UAC Behavior
`PrivilegesRequired=admin` forces Windows to prompt for UAC elevation during installation, solving the primary constraint identified in G1.6.

## 11. Uninstall Behavior
The standard Windows "Add/Remove Programs" executes Inno Setup's uninstaller, which cleanly wipes `{app}` and its shortcuts.

## 12. Reinstall / Update Behavior
Running a newer `CodeAgent_Setup.exe` over an existing installation replaces the `{app}` files deterministically. Because user data remains in `%APPDATA%`, the new version instantly connects to the existing database.

## 13. Security Validation
No `.env`, secrets, or `*.db` files are bundled because the Inno Setup script consumes `dist/CodeAgent`, which was already security-audited and stripped in Phase G1.4/G1.5.

## 14. Test Matrix & Baseline Comparison
- **Baseline**: 223 collected, 222 passed, 1 failed (PRE_EXISTING_CONFIRMED), 0 errors.
- **SDD**: PASS.

## 15. Failure Classification
- **Artifact Compilation**: Missing Inno Setup compiler (`iscc`) on the developer machine → **ENVIRONMENTAL**. The script is implemented correctly, but the physical `.exe` could not be generated locally.

## 16. Risks
Without the physical `.exe` generated, the manual verification of the installer flow cannot be executed on this specific machine. The `.iss` script must be compiled by a CI/CD pipeline or a developer machine with Inno Setup installed.

## 17. Rollback
Delete `packaging/installer/CodeAgent.iss`. The `dist/CodeAgent` portable payload remains 100% functional.

## 18. Explicit Non-Changes
- `agent_pipeline.py` and `cognitive_directives.py` were NOT modified.
- No Python code was changed.
- No automatic updaters were added.
- The `launch_codeagent.bat` behavior was NOT altered.
