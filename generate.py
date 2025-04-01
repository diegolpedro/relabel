#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Diego Pedro <diegolpedro@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Summary:
# Generador de etiquetas programático.
#
import os
import shutil
import subprocess

import joblib
import pdfplumber
import numpy as np
import pandas as pd
from pathlib import Path

from cfg import MODEL_PATH, BASE_DIR, OUT_PATH, OUT_DIR, URL_WEB
from flyer import qr_to_pdf
from print import generate_sheet


def predict_pdf(pdf_path: Path) -> str:
    """
    Clasifica un archivo PDF para determinar el tipo de envío de la etiqueta.

    La función carga un modelo de Machine Learning preentrenado (SVM) junto con
    su vectorizador y codificador de etiquetas. Luego, extrae el texto del PDF,
    lo transforma en una representación adecuada para el modelo y predice a qué
    categoría pertenece.

    Parámetros:
        pdf_path (Path): Ruta al archivo PDF que se desea clasificar.

    Retorna:
        str: Nombre de la clase predicha por el modelo, que indica el tipo de envío.

    Excepciones:
        RuntimeError: Se lanza si ocurre un error durante la carga del modelo,
                      la extracción de texto o la predicción.
    """
    try:
        # Cargar modelo pre-entrenado
        try:
            model = joblib.load(MODEL_PATH / "modelo_svm.pkl")
            vectorizer = joblib.load(MODEL_PATH / "vectorizer.pkl")
            label_encoder = joblib.load(MODEL_PATH / "label_encoder.pkl")
        except (FileNotFoundError, OSError) as e:
            raise RuntimeError(f"No se pudo cargar el modelo o sus componentes: {e}")

        # Extraer texto del PDF
        with pdfplumber.open(pdf_path) as pdf:
            text = " ".join(filter(None, (page.extract_text() for page in pdf.pages)))

        clean_text = text.strip()
        if not clean_text:
            raise RuntimeError(f"El archivo {pdf_path} no contiene texto válido.")

        # Transformar texto y predecir
        X_new = vectorizer.transform([clean_text])
        pred = model.predict(X_new)

        return label_encoder.inverse_transform(pred)[0]

    except Exception as e:
        raise RuntimeError(f"Error de predicción con el archivo {pdf_path}: {e}")


def generar_etiqueta():
    """
    Genera una etiqueta mitad de envío, mitad de promoción, a partir de dos PDFs pregenerados.

    La función busca un archivo PDF con el formato `<medio_venta>-<num_orden>.pdf`,
    lo clasifica utilizando un modelo de Machine Learning para determinar su tipo de envío y
    poder hacer los recortes necesarios. Por otro lado genera un código QR asociado a la orden,
    y crea un nuevo archivo PDF con el flyer promocional. Finalmente une ambos pdf en un pdf
    formato A5 final.
    Si hay una impresora predeterminada configurada en el sistema, intenta enviarla a imprimir.

    Procedimiento:
        1. Busca un archivo PDF válido en el directorio base.
        2. Extrae `medio_venta` y `num_orden` a partir del nombre del archivo.
        3. Clasifica el PDF con `predict_pdf()` para determinar el tipo de envío.
        4. Genera un código QR personalizado y lo utiliza en el flyer con `qr_to_pdf()`.
        5. Crea la etiqueta final con `generate_sheet()`.
        6. Si hay una impresora predeterminada, envía la etiqueta a imprimir.
        7. Mueve el archivo original a la carpeta de salida junto con el resultado.

    Excepciones:
        RuntimeError: Se lanza si no se encuentra un archivo PDF con el formato esperado.

    Ejemplo de uso:
        Colocar el PDF de la etiqueta de MercadoLibre o Correo Argentino en la raíz del
        proyecto, con el siguiente formato:

            <medio_venta>-<num_orden>.pdf

        Ejemplo de nombres de archivo:
            - `meli-123456.pdf`
            - `correo-987654.pdf`
    """
    # Buscar un PDF válido en el directorio base
    pdf_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".pdf") and "-" in f]
    if not pdf_files:
        raise RuntimeError("No se encontró ningún archivo con el formato esperado.")

    file = pdf_files[0]  # Toma el primer archivo encontrado
    medio_venta, num_orden = file.rsplit(".", 1)[0].split("-", 1)

    pdf_envio_path = Path(BASE_DIR) / file
    pdf_out_path = Path(OUT_PATH) / f"{medio_venta}{num_orden}.pdf"

    # Con la siguiente sentencia el modelo determinará (clasificara) de que
    # tipo de envio es la etiqueta. En base a esta eleccion se hará el
    # recorte de la misma.
    tipo_envio = predict_pdf(pdf_envio_path)

    # Genera qr para inserción
    qr_to_pdf(medio_venta, num_orden, URL_WEB)

    # Genera etiqueta final con ambas etiquetas
    generate_sheet(tipo_envio, pdf_envio_path, pdf_out_path)

    # Intentar enviar a imprimir (solo Linux)
    try:
        result = subprocess.run(
            ["lpstat", "-d"], capture_output=True, text=True, check=True
        )
        default_printer = result.stdout.strip()
    except Exception as e:
        print(f"Error al imprimir: {e}")
        default_printer = None

    if default_printer != "no system default destination":
        try:
            subprocess.run(["lp", str(pdf_out_path)], check=True)
        except subprocess.SubprocessError as e:
            print(f"Error al imprimir {pdf_out_path}: {e}")
    else:
        print(f"No hay impresora por defecto. Imprima manualmente {pdf_out_path}.")

    # Mover archivo procesado a la carpeta de salida
    shutil.move(pdf_envio_path, OUT_DIR)


if __name__ == "__main__":
    generar_etiqueta()
