import axios from "axios";

const BASE_URL_LOCAL = "http://localhost:5005";
const BASE_URL_IP    = "http://127.0.0.1:5005";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || BASE_URL_LOCAL,
  headers: { "Content-Type": "application/json" },
  timeout: 10000
});

// Auto-retry on network failure: localhost → 127.0.0.1
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    if (!config || config._retry) return Promise.reject(error);
    if (error.code === "ERR_NETWORK" || !error.response) {
      config._retry = true;
      config.baseURL = config.baseURL.includes("localhost")
        ? BASE_URL_IP : BASE_URL_LOCAL;
      console.warn(`Backend retry: ${config.baseURL}`);
      return API(config);
    }
    return Promise.reject(error);
  }
);

// -------------------------------------------------------------------------
// Core analysis endpoints
// -------------------------------------------------------------------------

/** Full analysis: accepts { ean, text, ocr_confidence, nutrients, product } */
export const analyzePayload = async (payload) => {
  const response = await API.post("/api/v1/analyze", payload);
  return response.data;
};

/** Barcode-only shortcut */
export const analyzeBarcode = async (ean) => {
  const response = await API.post("/api/v1/analyze", { ean });
  return response.data;
};

/**
 * OCR text analysis — forwards Tesseract confidence to backend.
 * @param {string} text         - Extracted ingredient text
 * @param {number} ocrConfidence - Mean Tesseract word confidence (0.0–1.0)
 * @param {object} product       - Optional product metadata override
 */
export const analyzeOcrText = async (text, ocrConfidence = 1.0, product = null) => {
  const payload = {
    text,
    ocr_confidence: ocrConfidence,
    ...(product ? { product } : {})
  };
  const response = await API.post("/api/v1/analyze", payload);
  return response.data;
};

// -------------------------------------------------------------------------
// Product information
// -------------------------------------------------------------------------

export const fetchProductInfo = async (barcode) => {
  const response = await API.get(`/api/v1/product/${barcode}`);
  return response.data;
};

// -------------------------------------------------------------------------
// Audit / HITL
// -------------------------------------------------------------------------

/** Fetch all audit records (optional ?status= filter) */
export const fetchAuditQueue = async (statusFilter = null) => {
  const params = statusFilter && statusFilter !== "all" ? { status: statusFilter } : {};
  const response = await API.get("/api/v1/audit/unmapped", { params });
  return response.data;
};

/** Fetch summary statistics on audit review queue */
export const fetchAuditStats = async () => {
  const response = await API.get("/api/v1/audit/stats");
  return response.data;
};

/** Delete an audit record by ID */
export const deleteAuditRecord = async (recordId) => {
  const response = await API.delete(`/api/v1/audit/${recordId}`);
  return response.data;
};

/**
 * Submit a reviewer action on an audit record.
 * @param {string}   recordId         - The audit record ID
 * @param {string}   action           - 'confirm' | 'reject' | 'correct'
 * @param {string[]} correctedTokens  - Required for 'correct'
 * @param {string}   reviewerNote     - Optional explanation
 */
export const submitAuditReview = async (
  recordId,
  action,
  correctedTokens = null,
  reviewerNote = ""
) => {
  const body = {
    action,
    reviewer_note: reviewerNote,
    ...(correctedTokens ? { corrected_tokens: correctedTokens } : {})
  };
  const response = await API.post(`/api/v1/audit/${recordId}/review`, body);
  return response.data;
};

// -------------------------------------------------------------------------
// Authentication & User Sessions
// -------------------------------------------------------------------------

export const setAuthToken = (token) => {
  if (token) {
    API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("flvs_token", token);
  } else {
    delete API.defaults.headers.common["Authorization"];
    localStorage.removeItem("flvs_token");
  }
};

// Auto-hydrate token from localStorage on import
const savedToken = localStorage.getItem("flvs_token");
if (savedToken) {
  API.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;
}

export const registerUser = async (username, email, password) => {
  const response = await API.post("/api/v1/auth/register", { username, email, password });
  return response.data;
};

export const loginUser = async (identifier, password) => {
  const response = await API.post("/api/v1/auth/login", { identifier, password });
  if (response.data && response.data.token) {
    setAuthToken(response.data.token);
  }
  return response.data;
};

export const logoutUser = async () => {
  try {
    await API.post("/api/v1/auth/logout");
  } finally {
    setAuthToken(null);
  }
};

