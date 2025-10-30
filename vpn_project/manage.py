#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys  # <-- 1. ДОБАВЛЕНО

def main():
    """Run administrative tasks."""

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    # 2. Добавляем корневой каталог проекта (где лежит этот manage.py) в sys.path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    # 3. Это гарантирует, что Python сможет найти 'vpn_project'
    sys.path.insert(0, PROJECT_ROOT)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    # 4. Эта строка у вас уже есть
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vpn_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()