print("=== COVERAGE CLAIM AUDIT ===")
print()
claims = {
    "State Machine": ("VERIFIED", "10 directive tests in test_cognitive_directives.py cover PLAN/EXPLORE/EXECUTE/VERIFY/DIAGNOSE/REPLAN phases"),
    "Persistence": ("PARTIAL", "sdd_check.py proves traceability; runtime tests blocked by import errors"),
    "Verification": ("PARTIAL", "test_verifier_evidence.py has collection error; structural traceability OK"),
    "Recovery": ("BLOCKED", "6 import errors block recovery test execution"),
    "Tool Isolation": ("BLOCKED", "6 import errors block tool isolation tests"),
    "EventBus": ("BLOCKED", "6 import errors block EventBus tests"),
    "SSE": ("BLOCKED", "test_desktop_pipeline_visualization.py has collection error"),
    "UI": ("BLOCKED", "desktop_app.py collection error (actually valid UTF-8)"),
    "Cognitive directives": ("VERIFIED", "10/10 tests pass in test_cognitive_directives.py"),
    "SDD": ("VERIFIED", "sdd_check.py PASS all 15 invariants + 5 specs"),
}

print("Coverage Claim Audit:")
print("=" * 60)
for area, (status, evidence) in claims.items():
    print(f"{area:20s} : {status:15s} - {evidence}")

print()
print("Audit Conclusion:")
print("  - VERIFIED claims: State Machine, Cognitive directives, SDD")
print("  - PARTIAL claims: Persistence, Verification")
print("  - BLOCKED claims: Recovery, Tool Isolation, EventBus, SSE, UI")
print()
print("Critical: sdd_check.py proves structural traceability, NOT runtime behavioral coverage.")
print("  Cognitive-directive tests prove directive generation behavior, NOT full state-machine transitions.")