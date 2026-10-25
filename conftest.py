"""Общие фикстуры pytest."""

import pytest
from ollama_client import OllamaClient


@pytest.fixture(scope="session")
def client() -> OllamaClient:
    """Клиент к Ollama. Пропускает тесты, если модель недоступна."""
    c = OllamaClient(model="llama3")
    if not c.is_available():
        pytest.skip("Ollama недоступен или модель llama3 не загружена")
    return c