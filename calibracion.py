#!/usr/bin/env python
"""
Experimentos que justifican dos decisiones del pipeline: el tamaño de fragmento
y el valor de k. Imprime evidencia, no modifica el índice ni el corpus.

Uso:  python calibracion.py
"""

import rag

# Caso de prueba de la fragmentación: el artículo 1 de la normativa de
# elegibilidad enumera cuatro condiciones que hay que cumplir TODAS. Si el corte
# separa la última condición del encabezado que dice "deberán cumplir todas las
# condiciones siguientes", el fragmento recuperado deja de ser evidencia:
# se lee como una regla suelta, sin saber de qué es condición.
ARCHIVO_FRAGMENTACION = "fip_elegibilidad_jugadores_2026.pdf"
ENCABEZADO = "deberán cumplir todas las condiciones siguientes"
ULTIMA_CONDICION = "36 (treinta y seis) meses"

CONSULTA_K = "¿Cuántos títulos mundiales masculinos ganó Argentina y en qué años?"


def experimento_fragmentacion():
    print("=" * 78)
    print("1. TAMAÑO DE FRAGMENTO")
    print("=" * 78)
    print(
        f"Documento: {ARCHIVO_FRAGMENTACION}\n"
        f'¿El encabezado "…{ENCABEZADO}" y la condición de los\n'
        f'"{ULTIMA_CONDICION}" quedan en el MISMO fragmento?\n'
    )

    documentos = [
        d for d in rag.cargar_pdfs() if d.metadata["archivo"] == ARCHIVO_FRAGMENTACION
    ]

    for tamanio, solapamiento in [(500, 50), (800, 100), (1200, 200)]:
        fragmentos = rag.fragmentar(documentos, tamanio, solapamiento)
        juntos = [
            f
            for f in fragmentos
            if ENCABEZADO in f.page_content and ULTIMA_CONDICION in f.page_content
        ]
        sueltos = [
            f
            for f in fragmentos
            if ULTIMA_CONDICION in f.page_content and ENCABEZADO not in f.page_content
        ]

        print(f"--- chunk_size={tamanio}, overlap={solapamiento} "
              f"→ {len(fragmentos)} fragmentos ---")
        if juntos:
            print("  ✔ La condición viaja con su encabezado.")
            print("    " + " ".join(juntos[0].page_content.split())[:150] + "…")
        else:
            print("  ✘ La condición quedó separada del encabezado.")
            for suelto in sueltos:
                print("    fragmento huérfano: "
                      + " ".join(suelto.page_content.split())[:150] + "…")
        print()


def experimento_k():
    print("=" * 78)
    print("2. VALOR DE k")
    print("=" * 78)
    print(f'Consulta: "{CONSULTA_K}"\n')

    indice = rag.abrir_indice()
    if rag.indice_vacio(indice):
        raise SystemExit("El índice está vacío. Ejecutá primero: python indexar.py")

    for k in (3, 6, 10):
        recuperados = rag.buscar(indice, CONSULTA_K, k=k)
        tipos = [d.metadata.get("tipo") for d, _ in recuperados]
        print(f"--- k={k} ---")
        for numero, (documento, distancia) in enumerate(recuperados, start=1):
            print(f"  {numero}. [{distancia:.4f}] {rag.referencia(documento)} "
                  f"({documento.metadata.get('tipo')})")
        print(f"  → {tipos.count('palmares')} de palmarés, "
              f"{tipos.count('edicion_mundial')} de ediciones, "
              f"{tipos.count('reglamento_fip')} de reglamentos, "
              f"{tipos.count('articulo_wikipedia')} de artículos.")
        print()


if __name__ == "__main__":
    experimento_fragmentacion()
    experimento_k()
