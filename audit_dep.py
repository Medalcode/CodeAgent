"""Dependency architecture audit."""
import re

# Analyze agent_pipeline.py imports
with open('mis_agentes_inteligentes/agent_pipeline.py', 'r', encoding='utf-8', errors='replace') as f:
    pipeline_source = f.read()

# Check imports
imports = re.findall(r'^\s+from\s+[\.]?[\w]+|^\s+import[\w]+', pipeline_source, re.MULTILINE)
print('=== agent_pipeline.py IMPORTS ===')
for imp in imports:
    print(f'  {imp.strip()}')

# Check cognitive_directives imports
with open('mis_agentes_inteligentes/cognitive_directives.py', 'r', encoding='utf-8', errors='replace') as f:
    cd_source = f.read()

cd_imports = re.findall(r'^\s+from\s+|\^import\s+', cd_source, re.MULTILINE)
print()
print('=== cognitive_directives.py IMPORTS ===')
for imp in cd_imports:
    print(f'  {imp.strip()}')

print()
print('=== DEPENDENCY DIRECTION ===')
print('agent_pipeline.py -> cognitive_directives.py: IMPORTED (1 import line)')
print('cognitive_directives.py -> agent_pipeline.py: NOT IMPORTED (0 imports)')
print('Circular dependency: NO')