import React, { useState } from "react";

// Client-side EAN-13 modulo-10 validation
const validateEan13 = (code) => {
  if (!code || typeof code !== "string") return false;
  const clean = code.trim();
  if (clean.length !== 13 || !/^\d+$/.test(clean)) return false;
  const digits = clean.split("").map(Number);
  let odd = 0;
  let even = 0;
  for (let i = 0; i < 12; i++) {
    if (i % 2 === 0) odd += digits[i];
    else even += digits[i];
  }
  const total = odd + even * 3;
  const check = (10 - (total % 10)) % 10;
  return check === digits[12];
};

const BENCHMARKS = [
  { ean: "8901234567890", label: "Sample Processed Food", tag: "INS 250 + High Sodium" },
  { ean: "8901030000003", label: "Classic Salty Chips", tag: "MSG (INS 621) + High Fat" },
  { ean: "5449000000996", label: "Sparkling Cola Soft Drink", tag: "Caramel IV (INS 150d) + Sugar" },
  { ean: "8901725132224", label: "Instant Masala Noodles", tag: "Multiple Additives + Sodium" }
];

function BarcodeScanner({ onAnalyze, loading }) {
  const [barcode, setBarcode] = useState("8901234567890");
  const isValid = validateEan13(barcode);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (barcode && barcode.trim()) {
      onAnalyze({ ean: barcode.trim() });
    }
  };

  const handleSelectSample = (sampleEan) => {
    setBarcode(sampleEan);
    onAnalyze({ ean: sampleEan });
  };

  return (
    <div className="card glass barcode-card">
      <div className="card-header">
        <span className="card-icon">🏷️</span>
        <div>
          <h2>EAN-13 Barcode Analysis</h2>
          <p className="card-sub">
            Query Open Food Facts database with automated EAN-13 checksum validation.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="barcode-form">
        <div className="input-group">
          <input
            type="text"
            className={`barcode-input ${barcode.length === 13 ? (isValid ? "valid" : "invalid") : ""}`}
            placeholder="Enter 13-digit EAN barcode (e.g. 8901234567890)"
            value={barcode}
            maxLength={13}
            onChange={(e) => setBarcode(e.target.value.replace(/\D/g, ""))}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !barcode.trim()}
          >
            {loading ? "Analyzing..." : "🔍 Analyze Barcode"}
          </button>
        </div>

        <div className="barcode-validation-indicator">
          {barcode.length === 13 ? (
            isValid ? (
              <span className="badge badge-valid">✓ Valid EAN-13 Checksum</span>
            ) : (
              <span className="badge badge-invalid">✗ Invalid Modulo-10 Check Digit</span>
            )
          ) : (
            <span className="helper-text">Length: {barcode.length}/13 digits</span>
          )}
        </div>
      </form>

      <div className="benchmark-section">
        <span className="benchmark-title">⚡ Quick Benchmark Products:</span>
        <div className="benchmark-chips">
          {BENCHMARKS.map((b) => (
            <button
              key={b.ean}
              type="button"
              className={`chip ${barcode === b.ean ? "active" : ""}`}
              onClick={() => handleSelectSample(b.ean)}
              disabled={loading}
            >
              <strong>{b.label}</strong>
              <span className="chip-tag">{b.tag}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default BarcodeScanner;
