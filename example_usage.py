"""
Пример использования BGE Reranker Extension
"""

import os
import sys

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

from main import rerank, BGEReranker, validate_config

def example_basic_usage():
    """Базовый пример использования"""
    print("=== Базовый пример использования ===\n")
    
    query = "машинное обучение"
    documents = [
        "Машинное обучение - это раздел искусственного интеллекта, который изучает алгоритмы и статистические модели",
        "Python - популярный язык программирования, используемый в data science",
        "Нейронные сети используются в глубоком обучении для решения сложных задач",
        "FastAPI - современный фреймворк для создания API на Python",
        "Базы данных хранят структурированную информацию для приложений"
    ]
    
    config = {
        "api_url": "http://localhost:8009",
        "timeout": 30,
        "top_k": 3
    }
    
    print(f"Запрос: {query}\n")
    print(f"Документов для ранжирования: {len(documents)}\n")
    
    try:
        results = rerank(query, documents, config)
        
        print("Результаты ранжирования (топ-3):\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Document: {result['document'][:80]}...")
            print(f"   Index: {result['index']}\n")
            
    except Exception as e:
        print(f"Ошибка: {e}")


def example_with_reranker_class():
    """Пример использования класса BGEReranker напрямую"""
    print("=== Пример использования класса BGEReranker ===\n")
    
    # Инициализация клиента
    reranker = BGEReranker(
        api_url="http://localhost:8009",
        timeout=30,
        top_k=5
    )
    
    # Проверка работоспособности
    print("Проверка работоспособности сервиса...")
    health = reranker.health_check()
    print(f"Статус: {health}\n")
    
    if health.get("status") != "ok":
        print("Сервис недоступен. Убедитесь, что Reranker API запущен.")
        return
    
    # Ранжирование
    query = "искусственный интеллект"
    documents = [
        "Искусственный интеллект - это технология будущего",
        "Погода сегодня солнечная и теплая",
        "AI помогает решать сложные задачи автоматизации",
        "Рецепт пирога с яблоками требует муки и сахара"
    ]
    
    print(f"Запрос: {query}\n")
    
    try:
        results = reranker.rerank(query, documents)
        
        print("Результаты:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   {result['document']}\n")
            
    except Exception as e:
        print(f"Ошибка: {e}")


def example_config_validation():
    """Пример валидации конфигурации"""
    print("=== Пример валидации конфигурации ===\n")
    
    # Правильная конфигурация
    good_config = {
        "api_url": "http://localhost:8009",
        "timeout": 30,
        "top_k": 5
    }
    
    try:
        validated = validate_config(good_config)
        print("✓ Конфигурация валидна:")
        print(f"  {validated}\n")
    except Exception as e:
        print(f"✗ Ошибка валидации: {e}\n")
    
    # Неправильная конфигурация
    bad_config = {
        "api_url": "",
        "timeout": -1,
        "top_k": 200
    }
    
    try:
        validated = validate_config(bad_config)
        print("✓ Конфигурация валидна:")
        print(f"  {validated}\n")
    except Exception as e:
        print(f"✗ Ошибка валидации (ожидаемо): {e}\n")


if __name__ == "__main__":
    print("Примеры использования BGE Reranker Extension\n")
    print("=" * 50 + "\n")
    
    # Запускаем примеры
    try:
        example_config_validation()
        example_basic_usage()
        example_with_reranker_class()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

