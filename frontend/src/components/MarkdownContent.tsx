import React from 'react';

interface MarkdownContentProps {
  content: string;
}

const escapeHtml = (str: string) => {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
};

export const MarkdownContent: React.FC<MarkdownContentProps> = ({ content }) => {
  const renderSafeMarkdown = (text: string) => {
    if (!text) return '';
    const parts = text.split(/```/);
    let html = '';
    for (let i = 0; i < parts.length; i++) {
      if (i % 2 === 0) {
        html += escapeHtml(parts[i]).replace(/\n/g, '<br/>');
      } else {
        const codeLines = parts[i].split('\n');
        const lang = codeLines[0].trim();
        const code = codeLines.slice(1).join('\n');
        html += `<div style="margin: 10px 0; background: #1e1e1e; border: 1px solid #333; border-radius: 4px;">
                  <div style="background: #2d2d2d; padding: 2px 8px; font-size: 11px; color: #888; border-bottom: 1px solid #333;">${escapeHtml(lang || 'code')}</div>
                  <pre style="margin: 0; padding: 10px; overflow-x: auto; font-family: Consolas, monospace; font-size: 12px; color: #d4d4d4;"><code>${escapeHtml(code)}</code></pre>
                 </div>`;
      }
    }
    return html;
  };

  return (
    <div 
      style={{ lineHeight: '1.5', fontSize: '13px', color: '#ccc' }} 
      dangerouslySetInnerHTML={{ __html: renderSafeMarkdown(content) }} 
    />
  );
};