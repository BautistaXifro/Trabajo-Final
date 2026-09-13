# Hallazgos — Trabajo Final

Bitácora cruda de resultados y decisiones metodológicas. Este documento es el insumo directo para redactar las secciones correspondientes de la tesis (ver `.docx`), pero NO reemplaza la redacción formal.

## Sub-proyecto 1 — Fundamentos

**Archivo de resultados:** `resultados_fundamentos_20260913_1422.csv`

### Decisiones metodológicas

- Costo open-source medido en dos columnas: `costo_electricidad_usd` (piso, estimada a partir de la potencia térmica de diseño (TDP) del hardware, no medida directamente) y `costo_instancia_usd` (oficial, usada para H2/H3, amortización de instancia cloud con la latencia real medida en Ollama).
- Modelos open-source servidos localmente vía Ollama, reemplazando Groq, para que costo y latencia se midan sobre la misma infraestructura real.
- Corpus: subconjunto de Bitext traducido al español (instrucción + referencia), persistido en `data/corpus_es_muestra.csv`.
- **Aviso sobre los parámetros de costo:** `CONSUMO_W` (20 W), `PRECIO_KWH_USD` (0.15 USD/kWh) y `PRECIO_INSTANCIA_HORA` (0.75 USD/h) en `src/framework_tf.py` son valores placeholder provisionales, todavía sin reemplazar por una cotización real y citada (ver comentarios en el código). Las cifras en USD de esta bitácora y de la tesis derivan de estos supuestos y por lo tanto son provisorias en su magnitud absoluta; la comparación relativa entre modelos sigue siendo válida porque los tres se calculan con los mismos parámetros.

### Resultados — baseline sin RAG

| modelo       |   bertscore_f1 |   rouge_l |   latencia_s |   costo_electricidad_usd |   costo_instancia_usd |   costo_oficial_usd |   indice |
|:-------------|---------------:|----------:|-------------:|-------------------------:|----------------------:|--------------------:|---------:|
| gpt-4o-mini  |       0.712005 |  0.23008  |      1.30155 |                  nan     |            nan        |            7.1e-05  | 0.797245 |
| llama-3.1-8b |       0.71536  |  0.23812  |      6.37675 |                    5e-06 |              0.001328 |            0.001328 | 0.562035 |
| mistral      |       0.71028  |  0.235515 |      9.24555 |                    8e-06 |              0.001926 |            0.001926 | 0.424655 |

### Observaciones

- BERTScore F1 queda prácticamente empatado entre los tres modelos (0.7103-0.7154 en la corrida real, gpt-4o-mini 0.7120, llama-3.1-8b 0.7154, mistral 0.7103) — una diferencia de ~0.005 entre el mejor y el peor, nada que discrimine calidad de forma relevante en este baseline sin RAG. En la práctica esto significa que el índice compuesto (`indice`) termina decidido casi enteramente por costo y latencia, no por calidad: gpt-4o-mini gana el índice (0.797) principalmente por ser barato y rápido (1.3s), no por responder mejor; mistral queda último (0.425) principalmente por ser el más lento (9.2s), no por responder peor. Si se repitiera este experimento sin la columna de costo/latencia, los tres modelos serían indistinguibles en este baseline.

### Pendiente

- Condición con RAG (Sub-proyecto 2).
- Escalado a 300-500 consultas (Sub-proyecto 3).
- Pruebas estadísticas (Sub-proyecto 4).
- Dashboard (Sub-proyecto 5).
