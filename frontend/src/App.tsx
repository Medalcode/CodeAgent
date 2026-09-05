import { useState, useEffect } from 'react';
import { apiClient } from './api/apiClient';
import { EventAdapter } from './events/EventAdapter';
import type { SSEEvent } from './types';
import { WorkspaceTree } from './components/WorkspaceTree';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState('idle');
  const [events, setEvents] = useState<SSEEvent[]>([]);

  useEffect(() => {
    let adapter: EventAdapter | null = null;
    if (taskId) {
      adapter = new EventAdapter((event) => {
        setEvents((prev) => [...prev, event]);
        if (event.event_type === 'TASK_COMPLETED' || event.event_type === 'TASK_FAILED' || event.event_type === 'TASK_CANCELLED') {
          setStatus(event.event_type.toLowerCase().replace('task_', ''));
        }
      });
      adapter.connect(taskId);
    }
    return () => {
      if (adapter) adapter.disconnect();
    };
  }, [taskId]);

  const handleStart = async () => {
    if (!prompt.trim()) return;
    try {
      setStatus('starting');
      setEvents([]);
      const res = await apiClient.createTask(prompt);
      setTaskId(res.task_id);
      setStatus('running');
    } catch (e) {
      console.error(e);
      setStatus('error');
    }
  };

  const handleCancel = async () => {
    if (!taskId) return;
    try {
      setStatus('cancelling');
      await apiClient.cancelTask(taskId);
    } catch (e) {
      console.error(e);
      setStatus('error');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', margin: 0, padding: 0, fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', background: '#1e1e1e', color: '#ccc' }}>
      {/* Sidebar: Workspace Tree */}
      <WorkspaceTree />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <header style={{ padding: '10px 20px', background: '#252526', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>CodeAgent</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px' }}>Status: 
              <span style={{ 
                color: status === 'running' ? '#4caf50' : 
                       status === 'error' || status === 'failed' ? '#f44336' : 
                       status === 'cancelled' ? '#ff9800' : '#888',
                marginLeft: '5px',
                fontWeight: 'bold',
                textTransform: 'uppercase'
              }}>
                {status}
              </span>
            </span>
          </div>
        </header>

        {/* Task Timeline / Chat Area */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', background: '#1e1e1e' }}>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {events.length === 0 && status === 'idle' && (
              <div style={{ textAlign: 'center', color: '#666', marginTop: '50px' }}>
                Enter a prompt to start a new task.
              </div>
            )}
            {events.map((ev, i) => (
              <div key={i} style={{ 
                marginBottom: '10px', 
                padding: '10px', 
                background: '#2d2d2d', 
                borderRadius: '4px',
                borderLeft: '4px solid #007acc'
              }}>
                <div style={{ fontSize: '11px', color: '#888', marginBottom: '5px' }}>
                  {ev.event_type}
                </div>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '13px' }}>
                  {JSON.stringify(ev.payload, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div style={{ padding: '20px', background: '#252526', borderTop: '1px solid #333' }}>
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '10px' }}>
            <input 
              type="text" 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="What do you want to build or modify?"
              disabled={status === 'running' || status === 'cancelling' || status === 'starting'}
              style={{ 
                flex: 1, 
                padding: '10px 15px', 
                borderRadius: '4px', 
                border: '1px solid #444', 
                background: '#3c3c3c', 
                color: '#fff',
                fontSize: '14px',
                outline: 'none'
              }}
            />
            <button 
              onClick={handleStart} 
              disabled={status === 'running' || status === 'cancelling' || status === 'starting'}
              style={{
                padding: '0 20px',
                background: '#007acc',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Send
            </button>
            <button 
              onClick={handleCancel} 
              disabled={status !== 'running'}
              style={{
                padding: '0 20px',
                background: status === 'running' ? '#d32f2f' : '#555',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: status === 'running' ? 'pointer' : 'not-allowed',
                fontWeight: 'bold'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;