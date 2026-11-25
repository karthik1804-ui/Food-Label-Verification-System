import React, { useState, useEffect } from "react";
import Tesseract from "tesseract.js";
import {
  analyzePayload,
  fetchCurrentUser,
  logoutUser,
  preprocessOcrImage
} from "./api";

// Clinical UI Components
import Icon from "./components/Icons";
import StepProgressBar from "./components/StepProgressBar";
import AuthCard from "./components/AuthCard";
import AllergySelectionView from "./components/AllergySelectionView";
import DietaryPreferencesView from "./components/DietaryPreferencesView";
import ProductScanningView from "./components/ProductScanningView";
import AnalysisResultsView from "./components/AnalysisResultsView";
import AnalysisHistoryView from "./components/AnalysisHistoryView";
import DashboardView from "./components/DashboardView";
import AuditQueueModal from "./components/AuditQueueModal";

import "./style.css";

// Compute mean word-level confidence from Tesseract result (0.0–1.0)
const computeOcrConfidence = (tesseractData) => {
  const words = tesseractData?.words || [];
  if (words.length === 0) return 1.0;
  const validWords = words.filter((w) => w.confidence > 0);
  if (validWords.length === 0) return 0.5;
  const mean = validWords.reduce((sum, w) => sum + w.confidence, 0) / validWords.length;
  return Math.round((mean / 100) * 1000) / 1000;
};

// Canvas preprocessing for OCR enhancement (client fallback)
const preprocessImageForOcr = (imageSrc, isUpload) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      let width = img.width;
      let height = img.height;

      if (isUpload && (width < 1500 || height < 1500)) {
        const target = 2000;
        if (width >= height) {
          height = Math.round(target * (height / width));
          width = target;
        } else {
          width = Math.round(target * (width / height));
          height = target;
        }
      }

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(imageSrc);

      ctx.drawImage(img, 0, 0, width, height);
      const imgData = ctx.getImageData(0, 0, width, height);
      const data = imgData.data;
      const orig = new Uint8ClampedArray(data);

      const contrast = 1.7;
      const brightness = 1.1;
      const centerWeight = isUpload ? 3.0 : 4.0;
      const neighborWeight = isUpload ? -0.5 : -0.75;

      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const idx = (y * width + x) * 4;
          const up = idx - width * 4;
          const down = idx + width * 4;
          const left = idx - 4;
          const right = idx + 4;

          for (let c = 0; c < 3; c++) {
            const sharp =
              centerWeight * orig[idx + c] +
              neighborWeight * (orig[up + c] + orig[down + c] + orig[left + c] + orig[right + c]);
            const val = (sharp * brightness - 127.5) * contrast + 127.5;
            data[idx + c] = val < 0 ? 0 : val > 255 ? 255 : val;
          }
        }
      }

      ctx.putImageData(imgData, 0, 0);
      resolve(canvas.toDataURL("image/jpeg", 0.95));
    };
    img.onerror = () => resolve(imageSrc);
    img.src = imageSrc;
  });
};

