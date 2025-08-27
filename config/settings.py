"""
Configuración centralizada de la aplicación
"""
import os
from pathlib import Path

# Configuración base
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuración de archivos
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
UPLOAD_FOLDER = BASE_DIR / 'uploads'
TEMP_FOLDER = BASE_DIR / 'temp'

# Configuración de procesamiento
REQUIRED_COLUMNS = [
    'Legajo', 'Nota', 'Promocionado', 'Apellido', 
    'Nombre', 'DNI', 'Edicion', 'Fecha de inicio', 'Facultad regional'
]
FACULTY_FILTER = ['FRBA', 'UTN FRBA']
MIN_GRADE = 1
MAX_GRADE = 10

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configuración de Vercel
VERCEL_DEPLOYMENT = os.getenv('VERCEL', 'False').lower() == 'true'

