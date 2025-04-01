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
# Generador de flyer promocional con codigo QR.
#
import fitz  # PyMuPDF
import os
import qrcode
from cfg import DATA_PATH, TEMP_PATH
from pathlib import Path

# Asegurar que el directorio temporal exista
TEMP_PATH.mkdir(parents=True, exist_ok=True)


def qr_to_pdf(medio_venta: str, nro_orden: str, url: str) -> Path:
    """Genera un QR y lo inserta en un flyer promocional en PDF.

    Args:
        medio_venta (str): Medio de venta del producto.
        nro_orden (str): Número de orden del producto.
        url (str): URL base donde se debe redirigir el QR.

    Returns:
        Path: Ruta del PDF generado.
    """

    # Construir URL con parámetros
    qr_url = f"{url}?origen={medio_venta}&id={nro_orden}"

    # Generar el código QR y guardarlo como imagen temporal
    qr = qrcode.make(qr_url)
    qr_path = TEMP_PATH / "interm.png"
    qr.save(qr_path)

    # Ruta del PDF original
    pdf_path = DATA_PATH / "flyer.pdf"
    if not pdf_path.exists():
        print(f"Error: El archivo {pdf_path} no existe.")
        return None

    # Ruta del PDF generado
    output_pdf = TEMP_PATH / "interm.pdf"

    # Insertar QR en el PDF
    try:
        with fitz.open(pdf_path) as doc:
            page = doc[0]  # Primer página
            rect = fitz.Rect(190, 295, 259, 364)  # Coordenadas del QR
            page.insert_image(rect, filename=str(qr_path))
            doc.save(output_pdf)
    except Exception as e:
        print(f"Error procesando el PDF: {e}")
        return None
    finally:
        # Eliminar imagen temporal
        if qr_path.exists():
            os.remove(qr_path)

    return output_pdf


def main():
    """Genera un flyer con código QR mediante datos suministrados.

    - Define una URL base para el QR.
    - Llama a la función `qr_to_pdf()` para generar el PDF con el QR insertado.
    - Si el PDF se genera correctamente, imprime la ruta del archivo.
    """
    url = "https://www.tuweb.com.ar"
    output = qr_to_pdf("WEB", "111102222", url)
    if output:
        print(f"Flyer generado: {output}")


if __name__ == "__main__":
    main()
