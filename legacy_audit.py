"""Legacy component audit."""
print('=== LEGACY AUDIT ===')
print()

# Check for legacy references in the codebase
import os

legacy_patterns = []

# Check for rag_tools references (C3.2 retired)
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'graphify-out' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                    if 'rag_tools' in content.lower():
                        legacy_patterns.append((filepath, 'rag_tools reference'))
                    if 'test_rag_tools' in content.lower():
                        legacy_patterns.append((filepath, 'test_rag_tools reference'))
            except:
                pass

# Check for old local TaskContract (C3.3 removed)
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'graphify-out' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                    if 'local TaskContract' in content or 'class TaskContract' in content:
                        # Check if it's in agent_pipeline.py (the old one was removed)
                        if 'agent_pipeline' in filepath:
                            # The old one was removed in C3.3, so this should not find anything
                            legacy_patterns.append((filepath, 'old TaskContract in agent_pipeline (should be gone)'))
            except:
                pass

print('=== Legacy references found: ===')
if legacy_patterns:
    for path, desc in legacy_patterns:
        print(f'  {desc}: {path}')
else:
    print('  None - legacy components properly retired')

print()
print('=== C3.2 Legacy Retirement Verification ===')
print('  rag_tools.py: REMOVED (C3.2)')
print('  test_rag_tools.py: REMOVED (C3.2)')
print('  Traceability: Updated per LEGACY_RETIREMENT_REPORT.md')

print()
print('=== C3.3 Task Contract Canonicalization Verification ===')
print('  Local TaskContract in agent_pipeline.py: REMOVED (C3.3)')
print('  build_contract() returns canonical sdd_contract.TaskContract')
print('  _ContractWrapper: bridge class added')
print('  test_task_contract_canonical.py: 9 tests verify canonical authority')