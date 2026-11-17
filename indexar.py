#!/usr/bin/env python
"""
Construye el índice vectorial Chroma a partir de los documentos de `datos/`.

Uso:
    python indexar.py            # indexa si la colección está vacía
    python indexar.py --rehacer  # borra la colección y la reconstruye

El índice se guarda en `chroma_db/`, que NO se versiona: se reconstruye
siempre desde los archivos publicados en `datos/`.
"""

import shutil
import sys

import rag


def inspeccionar(documentos, titulo):
    """Muestra qué se cargó antes de indexar, para poder revisar el texto extraído."""
    print(f"\n--- {titulo}: {len(documentos)} documentos ---")
    por_tipo = {}
    for documento in documentos:
        por_tipo.setdefault(documento.metadata.get("tipo", "?"), 0)
        por_tipo[documento.metadata.get("tipo", "?")] += 1
    for tipo, cantidad in sorted(por_tipo.items()):
        print(f"  {tipo:22} {cantidad:>5}")
    if documentos:
        muestra = documentos[0]
        print(f"  ejemplo -> {rag.referencia(muestra)}")
        print("  " + muestra.page_content[:200].replace("\n", " ") + "…")


def main():
    rehacer = "--rehacer" in sys.argv

    if rehacer and rag.DIR_CHROMA.exists():
        print(f"Borrando {rag.DIR_CHROMA}…")
        shutil.rmtree(rag.DIR_CHROMA)

    print("Cargando corpus desde", rag.DIR_DATOS)
    pdfs = rag.cargar_pdfs()
    wiki = rag.cargar_wikipedia()
    inspeccionar(pdfs, "Reglamentos FIP (PDF, una entrada por página)")
    inspeccionar(wiki, "Corpus histórico (Wikipedia)")

    fragmentos = rag.fragmentar(pdfs + wiki)
    largos = [len(f.page_content) for f in fragmentos]
    print(
        f"\nFragmentos: {len(fragmentos)} "
        f"(tamaño {rag.TAMANIO_FRAGMENTO} / solapamiento {rag.SOLAPAMIENTO}) "
        f"| caracteres: mín {min(largos)}, promedio {sum(largos)//len(largos)}, máx {max(largos)}"
    )

    indice = rag.abrir_indice()
    if not rag.indice_vacio(indice) and not rehacer:
        print(
            f"\nLa colección «{rag.COLECCION}» ya tiene "
            f"{indice._collection.count()} fragmentos. "
            "Usá --rehacer para reconstruirla."
        )
        return

    identificadores = [rag.id_fragmento(f, i) for i, f in enumerate(fragmentos)]

    # Chroma limita la cantidad de documentos por operación: cargamos por lotes.
    lote = 200
    for inicio in range(0, len(fragmentos), lote):
        indice.add_documents(
            documents=fragmentos[inicio : inicio + lote],
            ids=identificadores[inicio : inicio + lote],
        )
        print(f"  indexados {min(inicio + lote, len(fragmentos))}/{len(fragmentos)}")

    print(
        f"\nListo: {indice._collection.count()} fragmentos en «{rag.COLECCION}» "
        f"({rag.DIR_CHROMA})."
    )


if __name__ == "__main__":
    main()
