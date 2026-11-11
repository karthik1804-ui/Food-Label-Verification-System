"""
Module: Image-Based Barcode Detection and Decoding Service
==========================================================
Uses native OpenCV BarcodeDetector (cv2.barcode.BarcodeDetector) to detect and
decode 1D barcodes (EAN-13, EAN-8, UPC-A) from camera captures or uploaded images.

Important Constraint:
  - Do NOT invent confidence percentages.
  - Reports discrete status ('valid_ean13', 'invalid_checksum', 'not_detected', 'decoding_error').
  - Validates EAN-13 modulo-10 checksum deterministically.
"""

import io
import logging
from typing import Dict, Any, Optional, Tuple, Union
import numpy as np
import cv2

from services.barcode import validate_ean13, fetch_product_by_barcode
from services.audit import (
    BARCODE_STATUS_VALID,
    BARCODE_STATUS_INVALID,
    BARCODE_STATUS_NOT_PROVIDED,
    BARCODE_STATUS_LOOKUP_FAILED,
)

logger = logging.getLogger(__name__)

# Initialize OpenCV BarcodeDetector singleton
_BARCODE_DETECTOR: Optional[cv2.barcode.BarcodeDetector] = None


def get_barcode_detector() -> cv2.barcode.BarcodeDetector:
    """Returns singleton instance of cv2.barcode.BarcodeDetector."""
    global _BARCODE_DETECTOR
    if _BARCODE_DETECTOR is None:
        _BARCODE_DETECTOR = cv2.barcode.BarcodeDetector()
    return _BARCODE_DETECTOR


def decode_barcode_from_image(
    image_input: Union[bytes, np.ndarray],
    try_rotations: bool = True
) -> Dict[str, Any]:
    """
    Detects and decodes barcodes from image bytes or numpy image array.
    Applies multi-stage image enhancements (grayscale, CLAHE, rotations)
    to maximize real-world label capture resilience.

    Returns structured result:
      - success (bool)
      - barcode (str)
      - barcode_type (str)
      - decode_status (str)
      - is_valid_ean (bool)
      - product (dict)
      - bounding_box (list of [x, y] coordinates | None)
    """
    # 1. Convert input to cv2 image array
    if isinstance(image_input, bytes):
        nparr = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "success": False,
                "barcode": "",
                "barcode_type": "unknown",
                "decode_status": "decoding_error",
                "is_valid_ean": False,
                "product": {},
                "bounding_box": None,
                "error_message": "Failed to decode image buffer as a valid image."
            }
    elif isinstance(image_input, np.ndarray):
        img = image_input
    else:
        return {
            "success": False,
            "barcode": "",
            "barcode_type": "unknown",
            "decode_status": "decoding_error",
            "is_valid_ean": False,
            "product": {},
            "bounding_box": None,
            "error_message": "Invalid image input type."
        }

    detector = get_barcode_detector()

    # Pre-processing pipeline stages
    # Stage 1: Raw image
    # Stage 2: Grayscale with CLAHE contrast enhancement
    # Stage 3: 90 / 180 / 270 degree rotations
    variants = [img]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    variants.append(cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR) if len(img.shape) == 3 else enhanced)

    if try_rotations:
        variants.append(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
        variants.append(cv2.rotate(img, cv2.ROTATE_180))
        variants.append(cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE))

    for variant in variants:
        try:
            res = detector.detectAndDecodeWithType(variant)
            # OpenCV returns (retval, decoded_info, decoded_type, points)
            # or in older versions (decoded_info, decoded_type, points)
            if len(res) == 4:
                retval, decoded_info, decoded_type, points = res
            elif len(res) == 3:
                decoded_info, decoded_type, points = res
                retval = bool(decoded_info)
            else:
                continue

            if retval and decoded_info:
                # Handle single or tuple of decoded strings
                barcode_str = decoded_info[0] if isinstance(decoded_info, (list, tuple)) else str(decoded_info)
                barcode_str = barcode_str.strip()

                if not barcode_str:
                    continue

                btype = decoded_type[0] if isinstance(decoded_type, (list, tuple)) else str(decoded_type)

                # Validate checksum if EAN-13
                is_valid = validate_ean13(barcode_str)
                status = BARCODE_STATUS_VALID if is_valid else BARCODE_STATUS_INVALID

                # Look up product
                product_info = fetch_product_by_barcode(barcode_str)

                # Format bounding box
                bbox = None
                if points is not None and len(points) > 0:
                    try:
                        bbox = points[0].tolist() if hasattr(points[0], "tolist") else list(points[0])
                    except Exception:
                        bbox = None

                logger.info("Successfully detected barcode: %s (%s, valid=%s)", barcode_str, btype, is_valid)
                return {
                    "success": True,
                    "barcode": barcode_str,
                    "barcode_type": str(btype),
                    "decode_status": status,
                    "is_valid_ean": is_valid,
                    "product": product_info,
                    "bounding_box": bbox,
                    "error_message": None
                }
        except Exception as e:
            logger.debug("Barcode detection attempt error: %s", str(e))
            continue

    # No barcode found after all pipeline stages
    return {
        "success": False,
        "barcode": "",
        "barcode_type": "none",
        "decode_status": "not_detected",
        "is_valid_ean": False,
        "product": {},
        "bounding_box": None,
        "error_message": "No barcode detected in the provided image."
    }
