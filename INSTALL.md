# Инструкция по установке BGE Reranker Extension для Dify

## Шаг 1: Подготовка Reranker API сервера

Перед установкой расширения необходимо развернуть сервис BGE Reranker API.

### Вариант A: Использование Docker Compose (рекомендуется)

```bash
# Перейдите в корневую директорию проекта
cd /path/to/reranker

# Запустите сервис
docker-compose up -d

# Проверьте, что сервис работает
curl http://localhost:8009/health
```

### Вариант B: Ручная сборка Docker образа

```bash
# Соберите образ
docker build -t bge-reranker .

# Запустите контейнер
docker run -d \
  --name bge-reranker \
  -p 8009:8009 \
  --gpus all \
  bge-reranker

# Проверьте статус
curl http://localhost:8009/health
```

### Вариант C: Локальная установка (для разработки)

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите сервис
python app.py
# или
uvicorn app:app --host 0.0.0.0 --port 8009
```

## Шаг 2: Проверка доступности API

Убедитесь, что API доступен:

```bash
# Проверка health endpoint
curl http://your-server:8009/health

# Ожидаемый ответ:
# {
#   "status": "ok",
#   "model": "BAAI/bge-reranker-v2-m3",
#   "device": "cuda"
# }
```

## Шаг 3: Упаковка расширения

### Вариант A: Использование ZIP (для .difypkg)

```bash
# Перейдите в папку расширения
cd rerank

# Создайте ZIP архив
zip -r bge-reranker-extension.difypkg \
  manifest.json \
  main.py \
  requirements.txt \
  README.md \
  __init__.py \
  INSTALL.md

# Или используйте Python
python -m zipfile -c bge-reranker-extension.difypkg \
  manifest.json main.py requirements.txt README.md __init__.py INSTALL.md
```

### Вариант B: Использование tar.gz

```bash
cd rerank
tar -czf bge-reranker-extension.tar.gz \
  manifest.json \
  main.py \
  requirements.txt \
  README.md \
  __init__.py \
  INSTALL.md
```

## Шаг 4: Установка в Dify

### Через веб-интерфейс:

1. **Войдите в Dify** как администратор
2. **Перейдите в раздел Extensions/Plugins:**
   - Обычно находится в Settings → Extensions
   - Или в разделе Marketplace/Plugins
3. **Выберите "Install from Local Package"** или "Upload Extension"
4. **Загрузите файл:**
   - `bge-reranker-extension.difypkg` (если используется ZIP)
   - Или `bge-reranker-extension.tar.gz` (если используется tar.gz)
5. **Дождитесь установки** - Dify автоматически установит зависимости

### Через командную строку (если поддерживается):

```bash
# Если Dify поддерживает CLI установку
dify-cli extension install bge-reranker-extension.difypkg
```

## Шаг 5: Настройка расширения

После установки настройте расширение:

1. **Откройте настройки расширения** в Dify
2. **Укажите URL вашего Reranker API:**
   ```
   http://your-server:8009
   ```
   или
   ```
   https://your-domain.com:8009
   ```
3. **Настройте параметры:**
   - **Timeout:** 30 (секунды)
   - **Top K:** 5 (количество результатов)
4. **Сохраните настройки**

## Шаг 6: Тестирование

### Тест 1: Проверка установки

В интерфейсе Dify проверьте, что расширение появилось в списке установленных.

### Тест 2: Проверка подключения

Используйте тестовую функцию в настройках расширения (если доступна) или создайте тестовый workflow.

### Тест 3: Использование в Workflow

1. Создайте новый Workflow в Dify
2. Добавьте узел поиска документов
3. Добавьте узел Reranker
4. Подключите выход поиска к входу Reranker
5. Запустите workflow и проверьте результаты

## Устранение проблем

### Проблема: Расширение не загружается

**Решение:**
- Проверьте формат файла (должен быть .difypkg или .tar.gz)
- Убедитесь, что все файлы включены в архив
- Проверьте права доступа к файлу

### Проблема: Ошибка при установке зависимостей

**Решение:**
- Убедитесь, что на сервере Dify установлен Python 3.11+
- Проверьте доступ к PyPI для установки пакетов
- Установите зависимости вручную: `pip install requests>=2.31.0`

### Проблема: Не удается подключиться к API

**Решение:**
- Проверьте, что Reranker API запущен: `curl http://your-server:8009/health`
- Убедитесь, что URL в настройках правильный
- Проверьте сетевые настройки и файрвол
- Убедитесь, что Dify может достичь сервера Reranker API

### Проблема: Таймаут при использовании

**Решение:**
- Увеличьте значение timeout в настройках
- Проверьте производительность сервера Reranker API
- Убедитесь, что GPU доступен (для ускорения)

## Проверка версий

Убедитесь в совместимости версий:

- **Dify:** версия с поддержкой расширений
- **Reranker API:** 1.0+
- **Python:** 3.11+ (на сервере Dify)
- **requests:** 2.31.0+

## Дополнительная информация

- Основная документация: см. `README.md`
- API документация: см. `../API_DOCUMENTATION.md`
- Совместимость с Dify: см. `../DIFY_COMPATIBILITY.md`

## Поддержка

При возникновении проблем:
1. Проверьте логи Dify
2. Проверьте логи Reranker API
3. Убедитесь, что все сервисы запущены
4. Проверьте конфигурацию

