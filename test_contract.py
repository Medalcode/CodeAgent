from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator

evaluator = ComplexityRiskEvaluator()

# Test 1: direct build_contract
c1 = evaluator.build_contract('solo texto')
c2 = evaluator.build_contract('crea un archivo')
c3 = evaluator.build_contract('sistema completo')

print(f'Build 1 (CHAT): tools_allowed={c1.tools_allowed}')
print(f'Build 2 (ACTION): tools_allowed={c2.tools_allowed}')
print(f'Build 3 (FEATURE): tools_allowed={c3.tools_allowed}')

# Test 2: evaluate first
level = evaluator.evaluate('sistema completo')
print(f'\nLevel for feature goal: {level}')

# Test 3: build_contract after evaluate
c4 = evaluator.build_contract('sistema completo')
print(f'Build 4 (after evaluate): tools_allowed={c4.tools_allowed}')