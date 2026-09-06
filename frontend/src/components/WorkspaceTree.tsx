import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/apiClient';
import type { WorkspaceFile } from '../api/apiClient';

interface TreeNode {
  name: string;
  path: string;
  isFile: boolean;
  children?: { [key: string]: TreeNode };
}

export const WorkspaceTree: React.FC = () => {
  const [workspacePath, setWorkspacePath] = useState<string>('Loading...');
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['root']));

  const loadTree = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getWorkspaceTree();
      setWorkspacePath(data.path);
      setFiles(data.files);
      setTree(buildTree(data.files));
    } catch (err: any) {
      setError(err.message || 'Error loading workspace tree');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  const handleOpenFolder = async () => {
    // @ts-ignore
    if (window.pywebview && window.pywebview.api) {
      try {
        // @ts-ignore
        const res = await window.pywebview.api.open_folder_dialog();
        if (res && res.path) {
          loadTree();
        }
      } catch (e) {
        console.error(e);
      }
    } else {
      alert("Native folder picker is only available in Desktop App.");
    }
  };

  const buildTree = (workspaceFiles: WorkspaceFile[]): TreeNode => {
    const root: TreeNode = { name: 'root', path: 'root', isFile: false, children: {} };
    for (const f of workspaceFiles) {
      const parts = f.name.split('/');
      let current = root;
      let currentPath = '';
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        if (!current.children![part]) {
          current.children![part] = {
            name: part,
            path: currentPath,
            isFile: i === parts.length - 1,
            children: i === parts.length - 1 ? undefined : {}
          };
        }
        current = current.children![part];
      }
    }
    return root;
  };

  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  const renderNode = (node: TreeNode, depth: number = 0) => {
    const paddingLeft = depth * 12 + 10;
    const isExpanded = expandedNodes.has(node.path);

    if (node.isFile) {
      return (
        <div key={node.path} style={{ paddingLeft, cursor: 'default', color: '#ccc', padding: '2px 0 2px ' + paddingLeft + 'px', fontSize: '13px' }}>
          📄 {node.name}
        </div>
      );
    }

    return (
      <div key={node.path}>
        <div 
          onClick={() => toggleNode(node.path)}
          style={{ paddingLeft, cursor: 'pointer', fontWeight: 'bold', padding: '2px 0 2px ' + paddingLeft + 'px', fontSize: '13px', color: '#eee' }}
        >
          {isExpanded ? '📂' : '📁'} {node.name}
        </div>
        {isExpanded && node.children && (
          <div>
            {Object.values(node.children)
              .sort((a, b) => {
                if (a.isFile === b.isFile) return a.name.localeCompare(b.name);
                return a.isFile ? 1 : -1;
              })
              .map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#1e1e1e', width: '100%' }}>
      <div style={{ padding: '10px', borderBottom: '1px solid #333', background: '#252526' }}>
        <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#fff', textTransform: 'uppercase' }}>Workspace</h3>
        <div style={{ fontSize: '11px', color: '#9cdcfe', marginBottom: '10px', wordBreak: 'break-all' }}>
          {workspacePath}
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          <button onClick={handleOpenFolder} style={{ flex: 1, fontSize: '11px', padding: '4px', cursor: 'pointer', background: '#333', color: '#ccc', border: '1px solid #555', borderRadius: '3px' }}>Open Folder</button>
          <button onClick={loadTree} style={{ flex: 1, fontSize: '11px', padding: '4px', cursor: 'pointer', background: '#333', color: '#ccc', border: '1px solid #555', borderRadius: '3px' }}>Refresh</button>
        </div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 0' }}>
        {loading && <div style={{ padding: '10px', fontSize: '12px', color: '#888' }}>Loading...</div>}
        {error && <div style={{ padding: '10px', fontSize: '12px', color: '#f44' }}>{error}</div>}
        {!loading && !error && tree && tree.children && (
          Object.values(tree.children)
            .sort((a, b) => {
              if (a.isFile === b.isFile) return a.name.localeCompare(b.name);
              return a.isFile ? 1 : -1;
            })
            .map(child => renderNode(child, 0))
        )}
        {!loading && !error && files.length === 0 && (
          <div style={{ padding: '10px', fontSize: '12px', color: '#888' }}>No files found in workspace.</div>
        )}
      </div>
    </div>
  );
};