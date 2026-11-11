import React, { useRef } from "react";

function ImageUpload({ processImage, loading }) {
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      processImage(event.target.result, true);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="card glass upload-card">
      <div className="card-header">
        <span className="card-icon">📁</span>
        <div>
          <h2>Upload Ingredient Packaging Image</h2>
          <p className="card-sub">Drag and drop packaging image or browse files from device.</p>
        </div>
      </div>

      <div
        className="dropzone"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
      >
        <div className="dropzone-content">
          <span className="upload-icon">📤</span>
          <p>{loading ? "Processing image..." : "Drag & Drop or Click to Browse"}</p>
          <span className="file-hint">Supports PNG, JPG, JPEG with automated resolution upscaling</span>
        </div>
        <input
          type="file"
          ref={fileInputRef}
          className="hidden-file-input"
          accept="image/*"
          disabled={loading}
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              processFile(e.target.files[0]);
            }
          }}
        />
      </div>
    </div>
  );
}

export default ImageUpload;
