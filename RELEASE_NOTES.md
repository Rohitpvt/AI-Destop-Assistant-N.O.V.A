# Release Notes - N.O.V.A Phase 14 Stable Baseline Checkpoint

We are excited to announce the successful completion and verification of **Phase 14: Context-Aware Desktop Control**! N.O.V.A has been upgraded from a conversational desktop app into a safe, context-aware visual desktop automation assistant.

---

## ✨ Release Highlights

*   **Context-Aware Desktop Control**: Tracks the active app, window title, and active website (Google/YouTube recognition).
*   **Safe Approval Gate**: Intercepts risky coordinates, keystrokes, and scrolling actions; stages and asks for explicit `"confirm"` or `"cancel"` voice/chat commands.
*   **Active Window Mismatch Protection**: Asserts window title matches, preventing stale coordinate clicks if window switches.
*   **OCR Coordinate Targeting**: Harnesses `pytesseract.image_to_data` to parse layout structures, exact/partial coordinates, and ambiguity queries.
*   **Pronoun & Follow-up Resolution**: Resolves commands like `"click it"` naturally using the last visual target.
*   **Destructive Command Blocking**: Rejects system shutdowns, disk formats, and alt+f4 hotkeys directly at the safety verification gate.

---

## 🧪 Verification & Test Results

*   **Automated Tests**: Added 9 new unit tests covering session context, coordinate resolution, mismatch blocking, safety blocks, and approvals.
    *   **31/31 Tests Passed (100% Success)**
*   **Manual/Simulation Tests**: Ran 15 programmatic scenario tests validating full context updates, expired actions, low-risk browser routing, and confirmations.
    *   **15/15 Scenarios Passed (100% Success)**

---

## 🔒 Verification Baseline Details

*   **Release Target**: NOVA Phase 14 Stable Checkpoint
*   **Git Commit Hash**: `e6069fd5f1aaff1f68669232e2a05688679c6640`
*   **Status**: **Ready for Phase 15**
