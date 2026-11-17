#!/usr/bin/env python
"""
Descarga los reglamentos oficiales de la Federación Internacional de Pádel (FIP)
que forman la parte normativa del corpus.

Los PDF ya están versionados en `datos/`: este script existe para dejar
registrada la procedencia exacta (URL de origen) y para poder volver a bajarlos
si la cátedra quiere comprobar que son los mismos archivos.

Uso:  python scrapers/descargar_documentos_fip.py

Los documentos se publican en https://www.padelfip.com/es/documents/ para
consulta pública de federaciones, jugadores y prensa.
"""

import datetime
import hashlib
import pathlib

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "datos"

DOCUMENTOS = [
    (
        "fip_reglamento_mundiales_equipos_nacionales_2026.pdf",
        "https://www.padelfip.com/wp-content/uploads/2025/11/"
        "Reglamento-Ctos-Mundo-Equipos-Nacionales-12-de-Octubre-de-2026.pdf",
    ),
    (
        "fip_reglas_del_padel_2026.pdf",
        "https://www.padelfip.com/wp-content/uploads/2025/12/FIP_Reglas-del-Padel-1.pdf",
    ),
    (
        "fip_elegibilidad_jugadores_2026.pdf",
        "https://www.padelfip.com/wp-content/uploads/2025/08/"
        "FIP-elegibilidad-de-jugadores-4-febrero-2026-1.pdf",
    ),
    (
        "fip_competiciones.pdf",
        "https://www.padelfip.com/wp-content/uploads/2023/02/Competiciones-FIP.pdf",
    ),
]


def log(mensaje):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {mensaje}")


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, url in DOCUMENTOS:
        destino = DESTINO / nombre
        log(f"Descargando {nombre}…")
        respuesta = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        if respuesta.status_code != 200:
            log(f"  ERROR {respuesta.status_code} al pedir {url}")
            continue

        anterior = destino.read_bytes() if destino.exists() else None
        destino.write_bytes(respuesta.content)
        huella = hashlib.sha256(respuesta.content).hexdigest()[:16]

        estado = "nuevo"
        if anterior is not None:
            estado = "sin cambios" if anterior == respuesta.content else "ACTUALIZADO"
        log(f"  {len(respuesta.content):>8} bytes | sha256:{huella} | {estado}")

    log("Listo. Si algún archivo quedó ACTUALIZADO, conviene reindexar.")


if __name__ == "__main__":
    main()
