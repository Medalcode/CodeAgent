import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/apiClient';
import type { TaskInfo } from '../api/apiClient';

interface TaskHistoryProps {
  onSelectTask: (taskId: string) => void;
  currentTaskId: string | null;
}

export const TaskHistory: React.FC<TaskHistoryProps> = ({ onSelectTask, currentTaskId }) => {
  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const res = await apiClient.listTasks();
      setTasks(res.tasks || []);
    } catch (e) {
      console.error('Failed to load tasks', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#1e1e1e' }}>
      <div style={{ padding: '10px', borderBottom: '1px solid #333', background: '#252526', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: '0', fontSize: '14px', color: '#fff', textTransform: 'uppercase' }}>History</h3>
        <button onClick={loadTasks} style={{ fontSize: '11px', padding: '4px', cursor: 'pointer', background: '#333', color: '#ccc', border: '1px solid #555', borderRadius: '3px' }}>
          Refresh
        </button>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 0' }}>
        {loading && <div style={{ padding: '10px', fontSize: '12px', color: '#888' }}>Loading...</div>}
        {!loading && tasks.length === 0 && <div style={{ padding: '10px', fontSize: '12px', color: '#888' }}>No tasks found.</div>}
        {!loading && tasks.map(task => (
          <div 
            key={task.id}
            onClick={() => onSelectTask(task.id)}
            style={{ 
              padding: '10px', 
              cursor: 'pointer', 
              borderBottom: '1px solid #333',
              background: task.id === currentTaskId ? '#2d2d2d' : 'transparent',
              borderLeft: task.id === currentTaskId ? '3px solid #007acc' : '3px solid transparent'
            }}
          >
            <div style={{ fontSize: '12px', color: '#fff', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {task.goal || 'No goal'}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#888' }}>
              <span>{task.status}</span>
              <span>{task.created_at ? new Date(task.created_at).toLocaleDateString() : ''}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};