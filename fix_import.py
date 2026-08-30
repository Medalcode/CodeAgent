#!/usr/bin/env python3
with open('mis_agentes_inteligentes/agent_pipeline.py', 'r', errors='ignore') as f:
    content = f.read()
# Replace the relative import with absolute import
content = content.replace(
    'from .sdd_contract.task_contract import ChatTaskContract, ActionTaskContract, FeatureTaskContract',
    'from sdd_contract.task_contract import ChatTaskContract, ActionTaskContract, FeatureTaskContract'
)
with open('mis_agentes_inteligentes/agent_pipeline.py', 'w', errors='ignore') as f:
    f.write(content)
print('Done')