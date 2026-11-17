# Resultados de las pruebas

Generado automáticamente por `pruebas.py` el 2026-11-15 22:46.

Configuración: embeddings `bge-m3`, generación `granite4:latest` (temperatura 0), fragmentos de 1200 caracteres con 200 de solapamiento, k = 6.

## Resumen

| # | Pregunta | Respuesta/fuente esperada | Fragmento mejor rankeado | Respuesta del modelo | ¿Recuperó la fuente esperada? |
|---|---|---|---|---|---|
| R1 | ¿Cuántos jugadores puede inscribir un equipo nacional en categoría Absoluta en el Campeonato del Mundo por … | Mínimo 6 y máximo 8 jugadores — fip_reglamento_mundiales_equipos_nacionales_2026.pdf, pág. 6 (art. 2.5.2). | fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 5 | Un equipo nacional puede inscribir un mínimo de seis (6) y un máximo de ocho (8) jugadores en categoría Absoluta en el Campeonato del Mundo por Equipos Nacionales. (Fuente: … | sí ✔ |
| R2 | ¿Cuáles son las dimensiones del área de juego de una pista de pádel? | 10 metros de ancho por 20 de largo (medidas interiores), tolerancia 0,5% — fip_reglas_del_padel_2026.pdf, pág. 5. | fip_reglas_del_padel_2026.pdf, página 5 | Las dimensiones del área de juego de una pista de pádel son un rectángulo de 10 metros de ancho por 20 metros de largo (medidas interiores) con una tolerancia de 0,5% (Fuente: … | sí ✔ |
| R3 | ¿Qué condiciones tiene que cumplir un jugador para representar a un país en una competición oficial de la FIP? | Nacionalidad permanente, estar en regla con el miembro asociado, no haber representado nunca a otro país en un mundial o … | fip_elegibilidad_jugadores_2026.pdf, página 1 | Para representar a un país en una competición oficial de la FIP, un jugador debe cumplir con las siguientes condiciones: 1. Poseer la nacionalidad permanente del país, demostrable a través de un … | sí ✔ |
| R4 | ¿Quién ganó el Campeonato Mundial de Pádel masculino de 2024, dónde se jugó y cuál fue el resultado de la … | Argentina, en Doha, 2:1 sobre España — mundiales_padel_wikipedia.json (artículo «Campeonato Mundial de Pádel»). | mundiales_padel_wikipedia.json — Mundial 2024 — masculino | El Campeonato Mundial de Pádel masculino de 2024 fue ganado por Argentina, se jugó en Doha y el resultado de la final fue 2:1. (Fuente: mundiales_padel_wikipedia.json, pádel masculino) | sí ✔ |
| R5 | ¿Cuántos títulos mundiales masculinos ganó Argentina y en qué años? | 12 títulos: 1992, 1994, 1996, 2000, 2002, 2004, 2006, 2012, 2014, 2016, 2022 y 2024 — mundiales_padel_wikipedia.json (palmarés … | mundiales_padel_wikipedia.json — Palmarés de Argentina — masculino | Argentina ganó 12 títulos mundiales masculinos en los años: 1992, 1994, 1996, 2000, 2002, 2004, 2006, 2012, 2014, 2016, 2022 y 2024. (Fuente: mundiales_padel_wikipedia.json, Palmarés histórico de … | sí ✔ |
| S1 | ¿Cuántas entradas se vendieron para la final del Campeonato Mundial de Pádel de 2024? | No figura en el corpus. Se espera abstención. | mundiales_padel_wikipedia.json — Mundial 2024 — femenino | No encuentro esa información en el corpus. | se abstuvo ✔ |
| S2 | ¿Cuánto dinero en premios recibió el equipo campeón del Mundial de pádel de 2022? | No figura en el corpus. Se espera abstención. | mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel de 2022 | No encuentro esa información en el corpus. | se abstuvo ✔ |

## Detalle por caso

### R1 — ¿Cuántos jugadores puede inscribir un equipo nacional en categoría Absoluta en el Campeonato del Mundo por Equipos Nacionales?

**Esperado:** Mínimo 6 y máximo 8 jugadores — fip_reglamento_mundiales_equipos_nacionales_2026.pdf, pág. 6 (art. 2.5.2).

**Respuesta del modelo:**

```
Un equipo nacional puede inscribir un mínimo de seis (6) y un máximo de ocho (8) jugadores en categoría Absoluta en el Campeonato del Mundo por Equipos Nacionales. (Fuente: fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6)
```

**Fragmentos que entraron al contexto (k = 6):**

1. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 5` — distancia 0.5686
2. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 5` — distancia 0.6090
3. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6` — distancia 0.6528
4. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6` — distancia 0.8439
5. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 7` — distancia 0.8494
6. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 4` — distancia 0.8832

### R2 — ¿Cuáles son las dimensiones del área de juego de una pista de pádel?

**Esperado:** 10 metros de ancho por 20 de largo (medidas interiores), tolerancia 0,5% — fip_reglas_del_padel_2026.pdf, pág. 5.

**Respuesta del modelo:**

```
Las dimensiones del área de juego de una pista de pádel son un rectángulo de 10 metros de ancho por 20 metros de largo (medidas interiores) con una tolerancia de 0,5% (Fuente: fip_reglas_del_padel_2026.pdf, página 5).
```

**Fragmentos que entraron al contexto (k = 6):**

1. `fip_reglas_del_padel_2026.pdf, página 5` — distancia 0.6728
2. `fip_reglas_del_padel_2026.pdf, página 9` — distancia 0.7254
3. `fip_reglas_del_padel_2026.pdf, página 7` — distancia 0.7282
4. `fip_reglas_del_padel_2026.pdf, página 8` — distancia 0.7372
5. `fip_reglas_del_padel_2026.pdf, página 10` — distancia 0.7750
6. `fip_reglas_del_padel_2026.pdf, página 7` — distancia 0.7885

### R3 — ¿Qué condiciones tiene que cumplir un jugador para representar a un país en una competición oficial de la FIP?

**Esperado:** Nacionalidad permanente, estar en regla con el miembro asociado, no haber representado nunca a otro país en un mundial o continental absoluto y no haber representado a otro país en los últimos 36 meses — fip_elegibilidad_jugadores_2026.pdf, pág. 1.

**Respuesta del modelo:**

```
Para representar a un país en una competición oficial de la FIP, un jugador debe cumplir con las siguientes condiciones:

1. Poseer la nacionalidad permanente del país, demostrable a través de un documento oficial de identidad en curso de validez que indique claramente la nacionalidad.
2. Estar en regla con la afiliación al miembro asociado del país, incluido estar libre de sanciones y penalizaciones, así como estar libre de sanciones y penalizaciones de cualquier otro miembro asociado del cual se posee una licencia en curso de validez.
3. No haber representado nunca a otro país en un campeonato mundial o continental, categoría Absoluto, por equipos nacionales y/o parejas nacionales.
4. No haber representado a otro país en cualquiera competición oficial en los anteriores 36 (treinta y seis) meses al evento.

Fuente: fip_elegibilidad_jugadores_2026.pdf, página 1.
```

**Fragmentos que entraron al contexto (k = 6):**

1. `fip_elegibilidad_jugadores_2026.pdf, página 1` — distancia 0.4069
2. `fip_elegibilidad_jugadores_2026.pdf, página 1` — distancia 0.6132
3. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 8` — distancia 0.7105
4. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6` — distancia 0.7404
5. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 6` — distancia 0.7421
6. `fip_reglamento_mundiales_equipos_nacionales_2026.pdf, página 4` — distancia 0.7544

### R4 — ¿Quién ganó el Campeonato Mundial de Pádel masculino de 2024, dónde se jugó y cuál fue el resultado de la final?

**Esperado:** Argentina, en Doha, 2:1 sobre España — mundiales_padel_wikipedia.json (artículo «Campeonato Mundial de Pádel»).

**Respuesta del modelo:**

```
El Campeonato Mundial de Pádel masculino de 2024 fue ganado por Argentina, se jugó en Doha y el resultado de la final fue 2:1. (Fuente: mundiales_padel_wikipedia.json, pádel masculino)
```

**Fragmentos que entraron al contexto (k = 6):**

1. `mundiales_padel_wikipedia.json — Mundial 2024 — masculino` — distancia 0.4824
2. `mundiales_padel_wikipedia.json — Mundial 2024 — femenino` — distancia 0.5422
3. `mundiales_padel_wikipedia.json — Mundial 2026 — masculino` — distancia 0.6134
4. `mundiales_padel_wikipedia.json — Mundial 2022 — masculino` — distancia 0.6276
5. `mundiales_padel_wikipedia.json — Mundial 2021 — masculino` — distancia 0.6416
6. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.6483

### R5 — ¿Cuántos títulos mundiales masculinos ganó Argentina y en qué años?

**Esperado:** 12 títulos: 1992, 1994, 1996, 2000, 2002, 2004, 2006, 2012, 2014, 2016, 2022 y 2024 — mundiales_padel_wikipedia.json (palmarés masculino).

**Respuesta del modelo:**

```
Argentina ganó 12 títulos mundiales masculinos en los años: 1992, 1994, 1996, 2000, 2002, 2004, 2006, 2012, 2014, 2016, 2022 y 2024. (Fuente: mundiales_padel_wikipedia.json, Palmarés histórico de Argentina en el Campeonato Mundial de Pádel, categoría masculino)
```

**Fragmentos que entraron al contexto (k = 6):**

1. `mundiales_padel_wikipedia.json — Palmarés de Argentina — masculino` — distancia 0.6604
2. `mundiales_padel_wikipedia.json — Palmarés de Argentina — femenino` — distancia 0.7513
3. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.7850
4. `mundiales_padel_wikipedia.json — Selección masculina de pádel de Argentina` — distancia 0.8039
5. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.8220
6. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.8800

### S1 — ¿Cuántas entradas se vendieron para la final del Campeonato Mundial de Pádel de 2024?

**Esperado:** No figura en el corpus. Se espera abstención.

**Respuesta del modelo:**

```
No encuentro esa información en el corpus.
```

**Fragmentos que entraron al contexto (k = 6):**

1. `mundiales_padel_wikipedia.json — Mundial 2024 — femenino` — distancia 0.7049
2. `mundiales_padel_wikipedia.json — Mundial 2024 — masculino` — distancia 0.7099
3. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel de 2024` — distancia 0.8093
4. `mundiales_padel_wikipedia.json — Mundial 2026 — femenino` — distancia 0.8155
5. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.8248
6. `mundiales_padel_wikipedia.json — Mundial 2022 — femenino` — distancia 0.8269

### S2 — ¿Cuánto dinero en premios recibió el equipo campeón del Mundial de pádel de 2022?

**Esperado:** No figura en el corpus. Se espera abstención.

**Respuesta del modelo:**

```
No encuentro esa información en el corpus.
```

**Fragmentos que entraron al contexto (k = 6):**

1. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel de 2022` — distancia 0.7454
2. `mundiales_padel_wikipedia.json — Mundial 2022 — masculino` — distancia 0.7465
3. `mundiales_padel_wikipedia.json — Mundial 2022 — femenino` — distancia 0.7514
4. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.7896
5. `mundiales_padel_wikipedia.json — Campeonato Mundial de Pádel` — distancia 0.7954
6. `mundiales_padel_wikipedia.json — Mundial 2021 — masculino` — distancia 0.8155

