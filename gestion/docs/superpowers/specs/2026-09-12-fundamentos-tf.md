# Sub-proyecto 1: Fundamentos — Diseño

**Fecha:** 2026-09-12
**Trabajo Final:** Evaluación de LLMs para Soporte al Cliente Automatizado — Un Framework basado en Big Data
**Alumno:** Juan Bautista Xifro — UAI 2026

---

## 1. Objetivo

Dejar corriendo, de punta a punta y de forma reproducible, el **baseline sin RAG**
sobre los tres modelos definidos (GPT-4o mini, LLaMA 3.1 8B, Mistral), sobre una
muestra en español, con un modelo de costo defendible para los modelos open-source.

Este sub-proyecto resuelve los dos puntos metodológicos más débiles que dejó
`01_celda_experimental_minima.ipynb`:
- el modelo de costo de los modelos open-source (antes casi idéntico al de GPT-4o mini),
- la inconsistencia de idioma entre el corpus (inglés) y el alcance de la tesis (PyMEs
  latinoamericanas).

No incluye RAG, escalado a 300-500 consultas, pruebas estadísticas ni dashboard —
eso queda para los sub-proyectos 2 a 5.

---

## 2. Decisiones ya tomadas (contexto de por qué el diseño es así)

| Decisión | Valor |
|---|---|
| Costo de modelos open-source | Se mide de forma real, corriendo los modelos localmente vía **Ollama** en vez de vía Groq. Se reportan **dos** métricas de costo (ver §5), no una sola. |
| Modelos open-source concretos | Vía Ollama, reemplazando Groq por completo (generación + latencia + costo, todo sobre la misma infraestructura real). |
| Corpus | Se traduce al español un subconjunto de Bitext (`instruction` + `response`), preservando trazabilidad al dataset público original. Se persiste en archivo para no retraducir en cada corrida. |
| Flexibilidad de modelos | Los modelos citados en la tesis teórica (GPT-4o mini, LLaMA 3, Mistral) no son inamovibles: si por accesibilidad/costo conviene otro modelo equivalente, se usa y se documenta el cambio en la tesis. |
| Documentación de resultados | Dos documentos con roles distintos: `HALLAZGOS.md` (crudo, de trabajo) y el `.docx` de la tesis (redacción formal APA 7, por capítulo). |

---

## 3. Arquitectura y componentes

```
Trabajo Final/
├── venv/                          # Python 3.11 (no 3.14, por compatibilidad con torch/bert-score)
├── .env                           # OPENAI_API_KEY (Groq ya no es necesario)
├── src/
│   └── framework_tf.py            # Módulo compartido: MODELOS, _cliente(), generar(), costo_consulta()
├── data/
│   └── corpus_es_muestra.csv      # Muestra traducida, persistida (no se regenera si ya existe)
├── notebooks/
│   └── 02_fundamentos.ipynb       # Corre el baseline sin RAG sobre los 3 modelos, en español
├── resultados_<sello>.csv         # Igual que hoy: una fila por consulta, no solo promedios
├── HALLAZGOS.md                   # Bitácora cruda de resultados y decisiones
└── TF_Juan_Bautista_Xifro_2026_v3.docx   # Nueva versión con las secciones actualizadas
```

**Por qué un módulo compartido (`src/framework_tf.py`):** los sub-proyectos 2 (RAG) y
3 (escalado) van a necesitar el mismo cliente de modelos y el mismo modelo de costo.
Si esa lógica queda solo dentro del notebook 01, cada sub-proyecto siguiente la
reimplementaría o la copiaría. Extraerla ahora evita esa duplicación desde el principio.

---

## 4. Entorno

1. `brew install ollama`; levantar el servicio (`ollama serve`, o el daemon de background
   que instala Homebrew).
2. `ollama pull llama3.1:8b` y `ollama pull mistral` (~5 GB cada uno; hay 339 GB libres).
3. Venv: `/opt/homebrew/bin/python3.11 -m venv venv` (evitar 3.14, que instaló Homebrew
   por defecto — `torch`/`bert-score` no garantizan soporte tan reciente).
