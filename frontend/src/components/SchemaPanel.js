import React, { useState, useEffect } from "react";
import "./SidePanel.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function SchemaPanel({ onClose }) {
  const [schema, setSchema] = useState(null);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    fetch(`${API_URL}/schema`)
      .then((r) => r.json())
      .then((d) => setSchema(d.tables))
      .catch(() => {});
  }, []);

  const toggle = (table) =>
    setExpanded((prev) => ({ ...prev, [table]: !prev[table] }));

  return (
    <aside className="side-panel">
      <div className="panel-header">
        <span className="panel-title">Database Schema</span>
        <button className="panel-close" onClick={onClose}>✕</button>
      </div>

      {!schema ? (
        <div className="panel-empty">Loading schema…</div>
      ) : (
        <div className="schema-list">
          {Object.entries(schema).map(([table, info]) => (
            <div key={table} className="schema-table">
              <button
                className="schema-table-header"
                onClick={() => toggle(table)}
              >
                <span className="schema-table-icon">⬡</span>
                <span className="schema-table-name">{table}</span>
                <span className="schema-toggle">{expanded[table] ? "−" : "+"}</span>
              </button>
              {expanded[table] && (
                <div className="schema-columns">
                  <p className="schema-desc">{info.description}</p>
                  {info.columns.map((col) => (
                    <div key={col} className="schema-col">
                      <span className="col-dot" />
                      <span className="col-name">{col}</span>
                      {info.foreign_keys && info.foreign_keys[col] && (
                        <span className="col-fk">→ {info.foreign_keys[col]}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}
