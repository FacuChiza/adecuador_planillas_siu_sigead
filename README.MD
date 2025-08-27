# Adecuador de Planillas SIU Guaraní

Aplicación web para procesar y adaptar planillas de Excel del sistema SIU Guaraní para su importación en SIGEAD.

## 🚀 Características

- **Procesamiento en memoria**: No guarda archivos en el servidor
- **Validación robusta**: Verifica formato, estructura y contenido de archivos
- **Interfaz moderna**: Diseño responsive y intuitivo
- **Modal interactivo**: Guía visual con requisitos y ejemplos
- **Drag & Drop**: Carga de archivos por arrastre
- **Compatible con Vercel**: Despliegue serverless sin persistencia

## 📁 Estructura del Proyecto

```
adecuador_planillas_siu_sigead/
├── app.py                      # Aplicación principal Flask
├── config/                     # Configuración centralizada
│   ├── __init__.py
│   └── settings.py            # Configuraciones de la aplicación
├── utils/                      # Utilidades y procesamiento
│   ├── __init__.py
│   └── file_processor.py      # Procesamiento de archivos Excel
├── static/                     # Archivos estáticos
│   ├── css/
│   │   ├── style.css          # Estilos principales
│   │   └── components.css     # Componentes específicos
│   ├── js/
│   │   └── main.js            # JavaScript modular
│   └── images/                # Imágenes y recursos
├── templates/                  # Plantillas HTML
│   └── index.html             # Página principal
├── requirements.txt           # Dependencias Python
├── vercel.json               # Configuración Vercel
└── README.md                 # Documentación
```

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Procesamiento**: Pandas, OpenPyXL
- **Despliegue**: Vercel (Serverless)

## 📋 Requisitos del Sistema

- Python 3.8+
- Navegador web moderno
- Conexión a internet (para despliegue)

## 🔧 Instalación

### Desarrollo Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd adecuador_planillas_siu_sigead
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

5. **Abrir en navegador**
   ```
   http://localhost:5000
   ```

### Despliegue en Vercel

1. **Conectar repositorio a Vercel**
2. **Configurar variables de entorno** (opcional)
3. **Desplegar automáticamente**

## 📖 Uso de la Aplicación

### 1. Preparar el Archivo Excel
- **Formato**: `.xlsx` o `.xls` (máximo 16MB)
- **Columnas requeridas** (en este orden):
  1. Legajo
  2. Nota
  3. Promocion
  4. Apellido
  5. Nombre
  6. DNI
  7. Edicion
  8. Fecha de inicio
  9. Facultad regional

### 2. Cargar y Procesar
1. **Arrastrar archivo** o hacer clic para seleccionar
2. **Completar formulario** con datos del curso
3. **Hacer clic en "Subir Archivo"**
4. **Descargar archivos procesados**

### 3. Archivos Generados
- **Subir_Alumnos.csv**: Datos de estudiantes
- **Subir_Notas.csv**: Calificaciones y promociones

## 🎨 Características de la Interfaz

### Modal de Requisitos
- **Acceso**: Botón discreto bajo "Subir Archivo"
- **Contenido organizado**:
  - ✅ Requisitos obligatorios
  - 📸 Ejemplo visual ampliable
  - ⚠️ Notas importantes
  - 💡 Consejos prácticos

### Funcionalidades Interactivas
- **Drag & Drop**: Arrastrar archivos directamente
- **Validación en tiempo real**: Verificación de formato
- **Lightbox**: Ampliar imagen de ejemplo
- **Formateo automático**: Fechas DD/MM/YYYY
- **Persistencia**: Guarda datos del formulario

## 🔒 Seguridad y Validación

### Validaciones Implementadas
- **Tipo de archivo**: Solo Excel (.xlsx, .xls)
- **Tamaño**: Máximo 16MB
- **Estructura**: Exactamente 9 columnas
- **Contenido**: Solo registros FRBA
- **Notas**: Rango 1-10
- **Formulario**: Todos los campos requeridos

### Procesamiento Seguro
- **Sin persistencia**: Archivos procesados en memoria
- **Sesiones temporales**: Datos eliminados automáticamente
- **Validación estricta**: Previene errores de procesamiento

## 🚀 Despliegue

### Vercel (Recomendado)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Otros Servicios
- **Heroku**: Compatible con buildpacks Python
- **Railway**: Despliegue directo desde GitHub
- **DigitalOcean**: App Platform o Droplets

## 🐛 Solución de Problemas

### Errores Comunes

**"Archivo vacío"**
- Verificar que el Excel tenga datos
- Eliminar filas vacías al inicio
- Asegurar formato correcto

**"No se encontraron registros FRBA"**
- Verificar columna "Facultad regional"
- Buscar "FRBA" en los datos
- Revisar mayúsculas/minúsculas

**"Notas inválidas"**
- Verificar rango 1-10
- Eliminar caracteres no numéricos
- Revisar formato decimal

### Logs y Debugging
- **Desarrollo**: Logs en consola
- **Producción**: Archivo `logs/app.log`
- **Vercel**: Logs en dashboard

## 🤝 Contribución

1. **Fork** el proyecto
2. **Crear rama** para feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambios (`git commit -m 'Add AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir Pull Request**

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- **Issues**: GitHub Issues
- **Documentación**: Este README
- **Contacto**: [Tu información de contacto]

---

**Desarrollado con ❤️ para la UTN FRBA**

