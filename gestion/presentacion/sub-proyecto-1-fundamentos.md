---
marp: true
paginate: true
theme: default
---

# Sub-proyecto 1: Fundamentos
### Evaluación de LLMs para Soporte al Cliente Automatizado
Trabajo Final — Juan Bautista Xifro — UAI 2026

Baseline **sin RAG**: 3 modelos, 20 consultas, corrida real, 0 errores.

---

## Objetivo de esta etapa

Dejar corriendo, de punta a punta, la cadena completa del experimento:

- Entorno reproducible (Ollama local + Python 3.11)
- Modelo de costo **defendible** para los modelos open-source
- Corpus en español (no en inglés, para alinear con el alcance del TF)
- Corrida real contra los 3 modelos, sin errores
- Primeros resultados volcados a la tesis (Cap. 3.4, 4, 5, 6-parcial)

No busca resultados definitivos — busca **validar que la cadena funciona**
antes de escalar.

---

## Pipeline del notebook — 7 pasos

1. **Setup** — carga `.env`, verifica que Ollama está corriendo
2. **Dataset** — descarga Bitext (HuggingFace, ~27k filas en inglés), muestra
   estratificada de 20 (semilla=42), traducida al español con GPT-4o mini
   (se cachea, no se retraduce después)
3. **Generación** — envía las 20 consultas a los 3 modelos, mismo prompt,
   temperatura=0, semilla=42
4. **Calidad** — BERTScore F1 (español) + ROUGE-L, respuesta vs. referencia
5. **Costo** — dual: electricidad estimada (piso) + instancia cloud
   amortizada (oficial)
6. **Índice compuesto** — normaliza calidad/costo/latencia a [0,1] y
   promedia con igual peso
7. **Guardado** — CSV con una fila por consulta (no solo promedios)

---

## Modelos evaluados

| Modelo | Proveedor | Tipo | Cómo corre |
|---|---|---|---|
| `gpt-4o-mini` | OpenAI (API) | Propietario | Llamada a la nube, paga por token |
| `llama-3.1-8b` | Ollama (`llama3.1:8b`) | Código abierto | **Local**, en tu Mac (M3) |
| `mistral` | Ollama (`mistral`) | Código abierto | **Local**, en tu Mac (M3) |

Los dos modelos open-source ya no usan Groq (nube de un tercero) — corren
100% localmente, para que costo y latencia se midan sobre la misma
infraestructura real.

---

## El costo de los modelos "gratuitos" — no es cero

Aunque no se paga licencia, se reportan **dos** columnas de costo por
consulta:

| Métrica | Qué mide | Rol |
|---|---|---|
| `costo_electricidad_usd` | Consumo eléctrico estimado (TDP del hardware × latencia real) | Piso — 100% medible, sin cotización externa |
| `costo_instancia_usd` | Amortización de una instancia cloud con GPU, dividida entre consultas/hora reales | **Oficial** — la que se usa para contrastar H2/H3 |

⚠️ Los parámetros (`CONSUMO_W`, `PRECIO_KWH_USD`, `PRECIO_INSTANCIA_HORA`) son
**placeholders todavía sin cotización real citada** — documentado como
limitación explícita en el código, en `HALLAZGOS.md` y en la tesis.

---

## Resultados reales — costo promedio por consulta

| Modelo | Costo electricidad | Costo instancia (oficial) | Latencia media |
|---|---:|---:|---:|
| gpt-4o-mini | — (no aplica) | USD 0.000071 | 1.30 s |
| llama-3.1-8b | USD 0.000005 | USD 0.001328 | 6.38 s |
| mistral | USD 0.000008 | USD 0.001926 | 9.25 s |

**Costo total de la corrida completa (60 consultas):**
gpt-4o-mini USD 0.0014 · llama USD 0.0266 · mistral USD 0.0385
— la corrida entera costó **menos de 7 centavos de dólar** en total.

---

## Resultados reales — tabla completa

| Modelo | BERTScore F1 | Latencia | Costo oficial | Índice compuesto |
|---|---:|---:|---:|---:|
| gpt-4o-mini | 0.7120 | 1.30 s | USD 0.000071 | **0.797** |
| llama-3.1-8b | 0.7154 | 6.38 s | USD 0.001328 | 0.562 |
| mistral | 0.7103 | 9.25 s | USD 0.001926 | 0.425 |

