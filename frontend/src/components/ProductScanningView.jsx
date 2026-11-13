import React, { useState, useRef } from "react";
import Webcam from "react-webcam";
import Icon from "./Icons";

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

const PRESET_FORMULATIONS = [
  {
    name: "Instant Noodles",
    tag: "MSG + Thickeners + Caramel IV",
    text: "Ingredients: Refined Wheat Flour (Maida), Palm Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Thickeners (INS 508, INS 412), Acidity Regulators (INS 501(i), INS 500(i), INS 451(i)). Noodle Tastemaker: Hydrolysed Peanut Protein, Mixed Spices (15.5%) (Onion Powder, Coriander Powder, Chilli Powder, Turmeric Powder, Garlic Powder), Flavour Enhancer (INS 635, INS 621), Thickener (INS 508), Salt, Acidity Regulator (INS 330), Caramel Colour (INS 150d). CONTAINS WHEAT, PEANUT AND GLUTEN."
  },
  {
    name: "Sparkling Orange Drink",
    tag: "Synthetic Colours + Preservatives",
    text: "Ingredients: Carbonated Water, Sugar, Acidity Regulators (INS 330, INS 331), Preservative (INS 211), Synthetic Food Colour (INS 102, INS 110), Added Nature Identical Flavouring Substances (Orange). Contains Permitted Synthetic Food Colours."
  },
  {
    name: "Clean Fruit & Nut Bar",
    tag: "All-Natural • Zero Additives",
    text: "Ingredients: Rolled Oats, Raw Honey, Almonds, Pumpkin Seeds, Sunflower Seeds, Virgin Coconut Oil, Cinnamon Powder, Sea Salt. CONTAINS TREE NUTS (ALMONDS)."
  }
];