function App() {
  // Navigation & 5-Step Journey State
  // Views: 'dashboard' | 'flow' | 'history'
  // Steps: 1 = Account, 2 = Allergies, 3 = Preferences, 4 = Scan, 5 = Results
  const [currentView, setCurrentView] = useState("flow");
  const [currentStep, setCurrentStep] = useState(4);
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Authentication & Dietary Profile
  const [currentUser, setCurrentUser] = useState(null);
  const [dietaryProfile, setDietaryProfile] = useState(null);

  // Analysis State
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);

  // Auto-hydrate session from token on mount
  useEffect(() => {
    fetchCurrentUser()
      .then((data) => {
        if (data && data.user) {
          setCurrentUser(data.user);
          setDietaryProfile(data.dietary_profile);
          // Logged-in returning users land on Dashboard
          setCurrentView("dashboard");
        }
      })
      .catch(() => {
        // Guest mode - stays on scanner
      });
  }, []);

  // Handler: Run full backend verification payload
  const handleRunAnalysis = async (payload) => {
    setLoading(true);
    setErrorMessage("");
    try {
      const fullPayload = {
        ...payload,
        ...(dietaryProfile ? { dietary_profile: dietaryProfile } : {})
      };
      const data = await analyzePayload(fullPayload);
      setAnalysisResult(data);
      setCurrentView("flow");
      setCurrentStep(5); // Advance to Step 5: Personalised Results
    } catch (err) {
      console.error("Analysis failure:", err);
      const msg =
        err.response?.data?.message ||
        err.message ||
        "Analysis could not be completed. Please ensure the backend server is active.";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  // Handler: OCR processing for camera captures and uploaded images
  const handleOcrImage = async (imageSrc, isUpload = false, ocrConfig = "B") => {
    setLoading(true);
    setErrorMessage("");
    try {
      let ocrInput = imageSrc;
      let configUsed = ocrConfig;
      let preprocessingMetrics = null;

      if (ocrConfig === "B") {
        // Configuration B: Attempt OpenCV backend preprocessing (Laplacian blur + CLAHE + Sharpening)
        try {
          const prepRes = await preprocessOcrImage(imageSrc, "B", "best");
          if (prepRes && prepRes.enhanced_image_base64) {
            ocrInput = prepRes.enhanced_image_base64;
            configUsed = prepRes.configuration_used || "B";
            preprocessingMetrics = prepRes.quality_metrics || null;
          }
        } catch (prepErr) {
          console.warn("Backend OpenCV preprocessing bypassed, using client canvas fallback:", prepErr);
          ocrInput = await preprocessImageForOcr(imageSrc, isUpload);
          configUsed = "B (Client Fallback)";
        }
      } else {
        // Configuration A: Existing OCR directly on original image
        configUsed = "A (Original)";
      }

      // Perform OCR with Tesseract.js using standard configuration
      const worker = await Tesseract.createWorker("eng", 1);
      await worker.setParameters({
        tessedit_pageseg_mode: "6",
        preserve_interword_spaces: "1"
      });

      const res = await worker.recognize(ocrInput);
      await worker.terminate();

      const extracted = res.data.text;
      if (!extracted || !extracted.trim()) {
        setErrorMessage("No legible text could be recognized. Please ensure the packaging label is well-lit and in focus.");
        setLoading(false);
        return;
      }

      const ocrConfidence = computeOcrConfidence(res.data);

      await handleRunAnalysis({
        text: extracted,
        ocr_confidence: ocrConfidence,
        product: {
          name: isUpload ? "Uploaded Packaging Scan" : "Live Camera Capture",
          brand: "Scanned Label",
          category: "Physical Label OCR",
          ocr_pipeline_config: configUsed,
          preprocessing_metrics: preprocessingMetrics
        }
      });
    } catch (err) {
      console.error("OCR Pipeline error:", err);
      setErrorMessage(`OCR Processing Failed: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler: Barcode lookup analysis
  const handleBarcodeAnalyze = async (barcode) => {
    await handleRunAnalysis({ ean: barcode });
  };

  // Handler: Manual ingredient text analysis
  const handleManualTextAnalyze = async (text) => {
    await handleRunAnalysis({
      text,
      ocr_confidence: 1.0,
      product: {
        name: "Manual Ingredient Formulation",
        brand: "Direct Entry",
        category: "Direct Formulation Check"
      }
    });
  };

  // Handler: Sign out
  const handleSignOut = async () => {
    try {
      await logoutUser();
    } catch {
      // Ignored
    } finally {
      setCurrentUser(null);
      setDietaryProfile(null);
      setCurrentView("flow");
      setCurrentStep(1);
    }
  };

  const navigateToDashboard = () => {
    setCurrentView("dashboard");
    setMobileMenuOpen(false);
  };

  const navigateToScan = () => {
    setCurrentView("flow");
    setCurrentStep(4);
    setMobileMenuOpen(false);
  };

  const navigateToAllergies = () => {
    setCurrentView("flow");
    setCurrentStep(2);
    setMobileMenuOpen(false);
  };

  const navigateToPreferences = () => {
    setCurrentView("flow");
    setCurrentStep(3);
    setMobileMenuOpen(false);
  };

  const navigateToHistory = () => {
    setCurrentView("history");
    setMobileMenuOpen(false);
  };

  return (
    <div className="clinical-app-layout">
      {/* DESKTOP CLINICAL SIDEBAR */}
      <aside className={`clinical-sidebar ${mobileMenuOpen ? "mobile-open" : ""}`}>
        <div className="sidebar-brand-box">
          <div className="sidebar-logo-circle">
            <Icon name="shieldCheck" size={24} color="#00454A" />
          </div>
          <div className="sidebar-brand-text">
            <span className="brand-title">Food Label Verification</span>
            <span className="brand-subtitle">Health-Tech System</span>
          </div>
          <button
            type="button"
            className="mobile-close-sidebar-btn"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation"
          >
            <Icon name="x" size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className={`sidebar-nav-item ${currentView === "dashboard" ? "active" : ""}`}
            onClick={navigateToDashboard}
          >
            <Icon name="layoutDashboard" size={18} />
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${currentView === "flow" && currentStep === 3 ? "active" : ""}`}
            onClick={navigateToPreferences}
          >
            <Icon name="sliders" size={18} />
            <span>Dietary Preferences</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${currentView === "flow" && currentStep === 2 ? "active" : ""}`}
            onClick={navigateToAllergies}
          >
            <Icon name="shieldAlert" size={18} />
            <span>Food Allergies</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${currentView === "flow" && currentStep === 4 ? "active" : ""}`}
            onClick={navigateToScan}
          >
            <Icon name="camera" size={18} />
            <span>Scan Product</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${currentView === "history" ? "active" : ""}`}
            onClick={navigateToHistory}
          >
            <Icon name="history" size={18} />
            <span>Scan History</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() => {
              setShowAuditModal(true);
              setMobileMenuOpen(false);
            }}
          >
            <Icon name="clipboardList" size={18} />
            <span>HITL Audit</span>
          </button>
        </nav>

        {/* Sidebar Footer User Card */}
        <div className="sidebar-user-footer">
          {currentUser ? (
            <div className="sidebar-user-card">
              <div className="sidebar-avatar">
                <Icon name="user" size={16} color="#00454A" />
              </div>
              <div className="sidebar-user-info">
                <strong className="sidebar-user-name">{currentUser.username}</strong>
                <span className="sidebar-user-preset">
                  {dietaryProfile?.preset_name ? dietaryProfile.preset_name.replace("_", " ") : "Custom"}
                </span>
              </div>
              <button
                type="button"
                className="sidebar-logout-btn"
                onClick={handleSignOut}
                title="Sign out"
              >
                <Icon name="logOut" size={14} />
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="btn btn-outline btn-block btn-sm"
              onClick={() => {
                setCurrentView("flow");
                setCurrentStep(1);
                setMobileMenuOpen(false);
              }}
            >
              <Icon name="user" size={14} />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div className="clinical-main-wrapper">
        {/* Top Header Bar */}
        <header className="clinical-top-header">
          <div className="top-header-left">
            <button
              type="button"
              className="mobile-hamburger-btn"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
            >
              <Icon name="menu" size={22} />
            </button>
            <div className="header-status-indicator">
              <span className="status-dot online" />
              <span className="header-status-text">System Active</span>
            </div>
          </div>

          <div className="top-header-right">
            {currentUser ? (
              <div className="header-user-badge">
                <Icon name="shieldCheck" size={14} color="#00454A" />
                <span>{currentUser.username}</span>
                {dietaryProfile?.preset_name && (
                  <span className="header-preset-chip">
                    {dietaryProfile.preset_name.replace("_", " ")}
                  </span>
                )}
              </div>
            ) : (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => {
                  setCurrentView("flow");
                  setCurrentStep(1);
                }}
              >
                <Icon name="user" size={14} />
                <span>Sign In / Register</span>
              </button>
            )}
          </div>
        </header>

        {/* Global Error Alert Banner */}
        {errorMessage && (
          <div className="global-error-wrap">
            <div className="alert-banner alert-danger">
              <Icon name="alertTriangle" size={18} />
              <span style={{ flex: 1 }}>{errorMessage}</span>
              <button
                type="button"
                onClick={() => setErrorMessage("")}
                className="alert-dismiss-btn"
              >
                <Icon name="x" size={16} />
              </button>
            </div>
          </div>
        )}

        {/* 5-Step Workflow Progress Indicator */}
        {currentView === "flow" && (
          <StepProgressBar
            currentStep={currentStep}
            onSelectStep={(stepNum) => setCurrentStep(stepNum)}
            currentUser={currentUser}
          />
        )}

        {/* Dynamic Main Body Content */}
        <main className="clinical-main-body">
          {/* VIEW: DASHBOARD */}
          {currentView === "dashboard" && (
            <DashboardView
              currentUser={currentUser}
              dietaryProfile={dietaryProfile}
              onNavigateScan={navigateToScan}
              onNavigateAllergies={navigateToAllergies}
              onNavigatePreferences={navigateToPreferences}
              onNavigateHistory={navigateToHistory}
              onOpenAudit={() => setShowAuditModal(true)}
              onSelectScanRecord={(record) => {
                setAnalysisResult({
                  product: {
                    name: record.product_name,
                    brand: record.brand,
                    ean: record.ean,
                    category: record.category || "Past Scan Record"
                  },
                  personal_evaluation: {
                    personal_score: record.personal_score !== undefined ? record.personal_score : record.safety_score,
                    personal_verdict: record.personal_verdict || "Compatible",
                    allergen_alerts: record.allergen_alerts || [],
                    preference_conflicts: record.preference_conflicts || [],
                    caution_items: record.caution_items || [],
                    preset_name: record.preset_name || "custom"
                  },
                  safety_indicator: {
                    final_score: record.safety_score || record.personal_score || 95,
                    grade: record.grade || "A",
                    base_baseline_score: 100,
                    score_deductions: []
                  },
                  system_audit: record.system_audit || {
                    confidence: {
                      ocr_confidence: record.ocr_confidence || 1.0,
                      additive_match_confidence: 1.0,
                      barcode_decode_status: record.ean ? "valid_ean13" : "not_provided"
                    }
                  },
                  parsed_additives: record.parsed_additives || []
                });
                setCurrentView("flow");
                setCurrentStep(5);
              }}
            />
          )}

          {/* VIEW: SCAN HISTORY */}
          {currentView === "history" && (
            <AnalysisHistoryView
              onSelectScanRecord={(record) => {
                setAnalysisResult({
                  product: {
                    name: record.product_name,
                    brand: record.brand,
                    ean: record.ean,
                    category: record.category || "Past Scan Record"
                  },
                  personal_evaluation: {
                    personal_score: record.personal_score !== undefined ? record.personal_score : record.safety_score,
                    personal_verdict: record.personal_verdict || "Compatible",
                    allergen_alerts: record.allergen_alerts || [],
                    preference_conflicts: record.preference_conflicts || [],
                    caution_items: record.caution_items || [],
                    preset_name: record.preset_name || "custom"
                  },
                  safety_indicator: {
                    final_score: record.safety_score || record.personal_score || 95,
                    grade: record.grade || "A",
                    base_baseline_score: 100,
                    score_deductions: []
                  },
                  system_audit: record.system_audit || {
                    confidence: {
                      ocr_confidence: record.ocr_confidence || 1.0,
                      additive_match_confidence: 1.0,
                      barcode_decode_status: record.ean ? "valid_ean13" : "not_provided"
                    }
                  },
                  parsed_additives: record.parsed_additives || []
                });
                setCurrentView("flow");
                setCurrentStep(5);
              }}
              onBackToScan={navigateToScan}
              onBackToDashboard={navigateToDashboard}
            />
          )}

          {/* VIEW: 5-STEP JOURNEY FLOW */}
          {currentView === "flow" && (
            <>
              {/* STEP 1: ACCOUNT REGISTRATION / LOGIN */}
              {currentStep === 1 && (
                <AuthCard
                  currentUser={currentUser}
                  onAuthSuccess={(user, profile, isNewUser) => {
                    setCurrentUser(user);
                    setDietaryProfile(profile);
                    if (isNewUser) {
                      // New users proceed through onboarding: Step 2 Allergies
                      setCurrentStep(2);
                    } else {
                      // Returning users access dashboard
                      setCurrentView("dashboard");
                    }
                  }}
                  onContinueAsGuest={() => {
                    setCurrentStep(2);
                  }}
                  onSignOut={handleSignOut}
                />
              )}

              {/* STEP 2: FOOD ALLERGY SELECTION */}
              {currentStep === 2 && (
                <AllergySelectionView
                  currentProfile={dietaryProfile}
                  currentUser={currentUser}
                  onProfileUpdated={(updatedProfile) => {
                    setDietaryProfile(updatedProfile);
                  }}
                  onContinue={() => {
                    setCurrentStep(3);
                  }}
                  onBack={() => {
                    if (currentUser) {
                      setCurrentView("dashboard");
                    } else {
                      setCurrentStep(1);
                    }
                  }}
                />
              )}

              {/* STEP 3: DIETARY PREFERENCES & ADDITIVE AVOIDANCE */}
              {currentStep === 3 && (
                <DietaryPreferencesView
                  currentProfile={dietaryProfile}
                  currentUser={currentUser}
                  onProfileSaved={(prof) => {
                    setDietaryProfile(prof);
                  }}
                  onProceedToScan={() => {
                    setCurrentStep(4);
                  }}
                  onBackToAllergies={() => {
                    setCurrentStep(2);
                  }}
                />
              )}

              {/* STEP 4: SCAN FOOD INGREDIENTS & OPTIONAL BARCODE */}
              {currentStep === 4 && (
                <ProductScanningView
                  loading={loading}
                  dietaryProfile={dietaryProfile}
                  onAnalyzeOcr={handleOcrImage}
                  onAnalyzeBarcode={handleBarcodeAnalyze}
                  onAnalyzeManualText={handleManualTextAnalyze}
                />
              )}

              {/* STEP 5: PERSONALISED ANALYSIS RESULTS */}
              {currentStep === 5 && (
                <AnalysisResultsView
                  analysisResult={analysisResult}
                  dietaryProfile={dietaryProfile}
                  onScanAnother={() => {
                    setAnalysisResult(null);
                    setCurrentStep(4);
                  }}
                  onOpenPreferences={() => {
                    setCurrentStep(3);
                  }}
                  onBackToDashboard={navigateToDashboard}
                  onViewHistory={navigateToHistory}
                />
              )}
            </>
          )}
        </main>

        {/* Human-in-the-Loop Audit Queue Modal */}
        <AuditQueueModal
          isOpen={showAuditModal}
          onClose={() => setShowAuditModal(false)}
        />

        {/* Clean Application Footer */}
        <footer className="clinical-main-footer">
          <div className="footer-content">
            <span>&copy; {new Date().getFullYear()} Food Label Verification System</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
