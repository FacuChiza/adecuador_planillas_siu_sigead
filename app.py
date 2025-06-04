from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import pandas as pd
import csv
import traceback
from werkzeug.utils import secure_filename

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de carpetas y extensiones permitidas
UPLOAD_FOLDER = "/tmp/uploads"
PROCESSED_FOLDER = "/tmp/processed"
ALLOWED_EXTENSIONS = {"xlsx"}

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Ruta principal para la carga y procesamiento de archivos"""
    if request.method == 'POST':
        # Validar que se haya enviado un archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se ha seleccionado ningún archivo"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Archivo no válido"}), 400

        # Verificar extensión del archivo 
        if not allowed_file(file.filename):
            return jsonify({"error": "Archivo con formato incorrecto"}), 400

        # Guardar el archivo cargado en /tmp/
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Obtener datos del formulario
        propuesta = request.form.get('campo1', '')
        comision = request.form.get('campo2', '')
        actividad = request.form.get('campo3', '')
        periodo_lectivo = request.form.get('campo4', '')
        fecha_regular = request.form.get('campo5', '')
        fecha_promocion = request.form.get('campo6', '')

        try:
            # Leer el archivo Excel
            df = pd.read_excel(file_path, usecols=range(9))

            # Renombrar columnas para facilitar el procesamiento
            df.columns = ['Legajo', 'Nota', 'Promocion', 'Apellido', 'Nombre', 'DNI', 'Edicion', 'Fecha_de_inicio', 'Facultad_regional']

            # Filtrar solo los registros de FRBA y con notas válidas
            df = df[df['Facultad_regional'] == 'FRBA']
            df = df[pd.to_numeric(df['Nota'], errors='coerce').notna()]
            
            # Eliminar columnas innecesarias
            df = df.drop(columns=['Legajo', 'Promocion', 'Apellido', 'Nombre', 'Edicion', 'Fecha_de_inicio', 'Facultad_regional'])

            # Crear DataFrame para subir alumnos
            subir_alumnos_df = df[['DNI']].copy()
            subir_alumnos_df['Propuesta'] = propuesta
            subir_alumnos_df['Comision'] = comision
            subir_alumnos_df['Actividad'] = actividad
            subir_alumnos_df['Periodo Lectivo'] = periodo_lectivo

            # Guardar archivo de alumnos en /tmp/
            subir_alumnos_filename = f"Subir_Alumnos_{comision}_{actividad}.csv"
            processed_file_alumnos = os.path.join(PROCESSED_FOLDER, subir_alumnos_filename)
            subir_alumnos_df.to_csv(processed_file_alumnos, index=False, encoding="utf-8") 

            # Crear DataFrame para subir notas
            subir_notas_df = pd.DataFrame()
            subir_notas_df['documento'] = df['DNI']
            subir_notas_df['nota_regular'] = df['Nota']
            subir_notas_df['fecha_regular'] = fecha_regular 
            subir_notas_df['nota_promocion'] = ""
            subir_notas_df['fecha_promocion'] = fecha_promocion 

            # Guardar nuevo archivo de notas en /tmp/
            subir_notas_filename = f"Subir_Notas_{comision}_{actividad}.csv"
            processed_file_notas = os.path.join(PROCESSED_FOLDER, subir_notas_filename)
            subir_notas_df.to_csv(processed_file_notas, index=False, encoding="utf-8")

            # Devolver respuesta JSON con los archivos procesados
            return jsonify({
                "success": "Archivos procesados correctamente.",
                "uploaded_filename": filename,
                "processed_file_alumnos": url_for('download_file', file=subir_alumnos_filename),
                "processed_file_notas": url_for('download_file', file=subir_notas_filename)
            })

        except Exception as e:
            # En caso de error durante el procesamiento
            traceback.print_exc()  # Imprimir el error en la consola del servidor
            return jsonify({"error": "Error en el procesamiento del archivo"}), 500
    
    # Si es GET, renderizar la plantilla principal
    return render_template('index.html')

@app.route('/download')
def download_file():
    """Ruta para descargar archivos procesados"""
    file_path = request.args.get('file')
    full_path = os.path.join(PROCESSED_FOLDER, file_path)
    
    if file_path and os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        flash('Archivo no encontrado', 'error')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)