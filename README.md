# RAG sobre los Campeonatos Mundiales de Pádel

**Autor:** Cristian Cheij
**Materia:** Laboratorio de PLN: Analítica, Textos y Cultura (Procesamiento de Lenguaje Natural) — IFTS N.º 24
**Trabajo Integrador 2** — 16 noviembre de 2026

---

## 1. Problema y destinatario

> Este sistema permite que **una periodista deportiva** consulte **quién ganó cada
> edición del Mundial de pádel, dónde se jugó, con qué resultado, qué países
> acumulan más títulos y qué dice la normativa de la FIP sobre la competición,
> los equipos, la elegibilidad de los jugadores y las reglas de juego**
> en **los reglamentos oficiales de la Federación Internacional de Pádel y el
> historial publicado en Wikipedia**, para **escribir notas con datos
> verificables, pudiendo volver siempre al documento y a la página de origen**.

El caso es concreto: cuando se juega un Mundial, la redacción necesita chequear
rápido un dato histórico ("¿cuántos títulos lleva Argentina?") o un dato
normativo ("¿cuántos jugadores entran en una convocatoria?"), y necesita poder
citar de dónde salió.

### Qué puede responder

- Resultados, sedes, campeones, subcampeones y terceros puestos de **todas las
  ediciones** del Mundial masculino (1992–2026) y femenino (1992–2026).
- **Palmarés histórico** por país en ambas categorías.
- **Formato de competición** de las ediciones 2021, 2022 y 2024.
- **Reglamento de los Campeonatos del Mundo por Equipos Nacionales**:
  inscripción, composición de equipos, organizador, equipo arbitral.
- **Elegibilidad** para representar a un país en competiciones de la FIP.
- **Reglas del pádel**: pista, red, pelota, pala, puntuación, saque, faltas.
- Denominaciones y competiciones de propiedad exclusiva de la FIP.

### Qué NO puede responder

- Datos de asistencia, audiencias, premios en dinero o patrocinios: no están en
  ningún documento del corpus.
- Rankings individuales, resultados del circuito Premier Padel / Cupra FIP Tour
  partido por partido, o estadísticas de jugadores.
- Planteles completos de todas las ediciones (Wikipedia sólo los detalla para
  algunas).
- Cualquier interpretación jurídica de la normativa: **el corpus es documental,
  no normativo**; el sistema describe lo que dicen las fuentes.

---

## 2. Corpus

Todos los archivos están versionados en `datos/`. No hay documentos privados ni
datos personales.

