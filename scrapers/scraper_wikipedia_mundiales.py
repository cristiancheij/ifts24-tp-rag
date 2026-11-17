#!/usr/bin/env python
"""
Scraper del historial de los Campeonatos Mundiales de Pádel (Wikipedia en español).

Genera `datos/mundiales_padel_wikipedia.json`, que es la copia exacta del corpus
histórico que indexa el RAG. Se guarda el `revision_id` de cada artículo para que
cualquiera pueda volver a la versión exacta que se usó:

    https://es.wikipedia.org/w/index.php?oldid=<revision_id>

Uso:  python scrapers/scraper_wikipedia_mundiales.py

Licencia del contenido descargado: CC BY-SA 4.0 (Wikipedia).
"""

import datetime
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

API = "https://es.wikipedia.org/w/api.php"
UA = "ifts24-rag-mundiales-padel/1.0 (trabajo practico educativo)"

# Artículos que forman el corpus histórico. El primero es el que tiene las
# tablas de resultados y palmarés; los demás aportan contexto por edición.
ARTICULOS = [
    "Campeonato Mundial de Pádel",
    "Campeonato Mundial de Pádel de 2021",
    "Campeonato Mundial de Pádel de 2022",
    "Campeonato Mundial de Pádel de 2024",
    "Federación Internacional de Pádel",
    "Selección masculina de pádel de Argentina",
    "Selección femenina de pádel de Argentina",
]

ARTICULO_TABLAS = "Campeonato Mundial de Pádel"

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "mundiales_padel_wikipedia.json"


def log(mensaje):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {mensaje}")


def pedir_api(parametros):
    """Llama a la API de Wikipedia y devuelve el JSON de respuesta."""
    url = API + "?" + urllib.parse.urlencode({**parametros, "format": "json"})
    peticion = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta)


def descargar_articulo(titulo):
    """Devuelve (html, revision_id) del artículo pedido."""
    datos = pedir_api({"action": "parse", "page": titulo, "prop": "text|revid"})
    if "error" in datos:
        raise RuntimeError(f'No existe el artículo "{titulo}": {datos["error"]}')
    return datos["parse"]["text"]["*"], datos["parse"]["revid"]


# ---------------------------------------------------------------------------
# Conversión de HTML a texto legible
# ---------------------------------------------------------------------------

def expandir_tabla(tabla):
    """
    Convierte una tabla HTML en una grilla rectangular de strings, respetando
    rowspan y colspan. Sin esto, las filas con celdas combinadas quedan
    desalineadas y los datos se leen de la columna equivocada.
    """
    grilla = {}
    for fila_idx, fila in enumerate(tabla.find_all("tr")):
        columna = 0
        for celda in fila.find_all(["th", "td"]):
            while (fila_idx, columna) in grilla:
                columna += 1
            texto = celda.get_text(" ", strip=True)
            filas_ocupadas = int(celda.get("rowspan", 1))
            columnas_ocupadas = int(celda.get("colspan", 1))
            for df in range(filas_ocupadas):
                for dc in range(columnas_ocupadas):
                    grilla[(fila_idx + df, columna + dc)] = texto
            columna += columnas_ocupadas

    if not grilla:
        return []
    alto = max(f for f, _ in grilla) + 1
    ancho = max(c for _, c in grilla) + 1
    return [[grilla.get((f, c), "") for c in range(ancho)] for f in range(alto)]


def tabla_a_texto(tabla):
    """Rinde una tabla como líneas 'Encabezado: valor', legibles para el modelo."""
    grilla = expandir_tabla(tabla)
    if len(grilla) < 2:
        return ""

    encabezados = [re.sub(r"\s+", " ", c) for c in grilla[0]]
    lineas = []
    for fila in grilla[1:]:
        if fila == grilla[0]:  # encabezado repetido en el medio de la tabla
            continue
        partes = []
        for encabezado, valor in zip(encabezados, fila):
            valor = re.sub(r"\s+", " ", valor).strip()
            if not valor:
                continue
            encabezado = encabezado.strip()
            partes.append(f"{encabezado}: {valor}" if encabezado else valor)
        if partes:
            lineas.append(" | ".join(partes))
    return "\n".join(lineas)


