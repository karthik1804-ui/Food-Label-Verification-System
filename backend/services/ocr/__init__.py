"""
OCR Services Package: OpenCV Preprocessing, Tesseract Integration & Safety Gate
"""
from .image_preprocessor import (
    ImagePreprocessor,
    PreprocessedImageBundle,
    assess_image_quality,
    preprocess_label_image,
    decode_image_input,
    BLUR_THRESHOLD,
    MIN_RECOMMENDED_WIDTH,
    MIN_RECOMMENDED_HEIGHT,
    MAX_ALLOWED_DIMENSION
)
from .ocr_pipeline import (
    OcrPipeline,
    prepare_ocr_image
)
from .ocr_comparator import (
    compare_ocr_results,
    compute_levenshtein_similarity,
    detect_character_confusion_fixes,
    KNOWN_CONFUSION_PATTERNS
)

__all__ = [
    "ImagePreprocessor",
    "PreprocessedImageBundle",
    "OcrPipeline",
    "prepare_ocr_image",
    "compare_ocr_results",
    "compute_levenshtein_similarity",
    "detect_character_confusion_fixes",
    "KNOWN_CONFUSION_PATTERNS",
    "assess_image_quality",
    "preprocess_label_image",
    "decode_image_input",
    "BLUR_THRESHOLD",
    "MIN_RECOMMENDED_WIDTH",
    "MIN_RECOMMENDED_HEIGHT",
    "MAX_ALLOWED_DIMENSION"
]
