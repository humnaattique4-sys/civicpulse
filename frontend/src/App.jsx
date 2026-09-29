import React, { useState, useEffect } from "react";
import api from "./api";

const STATUSES = ["open", "in_progress", "resolved", "rejected"];
const CATEGORIES = ["water", "electricity", "sanitation", "streetlights", "roads", "other"];
const PRIORITIES = ["high", "normal", "low"];

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h2>Something went wrong.</h2>
          <p>Please refresh the page.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

function SubmitForm({ onSubmitted }) {
  const [text, setText] = useState("");
  const [location, setLocation] = useState("");
  const [contact, setContact] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.post("/api/complaints", {
        text,
        location,
        reporter_contact: contact || null,
      });
      setResult(res.data);
      setText("");
      setLocation("");
      setContact("");
      onSubmitted();
    } catch (err) {
      const data = err.response?.data;
      setError(
        data?.errors
          ? Object.entries(data.errors).map(([f, m]) => `${f}: ${m}`).join("; ")
          : data?.detail || "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Submit a Complaint</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Complaint</label>
          <br />
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
            minLength={10}
            maxLength={2000}
            rows={4}
            style={{ width: "100%" }}
          />
        </div>
        <div>
          <label>Location</label>
          <br />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            minLength={3}
            maxLength={200}
          />
        </div>
        <div>
          <label>Contact (optional)</label>
          <br />
          <input
            type="text"
            value={contact}
            onChange={(e) => setContact(e.target.value)}
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Submitting (AI triage can take a few seconds)..." : "Submit"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ border: "1px solid #ccc", padding: "1rem", marginTop: "1rem" }}>
          <p><strong>Category:</strong> {result.category}</p>
          <p><strong>Priority:</strong> {result.priority}</p>
          <p><strong>Summary:</strong> {result.ai_summary}</p>
          <p><strong>Triaged by:</strong> {result.triaged_by}</p>
        </div>
      )}
    </div>
  );
}

function Dashboard({ refreshKey, bumpRefresh }) {
  const [complaints, setComplaints] = useState([]);
  const [error, setError] = useState(null);
  const [statusError, setStatusError] = useState(null);
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const load = () => {
    const params = new URLSearchParams({ page, page_size: pageSize });
    if (category) params.set("category", category);
    if (priority) params.set("priority", priority);
    if (statusFilter) params.set("status", statusFilter);
    api
      .get(`/api/complaints?${params.toString()}`)
      .then((res) => {
        setComplaints(res.data);
        setError(null);
      })
      .catch(() => setError("Could not load complaints"));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey, category, priority, statusFilter, page]);

  const changeStatus = async (id, newStatus) => {
    setStatusError(null);
    try {
      await api.patch(`/api/complaints/${id}/status`, { status: newStatus });
      load();
      bumpRefresh();
    } catch (err) {
      setStatusError(err.response?.data?.detail || "Could not update status");
    }
  };

  return (
    <div>
      <h2>Dashboard</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {statusError && <p style={{ color: "red" }}>{statusError}</p>}

      <div style={{ marginBottom: "1rem" }}>
        <label>Category: </label>
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <label style={{ marginLeft: "1rem" }}>Priority: </label>
        <select
          value={priority}
          onChange={(e) => {
            setPriority(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All</option>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>

        <label style={{ marginLeft: "1rem" }}>Status: </label>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <table border="1" cellPadding="6" style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Location</th>
            <th>Summary</th>
            <th>Change status</th>
          </tr>
        </thead>
        <tbody>
          {complaints.map((c) => (
            <tr key={c.id}>
              <td>{c.category}</td>
              <td>{c.priority}</td>
              <td>{c.status}</td>
              <td>{c.location}</td>
              <td>{c.ai_summary}</td>
              <td>
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value) changeStatus(c.id, e.target.value);
                  }}
                >
                  <option value="">-- set status --</option>
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "1rem" }}>
        <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
          Previous
        </button>
        <span style={{ margin: "0 1rem" }}>Page {page}</span>
        <button disabled={complaints.length < pageSize} onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}

function CountList({ title, counts }) {
  return (
    <div>
      <h3>{title}</h3>
      <ul>
        {Object.entries(counts || {}).map(([key, count]) => (
          <li key={key}>{key}: {count}</li>
        ))}
      </ul>
    </div>
  );
}

function Stats() {
  const [stats, setStats] = useState(null);
  const [cacheStatus, setCacheStatus] = useState(null);
  const [error, setError] = useState(null);

  const load = () => {
    api
      .get("/api/stats")
      .then((res) => {
        setStats(res.data);
        setCacheStatus(res.headers["x-cache"] || "unknown");
        setError(null);
      })
      .catch(() => setError("Could not load stats"));
  };

  useEffect(() => {
    load();
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!stats) return <p>Loading...</p>;

  const total =
    stats.total ??
    Object.values(stats.by_category || {}).reduce((a, b) => a + b, 0);

  return (
    <div>
      <h2>Stats</h2>
      <p>
        Cache: <strong>{cacheStatus}</strong>{" "}
        <button onClick={load}>Refresh</button>
      </p>
      <p>Total complaints: {total}</p>
      <CountList title="By category" counts={stats.by_category} />
      <CountList title="By priority" counts={stats.by_priority} />
    </div>
  );
}

function App() {
  const [tab, setTab] = useState("submit");
  const [refreshKey, setRefreshKey] = useState(0);
  const bumpRefresh = () => setRefreshKey((k) => k + 1);

  return (
    <ErrorBoundary>
      <div style={{ maxWidth: 800, margin: "2rem auto", fontFamily: "sans-serif" }}>
        <h1>CivicPulse</h1>
        <nav style={{ marginBottom: "1rem" }}>
          <button onClick={() => setTab("submit")}>Submit</button>
          <button onClick={() => setTab("dashboard")}>Dashboard</button>
          <button onClick={() => setTab("stats")}>Stats</button>
        </nav>

        {tab === "submit" && <SubmitForm onSubmitted={bumpRefresh} />}
        {tab === "dashboard" && <Dashboard refreshKey={refreshKey} bumpRefresh={bumpRefresh} />}
        {tab === "stats" && <Stats />}
      </div>
    </ErrorBoundary>
  );
}

export default App;