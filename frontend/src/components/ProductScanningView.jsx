import React, { useState, useRef } from "react";
import Webcam from "react-webcam";
import Icon from "./Icons";
import OcrComparisonModal from "./OcrComparisonModal";

// Modulo-10 checksum validation for standard EAN-13 codes
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

const SAMPLE_BENCHMARK_PRODUCTS = [
  { ean: "8901234567890", name: "Sample Processed Food", note: "INS 250 + High Sodium" },
  { ean: "8901030000003", name: "Classic Salty Chips", note: "MSG (INS 621) + Oil" },
  { ean: "5449000000996", name: "Sparkling Cola Drink", note: "Caramel IV (INS 150d)" },
  { ean: "8901725132224", name: "Instant Masala Noodles", note: "Multiple INS Additives" }
];

export default function ProductScanningView({
  onAnalyzeOcr,
  onAnalyzeBarcode,
  onAnalyzeManualText,
  loading,
  dietaryProfile
}) {
  const [activeScanMode, setActiveScanMode] = useState("camera"); // 'camera' | 'upload' | 'barcode' | 'text'

  // Camera state
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [cameraError, setCameraError] = useState("");

  // Upload state
  const fileInputRef = useRef(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [uploadError, setUploadError] = useState("");

  // Barcode state (Optional)
  const [barcodeInput, setBarcodeInput] = useState("");
  const [barcodeFeedback, setBarcodeFeedback] = useState("");

  // Manual formulation text state
  const [manualText, setManualText] = useState("");

  // Developer / Diagnostics Section (Kept separate from primary clinical UX)
  const [showDevDiagnostics, setShowDevDiagnostics] = useState(false);
  const [ocrConfig, setOcrConfig] = useState("B"); // 'B' (OpenCV Preprocessing) | 'A' (Standard Raw)
  const [showComparisonModal, setShowComparisonModal] = useState(false);

  // ---------- Camera Handlers ----------
  const handleCapture = () => {
    if (!webcamRef.current) return;
    try {
      const screenshot = webcamRef.current.getScreenshot();
      if (screenshot) {
        setCapturedImage(screenshot);
        setCameraError("");
      } else {
        setCameraError("Camera capture returned empty frame. Please ensure camera permissions are granted.");
      }
    } catch (err) {
      setCameraError("Camera error: " + (err.message || err));
    }
  };

  const handleRetakeCamera = () => {
    setCapturedImage(null);
    setCameraError("");
  };

  // ---------- Upload Handlers ----------
  const handleFileProcess = (file) => {
    setUploadError("");
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setUploadError("Please upload a valid packaging image (PNG, JPEG, WEBP).");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setUploadError("Image exceeds 15MB limit. Please choose a smaller image.");
      return;
    }

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target.result);
    };
    reader.onerror = () => {
      setUploadError("Failed to read image file. Please try again.");
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveUploaded = () => {
    setUploadedImage(null);
    setUploadedFileName("");
    setUploadError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ---------- Barcode Handlers ----------
  const handleBarcodeChange = (val) => {
    setBarcodeInput(val);
    const clean = val.trim();
    if (!clean) {
      setBarcodeFeedback("");
    } else if (clean.length === 13) {
      if (validateEan13(clean)) {
        setBarcodeFeedback("✓ Valid EAN-13 barcode format");
      } else {
        setBarcodeFeedback("⚠️ Invalid EAN-13 checksum");
      }
    } else {
      setBarcodeFeedback(`${clean.length}/13 digits`);
    }
  };

  // ---------- Primary Submission Handlers ----------
  const handleAnalyzeActiveScan = () => {
    if (loading) return;

    if (activeScanMode === "camera") {
      if (!capturedImage) {
        setCameraError("Please capture an ingredient label image first.");
        return;
      }
      onAnalyzeOcr(capturedImage, false, ocrConfig);
    } else if (activeScanMode === "upload") {
      if (!uploadedImage) {
        setUploadError("Please upload an ingredient label image first.");
        return;
      }
      onAnalyzeOcr(uploadedImage, true, ocrConfig);
    } else if (activeScanMode === "barcode") {
      const clean = barcodeInput.trim();
      if (!clean) {
        setBarcodeFeedback("Please enter an EAN-13 barcode number.");
        return;
      }
      onAnalyzeBarcode(clean);
    } else if (activeScanMode === "text") {
      if (!manualText.trim()) return;
      onAnalyzeManualText(manualText);
    }
  };

  const activeImage =
    activeScanMode === "camera"
      ? capturedImage
      : activeScanMode === "upload"
      ? uploadedImage
      : null;

  return (
    <div className="clinical-page-container">
      {/* Page Header */}
      <div className="clinical-page-header">
        <h1 className="clinical-title">Scan Your Food Product</h1>
        <p className="clinical-description">
          Capture or upload the ingredients label to analyse your product.
        </p>
      </div>

      {/* Mode Selection Tabs */}
      <div className="clinical-scan-modes-tabs">
        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "camera" ? "active" : ""}`}
          onClick={() => setActiveScanMode("camera")}
        >
          <Icon name="camera" size={18} />
          <span>Take Photo</span>
        </button>

        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "upload" ? "active" : ""}`}
          onClick={() => setActiveScanMode("upload")}
        >
          <Icon name="upload" size={18} />
          <span>Upload Image</span>
        </button>

        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "barcode" ? "active" : ""}`}
          onClick={() => setActiveScanMode("barcode")}
        >
          <Icon name="barcode" size={18} />
          <span>Scan Barcode (Optional)</span>
        </button>

        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "text" ? "active" : ""}`}
          onClick={() => setActiveScanMode("text")}
        >
          <Icon name="fileText" size={18} />
          <span>Enter Ingredient Text</span>
        </button>
      </div>

      {/* ACTIVE MODE 1: CAMERA SCANNER */}
      {activeScanMode === "camera" && (
        <div className="card clinical-scan-card">
          <div className="camera-viewfinder-wrap">
            {!capturedImage ? (
              <>
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  className="camera-video-feed"
                  videoConstraints={{
                    facingMode: "environment",
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                  }}
                  onUserMediaError={(err) => {
                    setCameraError("Camera access denied or unavailable: " + (err.message || err));
                  }}
                />
                <div className="camera-target-crosshairs">
                  <div className="crosshair-bracket top-left" />
                  <div className="crosshair-bracket top-right" />
                  <div className="crosshair-bracket bottom-left" />
                  <div className="crosshair-bracket bottom-right" />
                  <div className="crosshair-prompt-pill">
                    <Icon name="camera" size={14} color="#ffffff" />
                    <span>Align ingredient label inside frame</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="captured-preview-container">
                <img src={capturedImage} alt="Captured food label" className="captured-preview-img" />
                <div className="preview-overlay-badge">
                  <Icon name="checkCircle" size={16} color="#16A34A" />
                  <span>Packaging Image Captured</span>
                </div>
              </div>
            )}
          </div>

          {cameraError && (
            <div className="alert-banner alert-danger" style={{ marginTop: "1rem" }}>
              <Icon name="alertTriangle" size={18} />
              <span>{cameraError}</span>
            </div>
          )}

          <div className="scan-controls-bar">
            {!capturedImage ? (
              <button
                type="button"
                className="btn btn-primary btn-large btn-capture"
                onClick={handleCapture}
                disabled={loading}
              >
                <Icon name="camera" size={20} />
                <span>Capture Packaging Photo</span>
              </button>
            ) : (
              <div className="captured-actions-row">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={handleRetakeCamera}
                  disabled={loading}
                >
                  <Icon name="refreshCw" size={16} />
                  <span>Retake Photo</span>
                </button>

                <button
                  type="button"
                  className="btn btn-primary btn-large"
                  onClick={handleAnalyzeActiveScan}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="btn-spinner" />
                      <span>Analysing Packaging...</span>
                    </>
                  ) : (
                    <>
                      <Icon name="activity" size={18} />
                      <span>Analyse Ingredients</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ACTIVE MODE 2: IMAGE UPLOAD */}
      {activeScanMode === "upload" && (
        <div className="card clinical-scan-card">
          {!uploadedImage ? (
            <div
              className="clinical-dropzone"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e) => handleFileProcess(e.target.files[0])}
              />
              <div className="dropzone-icon-circle">
                <Icon name="upload" size={32} color="#00454A" />
              </div>
              <h3 className="dropzone-title">Upload Ingredient Packaging Photo</h3>
              <p className="dropzone-sub">
                Drag and drop your label photograph here, or <span className="dropzone-link">browse files</span>
              </p>
              <span className="dropzone-spec">Supports JPG, PNG, WEBP up to 15MB</span>
            </div>
          ) : (
            <div className="uploaded-preview-wrap">
              <div className="uploaded-preview-header">
                <div className="uploaded-file-meta">
                  <Icon name="fileText" size={18} color="#00454A" />
                  <span className="file-name-text">{uploadedFileName || "Uploaded Packaging Label"}</span>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm text-danger"
                  onClick={handleRemoveUploaded}
                  disabled={loading}
                >
                  <Icon name="trash2" size={15} />
                  <span>Remove</span>
                </button>
              </div>

              <div className="uploaded-image-preview-box">
                <img src={uploadedImage} alt="Uploaded packaging label" className="uploaded-image-preview" />
              </div>

              <div className="uploaded-actions-bar">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  disabled={loading}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    style={{ display: "none" }}
                    onChange={(e) => handleFileProcess(e.target.files[0])}
                  />
                  <Icon name="refreshCw" size={16} />
                  <span>Replace Image</span>
                </button>

                <button
                  type="button"
                  className="btn btn-primary btn-large"
                  onClick={handleAnalyzeActiveScan}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="btn-spinner" />
                      <span>Processing Label...</span>
                    </>
                  ) : (
                    <>
                      <Icon name="activity" size={18} />
                      <span>Analyse Uploaded Image</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="alert-banner alert-danger" style={{ marginTop: "1rem" }}>
              <Icon name="alertTriangle" size={18} />
              <span>{uploadError}</span>
            </div>
          )}
        </div>
      )}

      {/* ACTIVE MODE 3: BARCODE SCANNER (OPTIONAL) */}
      {activeScanMode === "barcode" && (
        <div className="card clinical-scan-card">
          <div className="barcode-input-container">
            <div className="barcode-header-group">
              <div className="header-icon-box">
                <Icon name="barcode" size={24} color="#00454A" />
              </div>
              <div>
                <h3 className="barcode-title">Search by Product EAN-13 Barcode</h3>
                <p className="barcode-sub">
                  Retrieve verified ingredient schedules from Open Food Facts or benchmark catalogs.
                </p>
              </div>
            </div>

            <div className="form-group" style={{ marginTop: "1.25rem" }}>
              <label className="form-label" htmlFor="barcode-field">
                EAN-13 Barcode (13 digits):
              </label>
              <div className="input-with-icon">
                <Icon name="barcode" size={20} className="input-leading-icon" />
                <input
                  id="barcode-field"
                  type="text"
                  className="form-input barcode-input"
                  value={barcodeInput}
                  onChange={(e) => handleBarcodeChange(e.target.value)}
                  placeholder="e.g. 8901234567890"
                  maxLength={13}
                  disabled={loading}
                />
              </div>
              {barcodeFeedback && (
                <span className={`barcode-hint ${barcodeFeedback.includes("✓") ? "valid" : "neutral"}`}>
                  {barcodeFeedback}
                </span>
              )}
            </div>

            <div className="barcode-sample-chips">
              <span className="sample-label">Benchmark Test Products:</span>
              <div className="chips-row">
                {SAMPLE_BENCHMARK_PRODUCTS.map((prod) => (
                  <button
                    key={prod.ean}
                    type="button"
                    className="sample-chip-btn"
                    onClick={() => handleBarcodeChange(prod.ean)}
                  >
                    <span>{prod.name}</span>
                    <span className="chip-code">({prod.ean})</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="scan-controls-bar" style={{ marginTop: "1.5rem" }}>
              <button
                type="button"
                className="btn btn-primary btn-large btn-block"
                onClick={handleAnalyzeActiveScan}
                disabled={loading || !barcodeInput.trim()}
              >
                {loading ? (
                  <>
                    <div className="btn-spinner" />
                    <span>Searching Product Catalog...</span>
                  </>
                ) : (
                  <>
                    <Icon name="search" size={18} />
                    <span>Lookup & Verify Barcode</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ACTIVE MODE 4: MANUAL INGREDIENT TEXT */}
      {activeScanMode === "text" && (
        <div className="card clinical-scan-card">
          <div className="manual-text-container">
            <label className="form-label" htmlFor="manual-text-area">
              Paste Packaging Ingredient Declaration:
            </label>
            <textarea
              id="manual-text-area"
              rows={5}
              className="form-textarea"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder="e.g. Ingredients: Refined Wheat Flour, Sugar, Palm Oil, Acidity Regulators (INS 330, INS 331), Preservative (INS 211), Synthetic Food Colour (INS 102). CONTAINS WHEAT."
              disabled={loading}
            />

            <div className="scan-controls-bar" style={{ marginTop: "1.25rem" }}>
              <button
                type="button"
                className="btn btn-primary btn-large btn-block"
                onClick={handleAnalyzeActiveScan}
                disabled={loading || !manualText.trim()}
              >
                {loading ? (
                  <>
                    <div className="btn-spinner" />
                    <span>Parsing Formulation...</span>
                  </>
                ) : (
                  <>
                    <Icon name="activity" size={18} />
                    <span>Analyse Ingredient Text</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ADVANCED / DEVELOPER OCR SETTINGS (DISCRETE COLLAPSIBLE) */}
      <div style={{ marginTop: "1.5rem", textAlign: "center" }}>
        <button
          type="button"
          className="btn btn-ghost btn-xs text-muted"
          onClick={() => setShowDevDiagnostics(!showDevDiagnostics)}
          aria-expanded={showDevDiagnostics}
          style={{ fontSize: "0.75rem" }}
        >
          <Icon name="sliders" size={13} />
          <span>{showDevDiagnostics ? "Hide Advanced OCR Settings" : "Advanced OCR Settings"}</span>
          <Icon name={showDevDiagnostics ? "chevronUp" : "chevronDown"} size={13} />
        </button>

        {showDevDiagnostics && (
          <div className="card clinical-diagnostics-card" style={{ marginTop: "0.75rem", textAlign: "left" }}>
            <div className="diagnostics-body" style={{ padding: "1rem" }}>
              <div className="diagnostics-actions-row">
                <div className="diagnostics-config-picker">
                  <span className="config-label">Active OCR Pipeline:</span>
                  <div className="config-segmented">
                    <button
                      type="button"
                      className={`config-pill ${ocrConfig === "B" ? "active" : ""}`}
                      onClick={() => setOcrConfig("B")}
                    >
                      Configuration B (OpenCV + Tesseract)
                    </button>
                    <button
                      type="button"
                      className={`config-pill ${ocrConfig === "A" ? "active" : ""}`}
                      onClick={() => setOcrConfig("A")}
                    >
                      Configuration A (Raw Tesseract)
                    </button>
                  </div>
                </div>

                {activeImage && (
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    onClick={() => setShowComparisonModal(true)}
                  >
                    <Icon name="activity" size={14} />
                    <span>Side-by-Side OCR Comparison</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Side-by-Side OCR Comparison Modal */}
      {showComparisonModal && (
        <OcrComparisonModal
          isOpen={showComparisonModal}
          onClose={() => setShowComparisonModal(false)}
          activeImage={activeImage}
        />
      )}
    </div>
  );
}
