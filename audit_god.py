"""God Module Reassessment after D1 extraction."""
import re

print('=== GOD MODULE REASSESSMENT ===')
print()

# Analyze agent_pipeline.py responsibility count
with open('mis_agentes_inteligentes/agent_pipeline.py', 'r', encoding='utf-8', errors='replace') as f:
    pipeline_source = f.read()

# Count key responsibility areas by finding major function/class definitions
classes = re.findall(r'class\s+(\w+)\(', pipeline_source)
functions = re.findall(r'def\s+(_stage_\w+|run_pipeline|resume_session|run)\(', pipeline_source)

print('=== agent_pipeline.py ===')
print(f'Classes defined: {len(classes)} -> {classes}')
print(f'Key functions defined: {len(functions)} -> {functions}')
print()

# cognitive_directives.py
with open('mis_agentes_inteligentes/cognitive_directives.py', 'r', encoding='utf-8', errors='replace') as f:
    cd_source = f.read()

cd_funcs = re.findall(r'def\s+(\w+)\(', cd_source)
print('=== cognitive_directives.py ===')
print(f'Functions: {cd_funcs}')
print(f'Responsibility count: 1 (get_phase_cognitive_directive)')
print()

# tools.py - quick check
print('=== tools.py (high-level) ===')
try:
    with open('mis_agentes_inteligentes/tools.py', 'r', encoding='utf-8', errors='replace') as f:
        tools_source = f.read()
    tools_funcs = re.findall(r'def\s+(\w+)\(', tools_source)
    print(f'Functions in tools.py: {len(tools_funcs)}')
except:
    print('Could not read tools.py')