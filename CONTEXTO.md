# Contexto del proyecto — Trabajo Final

Documento de handoff para retomar el trabajo desde cualquier sesión.

---

## 1. El trabajo académico

**Título:** Evaluación de Modelos de Lenguaje de Gran Escala (LLMs) para Soporte al Cliente Automatizado: Un Framework basado en Big Data

**Alumno:** Juan Bautista Xifro
**Carrera:** Licenciatura en Gestión de la Tecnología Informática — UAI, 2026
**Profesora de TF:** Samela, Marcela Rosalba
**Modalidad:** Trabajo de Investigación, paradigma Design Science Research (Hevner et al., 2004)
**Enfoque:** cuantitativo experimental

**Documento de la tesis:** `TF_Juan_Bautista_Xifro_2026_v3.docx`
(si solo está el v2 en la carpeta, correr `python3 aplicar_cambios.py` para generar el v3)

---

## 2. Qué problema resuelve la investigación

Las PyMEs quieren automatizar su soporte al cliente con LLMs, pero no tienen
criterios para elegir qué modelo usar. La oferta es amplia y heterogénea
(propietarios vs. código abierto) y las diferencias en calidad, costo y latencia
son sustanciales.

La literatura aborda estas dimensiones **de forma fragmentada**:

- Barandoni et al. (2024) comparan modelos en calidad, sin costo ni latencia.
- Li et al. (2024) construyen un benchmark amplio, pero no evalúan RAG.
- Faysal (2024) contrasta hipótesis formalmente, pero no compara modelos entre sí.
- Vega et al. (2025) demuestran viabilidad técnica de RAG, sin comparación.

**El vacío:** no existe un instrumento que integre calidad + costo + latencia en
una única decisión, sobre datos propios de la organización.

---

## 3. Hipótesis

**H1 — Calidad en condiciones equivalentes**
Los modelos de código abierto (LLaMA 3, Mistral) con RAG alcanzan calidad
comparable a los propietarios (GPT-4o mini) con RAG, medido por BERTScore.

**H2 — Eficiencia de costos a escala**
Los modelos de código abierto con RAG tienen costo significativamente menor por
cada 1.000 consultas, manteniendo una diferencia de calidad inferior a
**0,02 puntos de BERTScore F1**.

**H3 — Índice compuesto (aporte original)**
Los modelos de código abierto con RAG presentan mejor relación
costo-calidad-latencia, evaluada mediante un índice compuesto que pondera de
forma equitativa las tres dimensiones.

> Las tres hipótesis se contrastan **solo con datos de la condición con RAG**.
> La condición sin RAG es **línea base de control**, no participa del contraste.

---

## 4. Por qué existe este notebook

`01_celda_experimental_minima.ipynb`

### El razonamiento

El orden natural sería seguir los objetivos específicos en secuencia:
pipeline Spark → RAG → evaluación → dashboard. Pero eso deja **sin ningún
resultado medible hasta muy avanzado el trabajo**, y si algo falla al final no
hay tiempo de reaccionar.

Por eso se empezó por el **módulo de evaluación**, que es el corazón del aporte.
Spark es infraestructura reemplazable; el índice compuesto es lo original.

### Qué hace

Ejecuta el recorrido completo del experimento en **escala mínima**:
20 preguntas, 1 modelo, sin RAG.

El objetivo no es obtener resultados publicables sino **validar que toda la
cadena funciona de punta a punta** antes de escalar. Resuelve de entrada los
problemas que después se vuelven costosos: autenticación de cada API, formato de
guardado, versión de BERTScore, manejo de rate limits.

Cuando esto corre sin errores, extender a 3 modelos × 2 condiciones es mecánico.

### Decisión de diseño clave

La función `generar(modelo_key, consulta, contexto=None)` es la pieza central:
recibe el nombre del modelo y **siempre devuelve la misma estructura**.

- Pasar de 1 a 3 modelos = agregar entradas al diccionario `MODELOS`
- Agregar RAG = pasar el parámetro `contexto`, que ya existe

No hay que reescribir nada en ninguno de los dos casos.

### Decisiones metodológicas ya fijadas

| Decisión | Valor | Motivo |
|---|---|---|
| Temperatura | 0.0 | Reproducibilidad: sin esto cada corrida da distinto y las pruebas estadísticas pierden validez |
| Semilla | 42 | Muestra reproducible |
| Muestreo | Estratificado por categoría | Evita sesgo hacia una sola intención |
| Métrica principal | BERTScore F1 | Captura equivalencia semántica; ROUGE penalizaría reformulaciones válidas |
| Métrica complementaria | ROUGE-L | Contraste: si diverge de BERTScore, indica reformulación con otro vocabulario |
| Prompt | Idéntico para todos los modelos | Si variara, no se podría atribuir la diferencia al modelo |

