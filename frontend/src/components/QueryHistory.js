import React from "react";
import "./SidePanel.css";

export default function QueryHistory({ history, onSelect, onClear, onClose }) {
  return (
    <aside className="side-panel">
      <div className="panel-header">
        <span className="panel-title">Query History</span>
        <div style={{ display: "flex", gap: "8px" }}>
          {history.length > 0 && (
            <button className="panel-close" onClick={onClear} title="Clear history">
              ✕ Clear
            </button>
          )}
          <button className="panel-close" onClick={onClose}>✕</button>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="panel-empty">No queries yet.</div>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <button
              key={item.id}
              className="history-item"
              onClick={() => onSelect(item)}
            >
              <span className="history-nl">{item.natural_language}</span>
              <div className="history-meta">
                <span className="history-tag">{item.row_count} rows</span>
                <span className="history-time">{item.timestamp}</span>
              </div>
              <code className="history-sql">{item.sql}</code>
            </button>
          ))}
        </div>
      )}
    </aside>
  );
}
