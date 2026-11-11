import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

function CameraScanner({ onCapture, onCameraError, loading }) {
  const webcamRef = useRef(null);
  const [localLoading, setLocalLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const handleUserMedia = (stream) => {
    try {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        const settings = typeof videoTrack.getSettings === "function" ? videoTrack.getSettings() : {};
        const actualWidth = settings.width;
        const actualHeight = settings.height;
        console.log(`Webcam started. Resolution: ${actualWidth}x${actualHeight}`);
        if (actualWidth && actualHeight && (actualWidth < 1280 || actualHeight < 720)) {
          console.warn(`Camera resolution is low: ${actualWidth}x${actualHeight}. This might affect OCR accuracy.`);
        }
      }
    } catch (err) {
      console.warn("Failed to retrieve actual camera stream specs:", err);
    }
  };

  const capture = async () => {
    if (!webcamRef.current || localLoading || loading) {
      return;
    }

    setLocalLoading(true);
    setStatusMessage("Focusing camera... Hold the ingredient label steady.");

    try {
      if (webcamRef.current.stream) {
        const videoTrack = webcamRef.current.stream.getVideoTracks()[0];
        if (videoTrack) {
          const capabilities = typeof videoTrack.getCapabilities === "function" ? videoTrack.getCapabilities() : {};
          if (capabilities.focusMode) {
            try {
              await videoTrack.applyConstraints({
                advanced: [{ focusMode: "continuous" }]
              });
            } catch (err) {
              console.warn("Autofocus setting not applied:", err);
            }
          }
        }
      }

      // Wait 1000ms for autofocus stabilization
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const imageSrc = webcamRef.current.getScreenshot();

      if (imageSrc) {
        setStatusMessage("Processing image and performing OCR...");
        await onCapture(imageSrc);
      } else {
        if (onCameraError) {
          onCameraError("Unable to capture image from camera stream. Please try again.");
        }
      }
    } catch (err) {
      console.error("Capture failure:", err);
      if (onCameraError) {
        onCameraError(`Failed to take screenshot: ${err.message || err}`);
      }
    } finally {
      setLocalLoading(false);
      setStatusMessage("");
    }
  };

  const isProcessing = localLoading || loading;

  return (
    <div className="card glass camera-scanner-container">
      <div className="card-header">
        <span className="card-icon">📷</span>
        <div>
          <h2>Camera Live OCR Scanner</h2>
          <p className="card-sub">Align ingredient list within the guide frame for automated extraction.</p>
        </div>
      </div>

      <div className="webcam-wrapper">
        <Webcam
          ref={webcamRef}
          audio={false}
          screenshotFormat="image/jpeg"
          screenshotQuality={0.95}
          onUserMedia={handleUserMedia}
          videoConstraints={{
            facingMode: "environment",
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          }}
          className="webcam-feed"
        />
        {/* Transparent guide frame */}
        <div className="camera-guide-box">
          <div className="camera-guide-text">Place Ingredient Label Inside This Box</div>
        </div>

        {/* Loading overlay */}
        {isProcessing && (
          <div className="camera-status-overlay">
            <div className="spinner"></div>
            <p className="camera-status-text">{statusMessage || "Scanning and assessing risk..."}</p>
          </div>
        )}
      </div>

      <button
        className={`btn btn-primary scan-btn ${isProcessing ? "disabled-btn" : ""}`}
        onClick={capture}
        disabled={isProcessing}
      >
        {isProcessing ? "⏳ Scan In Progress..." : "📸 Capture & Scan Label"}
      </button>

      {!isProcessing && (
        <div className="camera-guidance-tips">
          <div className="camera-guidance-title">💡 Scanning Tips</div>
          <ul className="camera-guidance-list">
            <li>📸 Hold camera steady</li>
            <li>🔍 Move closer if text is small</li>
            <li>✨ Avoid reflections & glare</li>
            <li>↔️ Keep ingredient text horizontal</li>
            <li>🔲 Fill most of the guide box</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default CameraScanner;
