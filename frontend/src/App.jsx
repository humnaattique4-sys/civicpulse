import { useState, useEffect } from "react";
import api from "./api";

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
      setError(err.response?.data?.detail || "Something went wrong");
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
          {loading ? "Submitting..." : "Submit"}
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

function Dashboard({ refreshKey }) {
  const [complaints, setComplaints] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/api/complaints?page_size=100")
      .then((res) => setComplaints(res.data))
      .catch(() => setError("Could not load complaints"));
  }, [refreshKey]);

  return (
    <div>
      <h2>Dashboard</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <table border="1" cellPadding="6" style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Location</th>
            <th>Summary</th>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [tab, setTab] = useState("submit");
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>CivicPulse</h1>
      <nav style={{ marginBottom: "1rem" }}>
        <button onClick={() => setTab("submit")}>Submit</button>
        <button onClick={() => setTab("dashboard")}>Dashboard</button>
      </nav>

      {tab === "submit" && (
        <SubmitForm onSubmitted={() => setRefreshKey((k) => k + 1)} />
      )}
      {tab === "dashboard" && <Dashboard refreshKey={refreshKey} />}
    </div>
  );
}

export default App;