4. `pip install -r requirements.txt` + agregar el paquete `ollama` (cliente Python oficial,
   habla con `localhost:11434`).
5. `.env`:
   ```
   OPENAI_API_KEY=...
   ```
   (Se quita la dependencia de `GROQ_API_KEY` salvo que se decida mantener Groq como
   comparación adicional más adelante — no en este sub-proyecto.)
6. La celda de credenciales del notebook se reescribe para usar `python-dotenv`
   (`load_dotenv()`) en vez del bloque de Colab Secrets, ya que se trabaja localmente.

---

## 5. Cliente unificado y modelo de costo

### 5.1 Extensión de `generar()` / `MODELOS`

Se agrega un proveedor `'ollama'` al diccionario `MODELOS` y a `_cliente()`. La firma y
el contrato de `generar(modelo_key, consulta, contexto=None)` **no cambian** — sigue
devolviendo `{'respuesta', 'latencia_s', 'tokens_in', 'tokens_out', 'error'}` — para que
los sub-proyectos 2 y 3 puedan seguir usándolo sin modificaciones.

Para Ollama, la latencia y los tokens salen directamente de la respuesta nativa de la
API (`total_duration`, `prompt_eval_count`, `eval_count`), no de una medición externa
con `time.perf_counter()` — son cifras reales de ejecución local.

```python
MODELOS = {
    'gpt-4o-mini':  {'proveedor': 'openai', 'id': 'gpt-4o-mini',        'tipo': 'propietario'},
    'llama-3.1-8b': {'proveedor': 'ollama', 'id': 'llama3.1:8b',        'tipo': 'open-source'},
    'mistral':      {'proveedor': 'ollama', 'id': 'mistral',            'tipo': 'open-source'},
}
```

### 5.2 Modelo de costo — dual, documentado

Para modelos propietarios: igual que hoy (tarifa oficial por millón de tokens).

Para modelos open-source (Ollama), se calculan **dos** columnas de costo, cada una con
un significado distinto y explícito:

| Columna | Fórmula | Qué mide | Rol en el análisis |
|---|---|---|---|
| `costo_electricidad_usd` | `(consumo_W / 1000) × (latencia_s / 3600) × precio_kWh_usd` | Costo marginal real de la energía consumida en tu M3 para esa consulta. 100% medible, sin depender de ninguna cotización externa. Subestima el costo total porque no incluye amortización de hardware. | Métrica de **sensibilidad / piso**: si la diferencia de costo frente a GPT-4o mini se sostiene incluso con esta cota inferior, la conclusión de H2 es más robusta. |
| `costo_instancia_usd` | `precio_hora_instancia / (3600 / latencia_s)`, con `latencia_s` medido realmente en Ollama (ya no simulado) | Costo si se alquilara una instancia cloud con GPU para servir el modelo en producción. Representa mejor el escenario que describe H2 ("costo operativo... por cada 1.000 consultas procesadas" implica un despliegue real, no una laptop). | Métrica **oficial** usada para contrastar H2 y para el índice compuesto de H3. |

`consumo_W` y `precio_kWh_usd` (para `costo_electricidad_usd`) y `precio_hora_instancia`
(para `costo_instancia_usd`) se citan con fuente y fecha de consulta — placeholders a
reemplazar antes de la corrida definitiva, igual que ya advertía el notebook 01.
Para `consumo_W` se usa como fuente el TDP publicado por Apple para el M3 (cifra
citable y estable); si se quiere mayor precisión, `powermetrics` permite medir consumo
real durante la corrida, pero requiere `sudo` y queda como mejora opcional, no como
bloqueante de este sub-proyecto.

Ambas columnas se guardan en el CSV de resultados por fila; ninguna reemplaza a la otra.

---

## 6. Corpus en español

1. Se toma la muestra estratificada ya existente (misma lógica del notebook 01: al
   menos 1 registro por categoría, semilla 42).
2. Se traduce `instruction` y `response` de cada fila con GPT-4o mini (costo estimado:
   centavos incluso para varios cientos de filas — se verifica el costo real antes de
   traducir el lote completo).
