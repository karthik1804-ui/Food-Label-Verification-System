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
      <div className="clinical-page-container">
        <div className="card clinical-auth-card user-logged-in-card">
          <div className="auth-avatar-circle">
            <Icon name="user" size={36} color="#00454A" />
          </div>
          <h2 className="user-signed-in-title">Signed in as {currentUser.username}</h2>
          <p className="user-signed-in-sub">
            {currentUser.email ? currentUser.email : "Active authenticated session"}
          </p>

          <div className="auth-actions-group">
            <button
              type="button"
              className="btn btn-primary btn-large"
              onClick={() => onContinueAsGuest ? onContinueAsGuest() : null}
            >
              <span>Proceed to Food Allergies</span>
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
      </div>
    );
  }

  const validateForm = () => {
    if (!username.trim()) {
      setError("Please enter a username or email identifier.");
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
        onAuthSuccess(loginData.user, loginData.dietary_profile, true); // new user flag
      } else {
        const loginData = await loginUser(username.trim(), password);
        onAuthSuccess(loginData.user, loginData.dietary_profile, false); // returning user flag
      }
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.error || "Authentication failed. Please check your credentials.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-layout">
      {/* LEFT SIDE: CLINICAL BRAND SHOWCASE */}
      <div className="auth-brand-side">
        <div className="brand-side-content">
          <div className="brand-badge-pill">
            <Icon name="shieldCheck" size={16} color="#D6FF65" />
            <span>Health-Tech Verification System</span>
          </div>

          <h1 className="brand-hero-title">
            Evidence-Based Food Label Verification
          </h1>

          <p className="brand-hero-desc">
            Empowering consumers, allergic individuals, and clinical dietitians with transparent ingredient analysis, Codex Alimentarius taxonomy mapping, and personalised safety scoring.
          </p>

          <div className="clinical-features-list">
            <div className="feature-item">
              <div className="feature-icon-circle">
                <Icon name="shieldAlert" size={18} color="#D6FF65" />
              </div>
              <div className="feature-text">
                <strong>Configurable Allergen Defense</strong>
                <span>Scans packaging formulations for the Top 11 major allergen families.</span>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon-circle">
                <Icon name="activity" size={18} color="#D6FF65" />
              </div>
              <div className="feature-text">
                <strong>Codex & FSSAI Additive Taxonomy</strong>
                <span>Instant classification across 750+ food additive codes and synonyms.</span>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-icon-circle">
                <Icon name="camera" size={18} color="#D6FF65" />
              </div>
              <div className="feature-text">
                <strong>OpenCV Enhanced Optical OCR</strong>
                <span>CLAHE contrast balancing and adaptive thresholding for packaging curves.</span>
              </div>
            </div>
          </div>

          <div className="clinical-trust-footer">
            <Icon name="shieldCheck" size={16} color="#D6FF65" />
            <span>Deterministic Rule-Based Intelligence • Zero Fabricated Claims</span>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE: AUTHENTICATION FORM */}
      <div className="auth-form-side">
        <div className="card clinical-auth-card">
          <div className="auth-card-top">
            <div className="auth-mini-icon">
              <Icon name="user" size={24} color="#00454A" />
            </div>
            <h2>{isRegister ? "Create Your Account" : "Sign In to Your Account"}</h2>
            <p className="auth-sub">
              {isRegister
                ? "Configure your personal food sensitivities and view previous scans."
                : "Enter your credentials to access your clinical dietary dashboard."}
            </p>
          </div>

          {/* Segmented Mode Switcher */}
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
              Register
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
                {isRegister ? "Username" : "Username or Email"}
              </label>
              <div className="input-with-icon">
                <Icon name="user" size={18} className="input-leading-icon" />
                <input
                  id="auth-username"
                  type="text"
                  className="form-input"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder={isRegister ? "e.g. food_care_user" : "Enter username or email"}
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
                    placeholder="you@domain.com"
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
                  Password {isRegister && <span className="helper-hint">(min. 6 chars)</span>}
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
                  <span>{isRegister ? "Create Account & Continue" : "Sign In & Access Dashboard"}</span>
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
            <span>Continue in Guest Mode (Quick Verification)</span>
            <Icon name="chevronRight" size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
