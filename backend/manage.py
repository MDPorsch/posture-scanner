#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scanner.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import Django. "
            "Make sure your virtual env is active and run: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
