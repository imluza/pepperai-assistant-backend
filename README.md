Загрузить Ollama: https://ollama.com/download

Установить необходимые модели:
ollama pull qwen2.5vl:latest
ollama pull gpt-oss:20b

Клонировать репозиторий и перейти в папку проекта.
Запустить сервисы:
docker compose up --build -d

Бэкенд будет доступен по адресу http://localhost:8000, документация — /docs.

Перед использованием убедиться, что Ollama запущен локально и модели доступны.

Гит на расширение VS Code: https://github.com/timkmit/pepperai-assistant

Запущенный "бэк-енд" с моделями - http://5.35.92.45/docs
