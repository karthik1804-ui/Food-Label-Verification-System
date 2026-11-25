"""
Module: Reusable OpenCV Image Preprocessor for Food Label OCR
==============================================================
Provides high-fidelity, adaptive computer vision preprocessing pipelines
to maximize Tesseract OCR text recognition for food packaging labels:
  - Format validation, corruption protection, and maximum dimension bounds
  - Aspect-ratio preserving intelligent resizing for small label fonts
  - Grayscale conversion and bilateral edge-preserving denoising
  - Contrast-Limited Adaptive Histogram Equalization (CLAHE) for curved surfaces
  - Unsharp-mask edge sharpening without ringing artifacts
  - Multi-version preservation: original, grayscale, CLAHE, sharpened, adaptive threshold
  - Graceful fallback to original image on any processing anomaly
"""

import time
import base64
import logging
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, Union
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Core thresholds
BLUR_THRESHOLD = 70.0
MIN_RECOMMENDED_WIDTH = 1200
MIN_RECOMMENDED_HEIGHT = 900
MAX_ALLOWED_DIMENSION = 4096
MAX_HARD_DIMENSION = 8192
MAX_ALLOWED_DECODED_PIXELS = 25_000_000  # 25 MP safety limit
MAX_ALLOWED_BYTES = 25 * 1024 * 1024  # 25 MB memory ceiling


@dataclass
class PreprocessedImageBundle:
    """
    Encapsulates all generated image variants, quality metrics,
    and processing timings for a single input frame.
    """
    is_valid: bool
    original: Optional[np.ndarray] = None
    grayscale: Optional[np.ndarray] = None
    contrast_enhanced: Optional[np.ndarray] = None
    sharpened: Optional[np.ndarray] = None
    adaptive_threshold: Optional[np.ndarray] = None
    best_candidate: Optional[np.ndarray] = None
    best_candidate_name: str = "original"
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    timings_ms: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None

    def get_candidate_by_name(self, name: str) -> Optional[np.ndarray]:
        """Returns a specific processed candidate by name."""
        name_lower = (name or "").lower()
        if name_lower == "original":
            return self.original
        elif name_lower == "grayscale":
            return self.grayscale
        elif name_lower in ("clahe", "contrast_enhanced"):
            return self.contrast_enhanced
        elif name_lower in ("sharp", "sharpened"):
            return self.sharpened
        elif name_lower in ("threshold", "adaptive_threshold", "binarized"):
            return self.adaptive_threshold
        elif name_lower in ("best", "auto"):
            return self.best_candidate if self.best_candidate is not None else self.original
        return self.best_candidate if self.best_candidate is not None else self.original

    def to_base64(self, variant: str = "best", quality: int = 92) -> Optional[str]:
        """Encodes specified variant to JPEG base64 string with data URI prefix."""
        target_img = self.get_candidate_by_name(variant)
        if target_img is None:
            return None
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), max(10, min(100, quality))]
            success, buffer = cv2.imencode(".jpg", target_img, encode_param)
            if not success:
                return None
            b64_data = base64.b64encode(buffer).decode("utf-8")
            return f"data:image/jpeg;base64,{b64_data}"
        except Exception as e:
            logger.warning("Failed to encode image to base64: %s", str(e))
            return None


