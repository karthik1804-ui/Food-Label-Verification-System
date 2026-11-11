"""
Phase 8 Tests: INS Detection & Additive Classification Engine Refinements
========================================================================
Comprehensive test suite verifying all 10 requirements:
  1. Extract INS numbers from OCR text (INS variants and OCR glitch normalization)
  2. Identify additives using official names
  3. Recognise alternative additive names and synonyms from taxonomy
  4. Text normalisation (1NS/1N5/IN5 glyph normalization)
  5. Match detected additives against the 750-entry taxonomy
  6. Identify functional categories (multi-classification supported)
  7. Identify individual canonical INS numbers
  8. Handle and report duplicate detections
  9. Record unmatched candidate terms in unmapped_tokens
  10. Report ambiguous detections (generic parent codes like INS 150/500, unnumbered category statements)
  11. Strict MSG rule: MSG is only assigned to Monosodium Glutamate / INS 621
  12. API endpoints: POST /api/v1/parser/parse and POST /api/v1/analyze
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.parser import (
    extract_additive_tokens,
    normalize_ocr_errors,
    parse_additives_detailed,
    parse_additives_and_audit,
    load_taxonomy,
    get_synonym_map
)
from app import app


class TestInsExtractionAndNormalization(unittest.TestCase):
    """Tests for extracting INS numbers and normalizing OCR glyph errors."""

    def test_extract_ins_numbers_various_formats(self):
        """Extracts standard INS, colon, hyphen, and sub-index formats."""
        text = "Contains INS 102, INS:211, INS-330, and INS 500(ii)."
        tokens = extract_additive_tokens(text)
        self.assertIn("INS 102", tokens)
        self.assertIn("INS 211", tokens)
        self.assertIn("INS 330", tokens)
        self.assertIn("INS 500(II)", tokens)

    def test_ocr_glitch_normalization(self):
        """Normalizes 1NS, 1N5, IN5, and OCR letter-number substitutions."""
        text = "Ingredients: 1NS 102, 1N5 211, IN5 330, INS l04, INS 5OO."
        tokens = extract_additive_tokens(text)
        self.assertIn("INS 102", tokens)
        self.assertIn("INS 211", tokens)
        self.assertIn("INS 330", tokens)
        self.assertIn("INS 104", tokens)
        self.assertIn("INS 500", tokens)

    def test_extract_parenthetical_category_codes(self):
        """Extracts parenthesized numbers after category descriptors (e.g. colour (102, 110))."""
        text = (
            "Refined flour, permitted artificial colour (102, 110), "
            "acidity regulators (330, 331), and emulsifier (322)."
        )
        tokens = extract_additive_tokens(text)
        self.assertIn("INS 102", tokens)
        self.assertIn("INS 110", tokens)
        self.assertIn("INS 330", tokens)
        self.assertIn("INS 331", tokens)
        self.assertIn("INS 322", tokens)


class TestOfficialNamesAndSynonyms(unittest.TestCase):
    """Tests identifying additives by official names and alternative synonyms."""

    def test_identify_additives_using_official_names(self):
        """Resolves official Codex / FSSAI names to canonical INS entries."""
        text = "Contains Tartrazine, Citric Acid, Sodium Benzoate, and Aspartame."
        res = parse_additives_detailed(text)
        codes = [a["code"] for a in res["parsed_additives"]]
        self.assertIn("INS 102", codes)
        self.assertIn("INS 330", codes)
        self.assertIn("INS 211", codes)
        self.assertIn("INS 951", codes)

    def test_recognise_alternative_additive_names(self):
        """Recognises synonyms such as FD&C Yellow 5, Equal, NutraSweet, Baking Soda."""
        text = "Sweetened with NutraSweet, coloured with FD&C Yellow 5, raised with Baking Soda."
        res = parse_additives_detailed(text)
        codes = [a["code"] for a in res["parsed_additives"]]
        self.assertIn("INS 951", codes)  # NutraSweet -> Aspartame
        self.assertIn("INS 102", codes)  # FD&C Yellow 5 -> Tartrazine
        self.assertIn("INS 500", codes)  # Baking Soda -> Sodium Bicarbonate

    def test_strict_msg_classification(self):
        """Only Monosodium Glutamate / INS 621 is classified as MSG; other enhancers are distinct."""
        # 1. Monosodium Glutamate / INS 621 IS MSG
        res1 = parse_additives_detailed("Contains Monosodium Glutamate and INS 621.")
        self.assertEqual(len(res1["parsed_additives"]), 1)
        item1 = res1["parsed_additives"][0]
        self.assertEqual(item1["code"], "INS 621")
        self.assertIn("Monosodium Glutamate", item1["name"])

        # 2. Disodium Guanylate (INS 627) and Disodium Inosinate (INS 631) are NOT MSG
        res2 = parse_additives_detailed("Seasoning contains INS 627 and INS 631.")
        codes2 = [a["code"] for a in res2["parsed_additives"]]
        names2 = [a["name"] for a in res2["parsed_additives"]]
        self.assertIn("INS 627", codes2)
        self.assertIn("INS 631", codes2)
        self.assertFalse(any("MSG" in n for n in names2))
        self.assertFalse(any("Monosodium Glutamate" in n for n in names2))


class TestPromptExampleAndCategorization(unittest.TestCase):
    """Tests the exact example input from project requirements and functional classifications."""

    def test_user_prompt_exact_example(self):
        """
        Tests user requirement example:
        'Sugar, permitted artificial colour INS 102, acidity regulator INS 330, flavour enhancer INS 621.'
        Expected:
        - INS 102: Colour.
        - INS 330: Acidity regulator.
        - INS 621: Flavour enhancer / monosodium glutamate.
        """
        input_text = "Sugar, permitted artificial colour INS 102, acidity regulator INS 330, flavour enhancer INS 621."
        res = parse_additives_detailed(input_text)
        additives = {a["clean_code"]: a for a in res["parsed_additives"]}

        self.assertIn("102", additives)
        self.assertIn("330", additives)
        self.assertIn("621", additives)

        # INS 102: Colour
        self.assertTrue(additives["102"]["is_color"])
        self.assertIn("Color", additives["102"]["functional_categories"])

        # INS 330: Acidity regulator
        self.assertIn("Acidity regulator", additives["330"]["functional_categories"])

        # INS 621: Flavour enhancer / monosodium glutamate
        self.assertIn("Flavor enhancer", additives["621"]["functional_categories"])
        self.assertIn("Monosodium Glutamate", additives["621"]["name"])

    def test_multi_category_identification(self):
        """Identifies multiple functional categories for versatile additives like Citric Acid (INS 330)."""
        res = parse_additives_detailed("Contains INS 330 and INS 951.")
        additives = {a["code"]: a for a in res["parsed_additives"]}

        # Citric acid has multiple functions: Acidity regulator, Antioxidant, Sequestrant
        cats_330 = additives["INS 330"]["functional_categories"]
        self.assertIn("Acidity regulator", cats_330)
        self.assertIn("Antioxidant", cats_330)

        # Aspartame is Sweetener and Flavor enhancer
        cats_951 = additives["INS 951"]["functional_categories"]
        self.assertIn("Sweetener", cats_951)
        self.assertIn("Flavor enhancer", cats_951)

        # Detected categories dict is properly populated
        self.assertIn("Acidity regulator", res["detected_categories"])
        self.assertIn("Sweetener", res["detected_categories"])
        self.assertIn("INS 330", res["detected_categories"]["Acidity regulator"])


class TestDeduplicationUnmappedAndAmbiguity(unittest.TestCase):
    """Tests duplicate handling, unmapped candidates, and ambiguity reporting."""

    def test_duplicate_mentions_deduplicated_cleanly(self):
        """Multiple mentions of same additive (by code and name) are collapsed into one entry."""
        text = "Ingredients: Tartrazine, INS 102, permitted colour INS 102, Citric Acid, INS 330."
        res = parse_additives_detailed(text)

        codes = [a["code"] for a in res["parsed_additives"]]
        self.assertEqual(codes.count("INS 102"), 1)
        self.assertEqual(codes.count("INS 330"), 1)

        # Duplicate log records multiple detections
        self.assertTrue(len(res["duplicate_detections"]) > 0)
        dup_codes = [d["code"] for d in res["duplicate_detections"]]
        self.assertIn("INS 102", dup_codes)

    def test_record_unmapped_terms(self):
        """Unrecognized additive tokens are captured in unmapped_tokens for audit logging."""
        text = "Contains INS 102, INS 9999, and Chemical X99."
        res = parse_additives_detailed(text)

        mapped_codes = [a["code"] for a in res["parsed_additives"]]
        self.assertIn("INS 102", mapped_codes)
        self.assertIn("INS 9999", res["unmapped_tokens"])

    def test_report_ambiguous_parent_code(self):
        """Generic parent codes like INS 150 or INS 500 trigger ambiguity reporting."""
        text = "Ingredients: Water, Sugar, INS 150, INS 500."
        res = parse_additives_detailed(text)

        self.assertTrue(len(res["ambiguous_detections"]) >= 2)
        amb_codes = [a.get("code") for a in res["ambiguous_detections"]]
        self.assertIn("INS 150", amb_codes)
        self.assertIn("INS 500", amb_codes)

    def test_report_generic_category_statement_without_code(self):
        """Generic statement like 'contains added preservatives' without INS code is reported as ambiguous."""
        text = "Potato chips with salt, contains added preservatives."
        res = parse_additives_detailed(text)

        self.assertTrue(len(res["ambiguous_detections"]) > 0)
        generic_types = [a.get("ambiguity_type") for a in res["ambiguous_detections"]]
        self.assertIn("generic_category_statement_without_code", generic_types)


class TestParserEndpoints(unittest.TestCase):
    """Integration tests for POST /api/v1/parser/parse and POST /api/v1/analyze."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_parser_parse_endpoint(self):
        """POST /api/v1/parser/parse returns complete detailed parsing structure."""
        payload = {
            "text": "Sugar, permitted artificial colour INS 102, acidity regulator INS 330, flavour enhancer INS 621."
        }
        res = self.client.post("/api/v1/parser/parse", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")

        result = data["result"]
        self.assertEqual(len(result["parsed_additives"]), 3)
        self.assertIn("Color", result["detected_categories"])
        self.assertIn("Acidity regulator", result["detected_categories"])
        self.assertIn("Flavor enhancer", result["detected_categories"])
        self.assertEqual(len(result["individual_ins_codes"]), 3)

    def test_analyze_endpoint_returns_phase8_metadata(self):
        """POST /api/v1/analyze returns detected_categories, individual_ins_codes, and ambiguous_detections."""
        payload = {
            "text": "Water, sugar, INS 150, acidity regulator INS 330",
            "ocr_confidence": 0.95
        }
        res = self.client.post("/api/v1/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertIn("detected_categories", data)
        self.assertIn("individual_ins_codes", data)
        self.assertIn("ambiguous_detections", data)
        self.assertIn("system_audit", data)
        self.assertIn("detected_categories", data["system_audit"])


if __name__ == "__main__":
    unittest.main()