| # | Documento | Archivo en `datos/` | Autor / organismo | Procedencia | Fecha / versión | Permiso o licencia |
|---|---|---|---|---|---|---|
| 1 | Reglamento de los Campeonatos del Mundo por Equipos Nacionales (Absoluto y Júnior) | `fip_reglamento_mundiales_equipos_nacionales_2026.pdf` | Federación Internacional de Pádel (FIP) | [padelfip.com/es/documents](https://www.padelfip.com/wp-content/uploads/2025/11/Reglamento-Ctos-Mundo-Equipos-Nacionales-12-de-Octubre-de-2026.pdf) | Aprobado en Asamblea General del 12/10/2026 | Documento normativo de publicación pública en el sitio oficial de la FIP, difundido para federaciones, clubes, jugadores y prensa. Se redistribuye sin modificar y con atribución. |
| 2 | Reglas del Pádel | `fip_reglas_del_padel_2026.pdf` | Federación Internacional de Pádel (FIP) | [padelfip.com/es/documents](https://www.padelfip.com/wp-content/uploads/2025/12/FIP_Reglas-del-Padel-1.pdf) | Revisión de aplicación 01/01/2026 | Ídem anterior. |
| 3 | Normativa sobre la elegibilidad de jugadores para representar a un País | `fip_elegibilidad_jugadores_2026.pdf` | Federación Internacional de Pádel (FIP) | [padelfip.com/es/documents](https://www.padelfip.com/wp-content/uploads/2025/08/FIP-elegibilidad-de-jugadores-4-febrero-2026-1.pdf) | 04/02/2026 | Ídem anterior. |
| 4 | Competiciones FIP | `fip_competiciones.pdf` | Federación Internacional de Pádel (FIP) | [padelfip.com/es/documents](https://www.padelfip.com/wp-content/uploads/2023/02/Competiciones-FIP.pdf) | Edición publicada en 2023 | Ídem anterior. |
| 5 | Historial de los Mundiales (7 artículos de Wikipedia en español, con sus tablas de resultados y palmarés) | `mundiales_padel_wikipedia.json` | Comunidad de Wikipedia en español | API de es.wikipedia.org, ver `scrapers/scraper_wikipedia_mundiales.py` | Consultado el 15/11/2026; cada artículo guarda su `revision_id` | **CC BY-SA 4.0** — permite redistribución con atribución y bajo la misma licencia |

### Procedencia verificable

- Los cuatro PDF se pueden volver a bajar con
  `python scrapers/descargar_documentos_fip.py`, que imprime el `sha256` de cada
  archivo para comprobar que son los mismos que están versionados.
- Cada artículo de Wikipedia guarda su número de revisión. La versión exacta que
  se indexó se consulta en
  `https://es.wikipedia.org/w/index.php?oldid=<revision_id>`. Esto importa
  porque Wikipedia cambia: el artículo principal ya incorpora el resultado del
  Mundial de 2026, disputado pocos días antes de este trabajo.

### Artículos de Wikipedia incluidos

`Campeonato Mundial de Pádel` · `Campeonato Mundial de Pádel de 2021` ·
`Campeonato Mundial de Pádel de 2022` · `Campeonato Mundial de Pádel de 2024` ·
`Federación Internacional de Pádel` · `Selección masculina de pádel de Argentina` ·
`Selección femenina de pádel de Argentina`

### Revisión del texto extraído

Antes de indexar se comparó el texto extraído contra el documento original:

- Los cuatro PDF tienen **texto digital extraíble** (no son escaneos, no hizo
  falta OCR). `PyPDFLoader` devuelve un documento por página, así que la cita
  conserva el número de página que ve el lector.
- Verificación puntual: la página 5 de `fip_reglas_del_padel_2026.pdf` dice
  *"El área de juego es un rectángulo de 10 metros de ancho por 20 metros de
  largo (medidas interiores) con una tolerancia de 0,5%"*, idéntico al PDF
  abierto en un visor.
- En Wikipedia, **los datos viven en tablas**, y el extractor de texto plano de
  la API las descarta. Por eso el scraper reconstruye cada tabla respetando
  `rowspan`/`colspan` (función `expandir_tabla`) y la rinde como líneas
  `Encabezado: valor`. Sin ese paso, las filas con celdas combinadas se
  desalineaban y el campeón de una edición aparecía en la columna de la sede.

---

## 3. Arquitectura

```
datos/*.pdf  ──PyPDFLoader──┐
                            ├─► Documents con metadatos de procedencia
datos/*.json ──scraper──────┘   (archivo, título, organismo, versión, página, url)
                            │
                            ▼
              RecursiveCharacterTextSplitter (1200 / 200)
                            │
                            ▼
                OllamaEmbeddings("bge-m3")  ──►  Chroma (chroma_db/)

pregunta ──► embedding con bge-m3 (el MISMO modelo del índice)
         ──► similarity_search_with_score(k=6)
         ──► contexto con "Fuente: archivo, página N"
         ──► ChatPromptTemplate ──► ChatOllama("granite4:latest", temp=0)
         ──► respuesta  +  los mismos fragmentos mostrados en Gradio
```

| Archivo | Qué hace |
|---|---|
| `rag.py` | El pipeline completo: carga, metadatos, fragmentación, índice, búsqueda, prompt y generación. |
| `indexar.py` | Construye el índice Chroma e imprime qué se cargó, para poder inspeccionarlo. |
| `app.py` | Interfaz Gradio. Llama a `rag.responder()`; no implementa un sistema propio. |
| `pruebas.py` | Corre los siete casos de prueba y escribe `pruebas/resultados.md`. |
| `calibracion.py` | Los dos experimentos que justifican el tamaño de fragmento y el valor de k. |
| `scrapers/descargar_documentos_fip.py` | Vuelve a bajar los PDF oficiales y muestra su `sha256`. |
| `scrapers/scraper_wikipedia_mundiales.py` | Arma `datos/mundiales_padel_wikipedia.json` desde la API de Wikipedia. |

### Modelos y versiones

| Pieza | Elección |
|---|---|
| Embeddings | `bge-m3` (Ollama) — multilingüe, sirve para un corpus en español con terminología deportiva y jurídica |
| Generación | `granite4:latest` (Ollama), `temperature=0` |
| Índice | Chroma persistido en `chroma_db/`, colección `mundiales_padel` |
| Python | 3.12 |

---

## 4. Instalación local

Requisitos previos: **Python 3.12**, [**uv**](https://docs.astral.sh/uv/) y
[**Ollama**](https://ollama.com/download) corriendo.

```bash
git clone <URL-DE-ESTE-REPOSITORIO>
cd rag_mundiales_padel

# 1. Entorno
uv venv --python 3.12
uv pip install -r requirements.txt

# 2. Modelos locales (≈3,3 GB entre los dos)
ollama pull bge-m3
ollama pull granite4:latest

# 3. Índice vectorial (se genera desde datos/)
uv run python indexar.py

# 4. Interfaz
uv run python app.py        # abre http://127.0.0.1:7860
```

Si preferís activar el entorno en lugar de usar `uv run`:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Linux / macOS: `source .venv/bin/activate`

y después `python indexar.py` y `python app.py`.

En el editor, seleccioná como intérprete el de `.venv` (en VS Code:
*Python: Select Interpreter* → `.venv`).

### Nota sobre tiempos (medida, no estimada)

Todo esto se desarrolló y se probó en una notebook **sin GPU utilizable por
Ollama**: AMD Ryzen 5 3450U (4 núcleos), 30 GB de RAM, Windows 11. Los tiempos
reales en ese equipo:

| Operación | Tiempo medido |
|---|---|
| Indexar los 269 fragmentos con `bge-m3` | ≈ 19 minutos (una sola vez) |
| Una respuesta con el modelo **ya cargado** en memoria | ≈ 2 minutos |
| Una respuesta con el modelo **en frío** (primera pregunta tras arrancar) | hasta 20 minutos |

`granite4` procesa unos 17,6 tokens/s de contexto y genera 7,3 tokens/s en este
equipo; con k = 6 el prompt ronda los 2000 tokens, de ahí los ~2 minutos. Con
GPU todo esto es cuestión de segundos.

Por eso `rag.py` fija `num_ctx=8192` al abrir el modelo: Ollama arranca
`granite4` con una ventana de 65536 tokens, que reserva ~8 GB de RAM y hace
todo mucho más lento. Con 8192 el modelo ocupa ~2,9 GB y el prompt entra
holgado.

**Para la demo:** conviene hacer una pregunta cualquiera antes de empezar a
grabar, para que Ollama ya tenga el modelo en memoria.

---

## 5. Reindexación

El índice se guarda en **`chroma_db/`**, que **no está versionado** (ver
`.gitignore`): se reconstruye siempre desde los archivos de `datos/`.

```bash
python indexar.py            # indexa sólo si la colección está vacía
python indexar.py --rehacer  # borra chroma_db/ y reconstruye desde cero
```

Hay que **rehacer** el índice cuando cambia cualquiera de estas cosas:

- el corpus (`datos/`), por ejemplo al volver a correr los scrapers;
- `TAMANIO_FRAGMENTO` o `SOLAPAMIENTO` en `rag.py`;
- **el modelo de embeddings**. Esto no es opcional: vectores de dos modelos
  distintos no son comparables entre sí. Si se cambia `MODELO_EMBEDDINGS`, hay
  que crear un índice nuevo, no mezclar.

Para actualizar el corpus:

```bash
python scrapers/descargar_documentos_fip.py      # PDF oficiales de la FIP
python scrapers/scraper_wikipedia_mundiales.py   # historial desde Wikipedia
python indexar.py --rehacer
```

---

## 6. Pruebas

Los siete casos se escribieron **antes** de evaluar el sistema y están
codificados en `pruebas.py`. Son cinco respondibles —al menos uno por cada
documento del corpus— y dos cuyo dato no existe en ninguna fuente.

La salida completa, con los seis fragmentos que entraron al contexto en cada
caso y sus distancias, está en **[`pruebas/resultados.md`](pruebas/resultados.md)**,
generada por `python pruebas.py`.

Resultado de la corrida del 15/11/2026, 22:46: **5 de 5** preguntas
respondibles recuperaron la fuente esperada y **2 de 2** preguntas sin respuesta
terminaron en abstención.

| # | Pregunta | Respuesta / fuente esperada | Fragmento recuperado (archivo y página) | Respuesta del modelo | ¿Qué observaste? |
|---|---|---|---|---|---|
| **R1** | ¿Cuántos jugadores puede inscribir un equipo nacional en categoría Absoluta? | Mínimo 6 y máximo 8 — `fip_reglamento_mundiales_equipos_nacionales_2026.pdf`, pág. 6, art. 2.5.2 | Entraron 6 fragmentos del mismo reglamento: **pág. 5** (0,5686), pág. 5, **pág. 6** (0,6528), pág. 6, 7 y 4 | "…un mínimo de seis (6) y un máximo de ocho (8) jugadores… (Fuente: fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6)" | Correcta y bien citada. **El fragmento mejor rankeado no fue el que tenía la respuesta**: la página 6 quedó tercera. Con k = 1 este caso fallaba. Es el mejor argumento para no usar k chico. |
| **R2** | ¿Dimensiones del área de juego de una pista? | 10 × 20 m interiores, tolerancia 0,5% — `fip_reglas_del_padel_2026.pdf`, pág. 5 | `fip_reglas_del_padel_2026.pdf`, **pág. 5** (0,6728) y cinco páginas más del mismo reglamento | "…un rectángulo de 10 metros de ancho por 20 metros de largo (medidas interiores) con una tolerancia de 0,5% (Fuente: …, página 5)." | Textual respecto del PDF, incluida la tolerancia. La página correcta quedó primera. |
| **R3** | ¿Condiciones para representar a un país en una competición oficial de la FIP? | Las cuatro condiciones del art. 1 — `fip_elegibilidad_jugadores_2026.pdf`, pág. 1 | `fip_elegibilidad_jugadores_2026.pdf`, **pág. 1** (0,4069 — la distancia más baja de toda la corrida) | Enumeró las cuatro condiciones completas, incluida la de los 36 meses, y citó archivo y página. | Es el caso que valida la decisión de fragmentación: la cuarta condición llegó **junto a su encabezado**. Con cortes de 500 u 800 habría llegado suelta. |
| **R4** | ¿Quién ganó el Mundial masculino 2024, dónde y con qué resultado? | Argentina, Doha, 2:1 sobre España — `mundiales_padel_wikipedia.json` | `mundiales_padel_wikipedia.json` — **Mundial 2024 — masculino** (0,4824); segundo el femenino del mismo año | "…fue ganado por Argentina, se jugó en Doha y el resultado de la final fue 2:1." | Los tres datos correctos, pero **omitió contra quién fue el 2:1**, que sí estaba en el fragmento. Respuesta incompleta, no incorrecta. La granularidad por edición funcionó: recuperó el párrafo exacto de 2024, no un pedazo de tabla. |
| **R5** | ¿Cuántos títulos masculinos ganó Argentina y en qué años? | 12 títulos, con los 12 años — `mundiales_padel_wikipedia.json`, palmarés masculino | `mundiales_padel_wikipedia.json` — **Palmarés de Argentina — masculino** (0,6604) | Los 12 años completos y en orden, con la fuente. | Sin errores ni años inventados. El palmarés femenino entró segundo (0,7513) y el modelo no los mezcló. |
| **S1** | ¿Cuántas entradas se vendieron para la final del Mundial 2024? | No figura en el corpus | Recuperó igual 6 fragmentos, el mejor **Mundial 2024 — femenino** (0,7049): lo más cercano que tenía, sin relación con entradas | "No encuentro esa información en el corpus." | **Se abstuvo.** Muestra que el buscador *siempre* devuelve algo: la distancia 0,7049 no significa que el fragmento sirva. |
| **S2** | ¿Cuánto dinero en premios recibió el campeón del Mundial 2022? | No figura en el corpus | Mejor fragmento: artículo **Campeonato Mundial de Pádel de 2022** (0,7454), que habla del torneo pero no de premios | "No encuentro esa información en el corpus." | **Se abstuvo**, incluso con fragmentos muy on-topic del año correcto, que es el caso donde más tentado estaría de inventar. |

### Limitaciones observadas

1. **Respuesta incompleta en R4.** El modelo dio campeón, sede y resultado, pero
   se comió el rival de la final, que estaba en el fragmento recuperado. El
   fallo no está en la extracción, ni en el corte, ni en la búsqueda: está en la
   **generación**, que resumió de más. Qué cambiaría: pedir explícitamente en el
   prompt que, cuando la pregunta tenga varias partes, las responda todas.
2. **La abstención funcionó en los dos casos, pero eso no la garantiza.** Son
   dos preguntas, con un modelo a temperatura 0 y un prompt que fija la fórmula
   literal. No es una medición de precisión general: es una comprobación del
   mecanismo. Con otra redacción de la pregunta el resultado podría ser otro.
3. **El ranking no es la respuesta.** En R1 el fragmento con el dato quedó
   tercero. Mostrar los fragmentos en la interfaz no es decorativo: es la única
   forma de ver que el primero no siempre es el bueno.

---

## 7. Decisiones y límites

### Fragmentación: 1200 caracteres, 200 de solapamiento

La unidad que miden `chunk_size` y `chunk_overlap` son **caracteres**, no
palabras ni tokens. Los reglamentos de la FIP están escritos en artículos
numerados de pocos párrafos, así que el corte tiene que respetar el artículo
completo.

El caso que decidió el valor está en `calibracion.py` y se puede reproducir con
`python calibracion.py`. El artículo 1 de la normativa de elegibilidad enumera
cuatro condiciones que el jugador debe cumplir **todas**. Si el corte separa la
última condición del encabezado que dice *"deberán cumplir todas las condiciones
siguientes"*, el fragmento deja de ser evidencia: se lee como una regla suelta y
no se sabe de qué es condición.

| chunk_size / overlap | Fragmentos de ese PDF | ¿La condición viaja con su encabezado? |
|---|---|---|
| 500 / 50 | 9 | ✘ queda huérfana |
| 800 / 100 | 6 | ✘ queda huérfana |
| **1200 / 200** | **4** | **✔ sí** |

Los 200 de solapamiento cubren el caso en que una condición queda igual partida
entre dos fragmentos. Los documentos cortos —una edición del Mundial, el
palmarés de un país— pasan enteros: el splitter sólo parte lo que supera el
tamaño.

El corpus completo da **269 fragmentos**: 119 de artículos de Wikipedia, 92 de
los reglamentos de la FIP, 35 de ediciones y 23 de palmarés.

Una corrección que salió de inspeccionar el resultado: el splitter dejaba
aislados ocho fragmentos de 18 a 47 caracteres que eran sólo un título de
sección (`## Participaciones`) o la línea `Artículo «…»`. No son evidencia de
nada y ensuciaban el ranking, así que `rag.py` descarta todo fragmento de menos
de 60 caracteres (`MINIMO_FRAGMENTO`). De ahí la diferencia entre los 277
fragmentos que produce el corte y los 269 que se indexan.

### Granularidad del corpus de datos

El JSON de Wikipedia no se indexa como un bloque único. Se generan tres clases
de documento porque se consultan de maneras distintas:

- **una edición** (35 documentos): un párrafo autocontenido por año y categoría;
- **un palmarés** (23 documentos): los títulos de un país en una categoría;
- **un artículo** (7 documentos, fragmentados): formato de competición,
  historia, planteles.

Así, "¿quién ganó en 2024?" recupera el párrafo exacto de esa edición en lugar
de un pedazo arbitrario de una tabla de 18 filas.

### k = 6

`k` es la cantidad de fragmentos que entran al contexto del modelo. El segundo
experimento de `calibracion.py` corre la misma consulta —*"¿cuántos títulos
mundiales masculinos ganó Argentina y en qué años?"*— con k = 3, 6 y 10:

| k | Qué entra al contexto |
|---|---|
| 3 | 2 fragmentos de palmarés + 1 del artículo principal. Alcanza, pero no deja margen si la consulta es menos literal. |
| **6** | Los mismos 3 + 3 fragmentos del artículo y de la selección argentina, que sirven de contexto. |
| 10 | Los mismos 6 + 4 fragmentos más **del mismo artículo de Wikipedia**: no aportan fuentes nuevas y alargan el prompt. |

El fragmento decisivo (`Palmarés de Argentina — masculino`, distancia 0,6604)
está primero en los tres casos: subir `k` no mejora la evidencia, sólo agrega
ruido del mismo origen.

El límite por abajo lo marcó la prueba **R1**: ahí el fragmento que contenía la
respuesta —página 6 del reglamento— quedó **tercero**, detrás de dos fragmentos
de la página 5. Con k = 1 o k = 2 esa pregunta se respondía mal. Entre ese piso
y el techo del experimento anterior, 6 da margen sin inflar el contexto. En la
interfaz es ajustable para poder inspeccionar el efecto.

### Prompt

El prompt define qué cuenta como evidencia: **sólo el contexto**, con prohibición
explícita de usar conocimiento previo, obligación de citar archivo y página, y
una fórmula literal de abstención (*"No encuentro esa información en el
corpus."*). **La abstención no está garantizada**: es una instrucción, no un
mecanismo. Lo que se puede afirmar es lo que se observó en las pruebas, que está
documentado arriba.

### Distancia ≠ confianza

La interfaz muestra la distancia de cada fragmento porque sirve para inspeccionar
el ranking del buscador. No es una probabilidad de que la respuesta sea
verdadera: un fragmento irrelevante puede tener distancia baja si comparte
vocabulario con la pregunta.

### Alcance de las citas

Que un fragmento esté en el contexto **no prueba** que el modelo lo haya
interpretado bien. Por eso la interfaz muestra los fragmentos y el contexto
literal: la verificación final la hace la persona que consulta, volviendo al PDF
o al artículo.

### Límites conocidos del corpus

- **Asimetría en los datos de Wikipedia:** la tabla masculina tiene 17 ediciones
  y la femenina 18, porque en 2018 sólo figura el torneo femenino. El sistema
  reproduce esa asimetría; no la corrige ni la explica.
- **`fip_competiciones.pdf` es de 2023** y el resto de la normativa es de 2026.
  Si hubiera contradicción entre ambos, el sistema no la detecta: muestra los
  dos fragmentos y es la persona la que tiene que decidir cuál rige.
- Wikipedia **no es una fuente oficial**. Para el historial es lo mejor
  disponible de forma libre y redistribuible, pero un dato publicable debería
  contrastarse contra la FIP. El sistema siempre dice de dónde salió cada cosa,
  justamente para poder hacer ese contraste.
- El corpus está **en español**. Algunos reglamentos de la FIP sólo existen en
  inglés y quedaron afuera.

---

## 8. Uso de IA

Este proyecto se construyó **con asistencia de IA**, en una sesión de trabajo
del 15 y 16 de noviembre de 2026, usando **Claude Code (modelo Claude de
Anthropic)**. Lo declaro en detalle porque la consigna lo pide y porque el
lector tiene derecho a saber qué parte del texto y del código no salió
directamente de mi mano.

| Momento | Para qué usé la IA |
|---|---|
| Delimitación del corpus | Buscar qué documentos públicos existen sobre los Mundiales de pádel y cuáles se pueden redistribuir legalmente. La elección final del caso, del destinatario y de los cinco documentos la tomé yo. |
| Ingesta | Escribir `scrapers/scraper_wikipedia_mundiales.py`, en particular la reconstrucción de tablas con `rowspan`/`colspan`, y `scrapers/descargar_documentos_fip.py`. |
| Pipeline | Escribir `rag.py`, `indexar.py` y `app.py` siguiendo la ruta de la unidad 014 (PyPDFLoader, RecursiveCharacterTextSplitter, OllamaEmbeddings, Chroma, ChatPromptTemplate, ChatOllama). |
| Calibración y pruebas | Escribir `calibracion.py` y `pruebas.py`, y redactar los siete casos de prueba. |
| Documentación | Redactar este README. |

**Verificaciones que se hicieron durante el desarrollo y que cualquiera puede
reproducir:**

- Se comprobó que los cuatro PDF tienen texto digital extraíble, contando
  páginas y caracteres por archivo: no hay escaneos ni hizo falta OCR.
- Se contrastó el texto extraído contra el PDF en los puntos que después se
  citan en las pruebas: dimensiones de la pista (pág. 5), composición de equipos
  (pág. 6, art. 2.5.2) y condiciones de elegibilidad (pág. 1).
- Se contrastó la salida del scraper contra las tablas del artículo de
  Wikipedia: 17 ediciones masculinas y 18 femeninas, campeón y sede de cada año,
  y los años del palmarés de Argentina y España.
- Los dos experimentos de `calibracion.py` y los siete casos de `pruebas.py` son
  **ejecuciones reales** en esta máquina, no texto redactado: la salida de
  `pruebas/resultados.md` la generó el propio script, con fecha y hora.
- Se revisó que ninguna afirmación de este README sobre el comportamiento del
  sistema —en particular sobre la abstención— sea más fuerte que lo que muestran
  las pruebas.

**Qué verifiqué personalmente, abriendo los archivos originales:**

- Abrí `fip_reglamento_mundiales_equipos_nacionales_2026.pdf` en la página 6 y
  leí el artículo 2.5.2 completo, comparándolo con el fragmento que recuperó el
  sistema en la prueba R1.
- Abrí `fip_reglas_del_padel_2026.pdf` en la página 5 y comparé la frase de las
  dimensiones de la pista con la respuesta de R2.
- Entré al artículo «Campeonato Mundial de Pádel» de Wikipedia y comparé la
  tabla de resultados con los datos que usó el sistema en R4 y R5.
- Ejecuté el proyecto completo desde cero y corrí la interfaz Gradio.

> Los cuatro puntos de este último bloque son los que tengo que poder sostener
> yo mismo frente a la cátedra. Están redactados en primera persona porque los
> hice; si algo de esto no se hubiera hecho, no correspondería afirmarlo.

---

## 9. Contenido del repositorio

```
rag_mundiales_padel/
├── app.py                 Interfaz Gradio
├── rag.py                 Pipeline RAG completo
├── indexar.py             Construcción del índice Chroma
├── pruebas.py             Los siete casos de prueba
├── calibracion.py         Experimentos de fragmentación y de k
├── requirements.txt
├── .gitignore             Excluye .venv/ y chroma_db/
├── datos/                 El corpus, versionado
│   ├── fip_reglamento_mundiales_equipos_nacionales_2026.pdf
│   ├── fip_reglas_del_padel_2026.pdf
│   ├── fip_elegibilidad_jugadores_2026.pdf
│   ├── fip_competiciones.pdf
│   └── mundiales_padel_wikipedia.json
├── pruebas/
│   └── resultados.md      Salida real de pruebas.py
└── scrapers/
    ├── descargar_documentos_fip.py
    └── scraper_wikipedia_mundiales.py
```

No se publican `.env`, credenciales, datos personales ni el índice vectorial
generado.
