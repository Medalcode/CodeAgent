import React, { useEffect, useRef } from 'react';
import type { SSEEvent } from '../types';
import { EventItem } from './EventItem';

interface EventTimelineProps {
  events: SSEEvent[];
  status: string;
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events, status }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '20px', background: '#1e1e1e' }} ref={containerRef}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        {events.length === 0 && status === 'idle' && (
          <div style={{ textAlign: 'center', color: '#666', marginTop: '50px' }}>
            Enter a prompt to start a new task.
          </div>
        )}
        {events.map((ev, i) => (
          <EventItem key={i} event={ev} />
        ))}
      </div>
    </div>
  );
};