60 consultas totales (3 modelos × 20), **0 errores**.

---

## Hallazgo 1 — La calidad no discrimina

BERTScore F1 queda **prácticamente empatado**: 0.7103 – 0.7154 (diferencia de
~0.005 entre el mejor y el peor).

En este baseline sin RAG, **ningún modelo responde mejor que otro** de forma
relevante — el índice compuesto termina decidido casi enteramente por costo
y latencia, no por calidad.

---

## Hallazgo 2 (⚠️ riesgo a vigilar) — El costo favorece a GPT-4o mini

Bajo el modelo de costo oficial, los modelos open-source salen
**18.6x (llama) y 27x (mistral) más caros por consulta** que GPT-4o mini —
lo opuesto a lo que predice H2.

**Por qué:** la fórmula de costo divide el precio de instancia entre
consultas/hora. La latencia real de Ollama corriendo localmente (6-9s) es
mucho mayor que la de la API de OpenAI (1.3s) → menos consultas/hora → más
costo por consulta.

**No invalida nada todavía** (las hipótesis se contrastan solo con la
condición CON RAG) — pero si RAG no cambia la latencia relativa, este mismo
patrón podría repetirse. A vigilar en el Sub-proyecto 2.

---

## Qué fue complejo en esta primera iteración

- **Diseñar un modelo de costo defendible** para algo que "no cuesta nada"
  (open-source) — terminamos con 2 métricas paralelas, no 1
- **Bug real de índices** en el muestreo estratificado (filas duplicadas
  silenciosas) — encontrado y corregido con test de regresión
- **Bug real de doble redondeo** en el texto insertado en la tesis — el
  costo de GPT-4o mini se mostraba ~40% más alto de lo real
- **Bug real de NaN vs. None** al mezclar costos de distintos modelos en un
  mismo DataFrame de pandas
- **Fricción operativa:** cuenta nueva de OpenAI sin crédito cargado,
  confusión ChatGPT Plus vs. API (son productos separados), un incidente de
  seguridad (clave pegada en el chat, resuelto revocándola al instante)

---

## Qué costó (tiempo y dinero) en esta iteración

| Recurso | Costo real |
|---|---|
| Llamadas a OpenAI (traducción + generación + smoke tests) | **< USD 0.10 en total** |
| Modelos Ollama descargados | ~10 GB de disco, gratis |
| Crédito cargado en OpenAI | USD 5 (alcanza para escalar a 500 consultas) |
| Tiempo de desarrollo | 8 tareas + 1 revisión final + 1 ronda de fix, con 2 bugs reales encontrados y corregidos en el camino |

El costo económico de correr el experimento es prácticamente nulo — el
costo real de esta etapa fue **tiempo de diseño e ingeniería**, no cómputo.

---

## Qué falta — Roadmap

| # | Sub-proyecto | Qué agrega |
|---|---|---|
| 2 | **RAG** | FAISS + LangChain, vía el parámetro `contexto` que `generar()` ya acepta |
| 3 | **Escalar la muestra** | De 20 a 300-500 consultas (recién ahí, Spark si el volumen lo justifica) |
| 4 | **Pruebas estadísticas** | Shapiro-Wilk → paramétrica o no paramétrica, contraste real de H1/H2/H3 |
| 5 | **Dashboard** | Streamlit sobre los CSV de resultados |
| 6 | **Cierre de la tesis** | Conclusiones, Líneas Futuras, Anexos |

**Completitud estimada del TF hoy: ~35-40%** (Cap. 1-3 completos, Cap. 4-6
parciales, resto pendiente).

---

## Próximo paso

**Sub-proyecto 2: RAG** — construir la base de conocimiento vectorial y
correr las configuraciones con contexto recuperado, para poder finalmente
contrastar H1, H2 y H3 (las hipótesis solo se prueban con RAG, esto fue
únicamente la línea base de control).

Mismo proceso: brainstorming → spec → plan → ejecución con revisión.
