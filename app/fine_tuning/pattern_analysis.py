"""
EditPatternAnalyzer: Detects systematic patterns in user edits to AI suggestions.

Uses lightweight string analysis (no heavy NLP dependencies) to identify:
- Deletion patterns: what users consistently remove from AI output
- Addition patterns: what users consistently add to AI output
- Tone shifts: changes in formality, length, or structure
"""

import re
from collections import Counter
from typing import List, Dict, Any, Tuple
from loguru import logger

from app.models import EditPattern, TrainingRecord


# Phrases that signal filler/hedging in AI output
_FILLER_PHRASES = [
    "let me analyze", "let me think", "i'll analyze", "i need to consider",
    "it's important to note", "it should be noted", "as an ai", "as a language model",
    "certainly", "absolutely", "of course", "great question", "excellent point",
    "i hope this helps", "feel free to", "please note that",
    "in conclusion", "to summarize", "in summary", "ultimately",
]

# Regex patterns for structural analysis
_BULLET_PATTERN = re.compile(r"^\s*[-•*]\s+", re.MULTILINE)
_NUMBER_PATTERN = re.compile(r"^\s*\d+[.)]\s+", re.MULTILINE)
_HEADER_PATTERN = re.compile(r"^#{1,3}\s+", re.MULTILINE)


