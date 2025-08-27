// Configuración de la aplicación
const CONFIG = {
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
    ALLOWED_EXTENSIONS: ['xls', 'xlsx'],
    DATE_FORMAT: 'DD/MM/YYYY'
};

// Clase principal de la aplicación
class AdecuadorApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadSavedFormValues();
        this.hideSections();
    }

    // Inicializar referencias a elementos del DOM
    initializeElements() {
        this.fileInput = document.getElementById("file");
        this.fileList = document.getElementById("file-list");
        this.dropZone = document.getElementById("drop-zone");
        this.errorContainer = document.getElementById("format-error-container");
        this.form = document.getElementById("upload-form");
        this.downloadSection = document.getElementById("download-section");
        this.restartButton = document.getElementById("restart-button");
        this.requirementsModal = document.getElementById("requirements-modal");
        
        // Campos del formulario
        this.campo1 = document.getElementById("campo1");
        this.campo2 = document.getElementById("campo2");
        this.campo3 = document.getElementById("campo3");
        this.campo4 = document.getElementById("campo4");
        this.campo5 = document.getElementById("campo5");
        this.campo6 = document.getElementById("campo6");
    }

    // Vincular eventos
    bindEvents() {
        this.bindFileEvents();
        this.bindFormEvents();
        this.bindModalEvents();
        this.bindDateFormatting();
    }

    // Eventos relacionados con archivos
    bindFileEvents() {
        this.fileInput.addEventListener("change", (e) => {
            this.handleFileSelection(e.target.files);
        });

        // Configuración de drag and drop
        ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
            this.dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ["dragenter", "dragover"].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.add("drag-over");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.remove("drag-over");
            }, false);
        });

        this.dropZone.addEventListener("drop", (event) => {
            const files = event.dataTransfer.files;
            this.fileInput.files = files;
            this.handleFileSelection(files);
        });
    }

    // Eventos del formulario
    bindFormEvents() {
        this.form.addEventListener("submit", (event) => {
            event.preventDefault();
            this.handleFormSubmit();
        });

        this.restartButton.addEventListener("click", () => {
            this.restartProcess();
        });
    }

    // Eventos del modal
    bindModalEvents() {
        const helpBtn = document.getElementById("show-requirements-help");
        if (helpBtn) {
            helpBtn.addEventListener("click", () => {
                this.showRequirementsModal();
            });
        }
    }

    // Formateo de fechas
    bindDateFormatting() {
        [this.campo5, this.campo6].forEach(input => {
            input.addEventListener("input", (e) => {
                this.formatDate(e.target);
            });
        });
    }

    // Formatear fecha automáticamente
    formatDate(input) {
        input.value = input.value
            .replace(/\D/g, '')
            .replace(/(\d{2})(\d)/, '$1/$2')
            .replace(/(\d{2})\/(\d{2})(\d)/, '$1/$2/$3')
            .substr(0, 10);
    }

    // Manejar selección de archivo
    handleFileSelection(files) {
        if (files.length > 0) {
            const file = files[0];
            const fileName = file.name;
            const fileExtension = fileName.split('.').pop().toLowerCase();
            
            if (CONFIG.ALLOWED_EXTENSIONS.includes(fileExtension)) {
                this.fileList.innerText = `📄 Archivo seleccionado: ${fileName}`;
                this.dropZone.classList.add("file-loaded");
                this.hideError();
            } else {
                this.fileList.innerText = "No hay archivo seleccionado";
                this.dropZone.classList.remove("file-loaded");
                this.showError("El formato del archivo no es válido. Por favor, seleccione un archivo Excel (.xls o .xlsx)");
                this.fileInput.value = "";
            }
        } else {
            this.fileList.innerText = "No hay archivo seleccionado";
            this.dropZone.classList.remove("file-loaded");
            this.hideError();
        }
    }

    // Manejar envío del formulario
    async handleFormSubmit() {
        if (!this.fileInput.files || this.fileInput.files.length === 0) {
            this.showError("Debe seleccionar un archivo para continuar");
            return;
        }

        this.saveFormValues();
        sessionStorage.setItem('formSubmitted', 'true');

        const formData = new FormData(this.form);
        
        try {
            const response = await fetch("/", {
                method: "POST",
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.log("Error recibido:", data.error);
                console.log("Errores detallados:", data.detailed_errors);
                this.showError(data.error, data.detailed_errors || []);
            } else {
                console.log("Procesamiento exitoso:", data);
                this.hideError();
                this.showDownloadSection(data);
            }
        } catch (error) {
            console.error("Error:", error);
            this.showError("Ocurrió un error al procesar su solicitud. Por favor, inténtelo de nuevo.");
        }
    }

    // Mostrar sección de descarga
    showDownloadSection(data) {
        this.form.style.display = "none";
        this.downloadSection.style.display = "block";
        
        document.getElementById("uploaded-file-name").textContent = data.uploaded_filename;

        const alumnosLink = document.getElementById("download-alumnos");
        alumnosLink.href = data.processed_file_alumnos;
        alumnosLink.style.display = "inline-block";

        const notasLink = document.getElementById("download-notas");
        notasLink.href = data.processed_file_notas;
        notasLink.style.display = "inline-block";
    }

    // Reiniciar proceso
    restartProcess() {
        this.form.style.display = "block";
        this.downloadSection.style.display = "none";
        
        this.fileInput.value = "";
        this.fileList.innerText = "No hay archivo seleccionado";
        this.dropZone.classList.remove("file-loaded");
        
        this.hideError();
        this.form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Mostrar modal de requisitos
    showRequirementsModal() {
        this.requirementsModal.style.display = "block";
        this.setupModalInteractions();
    }

    // Configurar interacciones del modal
    setupModalInteractions() {
        // Botón de cerrar
        const closeBtn = document.querySelector(".close-button");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                this.requirementsModal.style.display = "none";
            });
        }
        
        // Cerrar al hacer clic fuera
        this.requirementsModal.addEventListener("click", (event) => {
            if (event.target === this.requirementsModal) {
                this.requirementsModal.style.display = "none";
            }
        });
        
        // Imagen de ejemplo
        const exampleImageLink = document.getElementById("example-image-link");
        if (exampleImageLink) {
            exampleImageLink.addEventListener("click", (e) => {
                e.preventDefault();
                this.showImageLightbox();
            });
        }
    }

    // Mostrar lightbox de imagen
    showImageLightbox() {
        const lightbox = document.createElement("div");
        lightbox.id = "lightbox";
        Object.assign(lightbox.style, {
            position: "fixed",
            top: "0",
            left: "0",
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.9)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: "2000",
            cursor: "pointer"
        });
        
        const img = document.createElement("img");
        img.src = document.getElementById("example-image").src;
        Object.assign(img.style, {
            maxWidth: "95%",
            maxHeight: "95%",
            border: "3px solid white",
            borderRadius: "8px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.5)"
        });
        
        lightbox.appendChild(img);
        document.body.appendChild(lightbox);
        
        // Cerrar lightbox
        lightbox.addEventListener("click", () => {
            document.body.removeChild(lightbox);
        });
        
        // Cerrar con ESC
        const escHandler = (e) => {
            if (e.key === "Escape" && document.getElementById("lightbox")) {
                document.body.removeChild(lightbox);
                document.removeEventListener("keydown", escHandler);
            }
        };
        document.addEventListener("keydown", escHandler);
    }

    // Mostrar error
    showError(message, detailedErrors = []) {
        console.log("Mostrando error:", message);
        console.log("Errores detallados:", detailedErrors);
        
        // Crear mensaje dinámico basado en el tipo de error
        let dynamicMessage = this.createDynamicErrorMessage(message);
        
        let errorContent = `
            <div class="format-error">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <div class="error-message">${dynamicMessage}</div>
        `;
        
        // Agregar errores detallados si existen
        if (detailedErrors && detailedErrors.length > 0) {
            console.log("Agregando errores detallados al HTML");
            errorContent += `
                <div class="detailed-errors">
                    <div class="errors-title">Errores encontrados:</div>
                    <ul class="errors-list">
            `;
            
            detailedErrors.forEach(error => {
                if (typeof error === 'string') {
                    // Error consolidado (ya viene formateado desde el backend)
                    errorContent += `<li>• ${error}</li>`;
                } else if (error.fila && error.errores) {
                    // Error de fila específica (formato antiguo, mantener compatibilidad)
                    error.errores.forEach(rowError => {
                        errorContent += `<li>• Fila ${error.fila}: ${rowError}</li>`;
                    });
                }
            });
            
            errorContent += `
                    </ul>
                </div>
            `;
        }
        
        errorContent += `
                    <button id="show-requirements" type="button" class="requirements-btn">
                        <span class="btn-icon">📋</span>
                        <span class="btn-text">Ver requisitos de formato</span>
                    </button>
                </div>
            </div>
        `;
        
        this.errorContainer.innerHTML = errorContent;
        this.errorContainer.style.display = "block";
        this.errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Configurar botón de requisitos
        const showRequirementsBtn = document.getElementById("show-requirements");
        if (showRequirementsBtn) {
            showRequirementsBtn.addEventListener("click", () => {
                this.showRequirementsModal();
            });
        }
    }

    // Crear mensaje de error dinámico
    createDynamicErrorMessage(message) {
        const errorMessages = {
            'No se ha seleccionado ningún archivo': 'No has seleccionado ningún archivo para procesar. Por favor, arrastra un archivo Excel o haz clic para seleccionarlo.',
            'Archivo no válido': 'El archivo seleccionado no es válido. Asegúrate de que sea un archivo Excel (.xlsx o .xls).',
            'El formato del archivo no es válido': 'El archivo debe ser un archivo Excel (.xlsx o .xls). Por favor, verifica el formato y vuelve a intentarlo.',
            'El archivo es demasiado grande': 'El archivo excede el tamaño máximo permitido de 16MB. Por favor, comprime el archivo o selecciona uno más pequeño.',
            'Archivo con formato incorrecto': 'El archivo no tiene el formato correcto. Debe ser un archivo Excel con exactamente 9 columnas en el orden especificado.',
            'Campos requeridos faltantes': 'Faltan campos obligatorios en el formulario. Por favor, completa todos los campos marcados como requeridos.',
            'Debe seleccionar un archivo para continuar': 'Para continuar, necesitas seleccionar un archivo Excel válido. Arrastra el archivo o haz clic para seleccionarlo.',
            'Ocurrió un error al procesar su solicitud': 'Hubo un problema al procesar tu solicitud. Por favor, verifica que el archivo sea correcto e inténtalo nuevamente.',
            'El archivo no tiene la estructura correcta': 'El archivo no tiene la estructura esperada. Verifica que tenga exactamente 9 columnas en el orden correcto.',
            'No se encontraron registros válidos': 'No se encontraron registros válidos en el archivo. Verifica que los datos cumplan con los requisitos.',
            'Se encontraron errores en': 'Se encontraron errores en el archivo. Revisa los detalles a continuación y corrige los problemas antes de volver a intentarlo.'
        };

        // Buscar un mensaje personalizado o usar el original
        for (const [key, value] of Object.entries(errorMessages)) {
            if (message.includes(key) || key.includes(message)) {
                return value;
            }
        }

        // Si no encuentra un mensaje específico, usar el original pero con mejor formato
        return message;
    }

    // Ocultar error
    hideError() {
        this.errorContainer.innerHTML = "";
        this.errorContainer.style.display = "none";
    }

    // Guardar valores del formulario
    saveFormValues() {
        const formValues = {
            campo1: this.campo1.value,
            campo2: this.campo2.value,
            campo3: this.campo3.value,
            campo4: this.campo4.value
        };
        localStorage.setItem('formValues', JSON.stringify(formValues));
    }

    // Cargar valores guardados
    loadSavedFormValues() {
        const isPageRefresh = !sessionStorage.getItem('formSubmitted');
        
        if (isPageRefresh) {
            [this.campo1, this.campo2, this.campo3, this.campo4].forEach(field => {
                field.value = '';
            });
            localStorage.removeItem('formValues');
        } else {
            const savedValues = localStorage.getItem('formValues');
            if (savedValues) {
                const formValues = JSON.parse(savedValues);
                this.campo1.value = formValues.campo1 || '';
                this.campo2.value = formValues.campo2 || '';
                this.campo3.value = formValues.campo3 || '';
                this.campo4.value = formValues.campo4 || '';
            }
        }
        
        sessionStorage.removeItem('formSubmitted');
    }

    // Ocultar secciones al inicio
    hideSections() {
        this.downloadSection.style.display = "none";
        this.requirementsModal.style.display = "none";
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    new AdecuadorApp();
});

