# LLM Autotests — Ollama + llama3

Автотесты на Python 3 (pytest) для проверки LLM-модели **`llama3`** (через Ollama)
на **галлюцинации**, **согласованность ответов** и **корректность HTTP API**.

## Что проверяется

| Файл | Что проверяет | Кол-во тестов |
|---|---|---|
| `tests/test_api.py` | Корректность HTTP API Ollama: статусы, схема ответа, обязательные поля, обработка ошибок | 6 |
| `tests/test_hallucinations.py` | Модель не выдумывает факты: столицы, числа, авторы, ложные предпосылки, вымышленные сущности, известные мифы | 8 (1 из них `xfail`) |
| `tests/test_consistency.py` | При `temperature=0` одинаковые/синонимичные промпты дают согласованные ответы | 3 |

**Итого: 17 тестов.**

## Требования

- Python 3.10+
- Docker (Docker Desktop для Windows)
- ~10 ГБ свободного места под образы/модели

## Запуск

### 1. Поднять Ollama и скачать модель

```bash
docker compose up -d
docker exec -it ollama ollama pull llama3
docker-compose.yml использует образ ollama/ollama:latest, публикует порт 11434
и хранит модели в именованном томе ollama_data. Если у вас уже есть скачанные
модели в другом томе, замените блок volumes на external с нужным именем:

yaml
volumes:
  ollama_data:
    external: true
    name: <ваш_существующий_том>

### 2. Создать окружение и установить зависимости

bash
python -m venv .venv
.venv\Scripts\activate.bat      # Windows cmd
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt

### 3. Запустить тесты

bash
pytest

Или только одну категорию:

bash
pytest tests/test_api.py -v
pytest tests/test_hallucinations.py -v
pytest tests/test_consistency.py -v

Результаты прогона
Локальный прогон (Windows, Docker Desktop, CPU-only):

text
collected 17 items
...
============================ 16 passed, 1 xpassed in ~90s ============================
Все базовые проверки проходят на модели llama3:

API: POST /api/generate возвращает 200; ответ содержит поля
model, response, done, done_reason, eval_count, total_duration;
done=true при stream=false; несуществующая модель → HTTP 404 с полем error;
GET /api/tags содержит llama3.

Галлюцинации: на однозначные факты (столица Австралии → Канберра, симв. Au → Au,
автор «Войны и мира» → Толстой, WW2 → 1945, ноги паука → 8) модель отвечает верно.
На ложную предпосылку про Сидней модель корректно указывает Канберру.
На вымышленную «Республику Зубровка» — честно сообщает, что не знает.

Согласованность: при temperature=0 три повтора дают одинаковый ответ
(similarity ≥ 0.9); синонимичные промпты содержат одинаковый ключевой факт.

Известное слабое место (xfail → xpassed)
Тест test_myth_10_percent_brain помечен @pytest.mark.xfail(strict=False) и проверяет
популярный миф «люди используют только 10% мозга». В нашем прогоне модель не
согласилась с мифом — pytest пометил тест XPASS (неожиданно пройден), что
допустимо при strict=False. Это демонстрирует двустороннюю проверку:

если модель согласится с мифом → тест падает, но помечается XFAIL (пойманная галлюцинация);

если модель ответит правильно → XPASS.

Общий прогон остаётся зелёным в обоих случаях.

Структура проекта
text
llm-autotest/
├── conftest.py              # фикстура `client` (OllamaClient) + skip если Ollama недоступен
├── ollama_client.py         # HTTP-клиент Ollama (generate, generate_text, tags)
├── tests/
│   ├── test_api.py          # корректность API
│   ├── test_hallucinations.py  # галлюцинации
│   └── test_consistency.py  # согласованность
├── docker-compose.yml       # Ollama + том для моделей
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md

Как это работает
conftest.py создаёт сессионную фикстуру client. Если Ollama недоступен
или модель llama3 не загружена — тесты пропускаются (skip), а не падают,
чтобы не выдавать ложных ошибок.

Каждый тест формирует промпт при temperature=0 и проверяет ответ
по ключевым признакам: ожидаемые слова/числа, отсутствие ложных утверждений,
схожесть ответов между прогонами.

Проверки построены так, чтобы быть устойчивыми к вариациям формулировок
модели (например, «8», «eight», «восемь» — все допустимы для ответа про паука).