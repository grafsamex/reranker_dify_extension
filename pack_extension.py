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
    
    script_dir = Path(__file__).parent
    plugin_id = "bge-reranker-extension"
    output_file = script_dir / f"{plugin_id}.difypkg"
    
    # Создаем __init__.py файлы если нет
    for init_path in [
        script_dir / "models" / "__init__.py",
        script_dir / "models" / "rerank" / "__init__.py",
    ]:
        if not init_path.exists():
            init_path.parent.mkdir(parents=True, exist_ok=True)
            init_path.touch()

    # Файлы для включения (путь_в_проекте, путь_в_архиве)
    files_map = {
        "manifest.yaml": "manifest.yaml",
        "_assets/icon.svg": "_assets/icon.svg",
        "provider/bge_reranker.yaml": "provider/bge_reranker.yaml",
        "models/rerank/rerank.py": "models/rerank/rerank.py",
        "models/rerank/__init__.py": "models/rerank/__init__.py",
        "models/__init__.py": "models/__init__.py",
        "requirements.txt": "requirements.txt",
        "README.md": "README.md",
    }
    
    print(f"Упаковка расширения в {output_file}...")
    
    if output_file.exists():
        output_file.unlink()
        print("Удален старый пакет")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for src_rel, dst_rel in files_map.items():
            src_path = script_dir / src_rel
            if src_path.exists():
                zipf.write(src_path, dst_rel)
                print(f"  ✓ Добавлен: {dst_rel}")
            else:
                print(f"  ✗ Пропущен: {src_rel}")
                
        print("\nПроверка содержимого архива:")
        for info in zipf.infolist():
            print(f"  - {info.filename} ({info.file_size} bytes)")
    
    file_size = output_file.stat().st_size
    print(f"\n✓ Расширение упаковано успешно!")
    print(f"  Файл: {output_file}")
    print(f"  Размер: {file_size / 1024:.2f} KB")

if __name__ == "__main__":
    try:
        pack_extension()
    except Exception as e:
        print(f"Ошибка при упаковке: {e}")
        exit(1)
