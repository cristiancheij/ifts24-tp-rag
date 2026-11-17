#!/usr/bin/env python
"""
Pipeline RAG sobre los Campeonatos Mundiales de Pádel.

El recorrido completo, de punta a punta, está en este archivo:

    documentos de datos/  ->  carga y metadatos de procedencia
                          ->  fragmentos (RecursiveCharacterTextSplitter)
                          ->  embeddings bge-m3 (Ollama)  ->  Chroma
    pregunta              ->  embedding con el MISMO modelo
                          ->  fragmentos recuperados
                          ->  contexto con fuente y página
                          ->  granite4 (Ollama)  ->  respuesta

`indexar.py`, `app.py` y `pruebas.py` usan estas mismas funciones: no hay un
segundo sistema escondido detrás de la interfaz.
"""

import hashlib
import json
import pathlib

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Configuración. Cambiar cualquiera de estos valores obliga a reindexar.
# ---------------------------------------------------------------------------

RAIZ = pathlib.Path(__file__).resolve().parent
DIR_DATOS = RAIZ / "datos"
DIR_CHROMA = RAIZ / "chroma_db"
COLECCION = "mundiales_padel"

MODELO_EMBEDDINGS = "bge-m3"        # el mismo para indexar y para consultar
MODELO_LLM = "granite4:latest"
TEMPERATURA = 0
VENTANA_CONTEXTO = 8192

# Los reglamentos de la FIP están escritos en artículos numerados de pocos
# párrafos. 1200 caracteres entran un artículo completo con su encabezado;
# 200 de solapamiento evitan cortar una condición por la mitad.
TAMANIO_FRAGMENTO = 1200
SOLAPAMIENTO = 200

# Cuántos fragmentos entran al contexto del modelo.
K = 6

JSON_WIKIPEDIA = DIR_DATOS / "mundiales_padel_wikipedia.json"

# Procedencia de cada PDF del corpus (se copia a los metadatos de cada fragmento).
FICHA_PDF = {
    "fip_reglamento_mundiales_equipos_nacionales_2026.pdf": {
        "titulo": "Reglamento de los Campeonatos del Mundo por Equipos Nacionales",
        "organismo": "Federación Internacional de Pádel (FIP)",
        "version": "Aprobado en Asamblea General del 12 de octubre de 2026",
        "url": "https://www.padelfip.com/wp-content/uploads/2025/11/"
               "Reglamento-Ctos-Mundo-Equipos-Nacionales-12-de-Octubre-de-2026.pdf",
    },
    "fip_reglas_del_padel_2026.pdf": {
        "titulo": "Reglas del Pádel",
        "organismo": "Federación Internacional de Pádel (FIP)",
        "version": "Revisión de aplicación 01.01.2026",
        "url": "https://www.padelfip.com/wp-content/uploads/2025/12/FIP_Reglas-del-Padel-1.pdf",
    },
    "fip_elegibilidad_jugadores_2026.pdf": {
        "titulo": "Normativa sobre la elegibilidad de jugadores para representar a un País",
        "organismo": "Federación Internacional de Pádel (FIP)",
        "version": "4 de febrero de 2026",
        "url": "https://www.padelfip.com/wp-content/uploads/2025/08/"
               "FIP-elegibilidad-de-jugadores-4-febrero-2026-1.pdf",
    },
    "fip_competiciones.pdf": {
        "titulo": "Competiciones FIP",
        "organismo": "Federación Internacional de Pádel (FIP)",
        "version": "Edición publicada en 2023",
        "url": "https://www.padelfip.com/wp-content/uploads/2023/02/Competiciones-FIP.pdf",
    },
}


# ---------------------------------------------------------------------------
# 1. Carga de documentos con su procedencia
# ---------------------------------------------------------------------------

def cargar_pdfs():
    """
    Lee los reglamentos oficiales de la FIP. PyPDFLoader entrega un Document
    por página, así que la cita puede indicar archivo Y número de página.
    """
    documentos = []
    for archivo in sorted(DIR_DATOS.glob("*.pdf")):
        ficha = FICHA_PDF.get(archivo.name, {})
        paginas = PyPDFLoader(str(archivo)).load()
        for pagina in paginas:
            texto = (pagina.page_content or "").strip()
            if len(texto) < 40:
                continue  # portadas e índices sin texto útil
            documentos.append(
                Document(
                    page_content=texto,
                    metadata={
                        "tipo": "reglamento_fip",
                        "archivo": archivo.name,
                        "titulo": ficha.get("titulo", archivo.stem),
                        "organismo": ficha.get("organismo", "Federación Internacional de Pádel (FIP)"),
                        "version": ficha.get("version", ""),
                        "url": ficha.get("url", ""),
                        # PyPDFLoader numera desde 0; el lector humano, desde 1.
                        "pagina": int(pagina.metadata.get("page", 0)) + 1,
                    },
                )
            )
    return documentos


