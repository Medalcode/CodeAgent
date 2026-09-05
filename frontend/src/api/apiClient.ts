const API_BASE = '/api';

export interface TaskResponse {
  task_id: string;
  status: string;
}

export interface WorkspaceFile {
  name: string;
  content: string;
}

export interface WorkspaceTreeResponse {
  success: boolean;
  path: string;
  recent_workspaces: string[];
  files: WorkspaceFile[];
}

export const apiClient = {
  async createTask(prompt: string, agentType: string = 'SWE-agent', model: string = 'gemini-2.5-flash', provider: string = 'google'): Promise<TaskResponse> {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, agent_type: agentType, model, provider }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async cancelTask(taskId: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/cancel`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async getWorkspaceTree(): Promise<WorkspaceTreeResponse> {
    const res = await fetch(`${API_BASE}/workspace/tree`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
};