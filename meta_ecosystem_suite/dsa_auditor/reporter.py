"""Generates EU DSA compliance reports (JSON, with an optional
human-readable summary) from a batch of `DSAAdRecord` objects.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from meta_ecosystem_suite.dsa_auditor.schema import DSAAdRecord


class DSAReporter:
    """Builds and persists EU DSA transparency reports."""

    @staticmethod
    def build_report(records: list[DSAAdRecord]) -> dict[str, Any]:
        ai_flagged = [r for r in records if r.is_ai_generated and not r.ai_disclosure_present]

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_records": len(records),
            "ai_disclosure_violations": len(ai_flagged),
            "records": [r.model_dump(mode="json") for r in records],
        }

    @classmethod
    def write_json(cls, records: list[DSAAdRecord], output_path: str) -> str:
        report = cls.build_report(records)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return str(path)