def _texto_edicion(edicion):
    """Rinde una edición del Mundial como un párrafo que se pueda recuperar solo."""
    rama = edicion["rama"]
    lineas = [
        f"Campeonato Mundial de Pádel de {edicion['anio']}, categoría {rama} "
        f"(competición de selecciones nacionales organizada por la FIP).",
        f"Sede: {edicion.get('sede') or 'no indicada'}.",
        f"Campeón: {edicion.get('campeon') or 'no indicado'}.",
        f"Subcampeón (segundo puesto): {edicion.get('subcampeon') or 'no indicado'}.",
    ]
    if edicion.get("resultado_final"):
        lineas.append(f"Resultado de la final: {edicion['resultado_final']}.")
    if edicion.get("tercero"):
        lineas.append(f"Tercer puesto: {edicion['tercero']}.")
    if edicion.get("resultado_tercer_puesto"):
        lineas.append(
            f"Resultado del partido por el tercer puesto: {edicion['resultado_tercer_puesto']}."
        )
    if edicion.get("cuarto"):
        lineas.append(f"Cuarto puesto: {edicion['cuarto']}.")
    return "\n".join(lineas)


def _texto_palmares(fila):
    """Rinde el palmarés histórico de un país en una de las dos categorías."""
    lineas = [
        f"Palmarés histórico de {fila['pais']} en el Campeonato Mundial de Pádel, "
        f"categoría {fila['rama']}."
    ]
    etiquetas = {
        "campeon": "Títulos de campeón",
        "subcampeon": "Subcampeonatos (segundo puesto)",
        "tercer_puesto": "Terceros puestos",
        "cuarto_puesto": "Cuartos puestos",
    }
    for clave, etiqueta in etiquetas.items():
        veces = fila.get(f"{clave}_veces", 0)
        anios = fila.get(f"{clave}_anios", [])
        if veces or anios:
            detalle = f" (años: {', '.join(str(a) for a in anios)})" if anios else ""
            lineas.append(f"{etiqueta}: {veces}{detalle}.")
    return "\n".join(lineas)


