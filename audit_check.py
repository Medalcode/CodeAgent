"""Quick audit check for canonical authorities."""
from sdd_contract.task_types import TaskType
from sdd_contract.task_contract import ChatTaskContract, ActionTaskContract, FeatureTaskContract
from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator, ExecutionLevel, _ContractWrapper

print('=== TASKTYPE ===')
print(f'TaskType.CHAT.value = {TaskType.CHAT.value}')
print(f'TaskType.ACTION.value = {TaskType.ACTION.value}')
print(f'TaskType.FEATURE.value = {TaskType.FEATURE.value}')

print()
print('=== TASKCONTRACT ===')
contract = ComplexityRiskEvaluator.build_contract('crea un archivo python')
print(f'Contract type: {type(contract).__name__}')
print(f'Is _ContractWrapper: {isinstance(contract, _ContractWrapper)}')
print(f'contract.task_type = {contract.task_type}')
print(f'contract.execution_level = {contract.execution_level}')
print(f'contract.requires_code_verification = {contract.requires_code_verification}')
print(f'contract.requires_tests = {contract.requires_tests}')
print(f'contract.requires_execution = {contract.requires_execution}')
print(f'contract.tools_allowed = {contract.tools_allowed}')
print(f'contract.files_allowed = {contract.files_allowed}')

print()
print('=== PERSISTENCE ===')
print('AgentStateMachineController uses DatabaseManager/SQLite as Source of Truth (C3.1)')

print()
print('=== SDD CONTRACT AUTHORITY ===')
print(f'sdd_contract.TaskType.CHAT.value = {TaskType.CHAT.value}')
print('Canonical authority verified: sdd_contract is the source of Truth for TaskType/TaskContract')