class ImagePreprocessor:
    """
    Configurable OpenCV Preprocessing Pipeline for Food Label Verification.
    """

    def __init__(
        self,
        min_width: int = MIN_RECOMMENDED_WIDTH,
        min_height: int = MIN_RECOMMENDED_HEIGHT,
        max_dim: int = MAX_ALLOWED_DIMENSION,
        clahe_clip_limit: float = 2.2,
        clahe_grid_size: Tuple[int, int] = (8, 8),
        blur_threshold: float = BLUR_THRESHOLD
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_dim = max_dim
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_grid_size = clahe_grid_size
        self.blur_threshold = blur_threshold

    def decode_and_validate(self, image_input: Any) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Safely parses, decodes, and bounds-checks arbitrary image input:
        Accepts: raw bytes, bytearray, base64 strings, data URIs, or numpy ndarray.
        Returns: (decoded_bgr_image, validation_info)
        """
        if image_input is None:
            return None, {"is_valid": False, "error": "No image input provided (input is None)"}

        # Handle direct numpy ndarray
        if isinstance(image_input, np.ndarray):
            if image_input.size == 0:
                return None, {"is_valid": False, "error": "Empty or zero-dimensional numpy array"}
            if len(image_input.shape) not in (2, 3):
                return None, {"is_valid": False, "error": f"Unsupported ndarray dimensions: {len(image_input.shape)}D (must be 2D or 3D)"}
            
            img_arr = image_input
            if len(img_arr.shape) == 3:
                channels = img_arr.shape[2]
                if channels not in (1, 3, 4):
                    return None, {"is_valid": False, "error": f"Unsupported channel count: {channels} (must be 1, 3, or 4 channels)"}

            # Convert floating or integer dtypes safely to uint8
            if not np.issubdtype(img_arr.dtype, np.uint8):
                if np.issubdtype(img_arr.dtype, np.floating):
                    img_arr = np.clip(img_arr * 255.0 if img_arr.max() <= 1.0 else img_arr, 0, 255).astype(np.uint8)
                elif np.issubdtype(img_arr.dtype, np.integer):
                    img_arr = np.clip(img_arr, 0, 255).astype(np.uint8)
                else:
                    return None, {"is_valid": False, "error": f"Unsupported ndarray dtype: {img_arr.dtype}"}

            if len(img_arr.shape) == 2 or img_arr.shape[2] == 1:
                img = cv2.cvtColor(img_arr if len(img_arr.shape) == 2 else img_arr[:, :, 0], cv2.COLOR_GRAY2BGR)
            elif img_arr.shape[2] == 4:
                img = cv2.cvtColor(img_arr, cv2.COLOR_BGRA2BGR)
            else:
                img = img_arr.copy()
            return self._enforce_bounds(img)

        # Handle bytes or string inputs
        raw_bytes = None
        try:
            if isinstance(image_input, (bytes, bytearray)):
                raw_bytes = bytes(image_input)
            elif isinstance(image_input, str):
                clean_str = image_input.strip()
                if not clean_str:
                    return None, {"is_valid": False, "error": "Empty string provided"}
                if "," in clean_str:
                    clean_str = clean_str.split(",", 1)[1]
                raw_bytes = base64.b64decode(clean_str)
            else:
                return None, {"is_valid": False, "error": f"Unsupported input type: {type(image_input).__name__}"}
        except Exception as e:
            return None, {"is_valid": False, "error": f"Image decoding syntax error: {str(e)}"}

        if not raw_bytes or len(raw_bytes) == 0:
            return None, {"is_valid": False, "error": "Decoded image byte buffer is empty"}

        if len(raw_bytes) > MAX_ALLOWED_BYTES:
            return None, {"is_valid": False, "error": f"Image exceeds maximum allowable size of {MAX_ALLOWED_BYTES // (1024*1024)}MB"}

        try:
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None or img.size == 0:
                return None, {"is_valid": False, "error": "Corrupt or unrecognized image file format"}
            return self._enforce_bounds(img)
        except Exception as e:
            return None, {"is_valid": False, "error": f"cv2.imdecode failure: {str(e)}"}

    def _enforce_bounds(self, img: np.ndarray) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """Downscales excessively large images to safeguard server memory and rejects decompression bombs."""
        if img is None or img.size == 0:
            return None, {"is_valid": False, "error": "Cannot enforce bounds on empty or None image"}
        
        h, w = img.shape[:2]
        if h <= 0 or w <= 0:
            return None, {"is_valid": False, "error": "Invalid image dimensions (width or height is zero)"}

        # Protection against excessive decoded dimensions / memory bombs
        if w > MAX_HARD_DIMENSION or h > MAX_HARD_DIMENSION or (w * h) > MAX_ALLOWED_DECODED_PIXELS:
            return None, {
                "is_valid": False,
                "error": f"Image dimensions ({w}x{h}={w*h} pixels) exceed safety ceiling of {MAX_ALLOWED_DECODED_PIXELS} pixels or {MAX_HARD_DIMENSION}px dimension"
            }

        if w > self.max_dim or h > self.max_dim:
            scale = self.max_dim / float(max(w, h))
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            return img, {
                "is_valid": True,
                "original_dimensions": (w, h),
                "clamped_dimensions": (new_w, new_h),
                "was_clamped": True
            }
        return img, {
            "is_valid": True,
            "original_dimensions": (w, h),
            "clamped_dimensions": (w, h),
            "was_clamped": False
        }

    def assess_quality(self, img: np.ndarray) -> Dict[str, Any]:
        """
        Evaluates optical sharpness via Laplacian variance, assesses quadrant
        illumination uniformity, and grades overall image usability.
        """
        if img is None or img.size == 0:
            return {
                "is_valid": False,
                "blur_score": 0.0,
                "is_blurry": True,
                "lighting_uniformity_score": 0.0,
                "is_uneven_lighting": True,
                "dimensions": (0, 0),
                "quality_grade": "Unusable"
            }

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

        # 1. Laplacian sharpness metric
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = lap_var < self.blur_threshold

        # 2. Lighting uniformity across quadrants
        mid_y, mid_x = h // 2, w // 2
        quadrants = [
            gray[:mid_y, :mid_x],
            gray[:mid_y, mid_x:],
            gray[mid_y:, :mid_x],
            gray[mid_y:, mid_x:]
        ]
        quad_means = [float(np.mean(q)) for q in quadrants if q.size > 0]
        lighting_std = float(np.std(quad_means)) if quad_means else 0.0
        is_uneven = lighting_std > 35.0

        # 3. Overall quality grade
        if is_blurry or w < 400 or h < 300:
            grade = "Low" if lap_var > 40.0 else "Unusable"
        elif is_uneven or w < self.min_width or h < self.min_height:
            grade = "Adequate"
        else:
            grade = "High"

        return {
            "is_valid": True,
            "blur_score": round(lap_var, 2),
            "is_blurry": is_blurry,
            "lighting_uniformity_score": round(max(0.0, 100.0 - lighting_std * 2), 1),
            "is_uneven_lighting": is_uneven,
            "dimensions": (w, h),
            "quality_grade": grade
        }

    def resize_aspect_ratio(
        self,
        img: np.ndarray,
        upscale_small: bool = True
    ) -> Tuple[np.ndarray, bool, Tuple[int, int]]:
        """
        Normalizes image scale for small ingredient fonts, preserving exact aspect ratio.
        Caps scaling factor at 3.0x to avoid interpolative blur and strictly prevents
        upscaling beyond max_dim.
        """
        if img is None or img.size == 0:
            return img, False, (0, 0)

        h, w = img.shape[:2]
        if not upscale_small or (w >= self.min_width and h >= self.min_height):
            return img, False, (w, h)

        scale_x = max(1.0, self.min_width / max(1, w))
        scale_y = max(1.0, self.min_height / max(1, h))
        scale = min(3.0, max(scale_x, scale_y))

        # Strictly prevent upscaling beyond max_dim
        max_allowed_scale_x = self.max_dim / max(1.0, float(w))
        max_allowed_scale_y = self.max_dim / max(1.0, float(h))
        max_possible_scale = min(max_allowed_scale_x, max_allowed_scale_y)
        scale = min(scale, max_possible_scale)

        if scale > 1.05:
            new_w = min(self.max_dim, int(round(w * scale)))
            new_h = min(self.max_dim, int(round(h * scale)))
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            return resized, True, (new_w, new_h)

        return img, False, (w, h)

    def process(
        self,
        image_input: Any,
        upscale_small: bool = True,
        enable_adaptive_threshold: bool = True
    ) -> PreprocessedImageBundle:
        """
        Executes the full controlled preprocessing pipeline, creating and preserving
        multiple image variants:
          1. Original image
          2. Grayscale image
          3. CLAHE contrast-enhanced image
          4. Controlled unsharp-masked sharpened image
          5. Adaptive thresholded image
        Selects the best candidate dynamically while preserving all versions for fallback.
        """
        t0 = time.perf_counter()
        timings = {}

        # Stage 1: Validation and decoding
        img, val_info = self.decode_and_validate(image_input)
        timings["decode_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        if img is None:
            return PreprocessedImageBundle(
                is_valid=False,
                error_message=val_info.get("error", "Invalid image input"),
                timings_ms=timings
            )

        # Stage 2: Quality assessment
        t_qa = time.perf_counter()
        metrics = self.assess_quality(img)
        timings["quality_assess_ms"] = round((time.perf_counter() - t_qa) * 1000, 2)

        # Stage 3: Resizing (preserving aspect ratio)
        t_res = time.perf_counter()
        scaled_img, was_upscaled, proc_dims = self.resize_aspect_ratio(img, upscale_small=upscale_small)
        metrics["upscaled"] = was_upscaled
        metrics["processed_dimensions"] = proc_dims
        timings["resize_ms"] = round((time.perf_counter() - t_res) * 1000, 2)

        # Stage 4: Grayscale conversion
        t_gray = time.perf_counter()
        gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY) if len(scaled_img.shape) == 3 else scaled_img
        timings["grayscale_ms"] = round((time.perf_counter() - t_gray) * 1000, 2)

        # Stage 5: Selective edge-preserving denoising
        t_denoise = time.perf_counter()
        # Bilateral filter preserves sharp character boundaries while smoothing background noise
        denoised = cv2.bilateralFilter(gray, d=5, sigmaColor=35, sigmaSpace=35)
        timings["denoise_ms"] = round((time.perf_counter() - t_denoise) * 1000, 2)

        # Stage 6: CLAHE contrast enhancement
        t_clahe = time.perf_counter()
        clahe = cv2.createCLAHE(clipLimit=self.clahe_clip_limit, tileGridSize=self.clahe_grid_size)
        contrast_enhanced = clahe.apply(denoised)
        timings["clahe_ms"] = round((time.perf_counter() - t_clahe) * 1000, 2)

        # Stage 7: Controlled unsharp masking (sharpening small characters)
        t_sharp = time.perf_counter()
        blurred = cv2.GaussianBlur(contrast_enhanced, (0, 0), sigmaX=2.5)
        # Moderate weight: 1.35x contrast - 0.35x blurred to prevent noise amplification
        sharpened = cv2.addWeighted(contrast_enhanced, 1.35, blurred, -0.35, 0)
        timings["sharpen_ms"] = round((time.perf_counter() - t_sharp) * 1000, 2)

        # Stage 8: Adaptive thresholding (for severe uneven lighting or shadows)
        thresh_img = None
        if enable_adaptive_threshold:
            t_thresh = time.perf_counter()
            thresh_img = cv2.adaptiveThreshold(
                contrast_enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                21,
                10
            )
            timings["threshold_ms"] = round((time.perf_counter() - t_thresh) * 1000, 2)

        # Total pipeline time
        timings["total_preprocessing_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Determine best candidate dynamically based on quality metrics
        if metrics["is_blurry"]:
            # If blurry, unsharp masking can amplify blur rings; use CLAHE contrast
            best_candidate = contrast_enhanced
            best_candidate_name = "contrast_enhanced"
        elif metrics["is_uneven_lighting"] and thresh_img is not None:
            # If lighting is severely uneven across packaging, adaptive threshold balances it
            best_candidate = thresh_img
            best_candidate_name = "adaptive_threshold"
        else:
            # For standard food labels, sharpened gives crispest small INS font edges
            best_candidate = sharpened
            best_candidate_name = "sharpened"

        return PreprocessedImageBundle(
            is_valid=True,
            original=img,
            grayscale=gray,
            contrast_enhanced=contrast_enhanced,
            sharpened=sharpened,
            adaptive_threshold=thresh_img,
            best_candidate=best_candidate,
            best_candidate_name=best_candidate_name,
            quality_metrics=metrics,
            timings_ms=timings
        )


# Global default instance for convenience
_default_preprocessor = ImagePreprocessor()


def decode_image_input(image_input: Any) -> Optional[np.ndarray]:
    """Backward-compatible helper: decodes image input to BGR numpy array."""
    img, _ = _default_preprocessor.decode_and_validate(image_input)
    return img


def assess_image_quality(img: np.ndarray) -> Dict[str, Any]:
    """Backward-compatible helper: assesses image quality metrics."""
    return _default_preprocessor.assess_quality(img)


def preprocess_label_image(
    image_input: Any,
    upscale_small: bool = True
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Backward-compatible helper: returns (best_preprocessed_image, quality_metrics).
    """
    bundle = _default_preprocessor.process(image_input, upscale_small=upscale_small)
    if not bundle.is_valid:
        return None, {"is_valid": False, "error": bundle.error_message or "Preprocessing failed"}
    return bundle.best_candidate, bundle.quality_metrics
