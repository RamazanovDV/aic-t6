# T6 AI Agent

AI-агент с веб-интерфейсом и CLI для взаимодействия с LLM провайдерами.

## Возможности

- **Backend API** - Flask-сервер для обработки запросов к LLM
- **Web UI** - Адаптивный интерфейс (htmx + CSS)
- **CLI** - Командная строка для управления
- **Множественные провайдеры** - OpenAI, Anthropic, Ollama, кастомные OpenAI-совместимые
- **Контекст** - Markdown-файлы подмешиваются в system prompt
- **Сессии** - История хранится в файлах
- **Админ-панель** - Настройка провайдеров, контекста, API ключей
- **Debug режим** - Просмотр запросов и ответов LLM
- **Суммаризация** - Автоматическое сжатие длинной истории
- **Две панели** - Параллельные сессии в одном окне
- **Импорт/экспорт** - Сессии можно экспортировать и импортировать

## Быстрый старт

### 1. Установка зависимостей

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# UI
cd ../ui
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# CLI
cd ../cli
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка

Скопируйте примеры конфигов и заполните свои API ключи:

```bash
cp backend/config.example.yaml backend/config.yaml
cp ui/config.example.yaml ui/config.yaml
cp cli/config.example.yaml cli/config.yaml
```

### 3. Запуск

```bash
# Terminal 1 - Backend (порт 5000)
cd backend && source venv/bin/activate && python run.py

# Terminal 2 - Web UI (порт 5001)
cd ui && source venv/bin/activate && python run.py
```

### 4. Использование

- **Web UI**: http://localhost:5001
- **Админ-панель**: http://localhost:5001/admin
- **CLI**: см. раздел ниже

## Конфигурация

### Backend (`backend/config.yaml`)

```yaml
app:
  host: "0.0.0.0"
  port: 5000

auth:
  api_key: "your-secret-api-key"

llm:
  default_provider: "openai"
  default_messages_interval: 30  # Суммаризация каждые N сообщений
  summarizer_model: "gpt-4o-mini"  # Модель для суммаризации

  providers:
    openai:
      url: "https://api.openai.com/v1/chat/completions"
      api_key: "sk-..."
      model: "gpt-4o-mini"

    # Кастомный OpenAI-совместимый провайдер:
    custom:
      url: "https://your-api.com/v1/chat/completions"
      api_key: "key"
      model: "model-name"

    # Anthropic
    anthropic:
      url: "https://api.anthropic.com/v1/messages"
      api_key: "sk-ant-..."
      model: "claude-3-5-sonnet-20241022"

    # Ollama
    ollama:
      url: "http://localhost:11434/v1/chat/completions"
      api_key: "ollama"
      model: "llama3.1"

context:
  dir: "context"
  enabled_files:  # Файлы для включения в system prompt
    - "ABOUT.md"
    - "SOUL.md"
```

### Контекстные файлы

Создайте Markdown-файлы в директории `context/`. Управление какими файлами включать в system prompt осуществляется через `context.enabled_files` в config.yaml.

### Суммаризация

После N сообщений (по умолчанию 30) история автоматически суммаризируется. Это позволяет работать с длинными диалогами без превышения лимита контекста.

Настройки:
- `llm.default_messages_interval` - интервал суммаризации (по умолчанию 30)
- `llm.summarizer_model` - модель для суммаризации

В UI можно настроить интервал для каждой сессии отдельно.

## Web UI

### Чат

- Выбор провайдера и модели из выпадающих списков
- Переключатель Debug для просмотра запросов/ответов LLM
- Статистика по токенам (входные/выходные/всего)
- Кнопка 🔍 на сообщениях от модели для просмотра debug данных
- Две панели для параллельных сессий
- Автоматическая суммаризация длинной истории

### Админ-панель (`/admin`)

- **Auth** - Настройка API ключа для доступа к бэкенду
- **Providers** - Управление LLM провайдерами
- **Context** - Управление контекстными файлами (включить/выключить, создать, удалить, переименовать)

## CLI

```bash
# Отправить сообщение
python cli/main.py chat "Привет, как дела?"

# С провайдером
python cli/main.py chat "Привет" -p ollama

# Сессия
python cli/main.py chat "Привет" -s my-session

# Управление сессиями
python cli/main.py session list
python cli/main.py session reset
python cli/main.py session delete my-session

# Импорт/экспорт
python cli/main.py session export
python cli/main.py session import path/to/session.json

# Сбросить историю
python cli/main.py chat reset

# Проверить здоровье бэкенда
python cli/main.py health

# Показать настройки
python cli/main.py settings show
```

## API

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работоспособности |
| POST | `/chat` | Отправить сообщение |
| POST | `/chat/stream` | Отправить сообщение (streaming) |
| POST | `/chat/reset` | Сбросить историю |
| GET | `/sessions` | Список сессий |
| GET | `/sessions/<id>` | Получить сессию |
| DELETE | `/sessions/<id>` | Удалить сессию |
| POST | `/sessions/<id>/rename` | Переименовать сессию |
| POST | `/sessions/<id>/copy` | Копировать сессию |
| POST | `/sessions/<id>/clear-debug` | Очистить debug данные |
| GET | `/sessions/<id>/summarization-settings` | Настройки суммаризации |
| POST | `/sessions/<id>/summarization-settings` | Сохранить настройки суммаризации |
| POST | `/sessions/export` | Экспорт всех сессий |
| POST | `/sessions/import` | Импорт сессии |

### Заголовки

- `X-API-Key` - API ключ для аутентификации
- `X-Session-Id` - Идентификатор сессии

### Пример запроса

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -H "X-Session-Id: my-session" \
  -d '{"message": "Привет", "provider": "openai", "model": "gpt-4o-mini"}'
```

## Структура проекта

```
t6/
├── backend/                  # Flask API (порт 5000)
│   ├── app/
│   │   ├── routes.py        # API эндпоинты
│   │   ├── config.py        # Загрузка конфига
│   │   ├── context.py       # Загрузка markdown
│   │   ├── session.py       # Управление сессиями
│   │   ├── storage.py       # Файловое хранилище
│   │   ├── summarizer.py    # Суммаризация сообщений
│   │   └── llm/             # Провайдеры LLM
│   ├── config.yaml
│   └── run.py
├── ui/                      # Web UI (порт 5001)
│   ├── app.py
│   ├── static/
│   ├── templates/
│   │   ├── chat.html        # Основной чат
│   │   ├── admin.html       # Админ-панель
│   │   └── settings.html    # Настройки
│   ├── config.yaml
│   └── run.py
├── cli/                     # CLI
│   ├── main.py
│   └── config.yaml
├── context/                  # Markdown файлы для контекста
└── data/                     # Сессии (gitignore)
```

## Требования

- Python 3.13+
- Flask 3.1+
- PyYAML 6.0+
- Requests 2.32+
- Click 8.1+

## Лицензия

MIT