def html_a_texto(html):
    """
    Pasa el HTML del artículo a texto plano conservando títulos de sección y
    el contenido de las tablas (que es donde viven casi todos los datos).
    """
    sopa = BeautifulSoup(html, "html.parser")

    for basura in sopa.select(
        "sup.reference, .mw-editsection, table.navbox, .mw-empty-elt, style, .ambox"
    ):
        basura.decompose()

    contenido = sopa.select_one("div.mw-parser-output") or sopa
    bloques = []
    for elemento in contenido.find_all(
        ["h2", "h3", "h4", "p", "ul", "ol", "table"], recursive=True
    ):
        if elemento.find_parent("table"):  # ya se rinde con su tabla madre
            continue
        if elemento.name in ("h2", "h3", "h4"):
            titulo = elemento.get_text(" ", strip=True)
            if titulo and titulo not in ("Referencias", "Enlaces externos", "Véase también"):
                bloques.append(f"\n## {titulo}")
        elif elemento.name == "table":
            if "metadata" in (elemento.get("class") or []):
                continue
            texto = tabla_a_texto(elemento)
            if texto:
                bloques.append(texto)
        else:
            texto = re.sub(r"\s+", " ", elemento.get_text(" ", strip=True))
            if len(texto) > 3:
                bloques.append(texto)

    texto = "\n".join(bloques)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


# ---------------------------------------------------------------------------
# Extracción estructurada de las tablas de resultados y palmarés
# ---------------------------------------------------------------------------

def limpiar(valor):
    """Normaliza una celda: colapsa espacios y quita 'Detalle' / país duplicado."""
    valor = (valor or "").replace("​", "")  # marcas invisibles de las referencias
    valor = re.sub(r"\s+", " ", valor).strip()
    valor = re.sub(r"\s*Detalle\s*$", "", valor)
    # Wikipedia repite el nombre del país al lado del ícono de bandera
    # ("España España"); nos quedamos con una sola aparición.
    palabras = valor.split()
    mitad = len(palabras) // 2
    if palabras and mitad and palabras[:mitad] == palabras[mitad:]:
        valor = " ".join(palabras[:mitad])
    return valor.strip()


def parsear_tabla_resultados(tabla, rama):
    """Devuelve una lista de ediciones a partir de la tabla 'Año | Sede | ...'."""
    grilla = expandir_tabla(tabla)
    if not grilla:
        return []

    encabezados = [limpiar(c) for c in grilla[0]]
    # Las columnas vacías del encabezado son separadores decorativos.
    utiles = [i for i, e in enumerate(encabezados) if e]

    def buscar(*claves):
        for i in utiles:
            texto = encabezados[i].lower()
            if any(clave in texto for clave in claves):
                return i
        return None

    col = {
        "anio": buscar("año"),
        "sede": buscar("sede"),
        "campeon": buscar("campeón"),
        "resultado_final": buscar("final"),
        "subcampeon": buscar("segundo"),
        "tercero": buscar("tercer lugar"),
        "resultado_tercer_puesto": buscar("3.º y 4.º", "3r y 4º", "3º y 4º"),
        "cuarto": buscar("cuarto"),
    }

    ediciones = []
    for fila in grilla[1:]:
        anio_crudo = limpiar(fila[col["anio"]]) if col["anio"] is not None else ""
        coincidencia = re.search(r"(19|20)\d{2}", anio_crudo)
        if not coincidencia:
            continue
        edicion = {"rama": rama, "anio": int(coincidencia.group(0))}
        for clave, indice in col.items():
            if clave == "anio" or indice is None or indice >= len(fila):
                continue
            edicion[clave] = limpiar(fila[indice])
        ediciones.append(edicion)
    return ediciones


