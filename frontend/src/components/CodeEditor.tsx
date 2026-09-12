import React, { useState, useEffect, useRef } from 'react';
import type { WorkspaceFile } from '../api/apiClient';
import { apiClient } from '../api/apiClient';

interface CodeEditorProps {
  file: WorkspaceFile | null;
  onSaved: () => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ file, onSaved }) => {
  const [content, setContent] = useState('');
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (file) {
      setContent(file.content || '');
      setIsDirty(false);
      setError(null);
    } else {
      setContent('');
      setIsDirty(false);
    }
  }, [file]);

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    if (!isDirty && file) setIsDirty(true);
  };

  const handleSave = async () => {
    if (!file || !file.path) {
      setError('Cannot save: file path is unknown.');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      const res = await apiClient.saveFile(file.path, content);
      if (res.success) {
        setIsDirty(false);
        onSaved();
      } else {
        setError(res.error || 'Unknown save error');
      }
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  // Build line numbers
  const linesCount = Math.max(content.split('\n').length, 20);
  const lineNumbers = Array.from({ length: linesCount }, (_, i) => i + 1);

  if (!file) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#1e1e1e', color: '#666' }}>
        No File Open
      </div>
    );
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#1e1e1e', overflow: 'hidden' }}>
      {/* Editor Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 15px', background: '#252526', borderBottom: '1px solid #333' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <strong style={{ color: '#fff', fontSize: '14px' }}>
            {file.name} {isDirty ? '*' : ''}
          </strong>
          {saving && <span style={{ color: '#888', fontSize: '11px' }}>Saving...</span>}
          {error && <span style={{ color: '#f44336', fontSize: '11px' }}>{error}</span>}
        </div>
        <button 
          onClick={handleSave} 
          disabled={!isDirty || saving}
          style={{ 
            background: isDirty ? '#007acc' : '#333', 
            color: isDirty ? '#fff' : '#888', 
            border: 'none', 
            padding: '4px 12px', 
            borderRadius: '3px', 
            cursor: isDirty ? 'pointer' : 'not-allowed',
            fontSize: '11px' 
          }}
        >
          Save
        </button>
      </div>
      
      {/* Editor Body */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', position: 'relative' }}>
        <div style={{ 
          padding: '10px', 
          background: '#2d2d2d', 
          color: '#858585', 
          textAlign: 'right', 
          userSelect: 'none',
          fontFamily: 'Consolas, monospace',
          fontSize: '13px',
          lineHeight: '1.5',
          minWidth: '40px',
          overflowY: 'hidden'
        }}>
          {lineNumbers.map(n => <div key={n}>{n}</div>)}
        </div>
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          style={{
            flex: 1,
            background: '#1e1e1e',
            color: '#d4d4d4',
            border: 'none',
            padding: '10px',
            fontFamily: 'Consolas, monospace',
            fontSize: '13px',
            lineHeight: '1.5',
            resize: 'none',
            outline: 'none',
            whiteSpace: 'pre',
            overflow: 'auto'
          }}
          onScroll={(e) => {
            // Sync line numbers scroll
            if (e.target instanceof HTMLTextAreaElement && e.target.previousElementSibling) {
              (e.target.previousElementSibling as HTMLElement).scrollTop = e.target.scrollTop;
            }
          }}
        />
      </div>
    </div>
  );
};