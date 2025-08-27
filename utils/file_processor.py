"""
Módulo para el procesamiento de archivos Excel
"""
import pandas as pd
import io
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from werkzeug.utils import secure_filename
from config.settings import (
    ALLOWED_EXTENSIONS, REQUIRED_COLUMNS, FACULTY_FILTER,
    MIN_GRADE, MAX_GRADE
)

logger = logging.getLogger(__name__)

class FileProcessor:
    """Clase para procesar archivos Excel y generar CSVs"""
    
    def __init__(self):
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.required_columns = REQUIRED_COLUMNS
        self.faculty_filter = FACULTY_FILTER
        self.min_grade = MIN_GRADE
        self.max_grade = MAX_GRADE
    
    def validate_file_extension(self, filename: str) -> bool:
        """Validar extensión del archivo"""
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.allowed_extensions
    
    def validate_file_size(self, file_size: int, max_size: int) -> bool:
        """Validar tamaño del archivo"""
        return file_size <= max_size
    
    def read_excel_file(self, file_stream) -> Optional[pd.DataFrame]:
        """Leer archivo Excel y retornar DataFrame"""
        try:
            df = pd.read_excel(file_stream, engine='openpyxl')
            logger.info(f"Archivo Excel leído exitosamente. Filas: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"Error al leer archivo Excel: {str(e)}")
            return None
    
    def validate_excel_structure(self, df: pd.DataFrame) -> Tuple[bool, list]:
        """Validar estructura del DataFrame y retornar lista de errores específicos"""
        errores = []
        
        if df.empty:
            errores.append("El archivo está vacío")
            return False, errores
        
        # Validar número de columnas
        if len(df.columns) != len(self.required_columns):
            errores.append(f"El archivo tiene {len(df.columns)} columnas, debe tener exactamente {len(self.required_columns)}")
        
        # Verificar nombres y orden de columnas (case-insensitive)
        df_columns = [str(col).strip() for col in df.columns]
        required_cols = [col.strip() for col in self.required_columns]
        
        for i, (df_col, req_col) in enumerate(zip(df_columns, required_cols)):
            # Comparar ignorando mayúsculas/minúsculas
            if df_col.lower() != req_col.lower():
                errores.append(f"La columna {i+1} debe ser '{req_col}', pero es '{df_col}' (diferencia de mayúsculas/minúsculas)")
        
        # Si hay más columnas de las esperadas
        if len(df_columns) > len(required_cols):
            extra_cols = df_columns[len(required_cols):]
            errores.append(f"Columnas adicionales no permitidas: {', '.join(extra_cols)}")
        
        return len(errores) == 0, errores
    
    def filter_faculty_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtrar datos por facultad"""
        faculty_col = 'Facultad regional'
        
        if faculty_col not in df.columns:
            logger.warning(f"Columna '{faculty_col}' no encontrada")
            return df
        
        # Filtrar registros que coincidan exactamente con FRBA o UTN FRBA
        faculty_mask = df[faculty_col].astype(str).str.strip().str.lower().isin([
            'frba', 'utn frba'
        ])
        filtered_df = df[faculty_mask]
        
        logger.info(f"Registros filtrados por facultad: {len(filtered_df)} de {len(df)}")
        logger.info(f"Filtros aplicados: {self.faculty_filter}")
        return filtered_df
    
    def validate_data_content(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """Validar contenido de los datos y retornar registros válidos e inválidos"""
        errores = []
        valid_records = []
        
        logger.info(f"Iniciando validación de contenido para {len(df)} filas")
        
        # Crear un mapeo case-insensitive de nombres de columnas
        column_mapping = {col.lower(): col for col in df.columns}
        
        for idx, row in df.iterrows():
            row_errors = []
            
            # Validar facultad (case-insensitive) - más flexible
            faculty_col = self._find_column_case_insensitive(df, 'Facultad regional')
            if faculty_col:
                faculty_value = str(row[faculty_col]).strip()
                if not faculty_value or faculty_value == 'nan':
                    row_errors.append(f"Facultad está vacía")
                # Removemos la validación estricta de FRBA para ser más flexible
            
            # Validar nota (case-insensitive)
            nota_col = self._find_column_case_insensitive(df, 'Nota')
            if nota_col:
                nota_value = str(row[nota_col]).strip()
                
                # Valores especiales que son válidos
                special_values = ['-', 'ausente', 'equivalencia', 'equivalente', 'aprobado', 'desaprobado']
                if nota_value.lower() in special_values:
                    # Es un valor especial válido, no necesita validación numérica
                    pass
                else:
                    try:
                        grade = float(nota_value)
                        if grade < self.min_grade or grade > self.max_grade:
                            row_errors.append(f"Nota {grade} fuera del rango {self.min_grade}-{self.max_grade}")
                    except (ValueError, TypeError):
                        row_errors.append(f"Nota '{nota_value}' no es un número válido ni un valor especial permitido")
            
            # Validar DNI (case-insensitive)
            dni_col = self._find_column_case_insensitive(df, 'DNI')
            if dni_col:
                dni_value = str(row[dni_col]).strip()
                if not dni_value or not dni_value.isdigit() or len(dni_value) < 7:
                    row_errors.append(f"DNI '{dni_value}' no es válido (debe ser numérico y tener al menos 7 dígitos)")
            
            # Validar fecha (case-insensitive)
            fecha_col = self._find_column_case_insensitive(df, 'Fecha de inicio')
            if fecha_col:
                fecha_value = str(row[fecha_col]).strip()
                if fecha_value and fecha_value != 'nan':
                    # Validar formato de fecha flexible
                    if not self._is_valid_date_format(fecha_value):
                        row_errors.append(f"Fecha '{fecha_value}' no tiene formato válido (acepta DD/MM/YYYY, YYYY-MM-DD, etc.)")
            
            # Validar campos obligatorios (case-insensitive)
            required_fields = ['Apellido', 'Nombre']  # Removemos 'Legajo' de los campos obligatorios
            for field in required_fields:
                field_col = self._find_column_case_insensitive(df, field)
                if field_col:
                    field_value = str(row[field_col]).strip()
                    if not field_value or field_value == 'nan':
                        row_errors.append(f"Campo '{field}' está vacío")
            
            if row_errors:
                errores.append({
                    'fila': idx + 1,
                    'errores': row_errors
                })
                logger.debug(f"Fila {idx + 1} tiene errores: {row_errors}")
            else:
                valid_records.append(row)
        
        valid_df = pd.DataFrame(valid_records) if valid_records else pd.DataFrame()
        
        # Resetear índices para eliminar filas vacías
        if not valid_df.empty:
            valid_df = valid_df.reset_index(drop=True)
        
        logger.info(f"Validación completada: {len(valid_df)} registros válidos, {len(errores)} filas con errores")
        if errores:
            logger.info(f"Primeros 3 errores: {errores[:3]}")
        
        # Consolidar errores para hacerlos más concisos
        consolidated_errors = self._consolidate_errors(errores)
        
        return valid_df, consolidated_errors
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Validar formato de fecha flexible - acepta múltiples formatos"""
        import re
        from datetime import datetime
        
        # Si es NaN o vacío, es válido (opcional)
        if not date_str or date_str == 'nan' or date_str == 'None':
            return True
        
        # Patrones de fecha que aceptamos
        patterns = [
            r'^\d{1,2}/\d{1,2}/\d{4}$',  # DD/MM/YYYY
            r'^\d{4}-\d{1,2}-\d{1,2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$',  # YYYY-MM-DD HH:MM:SS
            r'^\d{1,2}-\d{1,2}-\d{4}$',  # DD-MM-YYYY
            r'^\d{1,2}/\d{1,2}/\d{2}$',  # DD/MM/YY
            r'^\d{4}/\d{1,2}/\d{1,2}$',  # YYYY/MM/DD
        ]
        
        # Verificar si coincide con algún patrón
        for pattern in patterns:
            if re.match(pattern, date_str):
                return True
        
        # Intentar parsear con pandas datetime (más flexible)
        try:
            pd.to_datetime(date_str, errors='raise')
            return True
        except:
            pass
        
        return False
    
    def _find_column_case_insensitive(self, df: pd.DataFrame, column_name: str) -> str:
        """Buscar una columna ignorando mayúsculas/minúsculas"""
        column_name_lower = column_name.lower()
        for col in df.columns:
            if col.lower() == column_name_lower:
                return col
        return None
    
    def _consolidate_errors(self, errores: list) -> list:
        """Consolidar errores para hacerlos más concisos y útiles"""
        if not errores:
            return []
        
        # Contar tipos de errores
        error_types = {}
        total_rows_with_errors = len(errores)
        
        for error in errores:
            for error_msg in error['errores']:
                if error_msg not in error_types:
                    error_types[error_msg] = []
                error_types[error_msg].append(error['fila'])
        
        # Crear mensajes consolidados
        consolidated = []
        
        for error_msg, rows in error_types.items():
            if len(rows) == 1:
                # Solo una fila con este error
                consolidated.append(f"Fila {rows[0]}: {error_msg}")
            elif len(rows) <= 5:
                # Pocas filas, mostrar todas
                rows_str = ', '.join(map(str, rows))
                consolidated.append(f"Filas {rows_str}: {error_msg}")
            else:
                # Muchas filas, mostrar resumen
                first_rows = rows[:3]
                remaining = len(rows) - 3
                rows_str = ', '.join(map(str, first_rows))
                if remaining > 0:
                    consolidated.append(f"Filas {rows_str} y {remaining} más: {error_msg}")
                else:
                    consolidated.append(f"Filas {rows_str}: {error_msg}")
        
        # Agregar resumen general si hay muchos errores
        if total_rows_with_errors > 10:
            consolidated.insert(0, f"⚠️ Se encontraron errores en {total_rows_with_errors} filas del archivo.")
        
        return consolidated
    
    def validate_grades(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """Validar notas y retornar registros válidos e inválidos"""
        grade_col = 'Nota'
        valid_records = []
        invalid_records = []
        
        for idx, row in df.iterrows():
            try:
                grade = float(row[grade_col])
                if self.min_grade <= grade <= self.max_grade:
                    valid_records.append(row)
                else:
                    invalid_records.append({
                        'row': idx + 1,
                        'grade': grade,
                        'reason': f'Nota fuera del rango {self.min_grade}-{self.max_grade}'
                    })
            except (ValueError, TypeError):
                invalid_records.append({
                    'row': idx + 1,
                    'grade': row[grade_col],
                    'reason': 'Nota no es un número válido'
                })
        
        valid_df = pd.DataFrame(valid_records) if valid_records else pd.DataFrame()
        
        # Resetear índices para eliminar filas vacías
        if not valid_df.empty:
            valid_df = valid_df.reset_index(drop=True)
        
        logger.info(f"Notas válidas: {len(valid_df)}, inválidas: {len(invalid_records)}")
        return valid_df, invalid_records
    
    def process_excel_file(self, file_stream, filename: str, form_data: dict = None) -> Dict[str, Any]:
        """Procesar archivo Excel completo"""
        try:
            logger.info(f"Iniciando procesamiento del archivo: {filename}")
            
            # Validar extensión
            if not self.validate_file_extension(filename):
                logger.warning(f"Extensión de archivo no válida: {filename}")
                return {
                    'success': False,
                    'error': f"Formato de archivo no válido. Formatos permitidos: {', '.join(self.allowed_extensions)}",
                    'detailed_errors': []
                }
            
            # Leer archivo
            df = self.read_excel_file(file_stream)
            if df is None:
                logger.error("No se pudo leer el archivo Excel")
                return {
                    'success': False,
                    'error': "No se pudo leer el archivo Excel",
                    'detailed_errors': []
                }
            
            logger.info(f"Archivo leído exitosamente. Columnas: {list(df.columns)}, Filas: {len(df)}")
            logger.info(f"Columnas esperadas: {self.required_columns}")
            
            # Validar estructura
            is_valid, structure_errors = self.validate_excel_structure(df)
            if not is_valid:
                logger.warning(f"Errores de estructura encontrados: {structure_errors}")
                return {
                    'success': False,
                    'error': "El archivo no tiene la estructura correcta",
                    'detailed_errors': structure_errors
                }
            
            logger.info("Estructura del archivo válida")
            
            # Filtrar por facultad
            filtered_df = self.filter_faculty_data(df)
            logger.info(f"Filtrado por facultad: {len(filtered_df)} registros de {len(df)} originales")
            
            # Validar contenido de datos
            valid_df, content_errors = self.validate_data_content(filtered_df)
            logger.info(f"Validación de contenido: {len(valid_df)} registros válidos, {len(content_errors)} errores")
            
            if valid_df.empty:
                logger.warning("No se encontraron registros válidos")
                return {
                    'success': False,
                    'error': "No se encontraron registros válidos en el archivo",
                    'detailed_errors': content_errors
                }
            
            # Generar CSVs con los datos del formulario
            alumnos_csv = self.generate_alumnos_csv(valid_df, form_data)
            notas_csv = self.generate_notas_csv(valid_df, form_data)
            
            logger.info(f"Procesamiento exitoso: {len(valid_df)} registros procesados")
            
            return {
                'success': True,
                'alumnos_csv': alumnos_csv,
                'notas_csv': notas_csv,
                'total_records': len(valid_df),
                'content_errors': content_errors
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}")
            return {
                'success': False,
                'error': f"Error interno del servidor: {str(e)}",
                'detailed_errors': []
            }
    
    def generate_alumnos_csv(self, df: pd.DataFrame, form_data: dict = None) -> str:
        """Generar CSV de alumnos con formato correcto"""
        try:
            # Buscar columnas de forma case-insensitive
            dni_col = self._find_column_case_insensitive(df, 'DNI')
            
            if not dni_col:
                raise ValueError("No se encontró la columna DNI necesaria para el CSV de alumnos")
            
            # Crear DataFrame con el formato correcto para alumnos
            # Usar datos de ejemplo o valores por defecto para los campos requeridos
            alumnos_data = []
            
            # Obtener valores del formulario o usar valores por defecto
            propuesta = form_data.get('campo1', 'asdasdasd') if form_data else 'asdasdasd'
            comision = form_data.get('campo2', 'asdasdasdas') if form_data else 'asdasdasdas'
            actividad = form_data.get('campo3', 'dasdasada') if form_data else 'dasdasada'
            periodo = form_data.get('campo4', 'asdasdadasd') if form_data else 'asdasdadasd'
            
            # Generar CSV manualmente para evitar problemas con pandas
            csv_lines = []
            csv_lines.append("DNI,Propuesta,Comision,Actividad,Periodo Lectivo")
            
            for idx, row in df.iterrows():
                dni_value = str(row[dni_col]).strip()
                if dni_value and dni_value != 'nan':
                    csv_line = f"{dni_value},{propuesta},{comision},{actividad},{periodo}"
                    csv_lines.append(csv_line)
            
            csv_content = '\n'.join(csv_lines)
            
            logger.info(f"CSV de alumnos generado: {len(csv_lines)-1} registros")
            logger.info(f"Contenido del CSV (primeras 3 líneas): {csv_lines[:3]}")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error generando CSV de alumnos: {str(e)}")
            raise
    
    def generate_notas_csv(self, df: pd.DataFrame, form_data: dict = None) -> str:
        """Generar CSV de notas con formato correcto"""
        try:
            # Buscar columnas de forma case-insensitive
            dni_col = self._find_column_case_insensitive(df, 'DNI')
            nota_col = self._find_column_case_insensitive(df, 'Nota')
            
            if not dni_col:
                raise ValueError("No se encontró la columna DNI necesaria para el CSV de notas")
            
            # Crear DataFrame con el formato correcto para notas
            notas_data = []
            
            # Obtener valores del formulario o usar valores por defecto
            fecha_regularidad = form_data.get('campo5', '12/31/2312') if form_data else '12/31/2312'
            fecha_promocion = form_data.get('campo6', '13/12/3131') if form_data else '13/12/3131'
            
            # Generar CSV manualmente para evitar problemas con pandas
            csv_lines = []
            csv_lines.append("documento,nota_regularidad,fecha_regularidad,nota_promocion,fecha_promocion")
            
            for idx, row in df.iterrows():
                dni_value = str(row[dni_col]).strip()
                nota_value = str(row[nota_col]).strip() if nota_col else '9'
                
                if dni_value and dni_value != 'nan':
                    csv_line = f"{dni_value},{nota_value},{fecha_regularidad},{nota_value},{fecha_promocion}"
                    csv_lines.append(csv_line)
            
            csv_content = '\n'.join(csv_lines)
            
            logger.info(f"CSV de notas generado: {len(csv_lines)-1} registros")
            logger.info(f"Contenido del CSV (primeras 3 líneas): {csv_lines[:3]}")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error generando CSV de notas: {str(e)}")
            raise

