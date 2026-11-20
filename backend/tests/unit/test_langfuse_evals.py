"""Unit tests for Langfuse evaluation pipeline and quality gate evaluators."""

import json

from evals.run_langfuse_evals import (
    DEFAULT_DATASET_PATH,
    evaluate_citation_grounding,
    evaluate_jurisdiction_accuracy,
    evaluate_pii_masking_check,
    run_evaluations,
)


class TestEvaluationDataset:
    """Verify integrity and coverage of dataset_dubai_setup.json."""

    def test_dataset_exists_and_contains_10_cases(self) -> None:
        assert DEFAULT_DATASET_PATH.exists()
        with open(DEFAULT_DATASET_PATH, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) >= 10

        # Verify required keys in each test case
        for item in data:
            assert "id" in item
            assert "input" in item
            assert "expected_output" in item

            inp = item["input"]
            assert "company_name" in inp
            assert "industry_sector" in inp
            assert "business_activity" in inp
            assert "revenue_model" in inp
            assert "uae_local_trade" in inp

            exp = item["expected_output"]
            assert exp["pathway"] in ("Mainland_DET", "FreeZone")
            assert "recommended_authority" in exp
            assert "required_compliance_checks" in exp
            assert len(exp["required_compliance_checks"]) > 0
            assert "expected_sources" in exp
            assert len(exp["expected_sources"]) > 0


class TestJurisdictionAccuracyEvaluator:
    """Verify jurisdiction accuracy scoring logic."""

    def test_exact_match_scores_1_0(self) -> None:
        actual = {"pathway": "Mainland_DET", "recommended_authority": "DET"}
        expected = {"pathway": "Mainland_DET", "recommended_authority": "DET"}
        score, reason = evaluate_jurisdiction_accuracy(actual, expected)
        assert score == 1.0
        assert "Exact match" in reason

    def test_alternative_authority_scores_0_95(self) -> None:
        actual = {"pathway": "FreeZone", "recommended_authority": "DIC"}
        expected = {
            "pathway": "FreeZone",
            "recommended_authority": "IFZA",
            "alternative_authorities": ["Dubai Internet City (DIC)"],
        }
        score, _ = evaluate_jurisdiction_accuracy(actual, expected)
        assert score >= 0.95

    def test_pathway_mismatch_scores_zero(self) -> None:
        actual = {"pathway": "FreeZone", "recommended_authority": "IFZA"}
        expected = {"pathway": "Mainland_DET", "recommended_authority": "DET"}
        score, reason = evaluate_jurisdiction_accuracy(actual, expected)
        assert score == 0.0
        assert "mismatch" in reason.lower()


class TestCitationGroundingEvaluator:
    """Verify official UAE citations evaluation."""

    def test_official_sources_score_high(self) -> None:
        sources = [
            "https://dubaidet.gov.ae/en/services",
            "https://investindubai.gov.ae/en/step1",
        ]
        expected = ["https://dubaidet.gov.ae", "https://investindubai.gov.ae"]
        score, reason = evaluate_citation_grounding(sources, expected)
        assert score >= 0.9
        assert "verified official citations" in reason

    def test_markdown_text_with_citations_extracted(self) -> None:
        text = "Check guidelines on [DET Portal](https://dubaidet.gov.ae) and [DMCC](https://www.dmcc.ae)."
        score, _ = evaluate_citation_grounding(text, ["https://dubaidet.gov.ae"])
        assert score >= 0.9

    def test_untrusted_sources_score_zero(self) -> None:
        sources = ["https://random-blog.xyz/dubai-setup", "https://unverified-forum.com"]
        score, reason = evaluate_citation_grounding(sources, ["https://dubaidet.gov.ae"])
        assert score == 0.0
        assert "None" in reason


class TestPIIMaskingEvaluator:
    """Verify zero-leakage PII evaluation."""

    def test_clean_or_redacted_payload_passes(self) -> None:
        payload = {
            "company": "Falcon Tech LLC",
            "passport": "[REDACTED_PASSPORT]",
            "emirates_id": "[REDACTED_EMIRATES_ID]",
            "iban": "[REDACTED_IBAN]",
        }
        score, reason = evaluate_pii_masking_check(payload)
        assert score == 1.0
        assert "Zero unredacted PII" in reason

    def test_unredacted_passport_fails(self) -> None:
        payload = {"founder": "John Doe", "passport": "N12345678"}
        score, reason = evaluate_pii_masking_check(payload)
        assert score == 0.0
        assert "PII Leak" in reason

    def test_unredacted_emirates_id_fails(self) -> None:
        payload = "Shareholder ID is 784-1988-1234567-1."
        score, reason = evaluate_pii_masking_check(payload)
        assert score == 0.0
        assert "Emirates ID" in reason

    def test_unredacted_uae_iban_fails(self) -> None:
        payload = {"bank": "ENBD", "account": "AE070331234567890123456"}
        score, reason = evaluate_pii_masking_check(payload)
        assert score == 0.0
        assert "IBAN" in reason


class TestEndToEndEvalRunner:
    """Verify end-to-end evaluation runner with dry_run."""

    def test_dry_run_passes_quality_gate(self) -> None:
        success = run_evaluations(
            dataset_path=DEFAULT_DATASET_PATH,
            min_accuracy=0.90,
            dry_run=True,
        )
        assert success is True

    def test_strict_quality_gate_fails_when_unreachable(self) -> None:
        # Require 1.05 (impossible) to confirm failure handling
        success = run_evaluations(
            dataset_path=DEFAULT_DATASET_PATH,
            min_accuracy=1.05,
            dry_run=True,
        )
        assert success is False
