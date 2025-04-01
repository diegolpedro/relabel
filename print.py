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
# Realiza los recortes y prepara la etiqueta final.
#
import fitz  # PyMuPDF
import io
import os
from pathlib import Path
from PIL import Image

from cfg import BASE_DIR, DATA_PATH, TEMP_PATH


def extract_high_res_image(
    page: fitz.Page, rect: fitz.Rect, dpi: int = 300, quality: int = 75
):
    """Extrae una imagen de alta resolución desde un área específica de un PDF.

    Args:
        page (fitz.Page): Página del PDF de la que se extraerá la imagen.
        rect (fitz.Rect): Rectángulo que define el área a extraer.
        dpi (int, optional): Resolución en DPI. Predeterminado en 300.
        quality (int, optional): Calidad de compresión JPEG (0-100). Predeterminado en 75.

    Returns:
        bytes: Imagen en formato JPEG comprimida en un buffer de memoria.
    """
    zoom = dpi / 72  # Factor de escalado
    mat = fitz.Matrix(zoom, zoom)  # Matriz de transformación
    # Extraer imagen con mayor resolución
    pix = page.get_pixmap(matrix=mat, clip=rect)

    # Si la imagen tiene transparencia, convertir a RGB
    if pix.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)

    # Convertir Pixmap a imagen de PIL (Pillow)
    img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Comprimir y convertir la imagen a JPEG
    img_bytes = io.BytesIO()
    img_pil.save(img_bytes, format="JPEG", quality=quality)

    return img_bytes.getvalue()


def generate_sheet(tipo_envio: str, label_envio: Path, output_file: Path):
    """Funcion para generar el archivo final a partir de los dos pdf que
    conformaran el archivo final. El de promo y el del envio, en hoja A5.

    Args:
        tipo_envio (str): Tipo de envío ("MercadoLibre" o "CorreoArg").
        label_envio (str): Ruta al archivo PDF de la etiqueta de envío.
        output_file (str): Ruta donde se guardará el PDF final.

    Returns:
        bool: True si el archivo se genera con éxito, False si hubo un error.
    """
    # Archivos de entrada
    pdf1_path = TEMP_PATH / "interm.pdf"  # Pdf de promo
    if not os.path.exists(pdf1_path):
        raise RuntimeError(
            f"No se encontró el archivo {pdf1_path}. Asegurese haber corrido 'flyer.py' antes."
        )
    if not os.path.exists(label_envio):  # Pdf del envio
        raise RuntimeError(f"No se encontró el archivo {label_envio}")

    # Definir áreas de extracción (x0, y0, x1, y1)
    rect1 = fitz.Rect(6, 10, 297, 410)
    a5_rect1 = fitz.Rect(0, 0, 297, 420)

    # Rectangulos para envio ---------------------------------
    # Pueden ir agregandose mas en funcion a envios utilizados
    envio_rects = {
        "MercadoLibre": {
            "rect2": fitz.Rect(30, 140, 297, 600),
            "a5_rect2": fitz.Rect(297, 10, 595, 440),
        },
        "CorreoArg": {
            "rect2": fitz.Rect(50, 57, 305, 490),
            "a5_rect2": fitz.Rect(297, 10, 595, 440),
        },
    }
    # --------------------------------------------------------

    # Validar tipo de envío y completo segun requiera
    if tipo_envio not in envio_rects:
        print(f"Error: Tipo de envío '{tipo_envio}' no soportado.")
        return False
    # Areas para envio
    rect2 = envio_rects[tipo_envio]["rect2"]
    a5_rect2 = envio_rects[tipo_envio]["a5_rect2"]

    try:
        # Crear un nuevo PDF en formato A5
        doc_final = fitz.open()

        # Extraer y procesar el PDF de promoción
        with fitz.open(pdf1_path) as doc1:
            page1 = doc1[0]
            stream1 = extract_high_res_image(page1, rect1, dpi=260)

        # Extraer y procesar el PDF de la etiqueta de envío
        with fitz.open(label_envio) as doc2:
            page2 = doc2[0]
            stream2 = extract_high_res_image(page2, rect2, dpi=260)

        # Crear una nueva página A5 y agregar imágenes (595x420 puntos)
        new_page = doc_final.new_page(width=595, height=420)
        new_page.insert_image(a5_rect1, stream=stream1)  # Pegar flyer
        new_page.insert_image(a5_rect2, stream=stream2, overlay=True)  # Pegar etiqueta

        # Dibujar línea punteada en el centro
        x_middle = 297  # Centro de la hoja
        y_start, y_end = 1, 419

        # Dibujar línea punteada con segmentos
        for y in range(y_start, y_end, 3):  # Espaciado de 3 puntos
            new_page.draw_line(
                (x_middle, y), (x_middle, y + 2), color=(0, 0, 0), width=0.5
            )

        # Insertar imagen de tijera en la parte inferior si existe
        tijera_path = DATA_PATH / "tijera.png"
        if os.path.exists(tijera_path):
            tijera_rect = fitz.Rect(x_middle - 6, y_end - 18, x_middle + 6, y_end)
            new_page.insert_image(tijera_rect, filename=tijera_path)

        # Guardar el PDF final
        doc_final.save(output_file)
        print(f"PDF generado con éxito: {output_file}")

    except Exception as e:
        raise RuntimeError(f"Error al generar el PDF: {e}")

    finally:
        doc_final.close()
        os.remove(pdf1_path)  # Eliminar archivo temporal


def main():
    output_path = BASE_DIR / "ejemplo_salida.pdf"
    generate_sheet("MercadoLibre", DATA_PATH / "ejemplo_ml.pdf", output_path)


if __name__ == "__main__":
    main()
