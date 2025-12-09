#!/usr/bin/env python3
"""
Скрипт для упаковки расширения BGE Reranker для Dify
"""

import os
import zipfile
import shutil
from pathlib import Path

def pack_extension():
    """Упаковывает расширение в .difypkg файл"""
    
    # Определяем пути
    script_dir = Path(__file__).parent
    extension_name = "bge-reranker-extension"
    output_file = script_dir / f"{extension_name}.difypkg"
    
    # Файлы для включения в пакет
    files_to_include = [
        "manifest.json",
        "main.py",
        "provider_registry.py",
        "requirements.txt",
        "README.md",
        "__init__.py",
        "INSTALL.md"
    ]
    
    print(f"Упаковка расширения в {output_file}...")
    
    # Удаляем старый файл, если существует
    if output_file.exists():
        output_file.unlink()
        print("Удален старый пакет")
    
    # Создаем ZIP архив
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in files_to_include:
            file_path = script_dir / file_name
            if file_path.exists():
                zipf.write(file_path, file_name)
                print(f"  ✓ Добавлен: {file_name}")
            else:
                print(f"  ✗ Пропущен (не найден): {file_name}")
    
    # Проверяем размер файла
    file_size = output_file.stat().st_size
    print(f"\n✓ Расширение упаковано успешно!")
    print(f"  Файл: {output_file}")
    print(f"  Размер: {file_size / 1024:.2f} KB")
    print(f"\nТеперь вы можете загрузить этот файл в Dify через веб-интерфейс.")

if __name__ == "__main__":
    try:
        pack_extension()
    except Exception as e:
        print(f"Ошибка при упаковке: {e}")
        exit(1)