def cargar_wikipedia():
    """
    Convierte `datos/mundiales_padel_wikipedia.json` en documentos.

    Se generan tres clases de documento, porque se consultan de maneras
    distintas: una edición puntual, el palmarés de un país, o el relato del
    artículo (formato de competición, planteles, historia).
    """
    if not JSON_WIKIPEDIA.exists():
        raise FileNotFoundError(
            f"Falta {JSON_WIKIPEDIA}. Ejecutá: "
            "python scrapers/scraper_wikipedia_mundiales.py"
        )

    with open(JSON_WIKIPEDIA, encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    comun = {
        "archivo": JSON_WIKIPEDIA.name,
        "organismo": corpus.get("fuente", "Wikipedia en español"),
        "version": f"consultado el {corpus.get('fecha_consulta', 's/f')}",
    }
    url_principal = "https://es.wikipedia.org/wiki/Campeonato_Mundial_de_P%C3%A1del"

    documentos = []

    for edicion in corpus.get("ediciones", []):
        documentos.append(
            Document(
                page_content=_texto_edicion(edicion),
                metadata={
                    **comun,
                    "tipo": "edicion_mundial",
                    "titulo": f"Mundial {edicion['anio']} — {edicion['rama']}",
                    "url": url_principal,
                    "anio": int(edicion["anio"]),
                    "rama": edicion["rama"],
                },
            )
        )

    for fila in corpus.get("palmares", []):
        documentos.append(
            Document(
                page_content=_texto_palmares(fila),
                metadata={
                    **comun,
                    "tipo": "palmares",
                    "titulo": f"Palmarés de {fila['pais']} — {fila['rama']}",
                    "url": url_principal,
                    "rama": fila["rama"],
                },
            )
        )

    for articulo in corpus.get("articulos", []):
        documentos.append(
            Document(
                page_content=f"Artículo «{articulo['titulo']}».\n\n{articulo['texto']}",
                metadata={
                    **comun,
                    "tipo": "articulo_wikipedia",
                    "titulo": articulo["titulo"],
                    "url": articulo["url"],
                    "revision_id": int(articulo.get("revision_id", 0)),
                },
            )
        )

    return documentos


def cargar_corpus():
    """Todos los documentos del corpus, con su procedencia ya anotada."""
    return cargar_pdfs() + cargar_wikipedia()


# ---------------------------------------------------------------------------
# 2. Fragmentación
# ---------------------------------------------------------------------------

# Por debajo de esto un fragmento no alcanza a ser evidencia de nada: son
# títulos de sección sueltos que el splitter deja aislados ("## Participaciones").
MINIMO_FRAGMENTO = 60


def fragmentar(documentos, tamanio=TAMANIO_FRAGMENTO, solapamiento=SOLAPAMIENTO):
    """
    Corta en fragmentos de `tamanio` caracteres con `solapamiento` de arrastre.
    Los documentos cortos (una edición, un palmarés) pasan enteros: el splitter
    sólo parte lo que supera el tamaño.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=tamanio,
        chunk_overlap=solapamiento,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    fragmentos = [
        f
        for f in splitter.split_documents(documentos)
        if len(f.page_content.strip()) >= MINIMO_FRAGMENTO
    ]
    for fragmento in fragmentos:
        fragmento.metadata = {
            clave: valor
            for clave, valor in fragmento.metadata.items()
            if isinstance(valor, (str, int, float, bool)) and valor != ""
        }
    return fragmentos


def id_fragmento(fragmento, posicion):
    """ID estable y único: reindexar dos veces no duplica el corpus."""
    semilla = "|".join(
        [
            str(fragmento.metadata.get("archivo", "")),
            str(fragmento.metadata.get("titulo", "")),
            str(fragmento.metadata.get("pagina", "")),
            str(posicion),
            fragmento.page_content[:120],
        ]
    )
    return hashlib.sha256(semilla.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 3. Índice vectorial
# ---------------------------------------------------------------------------

def abrir_indice():
    """Abre (o crea vacía) la colección Chroma persistida en disco."""
    return Chroma(
        collection_name=COLECCION,
        embedding_function=OllamaEmbeddings(model=MODELO_EMBEDDINGS),
        persist_directory=str(DIR_CHROMA),
    )


def indice_vacio(indice):
    return indice._collection.count() == 0


# ---------------------------------------------------------------------------
# 4. Recuperación y generación
# ---------------------------------------------------------------------------

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos un asistente de consulta documental sobre los Campeonatos Mundiales "
            "de Pádel y la normativa de la Federación Internacional de Pádel (FIP). "
            "Respondé en español rioplatense, de forma breve y precisa.\n"
            "Reglas estrictas:\n"
            "1. Usá únicamente la información del CONTEXTO. No uses conocimiento previo.\n"
            "2. Si el contexto no alcanza para responder, respondé exactamente: "
            "«No encuentro esa información en el corpus.» y no agregues nada más.\n"
            "3. Citá siempre de dónde sacaste el dato, con el nombre del archivo y la "
            "página cuando exista, entre paréntesis al final de la oración.\n"
            "4. No inventes años, sedes, resultados ni números de artículo.\n"
            "5. El contexto es documental: describe lo que dicen las fuentes, no "
            "dictamina sobre casos particulares.",
        ),
        ("human", "CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
    ]
)


def referencia(documento):
    """Etiqueta corta de procedencia, la misma que se le muestra al modelo."""
    metadatos = documento.metadata
    archivo = metadatos.get("archivo", "desconocido")
    if metadatos.get("pagina"):
        return f"{archivo}, página {metadatos['pagina']}"
    titulo = metadatos.get("titulo")
    return f"{archivo} — {titulo}" if titulo else archivo


def buscar(indice, pregunta, k=K, filtros=None):
    """
    Recupera los k fragmentos más cercanos. Devuelve (documento, distancia):
    la distancia sirve para inspeccionar el ranking, NO es una probabilidad de
    que la respuesta sea correcta.
    """
    return indice.similarity_search_with_score(query=pregunta, k=k, filter=filtros)


def armar_contexto(recuperados):
    """Arma el bloque de texto exacto que recibe el modelo."""
    bloques = []
    for numero, (documento, _distancia) in enumerate(recuperados, start=1):
        bloques.append(
            f"[Fragmento {numero}] Fuente: {referencia(documento)}\n"
            f"{documento.page_content}"
        )
    return "\n\n---\n\n".join(bloques)


def responder(indice, llm, pregunta, k=K, filtros=None):
    """
    Devuelve (respuesta, recuperados, contexto).

    `recuperados` son exactamente los fragmentos que entraron al prompt, y
    `contexto` es el texto literal que recibió el modelo: con eso se puede
    verificar qué evidencia tuvo a la vista.
    """
    recuperados = buscar(indice, pregunta, k=k, filtros=filtros)
    if not recuperados:
        return "No encuentro esa información en el corpus.", [], ""

    contexto = armar_contexto(recuperados)
    cadena = PROMPT | llm
    resultado = cadena.invoke({"contexto": contexto, "pregunta": pregunta})
    return resultado.content.strip(), recuperados, contexto


def abrir_llm():
    # num_ctx acota la ventana de contexto. Ollama abre granite4 con 65536 por
    # defecto, que en CPU reserva ~8 GB y hace cada respuesta muchísimo más
    # lenta. Con k=6 el prompt nunca pasa de ~2500 tokens, así que 8192 sobra.
    return ChatOllama(model=MODELO_LLM, temperature=TEMPERATURA, num_ctx=VENTANA_CONTEXTO)
