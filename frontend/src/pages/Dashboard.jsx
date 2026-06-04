import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import client from "../api/client";

const GRADE_COLOR = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };

export default function Dashboard() {
  const [domains, setDomains] = useState([]);
  const [newHostname, setNewHostname] = useState("");
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState({});
  const navigate = useNavigate();

  useEffect(() => { fetchDomains(); }, []);

  async function fetchDomains() {
    setLoading(true);
    const { data } = await client.get("/api/domains/");
    setDomains(data);
    setLoading(false);
  }

  async function addDomain(e) {
    e.preventDefault();
    if (!newHostname.trim()) return;
    await client.post("/api/domains/", { hostname: newHostname.trim() });
    setNewHostname("");
    fetchDomains();
  }

  async function triggerScan(domainId) {
    setScanning(s => ({ ...s, [domainId]: true }));
    try {
      const { data } = await client.post(`/api/domains/${domainId}/scan/`);
      // Poll until complete, then refresh
      await pollScan(data.scan_id);
      fetchDomains();
    } catch (err) {
      alert(err.response?.data?.detail || "Scan failed.");
    }
    setScanning(s => ({ ...s, [domainId]: false }));
  }

  async function pollScan(scanId) {
    while (true) {
      await new Promise(r => setTimeout(r, 2000));
      const { data } = await client.get(`/api/scans/${scanId}/`);
      if (data.status === "completed" || data.status === "failed") return data;
    }
  }

  async function verifyDomain(domainId) {
    const { data } = await client.post(`/api/domains/${domainId}/verify/`);
    alert(data.detail);
    fetchDomains();
  }

  function logout() {
    localStorage.clear();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Posture Scanner</h1>
        <button onClick={logout} className="text-sm text-gray-500 hover:text-red-500">Sign out</button>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Add domain */}
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="font-semibold text-gray-700 mb-3">Add a domain</h2>
          <form onSubmit={addDomain} className="flex gap-3">
            <input className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              type="text" placeholder="example.com" value={newHostname}
              onChange={e => setNewHostname(e.target.value)} />
            <button className="bg-blue-600 text-white rounded-lg px-6 py-2 hover:bg-blue-700 font-medium"
              type="submit">Add</button>
          </form>
        </div>

        {/* Domain list */}
        {loading ? <p className="text-gray-400 text-center">Loading…</p> : domains.map(d => (
          <div key={d.id} className="bg-white rounded-2xl shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold text-gray-800">{d.hostname}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {d.is_verified ? "✅ Verified" : "⚠️ Not verified"}
                </p>
              </div>
              {d.latest_grade && (
                <span className={`text-4xl font-bold ${GRADE_COLOR[d.latest_grade.grade] || "text-gray-600"}`}>
                  {d.latest_grade.grade}
                  <span className="text-sm text-gray-400 font-normal ml-1">{d.latest_grade.score}/100</span>
                </span>
              )}
            </div>
            <div className="flex gap-2 mt-4">
              {!d.is_verified && (
                <button onClick={() => verifyDomain(d.id)}
                  className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50">
                  Verify ownership
                </button>
              )}
              <button onClick={() => triggerScan(d.id)} disabled={!d.is_verified || scanning[d.id]}
                className="text-sm bg-blue-600 text-white rounded-lg px-3 py-1.5 hover:bg-blue-700 disabled:opacity-40">
                {scanning[d.id] ? "Scanning…" : "Run scan"}
              </button>
              {d.latest_grade && (
                <button onClick={() => navigate(`/scans/${d.latest_grade?.scan_id}/report`)}
                  className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50">
                  View report
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