export const fetchCurrentUser = async () => {
  const response = await API.get("/api/v1/auth/me");
  return response.data;
};

// -------------------------------------------------------------------------
// Dietary Profiles & History
// -------------------------------------------------------------------------

export const fetchDietaryProfile = async () => {
  const response = await API.get("/api/v1/profile");
  return response.data;
};

export const updateDietaryProfile = async (profileData) => {
  const response = await API.post("/api/v1/profile", profileData);
  return response.data;
};

export const fetchPreferences = async () => {
  const response = await API.get("/api/v1/profile/preferences");
  return response.data;
};

export const updateCategoryPreferences = async (categories) => {
  const response = await API.post("/api/v1/profile/preferences/categories", { categories });
  return response.data;
};

export const manageAdditivePreference = async (action, code, preferenceType = "avoid") => {
  const response = await API.post("/api/v1/profile/preferences/additives", {
    action,
    code,
    type: preferenceType
  });
  return response.data;
};

export const manageAllergies = async (action, allergens) => {
  const response = await API.post("/api/v1/profile/allergies", {
    action,
    allergens
  });
  return response.data;
};

export const fetchDietaryPresets = async () => {
  const response = await API.get("/api/v1/profile/presets");
  return response.data;
};

export const evaluatePreferences = async (rawText, additives = null, dietaryProfile = null) => {
  const payload = {
    raw_text: rawText,
    ...(additives ? { parsed_additives: additives } : {}),
    ...(dietaryProfile ? { dietary_profile: dietaryProfile } : {})
  };
  const response = await API.post("/api/v1/preferences/evaluate", payload);
  return response.data;
};

export const fetchUserHistory = async (limit = 20, offset = 0, search = "", verdict = "", hasAllergens = null) => {
  const params = {
    limit,
    offset,
    ...(search ? { search } : {}),
    ...(verdict && verdict !== "all" ? { verdict } : {}),
    ...(hasAllergens !== null ? { has_allergens: hasAllergens } : {})
  };
  const response = await API.get("/api/v1/history", { params });
  return response.data;
};

export const fetchHistoryDetail = async (recordId) => {
  const response = await API.get(`/api/v1/history/${recordId}`);
  return response.data;
};

export const deleteHistoryRecord = async (recordId) => {
  const response = await API.delete(`/api/v1/history/${recordId}`);
  return response.data;
};

export const clearUserHistory = async () => {
  const response = await API.delete("/api/v1/history");
  return response.data;
};

export const exportUserHistory = async (format = "json") => {
  const response = await API.get("/api/v1/history/export", {
    params: { format },
    responseType: "blob"
  });
  return response.data;
};

// -------------------------------------------------------------------------
// Barcode Image Decoding
// -------------------------------------------------------------------------

export const decodeBarcodeImage = async (formDataOrBase64) => {
  if (formDataOrBase64 instanceof FormData) {
    const response = await API.post("/api/v1/barcode/decode", formDataOrBase64, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return response.data;
  }
  const response = await API.post("/api/v1/barcode/decode", { image_base64: formDataOrBase64 });
  return response.data;
};

// -------------------------------------------------------------------------
// OCR Preprocessing & Section Extraction
// -------------------------------------------------------------------------

export const preprocessOcrImage = async (formDataOrBase64) => {
  if (formDataOrBase64 instanceof FormData) {
    const response = await API.post("/api/v1/ocr/preprocess", formDataOrBase64, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return response.data;
  }
  const response = await API.post("/api/v1/ocr/preprocess", { image_base64: formDataOrBase64 });
  return response.data;
};

export const extractIngredientSection = async (text, ocrConfidence = 1.0) => {
  const response = await API.post("/api/v1/ocr/extract-section", {
    text,
    ocr_confidence: ocrConfidence
  });
  return response.data;
};

// -------------------------------------------------------------------------
// Additive Parsing
// -------------------------------------------------------------------------

export const parseAdditivesDirect = async (text, ocrConfidence = 1.0) => {
  const response = await API.post("/api/v1/parser/parse", {
    text,
    ocr_confidence: ocrConfidence
  });
  return response.data;
};

// -------------------------------------------------------------------------
// Health check
// -------------------------------------------------------------------------

export const checkHealth = async () => {
  const response = await API.get("/api/health");
  return response.data;
};

export default API;
