# Настройка форматов данных

## Обзор

Расширение BGE Reranker поддерживает различные форматы входных и выходных данных для совместимости с разными системами (Dify, другие API, и т.д.).

## Форматы входных данных

### Проблема

Разные системы могут использовать разные названия полей для передачи документов:

- **`passages`** - используется в нашем API по умолчанию
- **`documents`** - используется в Dify и некоторых других системах
- **`texts`** - используется в некоторых API

### Решение

Расширение поддерживает настройку формата входных данных через параметр `input_format`:

#### Варианты:

1. **`"passages"`** - Использовать поле `passages` (формат нашего API)
   ```json
   {
     "query": "search query",
     "passages": ["doc1", "doc2"],
     "top_k": 5
   }
   ```

2. **`"documents"`** - Использовать поле `documents` (формат Dify)
   ```json
   {
     "query": "search query",
     "documents": ["doc1", "doc2"],
     "top_k": 5
   }
   ```

3. **`"auto"`** (по умолчанию) - Автоматическое определение
   - По умолчанию использует `passages` (наш API формат)
   - Можно изменить на `documents` если нужно

### Настройка в Dify

В настройках модели в Dify:

1. Перейдите в **Settings → Model Providers → Reranker**
2. Выберите **"BGE Reranker"**
3. В поле **"Input Format"** выберите:
   - `auto` - для автоматического определения (рекомендуется)
   - `passages` - для использования поля `passages`
   - `documents` - для использования поля `documents`

## Форматы выходных данных

### Проблема

Разные системы могут ожидать разные форматы ответа:

- **С полем `index`** - стандартный формат нашего API
- **Без поля `index`** - упрощенный формат для некоторых систем

### Решение

Расширение поддерживает настройку формата выходных данных через параметр `output_format`:

#### Варианты:

1. **`"standard"`** (по умолчанию) - Полный формат с индексом
   ```json
   {
     "results": [
       {
         "index": 0,
         "document": "text",
         "score": 8.234
       }
     ]
   }
   ```

2. **`"simple"`** - Упрощенный формат без индекса
   ```json
   {
     "results": [
       {
         "document": "text",
         "score": 8.234
       }
     ]
   }
   ```

### Настройка в Dify

В настройках модели:

1. Перейдите в **Settings → Model Providers → Reranker**
2. Выберите **"BGE Reranker"**
3. В поле **"Output Format"** выберите:
   - `standard` - полный формат с индексом (рекомендуется)
   - `simple` - упрощенный формат без индекса

## Примеры конфигурации

### Конфигурация для нашего API (по умолчанию)

```json
{
  "api_url": "http://localhost:8009",
  "timeout": 30,
  "top_k": 5,
  "input_format": "passages",
  "output_format": "standard"
}
```

### Конфигурация для Dify

```json
{
  "api_url": "http://localhost:8009",
  "timeout": 30,
  "top_k": 5,
  "input_format": "documents",
  "output_format": "simple"
}
```

### Конфигурация с автоопределением

```json
{
  "api_url": "http://localhost:8009",
  "timeout": 30,
  "top_k": 5,
  "input_format": "auto",
  "output_format": "standard"
}
```

## Программное использование

### Пример 1: Использование формата `documents`

```python
from main import rerank

config = {
    "api_url": "http://localhost:8009",
    "input_format": "documents",  # Использовать поле "documents"
    "output_format": "simple"     # Упрощенный формат ответа
}

results = rerank(
    query="search query",
    documents=["doc1", "doc2", "doc3"],
    config=config
)
```

### Пример 2: Использование формата `passages`

```python
from main import rerank

config = {
    "api_url": "http://localhost:8009",
    "input_format": "passages",   # Использовать поле "passages"
    "output_format": "standard"    # Полный формат с индексом
}

results = rerank(
    query="search query",
    documents=["doc1", "doc2", "doc3"],
    config=config
)
```

## Автоматическое определение

При использовании `input_format: "auto"`:

- Расширение по умолчанию использует `passages` (формат нашего API)
- Это обеспечивает совместимость с нашим API из коробки
- Если нужно использовать другой формат, явно укажите его

## Рекомендации

### Для использования с нашим API:

```json
{
  "input_format": "passages",
  "output_format": "standard"
}
```

### Для использования с Dify:

```json
{
  "input_format": "documents",
  "output_format": "simple"
}
```

### Для максимальной совместимости:

```json
{
  "input_format": "auto",
  "output_format": "standard"
}
```

## Устранение проблем

### Ошибка: "Unknown field 'documents'"

**Причина:** API ожидает поле `passages`, а отправляется `documents`

**Решение:** Измените `input_format` на `"passages"` или используйте `"auto"`

### Ошибка: "Unknown field 'passages'"

**Причина:** API ожидает поле `documents`, а отправляется `passages`

**Решение:** Измените `input_format` на `"documents"`

### Несовместимость формата ответа

**Причина:** Система ожидает другой формат ответа

**Решение:** Измените `output_format` на `"simple"` или `"standard"` в зависимости от требований

## Дополнительная информация

- См. `README.md` для полной документации
- См. `main.py` для реализации логики форматов
- См. `manifest.json` для схемы конфигурации

