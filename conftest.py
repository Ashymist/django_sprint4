import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Ensure Django package imports work even when pytest runs from a different cwd.
for path in (PROJECT_ROOT, PROJECT_ROOT / 'blogicum'):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')
