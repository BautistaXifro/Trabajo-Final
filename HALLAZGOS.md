# Hallazgos — Trabajo Final

Bitácora cruda de resultados y decisiones metodológicas. Este documento es el insumo directo para redactar las secciones correspondientes de la tesis (ver `.docx`), pero NO reemplaza la redacción formal.

## Sub-proyecto 1 — Fundamentos

**Archivo de resultados:** `resultados_fundamentos_20260913_1422.csv`

### Decisiones metodológicas

- Costo open-source medido en dos columnas: `costo_electricidad_usd` (piso, energía real medida en Apple M3) y `costo_instancia_usd` (oficial, usada para H2/H3, amortización de instancia cloud con la latencia real medida en Ollama).
- Modelos open-source servidos localmente vía Ollama, reemplazando Groq, para que costo y latencia se midan sobre la misma infraestructura real.
- Corpus: subconjunto de Bitext traducido al español (instrucción + referencia), persistido en `data/corpus_es_muestra.csv`.

### Resultados — baseline sin RAG

| modelo       |   bertscore_f1 |   rouge_l |   latencia_s |   costo_electricidad_usd |   costo_instancia_usd |   costo_oficial_usd |   indice |
|:-------------|---------------:|----------:|-------------:|-------------------------:|----------------------:|--------------------:|---------:|
| gpt-4o-mini  |       0.712005 |  0.23008  |      1.30155 |                  nan     |            nan        |            7.1e-05  | 0.797245 |
| llama-3.1-8b |       0.71536  |  0.23812  |      6.37675 |                    5e-06 |              0.001328 |            0.001328 | 0.562035 |
| mistral      |       0.71028  |  0.235515 |      9.24555 |                    8e-06 |              0.001926 |            0.001926 | 0.424655 |

### Observaciones

- [completar tras inspeccionar manualmente los resultados: outliers, errores de generación, respuestas vacías, etc.]

### Pendiente

- Condición con RAG (Sub-proyecto 2).
- Escalado a 300-500 consultas (Sub-proyecto 3).
- Pruebas estadísticas (Sub-proyecto 4).
- Dashboard (Sub-proyecto 5).
