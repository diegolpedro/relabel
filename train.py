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
# Generador de modelo de clasificacion de etiquetas para envios.
#
import os
import pdfplumber
import numpy as np
import joblib

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

from cfg import DATA_PATH, MODEL_PATH

# Rutas
DATA_DIRS = {
    "MercadoLibre": DATA_PATH / "labelsMl",
    "CorreoArg": DATA_PATH / "labelsCorreoArg",
}
SWORDS_FILE = MODEL_PATH / "custom_stopwords.txt"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrae el texto de un archivo PDF.

    Args:
        pdf_path (str): Ruta del archivo PDF a procesar.

    Returns:
        str: Texto extraído del PDF como una sola cadena de texto.
             Si el PDF no contiene texto seleccionable, devuelve una cadena vacía.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = " ".join(page.extract_text() or "" for page in pdf.pages)
    return text.strip()


def load_data():
    """Carga archivos PDF de los directorios especificados y extrae el texto.

    DATA_DIRS debe ser un diccionario donde:
        - Las claves representan etiquetas de clasificación.
        - Los valores son rutas a los directorios donde se encuentran los PDFs.

    Returns:
        tuple[list[str], list[str]]:
            - Una lista con el texto extraído de cada PDF.
            - Una lista con las etiquetas correspondientes a cada texto.
    """
    texts, labels = [], []
    for label, folder in DATA_DIRS.items():
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(folder, file)
                text = extract_text_from_pdf(pdf_path)
                if text:
                    texts.append(text)
                    labels.append(label)
    return texts, labels


def load_stopwords(file_path: Path) -> list:
    """Carga una lista de palabras (stopwords) desde un archivo de texto.

    Args:
        file_path (str): Ruta del archivo que contiene las stopwords,
                         donde cada línea del archivo es una palabra.

    Returns:
        list[str]: Lista de palabras stopwords sin espacios adicionales ni líneas vacías.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        stopwords = [line.strip() for line in f if line.strip()]
    return stopwords


def main():
    # Cargar datos de los Pdf
    texts, labels = load_data()

    # Convertir etiquetas a valores numéricos
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    stopwords = load_stopwords(SWORDS_FILE)  # Cargar stopwords

    # Crear Bag of Words con TF-IDF
    vectorizer = TfidfVectorizer(stop_words=stopwords, max_features=5000)
    X = vectorizer.fit_transform(texts)

    # Dividir datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Entrenar modelo (SVM en este caso)
    model = SVC(kernel="linear", probability=True)
    model.fit(X_train, y_train)

    # Evaluar modelo con validación cruzada
    scores = cross_val_score(model, X_train, y_train, cv=4)
    print(f"Precisión media del modelo: {np.mean(scores):.4f}")

    # Guardar el modelo, el vectorizador y el codificador de etiquetas
    joblib.dump(model, MODEL_PATH / "modelo_svm.pkl")
    joblib.dump(vectorizer, MODEL_PATH / "vectorizer.pkl")
    joblib.dump(label_encoder, MODEL_PATH / "label_encoder.pkl")


if __name__ == "__main__":
    main()
