"""Тесты на корректность HTTP API Ollama."""

import pytest
import requests


def test_generate_returns_200(client):
    """POST /api/generate должен вернуть HTTP 200."""
    response = requests.post(
        f"{client.base_url}/api/generate",
        json={"model": client.model, "prompt": "Hello", "stream": False},
        timeout=120,
    )
    assert response.status_code == 200


def test_generate_response_schema(client):
    """Ответ должен содержать обязательные поля."""
    data = client.generate("Say OK")
    required_fields = {"model", "response", "done", "done_reason", "eval_count", "total_duration"}
    missing = required_fields - data.keys()
    assert not missing, f"Отсутствуют поля: {missing}"


def test_generate_done_true(client):
    """При stream=false поле done должно быть True."""
    data = client.generate("Reply with a single word: yes")
    assert data["done"] is True
    assert data["done_reason"] == "stop"


def test_generate_response_non_empty(client):
    """Ответ модели не должен быть пустым."""
    data = client.generate("What is 2+2?")
    assert data["response"].strip(), "Ответ модели пустой"


def test_generate_invalid_model_returns_404(client):
    """Запрос с несуществующей моделью должен вернуть HTTP 404 и поле error."""
    response = requests.post(
        f"{client.base_url}/api/generate",
        json={"model": "nonexistent-model-xyz", "prompt": "hi", "stream": False},
        timeout=30,
    )
    assert response.status_code == 404
    assert "error" in response.json()


def test_tags_contains_llama3(client):
    """GET /api/tags должен содержать модель llama3."""
    data = client.tags()
    model_names = [m["name"] for m in data.get("models", [])]
    assert any("llama3" in name for name in model_names), (
        f"llama3 не найдена в списке моделей: {model_names}"
    )