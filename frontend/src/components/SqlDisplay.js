import React, { useState } from "react";
import "./SqlDisplay.css";

const KEYWORDS = [
  "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL",
  "ON", "GROUP", "BY", "ORDER", "HAVING", "LIMIT", "OFFSET", "AND", "OR", "NOT",
  "IN", "BETWEEN", "LIKE", "IS", "NULL", "AS", "DISTINCT", "COUNT", "SUM", "AVG",
  "MAX", "MIN", "CASE", "WHEN", "THEN", "ELSE", "END", "DESC", "ASC", "WITH"
];

function highlightSQL(sql) {
  if (!sql) return "";

  let result = sql;

  // Escape HTML
  result = result.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Strings
  result = result.replace(/'([^']*)'/g, "<span class='sql-string'>'$1'</span>");

  // Numbers
  result = result.replace(/\b(\d+\.?\d*)\b/g, "<span class='sql-number'>$1</span>");

  // Keywords
  KEYWORDS.forEach((kw) => {
    const regex = new RegExp(`\\b${kw}\\b`, "gi");
    result = result.replace(regex, `<span class='sql-keyword'>${kw}</span>`);
  });

  // Comments
  result = result.replace(/(--[^\n]*)/g, "<span class='sql-comment'>$1</span>");

  // Table/column refs (word.word)
  result = result.replace(
    /\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b/g,
    "<span class='sql-table'>$1</span>.<span class='sql-col'>$2</span>"
  );

  return result;
}

export default function SqlDisplay({ sql }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="sql-display">
      <div className="sql-header">
        <div className="sql-label">
          <span className="label-dot" />
          Generated SQL
        </div>
        <button className={`copy-btn ${copied ? "copied" : ""}`} onClick={handleCopy}>
          {copied ? "✓ Copied" : "⎘ Copy"}
        </button>
      </div>
      <div className="sql-body">
        <pre
          className="sql-code"
          dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }}
        />
      </div>
    </div>
  );
}
