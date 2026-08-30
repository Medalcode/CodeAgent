#!/usr/bin/env python3
with open('mis_agentes_inteligentes/agent_pipeline.py', 'r', errors='replace') as f:
    lines = f.readlines()
# Find and fix line 290 (index 289)
for i, line in enumerate(lines):
    if i == 289:  # line 290
        # Replace the problematic line with ASCII-safe version
        lines[i] = line.replace('\ufffd', '?').encode('ascii', errors='replace').decode('ascii')
        print(f'Fixed line {i+1}')
# Write back
with open('mis_agentes_inteligentes/agent_pipeline.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')