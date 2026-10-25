"""Тесты на согласованность ответов модели."""

import pytest
from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    """Коэффициент схожести двух строк (0.0–1.0)."""
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def test_deterministic_at_zero_temperature(client):
    """При temperature=0 одинаковый промпт должен давать идентичный ответ."""
    prompt = "What is the capital of France? Answer in one word."
    answers = [client.generate_text(prompt, temperature=0.0) for _ in range(3)]

    for i in range(1, len(answers)):
        sim = _similarity(answers[0], answers[i])
        assert sim >= 0.9, (
            f"Несогласованность! Ответы различаются (similarity={sim:.2f}):\n"
            f"  #1: {answers[0][:200]!r}\n"
            f"  #{i+1}: {answers[i][:200]!r}"
        )


def test_synonym_prompts_same_keyword(client):
    """Разные формулировки одного вопроса → одинаковый ключевой факт в ответе."""
    prompts = [
        "What is the capital of Japan?",
        "Which city is the capital of Japan?",
        "Name the capital city of Japan.",
    ]
    answers = [client.generate_text(p, temperature=0.0).lower() for p in prompts]

    for i, ans in enumerate(answers):
        assert "tokyo" in ans, (
            f"Промпт #{i+1} ({prompts[i]!r}) не содержит 'tokyo'. Ответ: {ans[:300]!r}"
        )


def test_multiple_choice_consistent(client):
    """Модель должна выбирать один и тот же вариант при повторах."""
    prompt = (
        "Which planet is closest to the Sun? "
        "Choose exactly one: Mercury, Venus, Earth, Mars."
    )
    answers = [client.generate_text(prompt, temperature=0.0).lower() for _ in range(3)]

    for ans in answers:
        assert "mercury" in ans, f"Ожидалось 'mercury' в ответе, получено: {ans[:200]!r}"