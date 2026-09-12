import type { ChatResponse, SSEEvent } from '../types';

export interface WorkspaceFile {
  name: string;
  path?: string;
  content?: string;
}

export interface WorkspaceTreeResponse {
  path: string;
  files: WorkspaceFile[];
}

export interface TaskInfo {
  id: string;
  status: string;
  goal: string;
  project_path: string;
  created_at?: string;
  updated_at?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async createTask(prompt: string): Promise<ChatResponse> {
    const res = await fetch(`${this.baseUrl}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, mode: 'autonomous' })
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  }

  async cancelTask(taskId: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/api/tasks/${taskId}/cancel`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to cancel task');
  }

  async getWorkspaceTree(): Promise<WorkspaceTreeResponse> {
    const res = await fetch(`${this.baseUrl}/api/workspace/tree`);
    if (!res.ok) throw new Error('Failed to fetch workspace tree');
    return res.json();
  }

  async listTasks(): Promise<{success: boolean, tasks: TaskInfo[]}> {
    const res = await fetch(`${this.baseUrl}/api/tasks`);
    if (!res.ok) throw new Error('Failed to list tasks');
    return res.json();
  }

  async getTaskEvents(taskId: string): Promise<{success: boolean, events: SSEEvent[]}> {
    const res = await fetch(`${this.baseUrl}/api/tasks/${taskId}/events`);
    if (!res.ok) throw new Error('Failed to fetch task events');
    return res.json();
  }

  async saveFile(filePath: string, content: string): Promise<{success: boolean, path?: string, error?: string}> {
    // If running in pywebview, use native API for parity if available
    // @ts-ignore
    if (window.pywebview && window.pywebview.api && window.pywebview.api.write_file) {
      try {
        // @ts-ignore
        const ok = await window.pywebview.api.write_file(filePath, content);
        if (ok) return { success: true, path: filePath };
        return { success: false, error: 'Pywebview write failed' };
      } catch (e: any) {
        return { success: false, error: e.message || String(e) };
      }
    }

    // Fallback to REST API
    const res = await fetch(`${this.baseUrl}/api/fs/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filePath, content })
    });
    return res.json();
  }
}

export const apiClient = new ApiClient();