class EditPatternAnalyzer:
    """
    Analyzes user modification patterns across settlement diffs to identify
    systematic issues with agent output quality.

    Uses only stdlib + Counter — no heavy NLP dependencies.
    """

    def analyze_deletion_patterns(
        self,
        records: List[TrainingRecord]
    ) -> List[EditPattern]:
        """
        Find phrases/words users consistently remove from AI output.

        Compares original_plan text tokens against final_plan tokens and
        counts what the user routinely strips out.
        """
        if not records:
            return []

        # Collect ngrams (1-4 words) that appear in original but not in final
        deletion_counter: Counter = Counter()
        total = len(records)

        for record in records:
            original_text = self._extract_text(record.original_plan)
            final_text = self._extract_text(record.final_plan)

            original_ngrams = set(self._extract_ngrams(original_text, max_n=4))
            final_ngrams = set(self._extract_ngrams(final_text, max_n=4))

            deleted = original_ngrams - final_ngrams
            for ngram in deleted:
                deletion_counter[ngram] += 1

        # Score filler phrases specially
        filler_hits = self._score_filler_phrases(records, deletion_counter)

        return self._build_patterns(
            deletion_counter,
            total,
            pattern_type="deletion",
            filler_hits=filler_hits,
            recommendation_template="Remove this phrase/content from agent prompts",
        )

    def analyze_addition_patterns(
        self,
        records: List[TrainingRecord]
    ) -> List[EditPattern]:
        """
        Find phrases/words users consistently add to AI output.

        Content the user adds signals what the agent is missing — these are
        prime candidates for prompt engineering improvements.
        """
        if not records:
            return []

        addition_counter: Counter = Counter()
        total = len(records)

        for record in records:
            original_text = self._extract_text(record.original_plan)
            final_text = self._extract_text(record.final_plan)

            original_ngrams = set(self._extract_ngrams(original_text, max_n=4))
            final_ngrams = set(self._extract_ngrams(final_text, max_n=4))

            added = final_ngrams - original_ngrams
            for ngram in added:
                addition_counter[ngram] += 1

        return self._build_patterns(
            addition_counter,
            total,
            pattern_type="addition",
            recommendation_template="Add this concept/phrasing to agent prompts",
        )

    def detect_tone_shifts(
        self,
        records: List[TrainingRecord]
    ) -> List[Dict[str, Any]]:
        """
        Identify systematic tone/structure changes between original and final.

        Checks for:
        - Length changes (users consistently shorten/lengthen output)
        - Formality shifts (informal → formal markers)
        - Structure shifts (prose → bullets, bullets → prose)
        """
        if not records:
            return []

        shifts = []
        length_deltas = []
        structure_changes: Counter = Counter()

        for record in records:
            original_text = self._extract_text(record.original_plan)
            final_text = self._extract_text(record.final_plan)

            if not original_text:
                continue

            # Length delta (positive = user expanded, negative = user shortened)
            delta = len(final_text) - len(original_text)
            length_deltas.append(delta)

            # Structure changes
            orig_bullets = len(_BULLET_PATTERN.findall(original_text))
            final_bullets = len(_BULLET_PATTERN.findall(final_text))
            orig_headers = len(_HEADER_PATTERN.findall(original_text))
            final_headers = len(_HEADER_PATTERN.findall(final_text))

            if final_bullets > orig_bullets + 2:
                structure_changes["prose_to_bullets"] += 1
            elif orig_bullets > final_bullets + 2:
                structure_changes["bullets_to_prose"] += 1

            if final_headers > orig_headers:
                structure_changes["added_headers"] += 1
            elif orig_headers > final_headers:
                structure_changes["removed_headers"] += 1

        total = len(length_deltas) or 1
        avg_delta = sum(length_deltas) / total

        if abs(avg_delta) > 100:
            direction = "expands" if avg_delta > 0 else "shortens"
            shifts.append({
                "type": "length",
                "description": f"Users consistently {direction} AI output (avg {avg_delta:+.0f} chars)",
                "avg_delta": round(avg_delta, 1),
                "recommendation": (
                    "Increase output length and detail"
                    if avg_delta > 0
                    else "Make output more concise"
                ),
            })

        for change_type, count in structure_changes.most_common():
            frequency = count / total
            if frequency >= 0.3:
                label = change_type.replace("_", " ")
                shifts.append({
                    "type": "structure",
                    "description": f"Users {label} in {frequency:.0%} of edits",
                    "frequency": round(frequency, 3),
                    "recommendation": f"Prompt agent to use {label.split()[-1]} style formatting",
                })

        return shifts

    def get_improvement_recommendations(
        self,
        deletion_patterns: List[EditPattern],
        addition_patterns: List[EditPattern],
        tone_shifts: List[Dict[str, Any]],
        threshold: float = 0.3,
    ) -> List[str]:
        """
        Synthesize all patterns into a prioritized list of prompt change recommendations.
        Filters to patterns appearing in >= threshold fraction of records.
        """
        recommendations = []

        high_freq_deletions = [p for p in deletion_patterns if p.frequency >= threshold]
        for pattern in high_freq_deletions[:5]:
            recommendations.append(
                f"[Deletion {pattern.frequency:.0%}] Remove '{pattern.pattern_text}' — {pattern.recommendation}"
            )

        high_freq_additions = [p for p in addition_patterns if p.frequency >= threshold]
        for pattern in high_freq_additions[:5]:
            recommendations.append(
                f"[Addition {pattern.frequency:.0%}] Add '{pattern.pattern_text}' — {pattern.recommendation}"
            )

        for shift in tone_shifts:
            recommendations.append(
                f"[Tone/Structure] {shift['description']} → {shift['recommendation']}"
            )

        if not recommendations:
            recommendations.append(
                "No strong patterns detected. Collect more settlements (aim for 20+) before drawing conclusions."
            )

        return recommendations

    # --- Private helpers ---

    def _extract_text(self, plan: Dict[str, Any]) -> str:
        """Recursively extract all string values from a nested dict/list."""
        parts = []
        self._collect_strings(plan, parts)
        return " ".join(parts).lower()

    def _collect_strings(self, obj: Any, parts: List[str]) -> None:
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                self._collect_strings(v, parts)
        elif isinstance(obj, list):
            for item in obj:
                self._collect_strings(item, parts)

    def _extract_ngrams(self, text: str, max_n: int = 4) -> List[str]:
        """Generate word ngrams (1 to max_n) from text, filtering short/stop words."""
        _STOP_WORDS = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "is", "it", "this", "that",
            "be", "are", "was", "were", "has", "have", "had", "not", "as",
        }
        tokens = [w for w in re.findall(r"\b[a-z]{3,}\b", text) if w not in _STOP_WORDS]
        ngrams = []
        for n in range(1, max_n + 1):
            for i in range(len(tokens) - n + 1):
                ngrams.append(" ".join(tokens[i : i + n]))
        return ngrams

    def _score_filler_phrases(
        self,
        records: List[TrainingRecord],
        counter: Counter,
    ) -> Dict[str, int]:
        """Boost known filler phrases in deletion counts."""
        filler_hits: Dict[str, int] = {}
        for record in records:
            original_text = self._extract_text(record.original_plan)
            final_text = self._extract_text(record.final_plan)
            for phrase in _FILLER_PHRASES:
                if phrase in original_text and phrase not in final_text:
                    filler_hits[phrase] = filler_hits.get(phrase, 0) + 1
                    counter[phrase] = counter.get(phrase, 0) + 1
        return filler_hits

    def _build_patterns(
        self,
        counter: Counter,
        total: int,
        pattern_type: str,
        recommendation_template: str,
        filler_hits: Dict[str, int] = None,
        min_count: int = 2,
        top_n: int = 20,
    ) -> List[EditPattern]:
        """Convert a Counter into a sorted list of EditPattern objects."""
        if not counter or total == 0:
            return []

        patterns = []
        for text, count in counter.most_common(top_n):
            if count < min_count:
                break
            frequency = count / total
            # Only surface patterns appearing in >= 20% of records
            if frequency < 0.2:
                continue
            is_filler = filler_hits and text in filler_hits
            recommendation = (
                f"Remove AI filler phrase '{text}' from prompts"
                if is_filler
                else f"{recommendation_template}: '{text}'"
            )
            patterns.append(
                EditPattern(
                    pattern_type=pattern_type,
                    pattern_text=text,
                    frequency=round(frequency, 3),
                    occurrence_count=count,
                    recommendation=recommendation,
                )
            )
        return patterns
