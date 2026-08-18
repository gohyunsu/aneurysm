from __future__ import annotations

import json
import unittest
from pathlib import Path

from aurora.aneug_official_source_reconciliation import (
    AneuGSourceReconciliationError,
    load_record,
    validate_record,
)


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results" / "aneug_official_source_reconciliation_20260818.json"


class AneuGOfficialSourceReconciliationTests(unittest.TestCase):
    def test_pinned_record_is_valid(self):
        record = load_record(RECORD)
        self.assertEqual(
            record["reconciliations"]["canonical_transient_case_count"]["decision"],
            730,
        )

    def test_html_count_cannot_silently_replace_final_release_count(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        record["reconciliations"]["canonical_transient_case_count"]["decision"] = 200
        with self.assertRaisesRegex(AneuGSourceReconciliationError, "canonical_count"):
            validate_record(record)


if __name__ == "__main__":
    unittest.main()
