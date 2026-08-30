from sdd_contract.task_router import TaskRouter

router = TaskRouter()

# Test classification
goals = [
    'implementa un sistema completo de autenticacion',
    'sistema completo',
    'implementa un sistema',
    'crea un archivo',
    'responde unicamente con OK'
]

for goal in goals:
    result = router.classify(goal)
    print(f'Goal: \"{goal}\" -> TaskType: {result.task_type.value}, confidence: {result.confidence}')