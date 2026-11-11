import React, { useState } from "react";
import { registerUser, loginUser } from "../api";

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await registerUser(username, email, password);
        // Auto-login after registration
        const loginData = await loginUser(username, password);
        onAuthSuccess(loginData.user, loginData.dietary_profile);
        onClose();
      } else {
        const loginData = await loginUser(username || email, password);
        onAuthSuccess(loginData.user, loginData.dietary_profile);
        onClose();
      }
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.error || "Authentication failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ margin: 0, fontSize: "1.25rem", color: "#1e293b" }}>
            {isRegister ? "Create Account" : "Sign In to Food Label Verification System"}
          </h2>
          <button onClick={onClose} style={closeButtonStyle}>×</button>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.25rem" }}>
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(""); }}
            style={{ ...tabStyle, borderBottom: !isRegister ? "2px solid #2563eb" : "none", fontWeight: !isRegister ? "bold" : "normal" }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(""); }}
            style={{ ...tabStyle, borderBottom: isRegister ? "2px solid #2563eb" : "none", fontWeight: isRegister ? "bold" : "normal" }}
          >
            Register
          </button>
        </div>

        {error && (
          <div style={{ backgroundColor: "#fef2f2", color: "#b91c1c", padding: "0.75rem", borderRadius: "6px", marginBottom: "1rem", fontSize: "0.875rem" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <label style={labelStyle}>{isRegister ? "Username (3-30 alphanumeric chars)" : "Username or Email"}</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={isRegister ? "e.g. food_researcher" : "username or email"}
              style={inputStyle}
            />
          </div>

          {isRegister && (
            <div>
              <label style={labelStyle}>Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                style={inputStyle}
              />
            </div>
          )}

          <div>
            <label style={labelStyle}>Password (min 6 characters)</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={inputStyle}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "0.75rem",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "6px",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer"
            }}
          >
            {loading ? "Processing..." : isRegister ? "Register & Sign In" : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(15, 23, 42, 0.6)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};

const modalStyle = {
  backgroundColor: "#ffffff",
  borderRadius: "12px",
  padding: "1.75rem",
  width: "90%",
  maxWidth: "420px",
  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
};

const closeButtonStyle = {
  background: "none",
  border: "none",
  fontSize: "1.5rem",
  color: "#64748b",
  cursor: "pointer"
};

const tabStyle = {
  background: "none",
  border: "none",
  padding: "0.5rem 1rem",
  cursor: "pointer",
  color: "#1e293b",
  fontSize: "0.95rem"
};

const labelStyle = {
  display: "block",
  fontSize: "0.85rem",
  fontWeight: 600,
  color: "#475569",
  marginBottom: "0.25rem"
};

const inputStyle = {
  width: "100%",
  padding: "0.6rem 0.75rem",
  border: "1px solid #cbd5e1",
  borderRadius: "6px",
  fontSize: "0.95rem",
  boxSizing: "border-box"
};