3. Se persiste en `data/corpus_es_muestra.csv`, agregando `instruction_es` /
   `response_es` sin tocar las columnas originales (se conserva `category`, `intent`,
   `instruction`, `response` en inglés como trazabilidad al dataset público).
4. Si el archivo ya existe, **no se retraduce** — se reutiliza tal cual. Esto evita
   gastar tokens de nuevo cada vez que se corre el notebook.
5. BERTScore se calcula con `lang='es'` sobre `instruction_es`/`response_es` en vez de
   `lang='en'`.

---

## 7. Notebook de fundamentos

`notebooks/02_fundamentos.ipynb`, estructurado igual que `01_celda_experimental_minima.ipynb`
pero:
- importa `src/framework_tf.py` en vez de definir todo inline,
- usa `data/corpus_es_muestra.csv` como fuente,
- corre `correr_experimento()` para los 3 modelos (GPT-4o mini vía OpenAI, LLaMA 3.1 8B
  y Mistral vía Ollama),
- calcula BERTScore (es) + ROUGE-L + ambas columnas de costo + índice compuesto,
- guarda el resultado consolidado en un único CSV con las 3×1 celdas experimentales
  (3 modelos, condición sin RAG).

---

## 8. Documentación de resultados

### 8.1 `HALLAZGOS.md` (nuevo, en la raíz del proyecto)

Bitácora de trabajo, sin pulir. Por cada sub-proyecto que se cierra, se agrega una
sección con:
- decisiones metodológicas tomadas y por qué,
- tabla resumen de resultados (medias, desvíos — no el CSV crudo),
- observaciones/anomalías a revisar después.

Este documento es el insumo directo para redactar las secciones correspondientes de la
tesis — se escribe pensando en que se pueda adaptar directamente a prosa académica.

### 8.2 Actualización del `.docx` (v2 → v3)

Usando el mismo mecanismo que `aplicar_cambios.py` (edita `word/document.xml` buscando
fragmentos de texto y generando una nueva versión del docx), se completan — en
redacción formal, APA 7ma edición — las secciones que corresponden a este sub-proyecto:

- **3.4 Dataset y corpus de datos**: párrafo sobre la traducción del subconjunto al
  español y su justificación metodológica.
- **Capítulo 4 (Diseño del Framework)**: arquitectura del cliente unificado de modelos
  y justificación del modelo de costo dual (electricidad real vs. instancia amortizada).
- **Capítulo 5 (Implementación y Prototipo)**: stack técnico real (Ollama local, OpenAI
  API, versiones), reemplazando el placeholder genérico actual.
- **Capítulo 6 (Experimentación y Resultados)**: solo la parte que corresponde a este
  sub-proyecto — resultados del baseline sin RAG para los 3 modelos. Se deja explícito
  en el texto que la sección se completa con la condición RAG en el sub-proyecto 2, para
  no dar la impresión de que el capítulo está cerrado.

Este patrón (HALLAZGOS.md primero, volcado pulido al `.docx` después) se repite en cada
sub-proyecto siguiente.

---

## 9. Testing / validación

- Prueba de humo por proveedor antes de correr el experimento completo: una consulta a
  GPT-4o mini y una a cada modelo Ollama, verificando que responden sin error.
- Verificar que Ollama está corriendo (`ollama list` o ping a `localhost:11434`) antes
  de intentar generar — fallar con un mensaje claro si no lo está, en vez de un stack
  trace de conexión rechazada.
- Verificar que `data/corpus_es_muestra.csv` no está vacío ni corrupto antes de usarlo
  como fuente (columnas esperadas presentes, sin filas con `instruction_es`/`response_es`
  nulos).
- Correr el experimento completo (3 modelos × 20 consultas) y confirmar 0 errores antes
  de dar el sub-proyecto por cerrado.

---

## 10. Fuera de alcance (queda para sub-proyectos siguientes)

- RAG (FAISS + LangChain) — sub-proyecto 2.
- Escalado a 300-500 consultas y Apache Spark — sub-proyecto 3.
- Pruebas estadísticas (Shapiro-Wilk → paramétrica/no paramétrica) — sub-proyecto 4.
- Dashboard en Streamlit — sub-proyecto 5.
