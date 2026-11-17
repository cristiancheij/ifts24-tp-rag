# RAG sobre los Campeonatos Mundiales de Pádel

**Autor:** Cristian Cheij

**Materia:** Laboratorio de PLN: Analítica, Textos y Cultura — IFTS N.º 24

**Trabajo Integrador 2** — 16 de noviembre de 2026

---

## 1. Problema y destinatario

> Este sistema permite que **una periodista deportiva** consulte **resultados,
> sedes, campeones y normativa de los Mundiales de pádel** en **los reglamentos
> oficiales de la FIP y el historial publicado en Wikipedia**, para **escribir
> notas con datos verificables, pudiendo volver al documento y a la página de
> origen**.

**Responde:** resultados, sedes y podios de todas las ediciones masculinas
(1992–2026) y femeninas (1992–2026); palmarés por país; formato de competición
de 2021, 2022 y 2024; reglamento de los Campeonatos del Mundo por Equipos
Nacionales; elegibilidad de jugadores; reglas de juego.

**No responde:** asistencia, audiencias, premios en dinero o patrocinios;
rankings individuales o resultados del circuito profesional; planteles completos
de todas las ediciones. Tampoco interpreta la normativa: el corpus es
documental, no normativo.

---

## 2. Corpus

Los cinco documentos están versionados en `datos/`. No hay documentos privados
ni datos personales.

