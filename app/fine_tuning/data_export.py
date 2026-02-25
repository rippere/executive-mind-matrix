"""
FineTuningDataPrep: Exports training data in JSONL format for Claude fine-tuning.

Produces conversation pairs in the Anthropic fine-tuning format:
  {"messages": [
    {"role": "system", "content": "<agent persona>"},
    {"role": "user",   "content": "<intent description>"},
    {"role": "assistant", "content": "<human-approved output>"}
  ]}

Only high-quality settlements (configurable min acceptance rate) are included.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

from app.models import TrainingRecord, FinetuningExample, DatasetValidationReport


# Agent system prompts — mirror the prompts in agent_router.py
AGENT_SYSTEM_PROMPTS: Dict[str, str] = {
    "The Entrepreneur": (
        "You are The Entrepreneur, a growth-focused strategic advisor. "
        "You analyze executive decisions through the lens of revenue generation, "
        "market expansion, and competitive advantage. You favor bold, high-upside moves "
        "and are willing to accept calculated risks for significant returns. "
        "Present your analysis in a structured, actionable format."
    ),
    "The Quant": (
        "You are The Quant, a quantitative analyst specializing in risk-adjusted returns. "
        "You analyze decisions using data-driven frameworks, probability assessments, "
        "and mathematical modeling. You focus on measurable outcomes, statistical significance, "
        "and evidence-based recommendations. Be precise, cite numbers, and quantify uncertainty."
    ),
    "The Auditor": (
        "You are The Auditor, a governance and compliance specialist. "
        "You analyze executive decisions through the lens of risk management, "
        "regulatory compliance, and ethical governance. You identify potential liabilities, "
        "ensure process integrity, and protect the organization from downside risks. "
        "Flag concerns clearly and recommend protective measures."
    ),
}

_DEFAULT_SYSTEM_PROMPT = (
    "You are an executive decision intelligence assistant. "
    "Analyze the given intent and provide structured, actionable recommendations."
)


class FineTuningDataPrep:
    """
    Prepares settlement diff records for Claude fine-tuning export.

    Usage:
        exporter = FineTuningDataPrep()
        path = await exporter.export_to_jsonl(
            records=training_records,
            output_path="data/finetuning_export.jsonl",
            min_acceptance_rate=0.75
        )
        report = exporter.validate_dataset(path)
    """

    def export_to_jsonl(
        self,
        records: List[TrainingRecord],
        output_path: str,
        min_acceptance_rate: float = 0.7,
        agent_name: Optional[str] = None,
        intent_descriptions: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Export filtered training records to JSONL for fine-tuning.

        Args:
            records: TrainingRecord list from TrainingAnalytics
            output_path: Destination file path (.jsonl)
            min_acceptance_rate: Only include records at or above this threshold (0–1)
            agent_name: Filter to a specific agent (None = all)
            intent_descriptions: Optional map of intent_id → description for richer context

        Returns:
            Path to the written JSONL file
        """
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        examples: List[FinetuningExample] = []
        skipped = 0

        for record in records:
            # Apply filters
            if record.acceptance_rate < min_acceptance_rate:
                skipped += 1
                continue
            if agent_name and record.agent_name and record.agent_name != agent_name:
                skipped += 1
                continue

            example = self._build_example(record, intent_descriptions)
            if example:
                examples.append(example)
            else:
                skipped += 1

        logger.info(
            f"Exporting {len(examples)} fine-tuning examples "
            f"(skipped {skipped} below threshold or malformed)"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(
                    json.dumps({"messages": example.messages}) + "\n"
                )

        logger.success(f"Fine-tuning dataset written to {output_path}")
        return output_path

    def validate_dataset(self, jsonl_path: str) -> DatasetValidationReport:
        """
        Validate a JSONL file for fine-tuning readiness.

        Checks:
        - File exists and is non-empty
        - Each line is valid JSON with a "messages" key
        - Each message has "role" and "content"
        - At least one assistant turn per example
        - Dataset has 50+ examples (Anthropic minimum)
        """
        errors: List[str] = []
        total = 0
        valid = 0
        acceptance_rates: List[float] = []

        if not os.path.exists(jsonl_path):
            return DatasetValidationReport(
                jsonl_path=jsonl_path,
                total_examples=0,
                valid_examples=0,
                invalid_examples=0,
                errors=[f"File not found: {jsonl_path}"],
                avg_acceptance_rate=0.0,
                ready_for_finetuning=False,
            )

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                total += 1
                try:
                    obj = json.loads(line)
                    self._validate_example(obj, line_num, errors)
                    valid += 1
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON — {e}")

        invalid = total - valid
        avg_rate = sum(acceptance_rates) / len(acceptance_rates) if acceptance_rates else 0.0

        if total < 50:
            errors.append(
                f"Dataset has only {total} examples; Anthropic recommends 50+ for fine-tuning"
            )

        ready = valid >= 50 and invalid == 0

        return DatasetValidationReport(
            jsonl_path=jsonl_path,
            total_examples=total,
            valid_examples=valid,
            invalid_examples=invalid,
            errors=errors,
            avg_acceptance_rate=round(avg_rate, 3),
            ready_for_finetuning=ready,
        )

    # --- Private helpers ---

    def _build_example(
        self,
        record: TrainingRecord,
        intent_descriptions: Optional[Dict[str, str]] = None,
    ) -> Optional[FinetuningExample]:
        """Build a single fine-tuning example from a TrainingRecord."""
        final_text = self._plan_to_text(record.final_plan)
        if not final_text.strip():
            return None

        system_prompt = AGENT_SYSTEM_PROMPTS.get(
            record.agent_name or "", _DEFAULT_SYSTEM_PROMPT
        )

        # User turn: prefer looked-up intent description, fall back to intent_id reference
        intent_desc = (
            (intent_descriptions or {}).get(record.intent_id)
            or f"Analyze this strategic intent (ID: {record.intent_id[:8]})"
        )

        messages = [
            {"role": "user", "content": intent_desc},
            {"role": "assistant", "content": final_text},
        ]

        # Prepend system turn only when we have a real persona
        if record.agent_name and record.agent_name in AGENT_SYSTEM_PROMPTS:
            messages.insert(0, {"role": "system", "content": system_prompt})

        return FinetuningExample(
            messages=messages,
            source_intent_id=record.intent_id,
            acceptance_rate=record.acceptance_rate,
        )

    def _plan_to_text(self, plan: Dict[str, Any]) -> str:
        """Serialize a plan dict to a readable text representation."""
        if not plan:
            return ""
        try:
            return json.dumps(plan, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(plan)

    def _validate_example(
        self,
        obj: Dict[str, Any],
        line_num: int,
        errors: List[str],
    ) -> None:
        """Validate a single parsed JSONL object, appending errors in-place."""
        if "messages" not in obj:
            errors.append(f"Line {line_num}: Missing 'messages' key")
            return

        messages = obj["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            errors.append(f"Line {line_num}: 'messages' must be a list with at least 2 items")
            return

        has_assistant = False
        for msg in messages:
            if not isinstance(msg, dict):
                errors.append(f"Line {line_num}: Message is not a dict")
                continue
            if "role" not in msg or "content" not in msg:
                errors.append(f"Line {line_num}: Message missing 'role' or 'content'")
                continue
            if msg["role"] not in {"system", "user", "assistant"}:
                errors.append(f"Line {line_num}: Unknown role '{msg['role']}'")
            if msg["role"] == "assistant":
                has_assistant = True

        if not has_assistant:
            errors.append(f"Line {line_num}: No assistant turn found")
