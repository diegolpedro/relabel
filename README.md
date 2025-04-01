# Relabel
[![Python Version](https://img.shields.io/badge/python-3+-green.svg?style=flat)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](GPLv3) 

Optimiza la impresión de etiquetas de envío combinándolas con flyers promocionales personalizados (con código QR) en un único PDF A5. Reduce el uso de papel y permite el seguimiento de campañas promocionales.

## ✨ Características Principales

* **Combinación de Documentos:** Fusiona una etiqueta de envío en PDF (ej. Mercado Envíos, Correo Argentino) y un flyer promocional en un solo archivo PDF de tamaño A5.
* **Personalización con QR:** Genera dinámicamente un código QR en el flyer, incrustando información útil como una URL de seguimiento, el origen de la venta y/o el número de orden.
* **Optimización de Impresión:** El formato A5 resultante facilita la impresión eficiente y reduce el desperdicio de papel.
* **Seguimiento de Campañas:** Permite rastrear el origen de visitas posteriores a la tienda a través del QR personalizado.
* **Clasificación Automática:** Incluye un **modelo SVM** para identificar el tipo de etiqueta si se entrena con datos de ejemplo.
* **Configurable:** Parámetros clave gestionados a través de `cfg.py`.

## 🚀 Cómo Funciona

El flujo general del proceso es el siguiente:

1.  **Entrada:** Recibe un archivos Pdf: la etiqueta del envío que se haya generado en la tienda o marketplace. Por lo general contiene mas de una hoja. (1er Pdf)
2.  **Generación de QR:** Obtiene datos de el medio de venta y numero de orden desde ese mismo pdf, crea un QR personalizado.
3.  **Inserción en Flyer:** Incrusta el código QR generado en el flyer base. (2do Pdf)
4.  **Fusión:** Combina la etiqueta de envío original (1er Pdf) y el flyer con el QR (2do Pdf) en un único documento A5.
5.  **Guías:** Añade una línea punteada e icono de tijeras para facilitar el corte manual.
6.  **Salida:** Guarda el documento final como un nuevo archivo PDF en la carpeta de salida y ofrece impresion.

## ⚙️ Instalación

Sigue estos pasos para configurar el entorno del proyecto:

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO> # Reemplaza con la URL real de tu repositorio
    cd relabel
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # Virtual Envs
    python -m venv venv
    # En Linux/macOS:
    source venv/bin/activate
    # En Windows:
    .\venv\Scripts\activate

    # Con Anaconda en Linux
    conda create -n <nombre> python==3.10
    conda activate <nombre> 
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Uso

### 1. (Solo primera vez) Entrenar el Modelo de Clasificación (SVM)

El sistema identificara automáticamente el tipo de etiqueta (ej., Correo Argentino, Mercado Envíos, etc basado en el texto de la etiqueta), si primero se entrena el modelo clasificador. Para esto se colocan las etiquetas de entrenamiento (Pdfs) en los directorios correspondientes dentro dee 'data'. Luego correr eel siguiente código.

```bash
python train.py
```

Este script:
* Lee los PDFs de eeentrenamiento ubicados en `data/labelsMl/` y `data/labelsCorreoArg/`.
* Extrae y procesa el texto.
* Vectoriza el texto usando [TF-IDF](https://es.wikipedia.org/wiki/Tf-idf) y elimina las stopwords personalizadas (`model/custom_stopwords.txt`).
* Entrena un clasificador [SVM](https://es.wikipedia.org/wiki/M%C3%A1quina_de_vectores_de_soporte).
* Guarda el modelo entrenado (`svm_model.pkl`), el vectorizador (`vectorizer.pkl`) y el codificador de etiquetas (`label_encoder.pkl`) en la carpeta `model/` para poder reutilizarlos.

Actualmente implementado con SVM en un escenario casi ideal. Dos clases bien definidas entre si. Esto explicaria la alta precisión y un buen rendimiento general del modelo. En un futuro puede plantearse la utilización de otros modelos. 

### 2. Generar el PDF Combinado para una Venta

El script principal para ejecutar el proceso completo para una etiqueta y datos de orden específicos es `generate.py`.

```bash
python generate.py
```

Este script orquesta la ejecución de:
* `flyer.py`: Para generar el flyer con el QR personalizado (guardado temporalmente en `tmp/`).
* `print.py`: Para tomar la etiqueta correspondiente, el flyer con QR, y fusionarlos en el PDF A5 final (guardado en `out/`).

**Nota Importante:** En esta primer implementacion y como todavia no formar parte de una integracion con otros sistemas, tanto 'Medio de venta' como 'Nro. de orden' seran tomados del nombre del Pdf deel envio. Por lo cual el nombre debera ser codificado como: '<Medio>-<Numero>.pdf' sin olvidar ni guion medio ni .pdf .

## 📁 Estructura del Proyecto

```
relabel/
│
├── data/                 # Datos de ejemplo y recursos
│   ├── labelsCorreoArg/  #   Ejemplos etiquetas Correo Argentino
│   ├── labelsMl/         #   Ejemplos etiquetas Mercado Envíos
│   ├── flyer.pdf         #   Flyer base para insertar QR
│   └── tijera.png        #   Icono para guía de corte
│
├── model/                # Archivos del modelo de clasificación
│   ├── custom_stopwords.txt # Stopwords personalizadas
│   ├── label_encoder.pkl #   Codificador de etiquetas entrenado
│   ├── svm_model.pkl     #   Modelo SVM entrenado
│   └── vectorizer.pkl    #   Vectorizador TF-IDF entrenado
│
├── out/                  # Directorio de salida para resultados generados
│
├── tmp/                  # Carpeta temporal para archivos intermedios
│
├── cfg.py                # Archivo de configuración principal
├── train.py              # Script para entrenar el modelo de Machine Learning clasificador
├── flyer.py              # Script para generar flyer con QR
├── print.py              # Script para fusionar etiqueta y flyer
├── generate.py           # Script principal para orquestar la generación
├── requirements.txt      # Dependencias de Python
├── LICENSE               # Licencia del proyecto
└── README.md             # Este archivo
```

## 🔧 Configuración

Puedes ajustar parámetros clave como rutas de archivos, la URL base para el QR u otras configuraciones directamente en el archivo `cfg.py`.

## 📄 Licencia

Este proyecto se distribuye bajo los términos de la licencia especificada en el archivo `LICENSE`. ```

README generado con IA y corregido por humano.