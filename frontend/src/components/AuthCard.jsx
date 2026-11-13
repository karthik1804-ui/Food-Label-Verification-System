import React, { useState } from "react";
import { registerUser, loginUser } from "../api";
import Icon from "./Icons";

export default function AuthCard({ onAuthSuccess, onContinueAsGuest, currentUser, onSignOut }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // If already logged in, show user profile card with sign out and continue
  if (currentUser) {
    return (
      <div className="card glass auth-card user-logged-in-card">
        <div className="auth-header">
          <div className="auth-avatar-circle">
            <Icon name="user" size={32} color="#059669" />
          </div>
          <h2>Signed in as {currentUser.username}</h2>
          <p className="auth-sub">
            {currentUser.email ? currentUser.email : "Active session"}
          </p>
        </div>

        <div className="auth-actions-group">
          <button
            type="button"
            className="btn btn-primary btn-large"
            onClick={() => onContinueAsGuest ? onContinueAsGuest() : null}
          >
            <span>Proceed to Dietary Profile</span>
            <Icon name="arrowRight" size={18} />
          </button>

          <button
            type="button"
            className="btn btn-outline"
            onClick={onSignOut}
          >
            <Icon name="logOut" size={16} />
            <span>Switch Account / Sign Out</span>
          </button>
        </div>
      </div>
    );
  }

  const validateForm = () => {
    if (!username.trim()) {
      setError("Please enter a username.");
      return false;
    }
    if (isRegister) {
      if (username.length < 3 || username.length > 30) {
        setError("Username must be between 3 and 30 characters.");
        return false;
      }
      if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
        setError("Please enter a valid email address.");
        return false;
      }
      if (password.length < 6) {
        setError("Password must be at least 6 characters.");
        return false;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match. Please verify.");
        return false;
      }
    } else {
      if (!password) {
        setError("Please enter your password.");
        return false;
      }
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isRegister) {
        await registerUser(username.trim(), email.trim(), password);
        setSuccessMsg("Account created! Signing you in...");
        const loginData = await loginUser(username.trim(), password);
        onAuthSuccess(loginData.user, loginData.dietary_profile);
      } else {
        const loginData = await loginUser(username.trim(), password);
        onAuthSuccess(loginData.user, loginData.dietary_profile);
      }
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.error || "Authentication failed. Please check your credentials.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card glass auth-card">
      <div className="auth-header">
        <div className="auth-logo-badge">
          <Icon name="shieldCheck" size={28} color="#059669" />
        </div>
        <h2>{isRegister ? "Create Your Free Account" : "Welcome Back"}</h2>
        <p className="auth-sub">
          {isRegister
            ? "Sign up to customize your personal dietary profile and save scan history."
            : "Sign in to access your allergen preferences and food scan history."}
        </p>
      </div>

      {/* Segmented Auth Mode Switcher */}
      <div className="auth-segmented-control">
        <button
          type="button"
          className={`auth-segment-btn ${!isRegister ? "active" : ""}`}
          onClick={() => { setIsRegister(false); setError(""); }}
        >
          Sign In
        </button>
        <button
          type="button"
          className={`auth-segment-btn ${isRegister ? "active" : ""}`}
          onClick={() => { setIsRegister(true); setError(""); }}
        >
          Create Account
        </button>
      </div>

      {error && (
        <div className="alert-banner alert-danger">
          <Icon name="alertCircle" size={18} />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="alert-banner alert-success">
          <Icon name="checkCircle" size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <div className="form-group">
          <label className="form-label" htmlFor="auth-username">
            {isRegister ? "Choose a Username" : "Username or Email"}
          </label>
          <div className="input-with-icon">
            <Icon name="user" size={18} className="input-leading-icon" />
            <input
              id="auth-username"
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={isRegister ? "e.g. food_care_user" : "Enter your username or email"}
              required
              autoComplete="username"
              disabled={loading}
            />
          </div>
        </div>

        {isRegister && (
          <div className="form-group">
            <label className="form-label" htmlFor="auth-email">
              Email Address
            </label>
            <div className="input-with-icon">
              <Icon name="fileText" size={18} className="input-leading-icon" />
              <input
                id="auth-email"
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                autoComplete="email"
                disabled={loading}
              />
            </div>
          </div>
        )}

        <div className="form-group">
          <div className="form-label-row">
            <label className="form-label" htmlFor="auth-password">
              Password {isRegister && <span className="helper-hint">(min. 6 characters)</span>}
            </label>
          </div>
          <div className="input-with-icon">
            <Icon name="shield" size={18} className="input-leading-icon" />
            <input
              id="auth-password"
              type={showPassword ? "text" : "password"}
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete={isRegister ? "new-password" : "current-password"}
              disabled={loading}
            />
            <button
              type="button"
              className="input-trailing-btn"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              <Icon name={showPassword ? "eyeOff" : "eye"} size={16} />
            </button>
          </div>
        </div>

        {isRegister && (
          <div className="form-group">
            <label className="form-label" htmlFor="auth-confirm-password">
              Confirm Password
            </label>
            <div className="input-with-icon">
              <Icon name="shield" size={18} className="input-leading-icon" />
              <input
                id="auth-confirm-password"
                type={showConfirmPassword ? "text" : "password"}
                className="form-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                required
                autoComplete="new-password"
                disabled={loading}
              />
              <button
                type="button"
                className="input-trailing-btn"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
              >
                <Icon name={showConfirmPassword ? "eyeOff" : "eye"} size={16} />
              </button>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary btn-large btn-block"
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="btn-spinner" />
              <span>{isRegister ? "Creating Account..." : "Signing In..."}</span>
            </>
          ) : (
            <>
              <span>{isRegister ? "Register & Continue" : "Sign In & Continue"}</span>
              <Icon name="arrowRight" size={18} />
            </>
          )}
        </button>
      </form>

      <div className="auth-footer-divider">
        <span>OR</span>
      </div>

      <button
        type="button"
        className="btn btn-ghost btn-block"
        onClick={onContinueAsGuest}
      >
        <span>Continue in Guest Mode (Quick Evaluation)</span>
        <Icon name="chevronRight" size={16} />
      </button>
    </div>
  );
}
