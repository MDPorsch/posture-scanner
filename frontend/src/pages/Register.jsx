import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";

export default function Register() {
  const [form, setForm] = useState({ email: "", full_name: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await client.post("/api/auth/register/", form);
      // Auto-login after registration
      const { data } = await client.post("/api/auth/login/", {
        email: form.email, password: form.password,
      });
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.email?.[0] || "Registration failed.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Create your account</h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            type="text" placeholder="Full name" value={form.full_name}
            onChange={e => setForm({ ...form, full_name: e.target.value })} />
          <input className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            type="email" placeholder="Email" value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })} required />
          <input className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            type="password" placeholder="Password (min 8 chars)" value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })} required />
          <button className="w-full bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 font-medium"
            type="submit">Create account</button>
        </form>
        <p className="mt-4 text-sm text-gray-500">
          Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