export default function ProductScanningView({
  onAnalyzeOcr,
  onAnalyzeBarcode,
  onAnalyzeManualText,
  loading,
  dietaryProfile
}) {
  const [activeScanMode, setActiveScanMode] = useState("camera"); // 'camera' | 'upload' | 'text'

  // Camera state
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [cameraError, setCameraError] = useState("");

  // Upload state
  const fileInputRef = useRef(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [uploadError, setUploadError] = useState("");

  // Text state
  const [manualText, setManualText] = useState("");

  // Optional Barcode state
  const [barcodeInput, setBarcodeInput] = useState("");
  const [barcodeFeedback, setBarcodeFeedback] = useState("");
  const [showBarcodeSection, setShowBarcodeSection] = useState(false);

  // ---------- Camera Handlers ----------
  const handleCapture = () => {
    if (!webcamRef.current) return;
    try {
      const screenshot = webcamRef.current.getScreenshot();
      if (screenshot) {
        setCapturedImage(screenshot);
        setCameraError("");
      } else {
        setCameraError("Camera capture returned empty frame. Please allow camera permissions.");
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
      setUploadError("Please select a valid image file (JPEG, PNG, WebP).");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setUploadError("File size exceeds 15 MB limit. Please use a smaller photo.");
      return;
    }

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target.result);
    };
    reader.onerror = () => {
      setUploadError("Failed to read selected image file.");
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleRemoveUploadedImage = () => {
    setUploadedImage(null);
    setUploadedFileName("");
    setUploadError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ---------- Barcode Handlers ----------
  const handleBarcodeChange = (val) => {
    const clean = val.replace(/\D/g, "");
    setBarcodeInput(clean);
    if (clean.length === 13) {
      const valid = validateEan13(clean);
      setBarcodeFeedback(valid ? "✓ Valid EAN-13 Checksum" : "⚠️ Invalid Modulo-10 Checksum Digit");
    } else if (clean.length > 0) {
      setBarcodeFeedback(`EAN-13 length: ${clean.length} / 13 digits`);
    } else {
      setBarcodeFeedback("");
    }
  };

  const handleBarcodeSubmit = (e) => {
    if (e) e.preventDefault();
    if (!barcodeInput.trim()) return;
    onAnalyzeBarcode(barcodeInput.trim());
  };

  const handleSelectBenchmark = (sampleEan) => {
    setBarcodeInput(sampleEan);
    setBarcodeFeedback("✓ Valid Benchmark EAN-13");
    onAnalyzeBarcode(sampleEan);
  };

  // ---------- Primary Analyze Action ----------
  const handleTriggerAnalysis = () => {
    if (activeScanMode === "camera") {
      if (capturedImage) {
        onAnalyzeOcr(capturedImage, false);
      } else {
        // Snap immediately and analyze
        if (webcamRef.current) {
          const shot = webcamRef.current.getScreenshot();
          if (shot) {
            onAnalyzeOcr(shot, false);
          } else {
            setCameraError("Please capture an image of the ingredient label first.");
          }
        }
      }
    } else if (activeScanMode === "upload") {
      if (!uploadedImage) {
        setUploadError("Please select or drop an image of the food label first.");
        return;
      }
      onAnalyzeOcr(uploadedImage, true);
    } else if (activeScanMode === "text") {
      if (!manualText.trim()) return;
      onAnalyzeManualText(manualText.trim());
    }
  };

  return (
    <div className="product-scanning-container">
      {/* Step Header */}
      <div className="section-intro-header">
        <div className="section-badge">
          <Icon name="camera" size={16} />
          <span>Step 3 of 4</span>
        </div>
        <h2>Scan Food Packaging or Ingredients</h2>
        <p>
          Capture or upload the physical ingredients declaration on the packaging for OCR analysis. Barcode scanning is completely optional.
        </p>
      </div>

      {/* Main Scan Mode Tabs */}
      <div className="scan-mode-tabs-container">
        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "camera" ? "active" : ""}`}
          onClick={() => setActiveScanMode("camera")}
        >
          <Icon name="camera" size={20} />
          <div className="tab-label-group">
            <span className="tab-title">Take a Photo</span>
            <span className="tab-sub">Live camera capture</span>
          </div>
        </button>

        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "upload" ? "active" : ""}`}
          onClick={() => setActiveScanMode("upload")}
        >
          <Icon name="upload" size={20} />
          <div className="tab-label-group">
            <span className="tab-title">Upload Packaging Image</span>
            <span className="tab-sub">Browse from device</span>
          </div>
        </button>

        <button
          type="button"
          className={`scan-mode-tab ${activeScanMode === "text" ? "active" : ""}`}
          onClick={() => setActiveScanMode("text")}
        >
          <Icon name="fileText" size={20} />
          <div className="tab-label-group">
            <span className="tab-title">Ingredient Text</span>
            <span className="tab-sub">Paste or test formulation</span>
          </div>
        </button>
      </div>

      {/* Primary Scanning Panel */}
      <div className="card glass scanning-main-panel">
        {/* MODE A: LIVE CAMERA */}
        {activeScanMode === "camera" && (
          <div className="camera-scan-layout">
            {cameraError && (
              <div className="alert-banner alert-warning" style={{ marginBottom: "1rem" }}>
                <Icon name="alertTriangle" size={18} />
                <span>{cameraError}</span>
              </div>
            )}

            {!capturedImage ? (
              <div className="webcam-viewport">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  screenshotQuality={0.95}
                  videoConstraints={{
                    facingMode: "environment",
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                  }}
                  className="webcam-feed-element"
                  onUserMediaError={(err) => setCameraError("Camera access denied or device not found: " + (err.message || err))}
                />

                {/* Consumer-friendly viewfinder overlay */}
                <div className="camera-viewfinder-overlay">
                  <div className="viewfinder-frame">
                    <span className="corner corner-tl" />
                    <span className="corner corner-tr" />
                    <span className="corner corner-bl" />
                    <span className="corner corner-br" />
                    <div className="viewfinder-hint">Align Ingredient List Inside Box</div>
                  </div>
                </div>

                <div className="camera-controls-bar">
                  <button
                    type="button"
                    className="btn btn-primary btn-large camera-capture-btn"
                    onClick={handleCapture}
                    disabled={loading}
                  >
                    <Icon name="camera" size={20} />
                    <span>Take Photo</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="captured-preview-container">
                <div className="preview-image-wrapper">
                  <img src={capturedImage} alt="Captured food label" className="captured-preview-img" />
                  <div className="preview-badge-status">
                    <Icon name="checkCircle" size={16} />
                    <span>Photo Ready for Analysis</span>
                  </div>
                </div>

                <div className="preview-action-buttons">
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
                    onClick={handleTriggerAnalysis}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="btn-spinner" />
                        <span>Analysing Label...</span>
                      </>
                    ) : (
                      <>
                        <span>Analyse Captured Label</span>
                        <Icon name="arrowRight" size={18} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            <div className="scanning-tips-bar">
              <div className="tip-item">💡 Hold camera steady with adequate lighting</div>
              <div className="tip-item">🔍 Ensure ingredient text is sharp and legible</div>
              <div className="tip-item">↔️ Keep text orientation horizontal</div>
            </div>
          </div>
        )}

        {/* MODE B: UPLOAD IMAGE */}
        {activeScanMode === "upload" && (
          <div className="upload-scan-layout">
            {uploadError && (
              <div className="alert-banner alert-warning" style={{ marginBottom: "1rem" }}>
                <Icon name="alertTriangle" size={18} />
                <span>{uploadError}</span>
              </div>
            )}

            {!uploadedImage ? (
              <div
                className="dropzone-area"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
              >
                <div className="dropzone-inner">
                  <div className="dropzone-icon-circle">
                    <Icon name="upload" size={32} color="#059669" />
                  </div>
                  <h3>Drag & drop food packaging photo here</h3>
                  <p>Or click to browse from your computer or phone</p>
                  <span className="dropzone-support-text">
                    Supports PNG, JPG, JPEG, WebP (high resolution recommended)
                  </span>
                </div>
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden-file-input"
                  accept="image/png, image/jpeg, image/jpg, image/webp"
                  disabled={loading}
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileProcess(e.target.files[0]);
                    }
                  }}
                />
              </div>
            ) : (
              <div className="uploaded-preview-container">
                <div className="uploaded-file-banner">
                  <div className="file-info-left">
                    <Icon name="fileText" size={20} color="#059669" />
                    <div>
                      <span className="file-name">{uploadedFileName || "Selected Packaging Image"}</span>
                      <span className="file-ready-tag">Ready for OCR Extraction</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={handleRemoveUploadedImage}
                    title="Remove or replace image"
                  >
                    <Icon name="x" size={16} />
                    <span>Replace Image</span>
                  </button>
                </div>

                <div className="uploaded-img-view">
                  <img src={uploadedImage} alt="Uploaded packaging label" className="uploaded-preview-img" />
                </div>

                <div className="preview-action-buttons">
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={handleRemoveUploadedImage}
                    disabled={loading}
                  >
                    <Icon name="trash2" size={16} />
                    <span>Remove</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-primary btn-large"
                    onClick={handleTriggerAnalysis}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="btn-spinner" />
                        <span>Analysing Label...</span>
                      </>
                    ) : (
                      <>
                        <span>Analyse Product</span>
                        <Icon name="arrowRight" size={18} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MODE C: MANUAL INGREDIENT TEXT */}
        {activeScanMode === "text" && (
          <div className="manual-text-scan-layout">
            <div className="manual-text-header">
              <label className="form-label" htmlFor="manual-text-input">
                Ingredient Declaration Text
              </label>
              <span className="helper-hint">
                Paste ingredient text directly from an e-commerce or label declaration:
              </span>
            </div>

            {/* Quick Formulation Presets */}
            <div className="sample-presets-chips">
              <span className="presets-label">⚡ Quick Samples:</span>
              {PRESET_FORMULATIONS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`chip-btn ${manualText === p.text ? "active" : ""}`}
                  onClick={() => setManualText(p.text)}
                  disabled={loading}
                >
                  <strong>{p.name}</strong>
                  <span className="chip-desc">{p.tag}</span>
                </button>
              ))}
            </div>

            <textarea
              id="manual-text-input"
              className="form-textarea"
              rows={5}
              placeholder="e.g. Ingredients: Water, Sugar, Acidity Regulators (INS 330, INS 331), Preservative (INS 211), Synthetic Food Colour (INS 102). CONTAINS PERMITTED FLAVOURS."
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              disabled={loading}
            />

            <div className="textarea-footer-row">
              <span className="char-count">
                {manualText.length} characters • {manualText.trim() ? manualText.trim().split(/\s+/).length : 0} words
              </span>
              {manualText && (
                <button
                  type="button"
                  className="btn-text-danger"
                  onClick={() => setManualText("")}
                >
                  Clear text
                </button>
              )}
            </div>

            <div className="preview-action-buttons" style={{ marginTop: "1rem" }}>
              <button
                type="button"
                className="btn btn-primary btn-large btn-block"
                onClick={handleTriggerAnalysis}
                disabled={loading || !manualText.trim()}
              >
                {loading ? (
                  <>
                    <div className="btn-spinner" />
                    <span>Analysing Formulation...</span>
                  </>
                ) : (
                  <>
                    <span>Analyse Product</span>
                    <Icon name="arrowRight" size={18} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* SEPARATE, VISUALLY DISTINCT OPTIONAL BARCODE SECTION */}
      <div className="optional-barcode-container card glass">
        <div
          className="optional-barcode-header"
          onClick={() => setShowBarcodeSection(!showBarcodeSection)}
          style={{ cursor: "pointer" }}
        >
          <div className="barcode-header-left">
            <div className="barcode-icon-circle">
              <Icon name="barcode" size={20} color="#2563eb" />
            </div>
            <div>
              <div className="barcode-title-row">
                <h3>Have a Product Barcode? (Optional)</h3>
                <span className="badge-optional">Optional Step</span>
              </div>
              <p className="barcode-desc">
                Scanning the barcode retrieves catalog information from Open Food Facts. Physical label scanning is the primary source of truth.
              </p>
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-sm" aria-label="Toggle barcode section">
            <Icon name={showBarcodeSection ? "chevronUp" : "chevronDown"} size={20} />
          </button>
        </div>

        {showBarcodeSection && (
          <div className="optional-barcode-body">
            <form onSubmit={handleBarcodeSubmit} className="barcode-entry-form">
              <div className="barcode-input-group">
                <div className="input-with-icon" style={{ flex: 1 }}>
                  <Icon name="barcode" size={18} className="input-leading-icon" />
                  <input
                    type="text"
                    className="form-input"
                    value={barcodeInput}
                    onChange={(e) => handleBarcodeChange(e.target.value)}
                    placeholder="Enter 13-digit EAN barcode (e.g. 8901234567890)"
                    maxLength={13}
                    disabled={loading}
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn-outline"
                  disabled={loading || !barcodeInput.trim()}
                >
                  <Icon name="search" size={16} />
                  <span>Lookup Barcode</span>
                </button>
              </div>

              {barcodeFeedback && (
                <div className={`barcode-feedback-tag ${barcodeFeedback.includes("Valid") ? "valid" : "warning"}`}>
                  {barcodeFeedback}
                </div>
              )}
            </form>

            <div className="barcode-benchmarks">
              <span className="benchmarks-title">Or test with catalog benchmarks:</span>
              <div className="benchmark-pills-row">
                {SAMPLE_BENCHMARK_PRODUCTS.map((prod) => (
                  <button
                    key={prod.ean}
                    type="button"
                    className="benchmark-pill"
                    onClick={() => handleSelectBenchmark(prod.ean)}
                    disabled={loading}
                  >
                    <span className="pill-name">{prod.name}</span>
                    <span className="pill-code">{prod.ean}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="analysis-progress-overlay">
          <div className="progress-modal-card card glass">
            <div className="progress-spinner-ring" />
            <h3>Evaluating Food Formulation</h3>
            <p>
              Applying computer vision OCR preprocessing, matching additives against verified INS taxonomy, and assessing dietary suitability...
            </p>
            <div className="progress-micro-indicators">
              <span>✓ Multimodal OCR</span>
              <span>•</span>
              <span>✓ 750+ INS Taxonomy</span>
              <span>•</span>
              <span>✓ Allergen Gate</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
