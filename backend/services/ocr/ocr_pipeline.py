"""
Module: OCR Pipeline Integration (Configuration A vs. Configuration B)
=====================================================================
Orchestrates the two OCR pipeline configurations:
  - Configuration A: Existing OCR (Original Image -> Tesseract)
  - Configuration B: Improved OCR (Original Image -> OpenCV Preprocessing -> Tesseract)

Preserves:
  - Identical Tesseract configuration (eng, psm 6, preserve_interword_spaces)
  - Word-level confidence calculation and safety gating
  - Full compatibility with INS parser and personalised dietary preference engine
  - Safe fallback to Configuration A whenever OpenCV preprocessing encounters errors
"""

import time
import base64
import logging
from typing import Dict, Any, Optional, Tuple, List
import cv2
import numpy as np

from .image_preprocessor import (
    ImagePreprocessor,
    PreprocessedImageBundle,
    _default_preprocessor
)

logger = logging.getLogger(__name__)


class OcrPipeline:
    """
    Manages dual-configuration OCR image pipeline with automatic error fallback.
    """

    def __init__(self, preprocessor: Optional[ImagePreprocessor] = None):
        self.preprocessor = preprocessor or _default_preprocessor

    def prepare_for_tesseract(
        self,
        image_input: Any,
        config: str = "B",
        variant: str = "best"
    ) -> Dict[str, Any]:
        """
        Prepares the image for Tesseract OCR execution under Configuration A or B.

        Parameters:
          - image_input: raw bytes, base64 data URI, or numpy array.
          - config: "A" (Existing/Original) or "B" (Improved OpenCV Preprocessed).
          - variant: "best" | "sharpened" | "contrast_enhanced" | "adaptive_threshold" | "original"

        Returns structured payload containing:
          - target_image: np.ndarray ready for Tesseract
          - target_image_base64: data URI for browser/node Tesseract
          - original_image_base64: data URI of original image for fallback/comparison
          - configuration_used: "A" or "B"
          - fallback_applied: bool
          - quality_metrics: dict
          - timings_ms: dict
          - candidate_name: str
        """
        t0 = time.perf_counter()
        config_clean = (config or "B").strip().upper()

        if config_clean not in ("A", "B"):
            config_clean = "B"

        # ----------------------------------------------------
        # CONFIGURATION A: Existing OCR (Original Image)
        # ----------------------------------------------------
        if config_clean == "A":
            img, val_info = self.preprocessor.decode_and_validate(image_input)
            if img is None:
                return {
                    "is_valid": False,
                    "error": val_info.get("error", "Invalid image input"),
                    "configuration_used": "A"
                }

            metrics = self.preprocessor.assess_quality(img)
            t_total = round((time.perf_counter() - t0) * 1000, 2)

            # Preserve original image representation without lossy re-encoding when already a valid data URI
            if (
                isinstance(image_input, str)
                and image_input.startswith("data:image/")
                and not val_info.get("was_clamped", False)
            ):
                img_b64 = image_input
            else:
                _, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                img_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

            return {
                "is_valid": True,
                "target_image": img,
                "target_image_base64": img_b64,
                "original_image_base64": img_b64,
                "configuration_used": "A",
                "fallback_applied": False,
                "candidate_name": "original",
                "quality_metrics": metrics,
                "timings_ms": {
                    "preprocessing_ms": t_total,
                    "total_ms": t_total
                }
            }

        # ----------------------------------------------------
        # CONFIGURATION B: Improved OCR (OpenCV Preprocessed)
        # ----------------------------------------------------
        try:
            bundle = self.preprocessor.process(image_input, upscale_small=True)
            if not bundle.is_valid:
                raise ValueError(bundle.error_message or "Preprocessing failed")

            target_img = bundle.get_candidate_by_name(variant)
            candidate_name = variant if variant != "best" else bundle.best_candidate_name

            target_b64 = bundle.to_base64(variant=candidate_name)
            orig_b64 = bundle.to_base64(variant="original")

            return {
                "is_valid": True,
                "target_image": target_img,
                "target_image_base64": target_b64,
                "original_image_base64": orig_b64,
                "configuration_used": "B",
                "fallback_applied": False,
                "candidate_name": candidate_name,
                "quality_metrics": bundle.quality_metrics,
                "timings_ms": bundle.timings_ms
            }

        except Exception as err:
            logger.warning("Configuration B preprocessing failed: %s. Falling back to Configuration A.", str(err))
            # Safe Fallback to Configuration A (Original Image)
            img, val_info = self.preprocessor.decode_and_validate(image_input)
            if img is not None:
                metrics = self.preprocessor.assess_quality(img)
                if (
                    isinstance(image_input, str)
                    and image_input.startswith("data:image/")
                    and not (val_info or {}).get("was_clamped", False)
                ):
                    img_b64 = image_input
                else:
                    _, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    img_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")
                return {
                    "is_valid": True,
                    "target_image": img,
                    "target_image_base64": img_b64,
                    "original_image_base64": img_b64,
                    "configuration_used": "A",
                    "fallback_applied": True,
                    "fallback_reason": str(err),
                    "candidate_name": "original",
                    "quality_metrics": metrics,
                    "timings_ms": {"preprocessing_ms": 0.0}
                }
            return {
                "is_valid": False,
                "error": f"Both Configuration B and Fallback A failed: {str(err)}",
                "configuration_used": "B",
                "fallback_applied": True
            }


_default_pipeline = OcrPipeline()


def prepare_ocr_image(
    image_input: Any,
    config: str = "B",
    variant: str = "best"
) -> Dict[str, Any]:
    """Top-level helper to prepare image under Configuration A or B."""
    return _default_pipeline.prepare_for_tesseract(image_input, config=config, variant=variant)
