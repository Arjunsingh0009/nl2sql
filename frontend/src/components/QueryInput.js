import React, { useRef, useEffect } from "react";
import "./QueryInput.css";

export default function QueryInput({ value, onChange, onSubmit, loading }) {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + "px";
    }
  }, [value]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className={`query-input-wrapper ${loading ? "loading" : ""}`}>
      <div className="query-prefix">
        <span className="prefix-symbol">$</span>
      </div>
      <textarea
        ref={textareaRef}
        className="query-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything… e.g. 'Show all employees earning above $80k in the Engineering department'"
        rows={1}
        disabled={loading}
        autoFocus
      />
      <button
        className={`query-submit ${loading ? "loading" : ""}`}
        onClick={onSubmit}
        disabled={loading || !value.trim()}
        title="Run query (Enter)"
      >
        {loading ? (
          <span className="submit-spinner" />
        ) : (
          <span className="submit-icon">↵</span>
        )}
      </button>
    </div>
  );
}
