# Adecuador Planillas SIU Sigead
Adecuador Planillas SIU Sigead es una herramienta desarrollada para facilitar la adecuación de planillas exportadas desde el SIU al formato requerido por el sistema SIGEAD, utilizado comúnmente en universidades e instituciones educativas para la carga de datos académicos y administrativos.

## ¿Para qué sirve este programa?
🧩 Cuando se exportan datos desde SIU, a menudo el formato no es compatible directamente con el sistema SIGEAD. Este script automatiza el proceso de:

- Modificación y reordenamiento de columnas.
- Conversión de formatos de texto y fecha.
- Limpieza de datos innecesarios.
- Generación de dos nuevas planillas listas para importar en SIGEAD.

Esto ahorra tiempo, evita errores manuales y mejora la eficiencia en la gestión de datos académicos.

## ¿Cómo modificar el funcionamiento de este programa? (informar antes de hacerlo)

🔧 **Requisitos**
- Python 3 instalado en tu equipo.
- Conocimientos medios de cómo ejecutar un script en Python.
- Tener el archivo Excel exportado desde SIU (formato .xlsx o .xls).

📦 **Instalación**

Cloná este repositorio:

```bash 
    git clone: https://github.com/FacuChiza/adecuador_planillas_siu_sigead.git
```

Accedé a la carpeta del proyecto:

```python
 pip install -r requirements.txt
```
▶️ **Ejecución** 

Una vez que tenés el archivo de entrada listo, podés ejecutar el script en la terminal con:
```python
 app.py
```

El programa se ejecutara seleccionar el archivo de entrada y generará automáticamente una nueva planilla con los datos adaptados al formato SIGEAD.

## Preguntas frecuentes❓ 

**¿Qué pasa si el archivo no tiene el formato esperado?**  

El script mostrará un mensaje de error indicando qué columna o dato no pudo procesarse.

**¿Puedo usarlo con LibreOffice en lugar de Excel?** 

Sí, siempre que el archivo esté en formato .xlsx o .xls.

**¿Puedo adaptarlo a otros formatos?** 

Sí, el código es abierto y puede modificarse para otros casos de uso similares.

## Autor 👨‍💻

Desarrollado por *Facundo L. Chiarenza* , full stack dev. 

Colaboraciones, mejoras y sugerencias son bienvenidas vía **pull request** o **issues** en este repositorio.

