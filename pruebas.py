#!/usr/bin/env python
"""
Corre los casos de prueba definidos ANTES de evaluar el sistema y deja el
resultado en `pruebas/resultados.md`.

Son siete casos: cinco respondibles (al menos uno por cada documento del
corpus) y dos cuyo dato no está en ningún documento, para ver si el sistema
se abstiene. La abstención NO está garantizada: se comprueba, no se promete.

Uso:  python pruebas.py
"""

import datetime
import pathlib
import textwrap

import rag

SALIDA = pathlib.Path(__file__).resolve().parent / "pruebas" / "resultados.md"

ABSTENCION = "No encuentro esa información en el corpus."

CASOS = [
    {
        "id": "R1",
        "pregunta": "¿Cuántos jugadores puede inscribir un equipo nacional en categoría "
                    "Absoluta en el Campeonato del Mundo por Equipos Nacionales?",
        "esperado": "Mínimo 6 y máximo 8 jugadores — "
                    "fip_reglamento_mundiales_equipos_nacionales_2026.pdf, pág. 6 (art. 2.5.2).",
        "fuente_esperada": "fip_reglamento_mundiales_equipos_nacionales_2026.pdf",
    },
    {
        "id": "R2",
        "pregunta": "¿Cuáles son las dimensiones del área de juego de una pista de pádel?",
        "esperado": "10 metros de ancho por 20 de largo (medidas interiores), tolerancia 0,5% — "
                    "fip_reglas_del_padel_2026.pdf, pág. 5.",
        "fuente_esperada": "fip_reglas_del_padel_2026.pdf",
    },
    {
        "id": "R3",
        "pregunta": "¿Qué condiciones tiene que cumplir un jugador para representar a un país "
                    "en una competición oficial de la FIP?",
        "esperado": "Nacionalidad permanente, estar en regla con el miembro asociado, no haber "
                    "representado nunca a otro país en un mundial o continental absoluto y no "
                    "haber representado a otro país en los últimos 36 meses — "
                    "fip_elegibilidad_jugadores_2026.pdf, pág. 1.",
        "fuente_esperada": "fip_elegibilidad_jugadores_2026.pdf",
    },
    {
        "id": "R4",
        "pregunta": "¿Quién ganó el Campeonato Mundial de Pádel masculino de 2024, "
                    "dónde se jugó y cuál fue el resultado de la final?",
        "esperado": "Argentina, en Doha, 2:1 sobre España — "
                    "mundiales_padel_wikipedia.json (artículo «Campeonato Mundial de Pádel»).",
        "fuente_esperada": "mundiales_padel_wikipedia.json",
    },
    {
        "id": "R5",
        "pregunta": "¿Cuántos títulos mundiales masculinos ganó Argentina y en qué años?",
        "esperado": "12 títulos: 1992, 1994, 1996, 2000, 2002, 2004, 2006, 2012, 2014, 2016, "
                    "2022 y 2024 — mundiales_padel_wikipedia.json (palmarés masculino).",
        "fuente_esperada": "mundiales_padel_wikipedia.json",
    },
    {
        "id": "S1",
        "pregunta": "¿Cuántas entradas se vendieron para la final del Campeonato Mundial "
                    "de Pádel de 2024?",
        "esperado": "No figura en el corpus. Se espera abstención.",
        "fuente_esperada": None,
    },
    {
        "id": "S2",
        "pregunta": "¿Cuánto dinero en premios recibió el equipo campeón del Mundial "
                    "de pádel de 2022?",
        "esperado": "No figura en el corpus. Se espera abstención.",
        "fuente_esperada": None,
    },
]


def recorte(texto, ancho=160):
    """Texto de una sola línea, apto para una celda de tabla Markdown."""
    limpio = " ".join((texto or "").split()).replace("|", "\\|")
    return textwrap.shorten(limpio, width=ancho, placeholder=" …")


def main():
    indice = rag.abrir_indice()
    if rag.indice_vacio(indice):
        raise SystemExit("El índice está vacío. Ejecutá primero: python indexar.py")
    llm = rag.abrir_llm()

    resultados = []
    for caso in CASOS:
        print(f"[{caso['id']}] {caso['pregunta'][:70]}…")
        respuesta, recuperados, _contexto = rag.responder(indice, llm, caso["pregunta"])

        fuentes = [rag.referencia(documento) for documento, _ in recuperados]
        archivos = [documento.metadata.get("archivo", "") for documento, _ in recuperados]

        resultados.append(
            {
                **caso,
                "respuesta": respuesta,
                "fuentes": fuentes,
                "distancias": [distancia for _, distancia in recuperados],
                "recupero_fuente_esperada": (
                    caso["fuente_esperada"] in archivos if caso["fuente_esperada"] else None
                ),
                "se_abstuvo": ABSTENCION.lower() in (respuesta or "").lower(),
            }
        )

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    lineas = [
        "# Resultados de las pruebas",
        "",
        f"Generado automáticamente por `pruebas.py` el "
        f"{datetime.datetime.now():%Y-%m-%d %H:%M}.",
        "",
        f"Configuración: embeddings `{rag.MODELO_EMBEDDINGS}`, generación "
        f"`{rag.MODELO_LLM}` (temperatura {rag.TEMPERATURA}), fragmentos de "
        f"{rag.TAMANIO_FRAGMENTO} caracteres con {rag.SOLAPAMIENTO} de solapamiento, k = {rag.K}.",
        "",
        "## Resumen",
        "",
        "| # | Pregunta | Respuesta/fuente esperada | Fragmento mejor rankeado | Respuesta del modelo | ¿Recuperó la fuente esperada? |",
        "|---|---|---|---|---|---|",
    ]
    for resultado in resultados:
        mejor = resultado["fuentes"][0] if resultado["fuentes"] else "—"
        if resultado["fuente_esperada"] is None:
            marca = "se abstuvo ✔" if resultado["se_abstuvo"] else "NO se abstuvo ✘"
        else:
            marca = "sí ✔" if resultado["recupero_fuente_esperada"] else "no ✘"
        lineas.append(
            f"| {resultado['id']} | {recorte(resultado['pregunta'], 110)} "
            f"| {recorte(resultado['esperado'], 130)} | {mejor} "
            f"| {recorte(resultado['respuesta'], 200)} | {marca} |"
        )

    lineas += ["", "## Detalle por caso", ""]
    for resultado in resultados:
        lineas += [
            f"### {resultado['id']} — {resultado['pregunta']}",
            "",
            f"**Esperado:** {resultado['esperado']}",
            "",
            "**Respuesta del modelo:**",
            "",
            "```",
            (resultado["respuesta"] or "(vacía)").strip(),
            "```",
            "",
            f"**Fragmentos que entraron al contexto (k = {rag.K}):**",
            "",
        ]
        for numero, (fuente, distancia) in enumerate(
            zip(resultado["fuentes"], resultado["distancias"]), start=1
        ):
            lineas.append(f"{numero}. `{fuente}` — distancia {distancia:.4f}")
        lineas.append("")

    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nEscrito {SALIDA}")

    aciertos = sum(1 for r in resultados if r["recupero_fuente_esperada"])
    abstenciones = sum(1 for r in resultados if r["fuente_esperada"] is None and r["se_abstuvo"])
    print(f"Recuperación correcta: {aciertos}/5 respondibles")
    print(f"Abstenciones: {abstenciones}/2 sin respuesta")


if __name__ == "__main__":
    main()
