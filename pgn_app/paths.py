from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]          # repo root
DATA_DIR = BASE_DIR / "datasets"
DATA_APP_DIR = DATA_DIR / "app"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
DICTS_DIR = BASE_DIR / "dicts"
