from pathlib import Path

# Directorios
MODEL_DIR = "model"
DATA_DIR = "data"
TEMP_DIR = "tmp"
OUT_DIR = "out"

# Rutas
BASE_DIR = Path(__file__).resolve().parent  # Directorio del script
DATA_PATH = BASE_DIR / DATA_DIR
MODEL_PATH = BASE_DIR / MODEL_DIR
TEMP_PATH = BASE_DIR / TEMP_DIR
OUT_PATH = BASE_DIR / OUT_DIR

# URL
URL_WEB = "https://www.3dcp.com.ar/eshop/catalogue/"
