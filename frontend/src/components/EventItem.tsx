import React from 'react';
import type { SSEEvent } from '../types';
import { MarkdownContent } from './MarkdownContent';

interface EventItemProps {
  event: SSEEvent;
}

export const EventItem: React.FC<EventItemProps> = ({ event }) => {
  const getBadgeStyle = (status: string) => {
    switch (status) {
      case 'VERIFIED': return { background: '#1b5e20', color: '#a5d6a7', border: '1px solid #2e7d32' };
      case 'VERIFICATION_FAILED': return { background: '#b71c1c', color: '#ef9a9a', border: '1px solid #c62828' };
      default: return { background: '#424242', color: '#e0e0e0', border: '1px solid #616161' };
    }
  };

  const renderVerification = (payload: any) => {
    if (!payload.verification_status) return null;
    const style = getBadgeStyle(payload.verification_status);
    return (
      <span style={{ 
        display: 'inline-block', 
        padding: '2px 8px', 
        borderRadius: '12px', 
        fontSize: '11px', 
        fontWeight: 'bold', 
        marginRight: '8px',
        ...style 
      }}>
        {payload.verification_status.replace('_', ' ')}
      </span>
    );
  };

  // Determine what to show
  let content = '';
  if (event.event_type === 'LLM_CALL_COMPLETED') {
    content = event.payload.response || event.payload.respuesta || '';
  } else if (event.event_type === 'TASK_COMPLETED') {
    content = event.payload.summary || 'Task completed successfully.';
  } else if (event.event_type === 'TASK_FAILED' || event.event_type === 'TASK_CANCELLED') {
    content = event.payload.error || event.payload.reason || 'Task ended.';
  } else if (event.event_type === 'TOOL_EXECUTED') {
    content = `Executed: ${event.payload.tool_name}`;
  } else if (event.event_type === 'TOOL_CALL') {
    content = `Calling: ${event.payload.tool_name}`;
  }

  return (
    <div style={{ 
      marginBottom: '10px', 
      padding: '12px', 
      background: '#2d2d2d', 
      borderRadius: '6px',
      borderLeft: `4px solid ${event.event_type.includes('FAIL') ? '#f44336' : event.event_type.includes('COMPLETED') ? '#4caf50' : '#007acc'}`
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
        {renderVerification(event.payload)}
        <span style={{ fontSize: '11px', color: '#888', fontWeight: 'bold' }}>
          {event.event_type}
        </span>
        {event.payload.timestamp && (
          <span style={{ fontSize: '11px', color: '#666', marginLeft: 'auto' }}>
            {new Date(event.payload.timestamp * 1000).toLocaleTimeString()}
          </span>
        )}
      </div>
      
      {content ? (
        <MarkdownContent content={content} />
      ) : (
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '12px', color: '#999' }}>
          {JSON.stringify(event.payload, null, 2)}
        </pre>
      )}
    </div>
  );
};