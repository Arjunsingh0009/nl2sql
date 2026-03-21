import React, { useState, useMemo } from "react";
import "./ResultsTable.css";

const PAGE_SIZE = 20;

export default function ResultsTable({ columns, rows }) {
  const [sortCol, setSortCol] = useState(null);
  const [sortDir, setSortDir] = useState("asc");
  const [page, setPage] = useState(0);
  const [filter, setFilter] = useState("");

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortCol(col);
      setSortDir("asc");
    }
    setPage(0);
  };

  const filtered = useMemo(() => {
    if (!filter.trim()) return rows;
    const f = filter.toLowerCase();
    return rows.filter((row) =>
      row.some((cell) => String(cell ?? "").toLowerCase().includes(f))
    );
  }, [rows, filter]);

  const sorted = useMemo(() => {
    if (sortCol === null) return filtered;
    const idx = columns.indexOf(sortCol);
    return [...filtered].sort((a, b) => {
      const av = a[idx] ?? "";
      const bv = b[idx] ?? "";
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
  }, [filtered, sortCol, sortDir, columns]);

  const paginated = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);

  if (!columns.length) {
    return (
      <div className="table-empty">
        <span>Query returned no results.</span>
      </div>
    );
  }

  return (
    <div className="results-table-wrapper">
      {rows.length > 5 && (
        <div className="table-toolbar">
          <input
            className="table-filter"
            type="text"
            placeholder="Filter results…"
            value={filter}
            onChange={(e) => { setFilter(e.target.value); setPage(0); }}
          />
          <span className="table-count">
            {filtered.length} of {rows.length} rows
          </span>
        </div>
      )}

      <div className="table-scroll">
        <table className="results-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className={sortCol === col ? "sorted" : ""}
                >
                  <span className="th-inner">
                    {col}
                    <span className="sort-icon">
                      {sortCol === col ? (sortDir === "asc" ? " ↑" : " ↓") : " ⇅"}
                    </span>
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginated.map((row, ri) => (
              <tr key={ri} className={ri % 2 === 0 ? "even" : "odd"}>
                {row.map((cell, ci) => (
                  <td key={ci}>
                    {cell === null ? (
                      <span className="null-value">NULL</span>
                    ) : typeof cell === "number" ? (
                      <span className="num-value">{cell.toLocaleString()}</span>
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            onClick={() => setPage(0)}
            disabled={page === 0}
          >«</button>
          <button
            className="page-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >‹</button>
          <span className="page-info">
            Page {page + 1} of {totalPages}
          </span>
          <button
            className="page-btn"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
          >›</button>
          <button
            className="page-btn"
            onClick={() => setPage(totalPages - 1)}
            disabled={page === totalPages - 1}
          >»</button>
        </div>
      )}
    </div>
  );
}