---

## 5. PENDIENTE — Lo que falta resolver

### 5.1 CRÍTICO: el modelo de costo

**Es el punto más débil del trabajo ahora mismo.**

Para modelos propietarios el costo es directo (precio por millón de tokens).
Para open-source **el costo no es cero**: hay consumo de cómputo. Comparar
"costo de API" contra "cero" invalidaría H2 — cualquier tribunal lo observaría.

El criterio adoptado es amortización de instancia cloud:

```
costo_por_consulta = precio_hora_instancia / consultas_por_hora
consultas_por_hora = 3600 / latencia_media
```

**El problema:** con el placeholder actual (`PRECIO_INSTANCIA_HORA = 0.75`), una
prueba con datos simulados dio:

| Modelo | Costo por 1.000 consultas |
|---|---|
| GPT-4o mini | USD 0,126 |
| LLaMA 3.1 8B | USD 0,115 |

Prácticamente iguales → **H2 no se sostendría**.

**Qué hay que hacer:**
- Conseguir una cotización real de instancia con GPU y citarla con fecha
- Definir y documentar el supuesto de **concurrencia** (¿cuántas consultas
  simultáneas sirve la misma GPU?). Esto cambia el resultado por completo.
- Alternativa mejor: instalar **Ollama** y medir el costo local real en lugar de
  estimarlo. Resuelve el problema de raíz.

### 5.2 Idioma del corpus

El dataset **Bitext Customer Support** (HuggingFace, ~27k pares) está en inglés,
pero la justificación del trabajo habla de PyMEs latinoamericanas.
Es una inconsistencia que alguien va a señalar.

No existe equivalente abierto en español:
- Bitext solo publica la versión en inglés (las de español son comerciales)
- MASSIVE (Amazon) tiene español pero **sin respuesta de referencia**, así que no
  sirve para BERTScore

**Opciones:**
1. Traducir un subconjunto de Bitext con un LLM *(recomendada: mantiene
   trazabilidad a un dataset público y es documentable)*
2. Generar corpus sintético en español *(más natural, menos reproducible)*
3. Mantener inglés y declarar el framework como agnóstico al idioma

> Si se traduce: traducir **también las respuestas de referencia**. Comparar
> respuestas en español contra referencias en inglés daría BERTScore bajísimo
> para todos los modelos y el experimento perdería sentido.

### 5.3 Módulo RAG

No está implementado. Pasos:
1. Construir corpus de conocimiento derivado del dataset
2. Generar embeddings e indexar en FAISS (vía LangChain)
3. Recuperar fragmentos relevantes por consulta
4. Pasarlos al parámetro `contexto` de `generar()` — **la función ya lo acepta**

### 5.4 Escalar la muestra

De 20 a **300-500 consultas** por configuración. Es el mínimo razonable para que
las pruebas estadísticas tengan potencia. Recién ahí conviene incorporar Spark
para el preprocesamiento.

### 5.5 Pruebas estadísticas

Deliberadamente sin definir en el Plan de TF. El procedimiento correcto:
1. Recolectar los datos
2. Verificar normalidad (Shapiro-Wilk)
3. Según el resultado: t-test/ANOVA (paramétrica) o Wilcoxon (no paramétrica)

Faysal (2024) usó Wilcoxon, pero **no hay que comprometerse antes de ver los datos**.

### 5.6 Dashboard

Streamlit sobre los CSV generados. Es lo último: sin datos no hay nada que mostrar.

---

## 6. Advertencia sobre el índice compuesto

La normalización min-max es **relativa al conjunto de modelos comparados**.
Con un solo modelo el índice devuelve 0.5 para todo y no tiene sentido.
Recién se vuelve interpretable con las 6 configuraciones corridas.

---

## 7. Entorno

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Credenciales en `.env` (NO versionar):
```
GROQ_API_KEY=...
OPENAI_API_KEY=...
```

- **Groq**: acceso gratuito a LLaMA y Mistral (con rate limit por minuto)
- **OpenAI**: GPT-4o mini, menos de USD 0,01 para 20 consultas

> La celda de credenciales del notebook está preparada para Colab y cae a
> variables de entorno. **Pendiente:** adaptarla para leer `.env` con
> `python-dotenv`.

---

## 8. Orden sugerido para avanzar

1. Correr el notebook tal cual y verificar que la cadena funciona
2. Resolver el modelo de costo (Ollama local)
3. Decidir el idioma del corpus
4. Extender a los 3 modelos sin RAG
5. Implementar RAG y correr las 6 configuraciones
6. Escalar la muestra
7. Pruebas estadísticas
8. Dashboard
