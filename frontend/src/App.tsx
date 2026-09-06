import { useState, useEffect } from 'react';
import { apiClient } from './api/apiClient';
import { EventAdapter } from './events/EventAdapter';
import type { SSEEvent } from './types';
import { WorkspaceTree } from './components/WorkspaceTree';
import { EventTimeline } from './components/EventTimeline';
import { TaskHistory } from './components/TaskHistory';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState('idle');
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [leftTab, setLeftTab] = useState<'workspace' | 'history'>('workspace');

  // Conexión SSE
  useEffect(() => {
    let adapter: EventAdapter | null = null;
    if (taskId && (status === 'starting' || status === 'running' || status === 'cancelling')) {
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
  }, [taskId, status]);

  const handleStart = async () => {
    if (!prompt.trim()) return;
    try {
      setStatus('starting');
      setEvents([]);
      const res = await apiClient.createTask(prompt);
      setTaskId(res.task_id || null);
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

  const handleNewTask = () => {
    setTaskId(null);
    setStatus('idle');
    setEvents([]);
    setPrompt('');
  };

  const handleSelectTask = async (id: string) => {
    setTaskId(id);
    setStatus('loading');
    setEvents([]);
    try {
      const res = await apiClient.getTaskEvents(id);
      setEvents(res.events || []);
      // If we loaded it from history, it's typically completed/failed
      setStatus('history'); 
    } catch (e) {
      console.error(e);
      setStatus('error');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', margin: 0, padding: 0, fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', background: '#1e1e1e', color: '#ccc' }}>
      
      {/* Sidebar (Workspace or History) */}
      <div style={{ display: 'flex', flexDirection: 'column', width: '250px', borderRight: '1px solid #333' }}>
        <div style={{ display: 'flex', background: '#252526', borderBottom: '1px solid #333' }}>
          <button 
            onClick={() => setLeftTab('workspace')} 
            style={{ flex: 1, padding: '10px', background: leftTab === 'workspace' ? '#1e1e1e' : 'transparent', color: leftTab === 'workspace' ? '#fff' : '#888', border: 'none', borderBottom: leftTab === 'workspace' ? '2px solid #007acc' : '2px solid transparent', cursor: 'pointer' }}
          >
            Workspace
          </button>
          <button 
            onClick={() => setLeftTab('history')} 
            style={{ flex: 1, padding: '10px', background: leftTab === 'history' ? '#1e1e1e' : 'transparent', color: leftTab === 'history' ? '#fff' : '#888', border: 'none', borderBottom: leftTab === 'history' ? '2px solid #007acc' : '2px solid transparent', cursor: 'pointer' }}
          >
            History
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {leftTab === 'workspace' ? <WorkspaceTree /> : <TaskHistory onSelectTask={handleSelectTask} currentTaskId={taskId} />}
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header */}
        <header style={{ padding: '10px 20px', background: '#252526', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>CodeAgent</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
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
            <button onClick={handleNewTask} style={{ padding: '4px 10px', background: '#333', color: '#ccc', border: '1px solid #555', borderRadius: '3px', cursor: 'pointer', fontSize: '12px' }}>
              + New Task
            </button>
          </div>
        </header>

        {/* Task Timeline / Chat Area */}
        <EventTimeline events={events} status={status} />

        {/* Input Area */}
        <div style={{ padding: '20px', background: '#252526', borderTop: '1px solid #333' }}>
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '10px' }}>
            <input 
              type="text" 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="What do you want to build or modify?"
              disabled={status === 'running' || status === 'cancelling' || status === 'starting'}
              onKeyDown={(e) => { if (e.key === 'Enter') handleStart(); }}
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
              disabled={status === 'running' || status === 'cancelling' || status === 'starting' || !prompt.trim()}
              style={{
                padding: '0 20px',
                background: '#007acc',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: (status === 'running' || status === 'cancelling' || status === 'starting' || !prompt.trim()) ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                opacity: (status === 'running' || status === 'cancelling' || status === 'starting' || !prompt.trim()) ? 0.5 : 1
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
                fontWeight: 'bold',
                opacity: status === 'running' ? 1 : 0.5
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