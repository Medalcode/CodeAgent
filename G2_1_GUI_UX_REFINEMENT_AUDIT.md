# CODEAGENT — PHASE G2.1: GUI UX REFINEMENT & FEATURE POLISH AUDIT

## 1. Executive Summary
This audit evaluated the current visual and interaction experience of the CodeAgent Desktop UI. The foundation is highly functional and fulfills the minimum viable experience, but several UX aspects present friction. The most critical gaps are the lack of a "Cancel" execution control, the transient nature of live streaming (which overwrites previous steps instead of building a log), the reliance on native browser `alert()` for errors, and the poor visual differentiation of Verification outcomes. No structural frontend refactoring is recommended; all improvements must be purely visual/UX changes within the existing architecture.

## 2. Objective
Identify concrete, high-value User Experience (UX) and User Interface (UI) improvements for the CodeAgent Desktop product, prioritizing clarity, feedback, and control without introducing structural or architectural changes.

## 3. Scope
A read-only audit of `localcode_claude_ui.html`. The backend, SSE, `EventBus`, and State Machine architectures were explicitly preserved and treated as immutable constraints.

## 4. Current UX
The interface is a 1575-line HTML/JS/CSS monolith. It successfully implements the full lifecycle of a task but relies on basic DOM manipulation to represent complex agentic states.

## 5. User Journey
1. **Launch**: GOOD.
2. **Workspace selection**: ACCEPTABLE (Native dialogs work well).
3. **Workspace loading**: ACCEPTABLE.
4. **Task input**: GOOD.
5. **Task submission**: GOOD.
6. **Running state**: NEEDS IMPROVEMENT (Lacks historical step context).
7. **Live progress**: NEEDS IMPROVEMENT (Steps overwrite each other too fast).
8. **Result**: GOOD (Markdown rendering).
9. **Verification**: NEEDS IMPROVEMENT (Verification results are visually indistinguishable from standard agent text).
10. **Error**: NEEDS IMPROVEMENT (Relies on browser `alert()`).

## 6. Information Hierarchy
- **Primary Action (Task Input)**: Clearly positioned.
- **Current State**: Represented via a "Working..." card, but lacks a clear progress bar or phase indicator.
- **Verification**: The core value proposition of CodeAgent (automated verification) is hidden inside plain markdown responses instead of having a dedicated visual badge.

## 7. Execution State UX
The user can tell if CodeAgent is "RUNNING" or "IDLE". However, the distinction between "TOOL EXECUTION" and "VERIFICATION" is extremely brief. The user cannot confidently answer "What exactly did it just do?" after a fast tool execution because the UI only shows the *current* state and immediately overwrites it.

## 8. Streaming UX
The `EventSource` correctly receives `STATE_ENTERED` and `TOOL_EXECUTED`. 
**Problem**: The frontend maps these to a single HTML element (`#workingStepText`) and overwrites its `textContent`. 
**Impact**: High-frequency tool executions flash instantly on screen and disappear, leaving the user with zero context of the sequence of actions taken. The streaming UX fails to build an ongoing "Reasoning / Action Log".

## 9. Error UX
Errors during chat execution are rendered as basic red text bubbles. 
Errors regarding filesystem operations (Save, Rename, Change Workspace) use native JavaScript `alert()` dialogs. 
This breaks immersion and provides poor affordance. Errors lack a "WHY" and "ACTION" format.

## 10. Result & Verification UX
CodeAgent's primary differentiator is SDD conditional verification. Currently, a successful or failed test run looks exactly like standard LLM output. There is no visual badge (e.g., `[PASS]`, `[FAIL]`) separating the verification phase from the generative phase.

## 11. Workspace UX
The file tree is a flat-looking indented list. It lacks visual clarity for deeply nested projects, though it functions correctly. 

## 12. Task Input UX
The input textarea supports standard enter-to-submit behavior, but does not clearly lock or disable itself during an active execution, potentially leading to race conditions if a user submits twice.

## 13. Control UX
**CRITICAL GAP**: There is no explicit "STOP" or "CANCEL" button during execution. The user must wait for the agent to finish, timeout, or physically close the application.

## 14. Accessibility
- **Keyboard Navigation**: Basic tabbing works, but focus rings are missing or inconsistent.
- **Contrast**: Generally acceptable in the dark theme.
- **Form Controls**: Buttons lack ARIA labels.

## 15. Window/Responsive Behavior
The CSS uses Flexbox effectively. The UI scales reasonably well down to standard laptop screen sizes (~1024x768). 

## 16. Visual Consistency
Mostly consistent. No major design system overhaul is required.

## 17. Frontend Structure
The monolith is tightly coupled (global variables manipulate DOM directly). 
**Decision**: DO NOT EXTRACT. The coupling is too high, and the architectural benefit of splitting files is purely aesthetic for the developer. It introduces risks without solving a direct user problem.

## 18. State Duplication
The GUI duplicates a superficial representation of the "Running" state based on SSE events. The true Source of Truth is `AgentPipeline`. This is acceptable for a thin client; no state ownership changes are needed.

## 19. Performance
DOM updates during high-frequency SSE events (overwriting textContent) are cheap. Memory growth is bounded because the UI doesn't append every single event, only the chat messages.

## 20. UX vs Architecture
All identified improvements are strictly UX/UI changes. None require altering the `EventBus` or adding new backend REST endpoints.

## 21. Prioritized Improvements

| Improvement | User Value | Evidence | Complexity | Risk | Priority |
|-------------|------------|----------|------------|------|----------|
| **Add Cancel/Stop Button** | High | Users cannot abort long/looping tasks. | Low | Low | P1 - HIGH VALUE |
| **Replace alerts with Toasts** | Medium | `alert()` blocks the main thread and breaks UX. | Low | Low | P1 - HIGH VALUE |
| **Verification Badges** | High | Verification is the core feature but visually hidden. | Low | Low | P1 - HIGH VALUE |
| **Log Step Accumulation** | High | Rapid SSE events are lost due to DOM overwriting. | Low | Low | P1 - HIGH VALUE |
| **Disable Input during Run** | Medium | Prevents double-submission race conditions. | Low | Low | P2 - MEDIUM VALUE |
| **File Tree Icons/Styling** | Low | purely visual polish. | Low | Low | P3 - POLISH |
| **Refactor HTML/CSS to files** | None | Solves a dev aesthetic, not a user problem. | High | High | P4 - DO NOT DO |

## 22. Single Workspace Risk
The backend uses a global `ACTIVE_WORKSPACE_DIR`. If a user opens two windows, they share the same backend state and will corrupt each other. The UI currently mitigates this by blocking `new_window()` in `DesktopIDEApi`. This mitigation is sufficient for the current MVP. Multi-workspace support is explicitly out of scope.

## 23. Testing
No automated UI tests exist. UX improvements must be smoke-tested manually.

## 24. SDD
**Status**: PASS

## 25. Risks
- Modifying DOM manipulation logic for the "Log Step Accumulation" might cause auto-scroll jank if not implemented carefully.

## 26. Decision
**B — UX POLISH JUSTIFIED**
There are clear, high-value, strictly-UX improvements (Cancel button, Verification Badges, Step Accumulation, and eliminating `alert()`) that significantly elevate the Desktop product without violating any architectural boundaries or requiring backend changes.

## 27. Recommended Next Phase
**G2.2: GUI UX IMPLEMENTATION**
Implement the specific P1 items defined in Section 21 directly inside `localcode_claude_ui.html`.

## 28. Explicit Non-Changes
- No code extracted into separate files.
- No React/Vue/Electron introduced.
- No backend API modified.
- No state ownership transferred.
