import React, { useState, useCallback } from "react";
import QueryInput from "./components/QueryInput";
import ResultsTable from "./components/ResultsTable";
import SqlDisplay from "./components/SqlDisplay";
import QueryHistory from "./components/QueryHistory";
import SchemaPanel from "./components/SchemaPanel";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const SAMPLE_QUESTIONS = [
  "Show all employees with salary above 80000",
  "Which department has the highest average salary?",
  "List top 5 students by GPA",
  "Count students per major",
  "Show total sales by region",
  "Find all employees hired after 2020",
  "Which products have less than 50 items in stock?",
  "Show employees with their department names",
  "What is the average GPA by major?",
  "Which employee made the most sales?",
];

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showSchema, setShowSchema] = useState(false);
  const [explainMode, setExplainMode] = useState(false);

  const handleSubmit = useCallback(async (q = query) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ natural_language: q, explain: explainMode }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");

      setResult(data);
      setHistory((prev) => [
        { id: Date.now(), natural_language: q, sql: data.sql, row_count: data.row_count, timestamp: new Date().toLocaleTimeString() },
        ...prev.slice(0, 19),
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [query, explainMode]);

  const handleDownloadCSV = async () => {
    if (!result) return;
    try {
      const res = await fetch(`${API_URL}/download-csv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ natural_language: query }),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nl2sql_${Date.now()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Download failed: " + err.message);
    }
  };

  const handleHistoryClick = (item) => {
    setQuery(item.natural_language);
    handleSubmit(item.natural_language);
    setShowHistory(false);
  };

  return (
    <div className="app">
      {/* Background grid */}
      <div className="bg-grid" />

      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-bracket">[</span>
            <span className="logo-text">NL</span>
            <span className="logo-arrow">→</span>
            <span className="logo-sql">SQL</span>
            <span className="logo-bracket">]</span>
          </div>
          <p className="tagline">Ask in English. Get SQL.</p>
        </div>
        <div className="header-right">
          <button
            className={`btn-ghost ${showSchema ? "active" : ""}`}
            onClick={() => { setShowSchema(!showSchema); setShowHistory(false); }}
          >
            <span className="btn-icon">⬡</span> Schema
          </button>
          <button
            className={`btn-ghost ${showHistory ? "active" : ""}`}
            onClick={() => { setShowHistory(!showHistory); setShowSchema(false); }}
          >
            <span className="btn-icon">◷</span> History
            {history.length > 0 && <span className="badge">{history.length}</span>}
          </button>
        </div>
      </header>

      <main className="main">
        {/* Side panels */}
        {showSchema && <SchemaPanel onClose={() => setShowSchema(false)} />}
        {showHistory && (
          <QueryHistory
            history={history}
            onSelect={handleHistoryClick}
            onClear={() => setHistory([])}
            onClose={() => setShowHistory(false)}
          />
        )}

        {/* Main content */}
        <div className="content">
          {/* Query Input Section */}
          <section className="query-section">
            <div className="section-label">
              <span className="label-dot" />
              Natural Language Query
            </div>
            <QueryInput
              value={query}
              onChange={setQuery}
              onSubmit={() => handleSubmit()}
              loading={loading}
            />

            {/* Options row */}
            <div className="options-row">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={explainMode}
                  onChange={(e) => setExplainMode(e.target.checked)}
                  className="toggle-input"
                />
                <span className="toggle-track">
                  <span className="toggle-thumb" />
                </span>
                <span>Explain query in English</span>
              </label>

              {result && (
                <button className="btn-ghost small" onClick={handleDownloadCSV}>
                  ↓ Download CSV
                </button>
              )}
            </div>

            {/* Sample questions */}
            <div className="samples">
              <span className="samples-label">Try:</span>
              <div className="samples-list">
                {SAMPLE_QUESTIONS.slice(0, 5).map((q, i) => (
                  <button
                    key={i}
                    className="sample-chip"
                    onClick={() => { setQuery(q); handleSubmit(q); }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Error */}
          {error && (
            <div className="error-box">
              <span className="error-icon">⚠</span>
              <div>
                <strong>Query Error</strong>
                <p>{error}</p>
              </div>
              <button className="error-close" onClick={() => setError(null)}>✕</button>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="loading-box">
              <div className="loading-spinner" />
              <div className="loading-text">
                <span>Translating to SQL</span>
                <span className="loading-dots"><span>.</span><span>.</span><span>.</span></span>
              </div>
            </div>
          )}

          {/* Results */}
          {result && !loading && (
            <div className="results-container">
              {/* SQL Display */}
              <SqlDisplay sql={result.sql} />

              {/* Explanation */}
              {result.explanation && (
                <div className="explanation-box">
                  <span className="section-label"><span className="label-dot accent" />Explanation</span>
                  <p className="explanation-text">{result.explanation}</p>
                </div>
              )}

              {/* Stats row */}
              <div className="stats-row">
                <div className="stat">
                  <span className="stat-value">{result.row_count}</span>
                  <span className="stat-label">rows returned</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{result.execution_time_ms.toFixed(0)}ms</span>
                  <span className="stat-label">execution time</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{result.columns.length}</span>
                  <span className="stat-label">columns</span>
                </div>
              </div>

              {/* Table */}
              <ResultsTable columns={result.columns} rows={result.rows} />
            </div>
          )}

          {/* Empty state */}
          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-graphic">
                <div className="empty-ring r1" />
                <div className="empty-ring r2" />
                <div className="empty-ring r3" />
                <span className="empty-icon">⌨</span>
              </div>
              <h2 className="empty-title">Ask anything about your data</h2>
              <p className="empty-sub">
                Type a question in plain English above.<br />
                NL2SQL will write and execute the SQL for you.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
