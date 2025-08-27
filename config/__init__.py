"""
Módulo de configuración de la aplicación
"""

from .settings import *

__all__ = [
    'BASE_DIR', 'DEBUG', 'SECRET_KEY', 'MAX_FILE_SIZE', 'ALLOWED_EXTENSIONS',
    'REQUIRED_COLUMNS', 'FACULTY_FILTER', 'MIN_GRADE', 'MAX_GRADE',
    'LOG_LEVEL', 'LOG_FILE', 'VERCEL_DEPLOYMENT'
]

