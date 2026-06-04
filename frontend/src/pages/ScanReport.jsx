import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import client from "../api/client";

const STATUS_BADGE = {
  pass: "bg-green-100 text-green-700",
  warn: "bg-yellow-100 text-yellow-700",
  fail: "bg-red-100 text-red-700",
  info: "bg-gray-100 text-gray-600",
};

const CATEGORY_LABEL = {
  tls: "TLS / SSL",
  headers: "HTTP Headers",
  cookies: "Cookies",
  redirects: "Open Redirects",
};

export default function ScanReport() {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    client.get(`/api/scans/${scanId}/report/`).then(r => {
      setReport(r.data);
      client.get(`/api/domains/${r.data.domain}/history/`).then(h => setHistory(h.data));
    });
  }, [scanId]);

  if (!report) return <p className="text-center mt-20 text-gray-400">Loading report…</p>;

  const byCategory = report.check_results.reduce((acc, r) => {
    (acc[r.category] = acc[r.category] || []).push(r);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <button onClick={() => navigate("/")} className="text-sm text-blue-600 hover:underline">← Dashboard</button>
        <h1 className="text-xl font-bold text-gray-800">Scan Report #{scanId}</h1>
        <span />
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Score summary */}
        <div className="bg-white rounded-2xl shadow p-6 flex gap-8 items-center">
          <div className="text-center">
            <p className="text-6xl font-bold text-gray-800">{report.grade}</p>
            <p className="text-gray-400 text-sm mt-1">{report.score} / 100</p>
          </div>
          <div className="flex-1">
            {history.length > 1 && (
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="created_at" hide />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={v => [`${v}`, "Score"]} />
                  <Line type="monotone" dataKey="score" stroke="#2563EB" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
            {history.length <= 1 && <p className="text-gray-400 text-sm">Run more scans to see score history.</p>}
          </div>
        </div>

        {/* Checks by category */}
        {Object.entries(byCategory).map(([category, checks]) => (
          <div key={category} className="bg-white rounded-2xl shadow p-6">
            <h2 className="font-semibold text-gray-700 mb-4">{CATEGORY_LABEL[category] || category}</h2>
            <div className="space-y-3">
              {checks.map(c => (
                <div key={c.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full mt-0.5 ${STATUS_BADGE[c.status]}`}>
                    {c.status.toUpperCase()}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800">{c.check_key.replace(/_/g, " ")}</p>
                    {c.observed_value && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">{c.observed_value}</p>
                    )}
                    {c.remediation && (
                      <p className="text-xs text-blue-600 mt-1">{c.remediation}</p>
                    )}
                  </div>
                  <span className="text-xs text-gray-400 shrink-0">{c.severity}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
