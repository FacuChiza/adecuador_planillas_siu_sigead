"""
Aplicación principal Flask para el procesamiento de planillas SIU
"""
import os
import logging
import tempfile
import uuid
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template, send_file, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
from io import BytesIO

from config.settings import *
from utils.file_processor import FileProcessor

# Diccionario global para almacenar archivos temporales
temp_files = {}

def setup_logging(app):
    """Configurar logging de la aplicación"""
    if not app.debug:
        # Crear directorio de logs si no existe
        log_dir = BASE_DIR / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Configurar handler de archivo
        file_handler = RotatingFileHandler(
            LOG_FILE, 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Aplicación iniciada')

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'simple-secret-key-for-public-app'
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    
    # Configurar logging
    setup_logging(app)
    
    return app

app = create_app()
file_processor = FileProcessor()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Ruta principal para la carga y procesamiento de archivos"""
    if request.method == 'POST':
        try:
            # Validar que se haya enviado un archivo
            if 'file' not in request.files:
                return jsonify({"error": "No se ha seleccionado ningún archivo"}), 400

            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "Archivo no válido"}), 400

            # Validar tamaño del archivo
            if not file_processor.validate_file_size(file.content_length, MAX_FILE_SIZE):
                return jsonify({"error": f"El archivo es demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB"}), 400

            # Verificar extensión del archivo 
            if not file_processor.validate_file_extension(file.filename):
                return jsonify({"error": f"Archivo con formato incorrecto. Formatos permitidos: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

            # Validar datos del formulario
            form_data = request.form
            required_fields = ['campo1', 'campo2', 'campo3', 'campo4', 'campo5', 'campo6']
            missing_fields = [field for field in required_fields if not form_data.get(field)]
            
            if missing_fields:
                return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"}), 400

            # Procesar el archivo con los datos del formulario
            result = file_processor.process_excel_file(file.stream, file.filename, form_data)
            
            if not result['success']:
                error_response = {
                    "error": result['error'],
                    "detailed_errors": result.get('detailed_errors', [])
                }
                return jsonify(error_response), 400

            # Generar nombres de archivos con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comision = form_data.get('campo2', '')
            actividad = form_data.get('campo3', '')
            
            alumnos_filename = f"Subir_Alumnos_{comision}_{actividad}_{timestamp}.csv"
            notas_filename = f"Subir_Notas_{comision}_{actividad}_{timestamp}.csv"

            # Generar IDs únicos para los archivos
            file_id = str(uuid.uuid4())
            
            # Crear archivos temporales para descarga
            temp_dir = tempfile.gettempdir()
            alumnos_temp_path = os.path.join(temp_dir, f"{file_id}_alumnos.csv")
            notas_temp_path = os.path.join(temp_dir, f"{file_id}_notas.csv")
            
            # Guardar archivos temporales
            with open(alumnos_temp_path, 'w', encoding='utf-8') as f:
                f.write(result['alumnos_csv'])
            with open(notas_temp_path, 'w', encoding='utf-8') as f:
                f.write(result['notas_csv'])
            
            # Almacenar información en diccionario global
            temp_files[file_id] = {
                'alumnos_path': alumnos_temp_path,
                'notas_path': notas_temp_path,
                'alumnos_filename': alumnos_filename,
                'notas_filename': notas_filename,
                'timestamp': datetime.now()
            }
            
            # Limpiar archivos antiguos (más de 1 hora)
            current_time = datetime.now()
            expired_files = []
            for fid, file_info in temp_files.items():
                if (current_time - file_info['timestamp']).total_seconds() > 3600:  # 1 hora
                    expired_files.append(fid)
            
            for fid in expired_files:
                try:
                    os.remove(temp_files[fid]['alumnos_path'])
                    os.remove(temp_files[fid]['notas_path'])
                    del temp_files[fid]
                except:
                    pass
            
            # Verificar que los datos se guardaron correctamente
            app.logger.info(f"Archivos procesados: {alumnos_filename}, {notas_filename}")
            app.logger.info(f"File ID: {file_id}")
            app.logger.info(f"Archivos temporales creados: {alumnos_temp_path}, {notas_temp_path}")
            app.logger.info(f"Archivos en memoria: {len(temp_files)}")

            # Devolver respuesta JSON con los archivos procesados
            return jsonify({
                "success": f"Archivos procesados correctamente. Se procesaron {result['total_records']} registros.",
                "uploaded_filename": file.filename,
                "processed_file_alumnos": url_for('download_file', file_id=file_id, file_type='alumnos'),
                "processed_file_notas": url_for('download_file', file_id=file_id, file_type='notas'),
                "records_count": result['total_records']
            })

        except RequestEntityTooLarge:
            return jsonify({"error": f"El archivo es demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB"}), 413
        except Exception as e:
            app.logger.error(f"Error inesperado: {str(e)}")
            return jsonify({"error": "Error interno del servidor. Por favor, intente nuevamente."}), 500
    
    # Si es GET, renderizar la plantilla principal
    return render_template('index.html')

@app.route('/download')
def download_file():
    """Ruta para descargar archivos procesados usando file_id"""
    try:
        file_id = request.args.get('file_id')
        file_type = request.args.get('file_type')
        
        if not file_id or not file_type:
            return jsonify({"error": "Parámetros de descarga incompletos"}), 400
        
        app.logger.info(f"Solicitud de descarga: file_id={file_id}, file_type={file_type}")
        app.logger.info(f"Archivos disponibles: {list(temp_files.keys())}")
        
        # Verificar si el file_id existe
        if file_id not in temp_files:
            app.logger.error(f"File ID no encontrado: {file_id}")
            return jsonify({"error": "Archivo no encontrado o expirado"}), 404
        
        file_info = temp_files[file_id]
        
        # Determinar qué archivo descargar
        if file_type == 'alumnos':
            file_path = file_info['alumnos_path']
            filename = file_info['alumnos_filename']
        elif file_type == 'notas':
            file_path = file_info['notas_path']
            filename = file_info['notas_filename']
        else:
            app.logger.error(f"Tipo de archivo no válido: {file_type}")
            return jsonify({"error": "Tipo de archivo no válido"}), 400
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            app.logger.error(f"Archivo no encontrado en disco: {file_path}")
            return jsonify({"error": "Archivo no encontrado en disco"}), 404
            
        app.logger.info(f"Descarga de archivo: {file_path} -> {filename}")
        
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
        # Agregar headers para evitar problemas de caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error en descarga: {str(e)}")
        return jsonify({"error": f"Error al descargar el archivo: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": f"El archivo es demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Página no encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Error interno: {str(e)}")
    return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/test-session')
def test_session():
    """Ruta de prueba para verificar el estado de los archivos temporales"""
    return jsonify({
        "temp_files_count": len(temp_files),
        "temp_files_ids": list(temp_files.keys()),
        "temp_files_info": {
            fid: {
                "alumnos_filename": info['alumnos_filename'],
                "notas_filename": info['notas_filename'],
                "timestamp": info['timestamp'].isoformat(),
                "alumnos_exists": os.path.exists(info['alumnos_path']),
                "notas_exists": os.path.exists(info['notas_path'])
            }
            for fid, info in temp_files.items()
        }
    })

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=DEBUG
    )
