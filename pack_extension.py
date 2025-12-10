#!/usr/bin/env python3
"""
Скрипт для упаковки и подписи плагина BGE Reranker для Dify
Использует официальный инструмент Dify CLI для подписи
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path

def check_dify_cli():
    """Проверяет наличие Dify CLI"""
    # Пробуем разные варианты команды
    commands_to_try = [
        ["dify", "--version"],
        ["dify-cli", "--version"],
        ["python", "-m", "dify", "--version"],
        ["python", "-m", "dify_cli", "--version"],
    ]
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Dify CLI найден: {result.stdout.strip()}")
                # Возвращаем базовую команду для использования
                if cmd[0] == "python":
                    return ["python", "-m", cmd[2]]
                else:
                    return [cmd[0]]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("✗ Dify CLI не найден!")
    print("\nПопробуйте установить одним из способов:")
    print("  1. pip install dify-cli")
    print("  2. pip install dify-plugin-toolkit")
    print("  3. Или скачайте официальный инструмент с GitHub")
    print("\nАльтернатива: Для локальной разработки можно отключить проверку подписи в Dify")
    return None

def pack_plugin():
    """Упаковывает плагин в .difypkg файл"""
    
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

    # Файлы для включения
    files_map = {
        "manifest.yaml": "manifest.yaml",
        "_assets/icon.svg": "_assets/icon.svg",
        "provider/bge_reranker.yaml": "provider/bge_reranker.yaml",
        "provider/bge_reranker.py": "provider/bge_reranker.py",
        "models/rerank/rerank.py": "models/rerank/rerank.py",
        "models/rerank/__init__.py": "models/rerank/__init__.py",
        "models/__init__.py": "models/__init__.py",
        "requirements.txt": "requirements.txt",
        "README.md": "README.md",
        "main.py": "main.py",
        "__init__.py": "__init__.py",
    }
    
    print(f"Упаковка плагина в {output_file}...")
    
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
    print(f"\n✓ Плагин упакован успешно!")
    print(f"  Файл: {output_file}")
    print(f"  Размер: {file_size / 1024:.2f} KB")
    
    return output_file

def sign_plugin(plugin_file: Path, private_key: Path = None):
    """Подписывает плагин используя Dify CLI"""
    
    dify_cmd = check_dify_cli()
    if not dify_cmd:
        print("\n⚠ Плагин упакован, но не подписан.")
        print("\nДля локальной разработки:")
        print("  1. Отключите проверку подписи в Dify (docker-compose.override.yaml)")
        print("  2. Или установите Dify CLI для подписи")
        return None
    
    # Если ключ не указан, пытаемся найти или создать
    if private_key is None:
        key_name = "bge_reranker_key"
        private_key = Path(__file__).parent / f"{key_name}.private.pem"
        
        if not private_key.exists():
            print(f"\nГенерация пары ключей: {key_name}...")
            try:
                # Используем команду из check_dify_cli
                cmd = dify_cmd + ["signature", "generate", "-f", str(key_name)]
                
                result = subprocess.run(
                    cmd,
                    cwd=Path(__file__).parent,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"✓ Ключи созданы: {key_name}.private.pem и {key_name}.public.pem")
                else:
                    print(f"✗ Ошибка создания ключей:")
                    print(f"  Команда: {' '.join(cmd)}")
                    print(f"  Статус: {result.returncode}")
                    print(f"  Вывод: {result.stdout}")
                    print(f"  Ошибки: {result.stderr}")
                    return None
            except Exception as e:
                print(f"✗ Ошибка при генерации ключей: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    if not private_key.exists():
        print(f"✗ Приватный ключ не найден: {private_key}")
        return None
    
    # Подписываем плагин
    signed_file = plugin_file.parent / f"{plugin_file.stem}.signed.difypkg"
    print(f"\nПодписание плагина...")
    print(f"  Ключ: {private_key}")
    print(f"  Команда: {dify_cmd}")
    
    try:
        # Используем команду из check_dify_cli
        cmd = dify_cmd + ["signature", "sign", str(plugin_file), "-p", str(private_key)]
        
        print(f"  Выполняется: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if signed_file.exists():
                print(f"✓ Плагин подписан успешно!")
                print(f"  Подписанный файл: {signed_file}")
                print(f"\n📝 Важно:")
                public_key = private_key.parent / private_key.name.replace('.private', '.public')
                print(f"  1. Публичный ключ: {public_key}")
                print(f"  2. Разместите публичный ключ в Dify для проверки подписи")
                print(f"  3. Или отключите проверку подписи в настройках Dify для разработки")
                return signed_file
            else:
                print(f"⚠ Подпись выполнена, но файл не найден: {signed_file}")
                print(f"  Проверьте вывод команды:")
                print(f"  {result.stdout}")
        else:
            print(f"✗ Ошибка подписи:")
            print(f"  Команда: {' '.join(cmd)}")
            print(f"  Статус: {result.returncode}")
            print(f"  Вывод: {result.stdout}")
            print(f"  Ошибки: {result.stderr}")
    except Exception as e:
        print(f"✗ Ошибка при подписи: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def main():
    """Главная функция"""
    print("=" * 60)
    print("Dify Plugin Packager & Signer")
    print("=" * 60)
    
    # Упаковка
    plugin_file = pack_plugin()
    if not plugin_file:
        print("✗ Ошибка упаковки плагина")
        sys.exit(1)
    
    # Подпись (опционально)
    print("\n" + "=" * 60)
    signed_file = sign_plugin(plugin_file)
    
    if signed_file:
        print(f"\n✅ Готово! Используйте файл: {signed_file.name}")
    else:
        print(f"\n✅ Плагин упакован: {plugin_file.name}")
        print("   (Для продакшена требуется подпись)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        sys.exit(1)