def parsear_tabla_palmares(tabla, rama):
    """Devuelve el palmarés por país: cuántas veces y en qué años."""
    grilla = expandir_tabla(tabla)
    if not grilla:
        return []

    encabezados = [limpiar(c).lower() for c in grilla[0]]
    puestos = {
        "campeon": next((i for i, e in enumerate(encabezados) if "campeón" in e and "sub" not in e), None),
        "subcampeon": next((i for i, e in enumerate(encabezados) if "subcampeón" in e), None),
        "tercer_puesto": next((i for i, e in enumerate(encabezados) if "tercer" in e), None),
        "cuarto_puesto": next((i for i, e in enumerate(encabezados) if "cuarto" in e), None),
    }

    filas = []
    for fila in grilla[1:]:
        pais = limpiar(fila[0])
        if not pais or pais.lower() == "país":
            continue
        registro = {"rama": rama, "pais": pais}
        for puesto, indice in puestos.items():
            celda = limpiar(fila[indice]) if indice is not None and indice < len(fila) else ""
            cantidad = re.match(r"(\d+)", celda)
            registro[f"{puesto}_veces"] = int(cantidad.group(1)) if cantidad else 0
            registro[f"{puesto}_anios"] = [int(a) for a in re.findall(r"(?:19|20)\d{2}", celda)]
        filas.append(registro)
    return filas


def extraer_tablas(html):
    """Ubica las cuatro tablas del artículo principal usando los títulos previos."""
    sopa = BeautifulSoup(html, "html.parser")
    for basura in sopa.select("sup.reference, .mw-editsection"):
        basura.decompose()

    ediciones, palmares = [], []
    seccion = None
    for elemento in sopa.find_all(["h2", "h3", "table"]):
        if elemento.name in ("h2", "h3"):
            seccion = elemento.get_text(" ", strip=True).lower()
            continue
        if seccion is None:
            continue
        rama = "masculino" if "masculino" in seccion else ("femenino" if "femenino" in seccion else None)
        if rama is None:
            continue
        if "campeonato del mundo" in seccion:
            ediciones += parsear_tabla_resultados(elemento, rama)
        elif "pádel" in seccion:  # subsecciones del palmarés
            palmares += parsear_tabla_palmares(elemento, rama)
    return ediciones, palmares


# ---------------------------------------------------------------------------

def main():
    hoy = datetime.date.today().isoformat()
    corpus = {
        "fuente": "Wikipedia en español",
        "licencia": "CC BY-SA 4.0",
        "fecha_consulta": hoy,
        "articulos": [],
        "ediciones": [],
        "palmares": [],
    }

    for titulo in ARTICULOS:
        log(f"Descargando «{titulo}»…")
        try:
            html, revision = descargar_articulo(titulo)
        except Exception as error:  # noqa: BLE001 - queremos seguir con el resto
            log(f"  ERROR: {error}")
            continue

        corpus["articulos"].append(
            {
                "titulo": titulo,
                "url": "https://es.wikipedia.org/wiki/" + urllib.parse.quote(titulo.replace(" ", "_")),
                "revision_id": revision,
                "texto": html_a_texto(html),
            }
        )

        if titulo == ARTICULO_TABLAS:
            ediciones, palmares = extraer_tablas(html)
            corpus["ediciones"] = sorted(ediciones, key=lambda e: (e["rama"], e["anio"]))
            corpus["palmares"] = palmares
            log(f"  {len(ediciones)} ediciones y {len(palmares)} filas de palmarés")

        time.sleep(1)  # cortesía con los servidores de Wikimedia

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(corpus, archivo, indent=2, ensure_ascii=False)

    log(f"Guardado {SALIDA} ({len(corpus['articulos'])} artículos).")


if __name__ == "__main__":
    main()
