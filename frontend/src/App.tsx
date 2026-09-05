import { useState, useRef } from 'react'
import './App.css'
import { apiClient } from './api/apiClient'
import { EventAdapter } from './events/EventAdapter'
import type { SSEEvent, TaskStatus } from './types'

function App() {
  const [prompt, setPrompt] = useState('')
  const [status, setStatus] = useState<TaskStatus>('IDLE')
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [error, setError] = useState<string | null>(null)
  
  const currentTaskId = useRef<string | null>(null)
  const eventAdapter = useRef<EventAdapter | null>(null)

  const handleStart = async () => {
    if (!prompt.trim()) return;
    setError(null);
    setEvents([]);
    setStatus('RUNNING');
    
    const taskId = 'task-' + Date.now();
    currentTaskId.current = taskId;
    
    if (!eventAdapter.current) {
      eventAdapter.current = new EventAdapter((ev) => {
        setEvents((prev) => [...prev, ev]);
        if (ev.event_type === 'TASK_COMPLETED' || ev.event_type === 'TASK_FAILED' || ev.event_type === 'TASK_CANCELLED') {
          setStatus(ev.event_type === 'TASK_COMPLETED' ? 'COMPLETED' : (ev.event_type === 'TASK_FAILED' ? 'FAILED' : 'CANCELLED'));
          eventAdapter.current?.disconnect();
        }
      });
    }
    eventAdapter.current.connect(taskId);

    try {
      const res = await apiClient.startChat(prompt, taskId);
      if (!res.success) {
        setError(res.error || 'API Error');
        setStatus('FAILED');
        eventAdapter.current.disconnect();
      }
    } catch (err: any) {
      setError(err.message);
      setStatus('FAILED');
      eventAdapter.current.disconnect();
    }
  };

  const handleCancel = async () => {
    if (currentTaskId.current) {
      await apiClient.cancelTask(currentTaskId.current);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>CodeAgent Frontend (Foundation)</h1>
      <div>
        <strong>Status: </strong> {status}
      </div>
      {error && <div style={{ color: 'red', margin: '10px 0' }}>{error}</div>}
      
      <div style={{ marginTop: '20px' }}>
        <textarea 
          rows={4} 
          cols={50} 
          value={prompt} 
          onChange={(e) => setPrompt(e.target.value)}
          disabled={status === 'RUNNING'}
          placeholder="Enter task objective..."
        />
      </div>
      <div style={{ marginTop: '10px' }}>
        <button onClick={handleStart} disabled={status === 'RUNNING'}>Start Task</button>
        <button onClick={handleCancel} disabled={status !== 'RUNNING'} style={{ marginLeft: '10px' }}>Cancel Task</button>
      </div>

      <div style={{ marginTop: '30px' }}>
        <h3>Event Timeline</h3>
        <div style={{ height: '300px', overflowY: 'auto', border: '1px solid #ccc', padding: '10px' }}>
          {events.map((ev, i) => (
            <div key={i} style={{ marginBottom: '8px', borderBottom: '1px solid #eee' }}>
              <strong>{ev.event_type}</strong>
              <pre style={{ fontSize: '12px', margin: '4px 0' }}>{JSON.stringify(ev.payload, null, 2)}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