| # | Documento | Archivo | Organismo | Fecha / versión | Licencia o permiso |
|---|---|---|---|---|---|
| 1 | [Reglamento de los Campeonatos del Mundo por Equipos Nacionales](https://www.padelfip.com/wp-content/uploads/2025/11/Reglamento-Ctos-Mundo-Equipos-Nacionales-12-de-Octubre-de-2026.pdf) | `fip_reglamento_mundiales_equipos_nacionales_2026.pdf` | Federación Internacional de Pádel (FIP) | Asamblea General del 12/10/2026 | Publicación pública en el sitio oficial de la FIP, difundida para federaciones, clubes y prensa. Se redistribuye sin modificar y con atribución. |
| 2 | [Reglas del Pádel](https://www.padelfip.com/wp-content/uploads/2025/12/FIP_Reglas-del-Padel-1.pdf) | `fip_reglas_del_padel_2026.pdf` | FIP | Revisión 01/01/2026 | Ídem |
| 3 | [Elegibilidad de jugadores para representar a un País](https://www.padelfip.com/wp-content/uploads/2025/08/FIP-elegibilidad-de-jugadores-4-febrero-2026-1.pdf) | `fip_elegibilidad_jugadores_2026.pdf` | FIP | 04/02/2026 | Ídem |
| 4 | [Competiciones FIP](https://www.padelfip.com/wp-content/uploads/2023/02/Competiciones-FIP.pdf) | `fip_competiciones.pdf` | FIP | 2023 | Ídem |
| 5 | Historial de los Mundiales: 7 artículos de Wikipedia en español con sus tablas de resultados y palmarés | `mundiales_padel_wikipedia.json` | Wikipedia en español | Consultado el 15/11/2026 | **CC BY-SA 4.0** |

**Procedencia verificable.** Los PDF se vuelven a bajar con
`python scrapers/descargar_documentos_fip.py`, que imprime el `sha256` de cada
archivo. El JSON guarda el `revision_id` de cada artículo, así que la versión
exacta que se indexó se consulta en
`https://es.wikipedia.org/w/index.php?oldid=<revision_id>`. Importa, porque el
artículo principal ya incorpora el Mundial de 2026, disputado días antes de
este trabajo.

**Revisión del texto extraído.** Los cuatro PDF tienen texto digital extraíble;
no hay escaneos ni hizo falta OCR. Se comparó el texto cargado contra el
original en los puntos que después se citan: dimensiones de la pista (pág. 5),
composición de equipos (pág. 6) y condiciones de elegibilidad (pág. 1).

En Wikipedia los datos viven en **tablas**, que el extractor de texto plano
descarta. Por eso el scraper reconstruye cada tabla respetando `rowspan` y
`colspan` y la rinde como líneas `Encabezado: valor`. Sin ese paso, las filas
con celdas combinadas se desalineaban y el campeón de una edición aparecía en
la columna de la sede.

---

## 3. Arquitectura

```
datos/*.pdf  --PyPDFLoader (1 doc por página)--+
                                               +-> Documents con procedencia
datos/*.json --scraper-------------------------+   (archivo, título, versión, página, url)
                                               |
                     RecursiveCharacterTextSplitter (1200 / 200)
                                               |
                        OllamaEmbeddings bge-m3 --> Chroma (269 fragmentos)

pregunta --> embedding con el MISMO modelo --> 6 fragmentos más cercanos
         --> contexto con "Fuente: archivo, página N" --> ChatOllama granite4
         --> respuesta + los mismos fragmentos mostrados en Gradio
```

| Archivo | Qué hace |
|---|---|
| `rag.py` | El pipeline completo: carga, metadatos, fragmentación, índice, búsqueda, prompt y generación. |
| `indexar.py` | Construye el índice e imprime qué se cargó, para poder inspeccionarlo. |
| `app.py` | Interfaz Gradio. Llama a `rag.responder()`; no implementa un sistema aparte. |
| `pruebas.py` | Corre los 7 casos y escribe `pruebas/resultados.md`. |
| `scrapers/` | Descarga de los PDF de la FIP y scraping del historial de Wikipedia. |

Modelos locales vía Ollama: **`bge-m3`** para embeddings y **`granite4:latest`**
(3,4 B, Q4_K_M) con `temperature=0` para generación. Python 3.12.

---

## 4. Instalación local

Requisitos: **Python 3.12**, [**uv**](https://docs.astral.sh/uv/) y
[**Ollama**](https://ollama.com/download) corriendo.

```bash
git clone https://github.com/cristiancheij/ifts24-tp-rag.git
cd ifts24-tp-rag

uv venv --python 3.12
uv pip install -r requirements.txt

ollama pull bge-m3
ollama pull granite4:latest

uv run python indexar.py     # construye el índice desde datos/
uv run python app.py         # abre http://127.0.0.1:7860
```

Para activar el entorno en lugar de usar `uv run`:
`.venv\Scripts\Activate.ps1` en Windows, `source .venv/bin/activate` en Linux o
macOS. En el editor, seleccionar el intérprete de `.venv`.

### Tiempos medidos (sin GPU)

Probado en una notebook **AMD Ryzen 5 3450U, 4 núcleos, sin GPU utilizable por
Ollama**: el modelo procesa 17,6 tokens/s de contexto y genera 7,3 tokens/s.

| Operación | Tiempo |
|---|---|
| Indexar los 269 fragmentos | ≈ 19 minutos, una sola vez |
| Una respuesta con el modelo ya cargado | ≈ 2 minutos |
| La primera respuesta tras arrancar | hasta 20 minutos |

`rag.py` fija `num_ctx=8192` al abrir el modelo: Ollama arranca `granite4` con
una ventana de 65536 tokens que reserva ~8 GB de RAM y lo vuelve mucho más
lento. Con 8192 ocupa ~2,9 GB y el prompt entra holgado. Con GPU todo esto es
cuestión de segundos.

---

## 5. Reindexación

El índice vive en `chroma_db/` y **no está versionado**: se reconstruye desde
los archivos de `datos/`.

```bash
python indexar.py            # indexa sólo si la colección está vacía
python indexar.py --rehacer  # borra chroma_db/ y reconstruye
```

Hay que rehacerlo si cambia el corpus, el tamaño de fragmento o el solapamiento,
y **obligatoriamente si cambia el modelo de embeddings**: vectores de modelos
distintos no son comparables, no se pueden mezclar en un mismo índice.

---

## 6. Pruebas

Los siete casos se escribieron **antes** de evaluar el sistema y están en
`pruebas.py`: cinco respondibles —al menos uno por documento— y dos cuyo dato no
existe en ninguna fuente. La salida completa, con los seis fragmentos y sus
distancias en cada caso, está en
**[`pruebas/resultados.md`](pruebas/resultados.md)**.

Corrida del 15/11/2026: **5 de 5** respondibles recuperaron la fuente esperada y
**2 de 2** sin respuesta terminaron en abstención.

| # | Pregunta | Fuente esperada | Fragmento recuperado | Respuesta del modelo | Observación |
|---|---|---|---|---|---|
| R1 | Jugadores por equipo en categoría Absoluta | Reglamento de Mundiales, pág. 6 | pág. 5 (0,57), pág. 5, **pág. 6 (0,65)**, 6, 7, 4 | "mínimo de seis (6) y un máximo de ocho (8) jugadores… (página 6)" | Correcta. **El mejor rankeado no fue el que tenía la respuesta**: la pág. 6 quedó tercera. Con `k` chico este caso fallaba. |
| R2 | Dimensiones de la pista | Reglas del Pádel, pág. 5 | **pág. 5 (0,67)** + 5 páginas del mismo reglamento | "10 metros de ancho por 20 metros de largo (medidas interiores) con una tolerancia de 0,5% (página 5)" | Textual respecto del PDF, incluida la tolerancia. |
| R3 | Condiciones para representar a un país | Elegibilidad, pág. 1 | **pág. 1 (0,41)**, la distancia más baja de la corrida | Enumeró las cuatro condiciones completas, con archivo y página | Valida la decisión de fragmentación: la cuarta condición llegó junto a su encabezado. |
| R4 | Campeón, sede y resultado del Mundial masculino 2024 | Wikipedia, edición 2024 | **Mundial 2024 — masculino (0,48)** | "ganado por Argentina, se jugó en Doha y el resultado de la final fue 2:1" | Los tres datos correctos, pero **omitió contra quién fue el 2:1**, que estaba en el fragmento. |
| R5 | Títulos masculinos de Argentina y en qué años | Wikipedia, palmarés masculino | **Palmarés de Argentina — masculino (0,66)** | Los 12 años completos y en orden, con la fuente | Sin años inventados. El palmarés femenino entró segundo y no los mezcló. |
| S1 | Entradas vendidas en la final de 2024 | No figura en el corpus | Mundial 2024 — femenino (0,70), sin relación con entradas | "No encuentro esa información en el corpus." | **Se abstuvo.** El buscador devuelve algo igual: la distancia no indica que el fragmento sirva. |
| S2 | Premio en dinero del campeón 2022 | No figura en el corpus | Artículo del Mundial 2022 (0,75), que no habla de premios | "No encuentro esa información en el corpus." | **Se abstuvo**, incluso con fragmentos del año correcto. |

### Limitaciones observadas

1. **Respuesta incompleta en R4.** El fallo no está en la extracción, ni en el
   corte, ni en la búsqueda —el fragmento correcto salió primero—: está en la
   **generación**, que resumió de más. Qué cambiaría: pedir en el prompt que,
   si la pregunta tiene varias partes, las responda todas.
2. **La abstención funcionó, pero eso no la garantiza.** Son dos casos con
   temperatura 0 y una fórmula fijada en el prompt. Es una comprobación del
   mecanismo, no una medición de precisión.
3. **El ranking no es la respuesta.** En R1 el fragmento con el dato quedó
   tercero. Mostrar los fragmentos no es decorativo: es la única forma de ver
   que el primero no siempre es el bueno.

---

## 7. Decisiones y límites

**Fragmentos de 1200 caracteres con 200 de solapamiento.** El artículo 1 de la
normativa de elegibilidad enumera cuatro condiciones que hay que cumplir
*todas*. Si el corte separa la última del encabezado que lo aclara, el fragmento
deja de ser evidencia: se lee como una regla suelta. Al probar tres cortes
sobre ese mismo PDF:

| chunk_size / overlap | ¿La condición viaja con su encabezado? |
|---|---|
| 500 / 50 | ✘ queda huérfana |
| 800 / 100 | ✘ queda huérfana |
| **1200 / 200** | **✔ sí** |

El corpus da **269 fragmentos**: 119 de artículos de Wikipedia, 92 de los
reglamentos, 35 de ediciones y 23 de palmarés. Se descarta todo fragmento de
menos de 60 caracteres, porque el splitter dejaba aislados títulos de sección
sueltos que no son evidencia de nada.

**k = 6.** El piso lo marcó R1, donde el fragmento con la respuesta quedó
tercero: con `k` de 1 o 2 esa pregunta fallaba. El techo se vio consultando el
índice con k de 3, 6 y 10: pasar de 6 a 10 no trae fuentes nuevas, trae más
pedazos del mismo artículo de Wikipedia. En la interfaz `k` es ajustable, para
poder inspeccionar ese efecto.

**Granularidad del corpus histórico.** El JSON no se indexa como un bloque: se
generan documentos separados por edición (35), por palmarés de país (23) y por
artículo (7). Así una pregunta por el campeón de 2024 recupera el párrafo
exacto de esa edición y no un pedazo de una tabla de 18 filas.

**Prompt.** Define qué cuenta como evidencia: sólo el contexto, sin conocimiento
previo, con obligación de citar archivo y página y una fórmula literal de
abstención. Es una instrucción, no un mecanismo que lo impida.

**Distancia ≠ confianza.** La interfaz la muestra para inspeccionar el ranking.
No es una probabilidad de que la respuesta sea verdadera.

**Alcance de las citas.** Que un fragmento esté en el contexto no prueba que el
modelo lo haya interpretado bien. Por eso la interfaz muestra los fragmentos y
el contexto literal: la verificación final la hace quien consulta.

### Límites del corpus

- La tabla masculina de Wikipedia tiene 17 ediciones y la femenina 18, porque en
  2018 sólo figura el torneo femenino. El sistema reproduce esa asimetría; no la
  corrige ni la explica.
- `fip_competiciones.pdf` es de 2023 y el resto de la normativa es de 2026. Si
  hubiera contradicción, el sistema no la detecta: muestra los dos fragmentos.
- Wikipedia no es fuente oficial. Para el historial es lo mejor disponible de
  forma libre y redistribuible, pero un dato publicable debería contrastarse
  contra la FIP. El sistema siempre dice de dónde salió cada cosa, justamente
  para permitir ese contraste.
- El corpus está en español; algunos reglamentos de la FIP sólo existen en
  inglés y quedaron afuera.

---

## 8. Uso de IA

Usé **Claude Code** como asistente durante el desarrollo: para
relevar qué documentos públicos sobre los Mundiales eran redistribuibles,
escribir los scrapers y el código del pipeline a partir de los cuadernos que usamos
a lo largo de la cursada, y redactar esta documentación.

La definición del caso y del destinatario, la elección de los cinco documentos
del corpus y la redacción de los siete casos de prueba fueron decisiones mías.

Verifiqué los PDF en las páginas que el sistema cita —composición de equipos (pág. 6),
dimensiones de la pista (pág. 5) y elegibilidad (pág. 1)— y las comparé con los 
fragmentos recuperados; contrasté la salida del scraper contra las tablas del artículo de Wikipedia;
y ejecuté el proyecto completo, corriendo los siete casos de prueba. Los resultados de `pruebas/resultados.md` son ejecuciones reales en
mi máquina, generadas por el propio script.

---


