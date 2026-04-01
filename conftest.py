import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'blogicum'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')