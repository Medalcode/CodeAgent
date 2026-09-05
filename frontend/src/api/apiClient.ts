import type { ChatResponse } from '../types';

const API_BASE = '/api';

export const apiClient = {
  async startChat(prompt: string, taskId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, task_id: taskId })
    });
    return res.json();
  },

  async cancelTask(taskId: string): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return res.json();
  }
};
