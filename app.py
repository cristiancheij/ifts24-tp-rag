#!/usr/bin/env python
"""
Interfaz Gradio del RAG sobre los Campeonatos Mundiales de Pádel.

La interfaz no implementa ningún sistema propio: llama a `rag.responder()`,
el mismo que usan `indexar.py` y `pruebas.py`. Muestra por separado la
respuesta del modelo y los fragmentos que efectivamente entraron al contexto,
con archivo y página.

Uso:
    python indexar.py    # una sola vez (o tras cambiar el corpus)
    python app.py        # abre http://127.0.0.1:7860
"""

import html

import gradio as gr

import rag

# Se abren una vez al arrancar: levantar el índice en cada pregunta sería lento.
INDICE = rag.abrir_indice()
LLM = rag.abrir_llm()

if rag.indice_vacio(INDICE):
    raise SystemExit(
        "El índice está vacío. Ejecutá primero:  python indexar.py\n"
        "(requiere Ollama corriendo y el modelo bge-m3 descargado)"
    )


def tarjeta_fragmento(numero, documento, distancia):
    """Una tarjeta HTML por fragmento recuperado, con su procedencia."""
    metadatos = documento.metadata
    pagina = metadatos.get("pagina")
    url = metadatos.get("url", "")

    filas = [
        ("Archivo", html.escape(str(metadatos.get("archivo", "—")))),
        ("Documento", html.escape(str(metadatos.get("titulo", "—")))),
        ("Página", str(pagina) if pagina else "— (no es PDF)"),
        ("Tipo", html.escape(str(metadatos.get("tipo", "—")))),
        ("Origen", html.escape(str(metadatos.get("organismo", "—")))),
        ("Versión", html.escape(str(metadatos.get("version", "—")))),
        ("Distancia", f"{distancia:.4f}"),
    ]
    detalle = "".join(
        f"<tr><td style='padding:2px 10px 2px 0; color:#666; white-space:nowrap'>{k}</td>"
        f"<td style='padding:2px 0'>{v}</td></tr>"
        for k, v in filas
    )
    enlace = (
        f"<div style='margin:6px 0'><a href='{html.escape(url)}' target='_blank'>"
        f"Ver la fuente original ↗</a></div>"
        if url
        else ""
    )

    return f"""
<div style="border:1px solid #d0d0d0; border-radius:8px; padding:12px; margin-bottom:14px">
  <h4 style="margin:0 0 8px 0">Fragmento #{numero}</h4>
  <table style="font-size:0.9em; border-collapse:collapse">{detalle}</table>
  {enlace}
  <pre style="white-space:pre-wrap; overflow-wrap:break-word; background:#f6f6f6;
              padding:10px; border-radius:6px; margin-top:8px; font-size:0.9em">{html.escape(documento.page_content)}</pre>
</div>
"""


def procesar(pregunta, k):
    if not pregunta or not pregunta.strip():
        return "_Escribí una pregunta._", "", ""

    respuesta, recuperados, contexto = rag.responder(
        INDICE, LLM, pregunta.strip(), k=int(k)
    )

    fragmentos = "".join(
        tarjeta_fragmento(numero, documento, distancia)
        for numero, (documento, distancia) in enumerate(recuperados, start=1)
    )
    if not fragmentos:
        fragmentos = "<p>El buscador no devolvió fragmentos.</p>"

    aviso = (
        "<p style='font-size:0.85em; color:#666'>La <b>distancia</b> ordena el ranking "
        "del buscador (más chica = más cercana en el espacio de embeddings). "
        "No es una probabilidad de que la respuesta sea verdadera.</p>"
    )

    return respuesta, aviso + fragmentos, contexto


EJEMPLOS = [
    "¿Quién ganó el Mundial de pádel masculino de 2024 y contra quién jugó la final?",
    "¿Cuántos títulos mundiales masculinos ganó Argentina y en qué años?",
    "¿Cuántos jugadores puede inscribir una selección en el Campeonato del Mundo por Equipos Nacionales?",
    "¿Qué condiciones tiene que cumplir un jugador para representar a un país en una competición oficial de la FIP?",
    "¿Cuánto mide una pista de pádel según el reglamento de la FIP?",
    "¿Cuántas entradas vendió la final del Mundial de pádel de 2024?",
]


with gr.Blocks(title="RAG — Mundiales de Pádel") as interfaz:
    gr.Markdown(
        """
# Consultas sobre los Mundiales de Pádel
Sistema de consulta documental para periodismo deportivo.
Responde **sólo** con lo que dicen los reglamentos oficiales de la **FIP** y el
historial de los Campeonatos Mundiales publicado en **Wikipedia**, y muestra
los fragmentos exactos que recibió el modelo.
"""
    )

    with gr.Row():
        pregunta = gr.Textbox(
            label="Pregunta",
            placeholder="Por ejemplo: ¿en qué sede se jugó el Mundial de 2022?",
            lines=2,
            scale=5,
        )
        k = gr.Slider(
            label="k (fragmentos al contexto)",
            minimum=1,
            maximum=12,
            step=1,
            value=rag.K,
            scale=1,
        )

    enviar = gr.Button("Preguntar", variant="primary")

    gr.Examples(examples=[[e] for e in EJEMPLOS], inputs=[pregunta], label="Ejemplos")

    with gr.Tab("Respuesta"):
        salida_respuesta = gr.Markdown(label="Respuesta del modelo")

    with gr.Tab("Fragmentos recuperados"):
        salida_fragmentos = gr.HTML(label="Fragmentos que entraron al contexto")

    with gr.Tab("Contexto literal enviado al modelo"):
        salida_contexto = gr.Textbox(
            label="Texto exacto del prompt",
            lines=20,
        )

    gr.Markdown(
        f"""
---
**Modelos:** embeddings `{rag.MODELO_EMBEDDINGS}` · generación `{rag.MODELO_LLM}` (ambos locales, vía Ollama).
**Fragmentación:** {rag.TAMANIO_FRAGMENTO} caracteres con {rag.SOLAPAMIENTO} de solapamiento.
El sistema puede equivocarse: la respuesta vale lo que valen los fragmentos de abajo.
"""
    )

    entradas = [pregunta, k]
    salidas = [salida_respuesta, salida_fragmentos, salida_contexto]
    enviar.click(fn=procesar, inputs=entradas, outputs=salidas)
    pregunta.submit(fn=procesar, inputs=entradas, outputs=salidas)


if __name__ == "__main__":
    interfaz.launch()
