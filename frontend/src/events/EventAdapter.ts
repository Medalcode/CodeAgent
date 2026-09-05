import type { SSEEvent } from '../types';

export class EventAdapter {
  private eventSource: EventSource | null = null;
  private onEventCallback: (event: SSEEvent) => void;

  constructor(onEvent: (event: SSEEvent) => void) {
    this.onEventCallback = onEvent;
  }

  connect(taskId: string) {
    this.disconnect();
    const url = `/api/pipeline/events?task_id=${encodeURIComponent(taskId)}`;
    this.eventSource = new EventSource(url);

    this.eventSource.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data) as SSEEvent;
        this.onEventCallback(parsed);
      } catch (err) {
        console.warn('Failed to parse SSE event', err);
      }
    };

    this.eventSource.onerror = () => {
      console.warn('SSE EventSource error/closed');
      this.disconnect();
    };
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
