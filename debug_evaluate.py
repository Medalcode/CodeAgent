from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator

# Test various goals
goals = [
    'responde unicamente con OK',
    'crea action_final.py y ejecútalo',
    'implementa un sistema completo de autenticación',
    'hola',
    'crea un archivo python'
]

for goal in goals:
    level = ComplexityRiskEvaluator.evaluate(goal)
    print(f'Goal: "{goal}" -> Level: {level}')