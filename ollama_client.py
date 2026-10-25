"""HTTP-клиент для работы с Ollama API."""

import requests
from typing import Optional


class OllamaClient:
    """Обёртка над HTTP API Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.0, stream: bool = False) -> dict:
        """
        Отправляет промпт в модель.

        Returns:
            dict: JSON-ответ от Ollama.
        Raises:
            requests.HTTPError: при статусе != 2xx.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temperature},
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    def generate_text(self, prompt: str, temperature: float = 0.0) -> str:
        """Возвращает только текст ответа модели."""
        return self.generate(prompt, temperature=temperature).get("response", "")

    def tags(self) -> dict:
        """Список доступных моделей."""
        response = requests.get(f"{self.base_url}/api/tags", timeout=10)
        response.raise_for_status()
        return response.json()

    def is_available(self) -> bool:
        """Проверяет, что Ollama доступен и модель загружена."""
        try:
            models = [m["name"] for m in self.tags().get("models", [])]
            # llama3 может быть "llama3:latest" или "llama3"
            return any(self.model in m for m in models)
        except requests.RequestException:
            return False