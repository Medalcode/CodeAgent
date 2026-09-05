export type TaskStatus = 'IDLE' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'CANCELLED' | 'FAILED';

export interface SSEEvent {
  event_type: 'TASK_CREATED' | 'STATE_CHANGED' | 'TOOL_CALL' | 'LLM_CALL_COMPLETED' | 'TASK_COMPLETED' | 'TASK_FAILED' | 'TASK_CANCELLED' | 'TOOL_EXECUTED';
  task_id: string;
  payload: any;
}

export interface ChatResponse {
  success: boolean;
  respuesta?: string;
  terminal_tasks?: string[];
  error?: string;
  task_id?: string;
  mode?: string;
}