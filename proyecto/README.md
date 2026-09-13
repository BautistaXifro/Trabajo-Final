# Trabajo Final — Evaluación de LLMs para Soporte al Cliente Automatizado

Framework comparativo de LLMs (propietarios vs. código abierto) para soporte al
cliente, evaluando calidad semántica, costo operativo y latencia. Trabajo Final
de Juan Bautista Xifro — UAI, 2026.

Este README cubre el **Sub-proyecto 1 (Fundamentos)**: el baseline sin RAG.
Los sub-proyectos siguientes (RAG, escalado, estadística, dashboard) agregarán
sus propios pasos a medida que se implementen.

> **Esta carpeta (`proyecto/`) es todo lo necesario para correr y entregar el
> TF** — código, notebook, corpus, resultados y la tesis en su versión
> vigente. Todos los comandos de este README asumen que estás parado adentro
> de esta carpeta (`cd proyecto`). La carpeta hermana `../gestion/` contiene
> material de trabajo interno (contexto, hallazgos crudos, specs/planes de
> desarrollo) que **no forma parte de la entrega**.

---

## 1. Requisitos

| Requisito | Versión | Para qué |
|---|---|---|
| macOS o Linux | — | Probado en macOS (Apple Silicon). Ollama también soporta Linux/Windows, pero los pasos de instalación de abajo son para macOS con Homebrew. |
| Python | **3.11** (no 3.14 — hay incompatibilidades con `torch`/`bert-score` en versiones muy nuevas) | Entorno del proyecto |
| [Ollama](https://ollama.com) | cualquier versión reciente | Servir los modelos open-source (LLaMA 3.1 8B, Mistral) localmente |
| Cuenta de **OpenAI** (personal, no corporativa) | — | Acceso a GPT-4o mini vía API. Necesita crédito cargado en `platform.openai.com/settings/organization/billing` — **la suscripción de ChatGPT Plus NO cubre esto**, son productos y facturación separados. |
| Conexión a internet | — | Descarga del dataset (HuggingFace) y del modelo de BERTScore (~500 MB, solo la primera vez) |
| Espacio en disco | ~10-12 GB libres | Los dos modelos de Ollama pesan ~4-5 GB cada uno |

## 2. Instalación

```bash
# 1. Instalar y arrancar Ollama
brew install ollama
brew services start ollama

# 2. Descargar los modelos open-source (una sola vez, ~10 GB)
ollama pull llama3.1:8b
ollama pull mistral

# 3. Crear el entorno virtual con Python 3.11 (NO uses python3 a secas si tu
#    default es otra versión)
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Credenciales
cat > .env << 'EOF'
OPENAI_API_KEY=tu_clave_personal_aca
EOF
```

⚠️ `.env` está en `.gitignore` — nunca se versiona ni se comparte. Usá una
clave de **tu cuenta personal** de OpenAI, no una corporativa (evita problemas
de política de uso aceptable y de facturación cruzada).

### Verificar que el entorno funciona

```bash
source venv/bin/activate
python3 -c "
import sys; sys.path.insert(0, '.')
from src import framework_tf as ftf
ftf.verificar_ollama()
print('Ollama OK')
for modelo in ftf.MODELOS:
    out = ftf.generar(modelo, '¿Cómo cancelo mi pedido?')
    print(modelo, '->', out['error'] or out['respuesta'][:60])
"
```

Si `gpt-4o-mini` falla con un error de cuota/billing, cargá crédito en tu
cuenta de OpenAI (con USD 5 alcanza de sobra para todo el experimento).

## 3. Cómo correr el notebook

**Opción A — ejecutarlo de punta a punta sin abrir Jupyter:**

```bash
source venv/bin/activate
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 02_fundamentos.ipynb
```

**Opción B — abrirlo interactivamente** (Jupyter Lab, VS Code con la extensión
de Jupyter, etc.) y correr las celdas en orden.

**Para regenerar el notebook desde cero** (si se necesita cambiar alguna celda,
se edita el generador, no el `.ipynb` a mano):

```bash
python3 scripts/crear_notebook_fundamentos.py
```

La primera corrida tarda varios minutos: descarga el dataset, traduce la
muestra al español (llamadas reales a OpenAI, centavos de costo), descarga el
modelo de BERTScore (~500 MB) y corre inferencia local en Ollama para 2 de los
3 modelos. Corridas siguientes son más rápidas porque el corpus en español y
el modelo de BERTScore ya quedan cacheados en disco.

## 3.1 Cómo correr los tests

```bash
source venv/bin/activate
venv/bin/python3 -m pytest tests/ -v
```

⚠️ Usá `venv/bin/python3 -m pytest`, no solo `pytest` a secas — en algunos
shells (con `pyenv` u otros gestores de versiones instalados), el comando
`pytest` puede resolver a un `pytest` de OTRO entorno Python en el `PATH`,
dando resultados que parecen correctos pero corrieron contra el código
equivocado. `venv/bin/python3 -m pytest` fuerza a usar siempre el intérprete
de este proyecto. Deberían pasar 16/16.

## 4. Inputs y outputs

**Inputs:**
- Dataset [Bitext Customer Support](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset) — se descarga automáticamente de HuggingFace la primera vez, no requiere configuración.
- `data/corpus_es_muestra.csv` — muestra de 20 consultas traducida al español. Se genera automáticamente la primera vez; si ya existe, **no se vuelve a traducir** (ahorra tiempo y costo).

**Outputs:**
- `resultados_fundamentos_<fecha_hora>.csv` — una fila por cada consulta enviada a cada modelo (60 filas: 3 modelos × 20 consultas), con métricas de calidad, latencia y costo.
- `HALLAZGOS.md` — bitácora legible con el resumen de resultados y las decisiones metodológicas (se regenera con un script puntual después de cada corrida, no automáticamente).

## 5. Estructura del repositorio

```
src/framework_tf.py     → cliente unificado de modelos (OpenAI + Ollama) + modelo de costo dual
src/corpus.py           → muestreo estratificado + traducción del corpus
tests/                  → tests unitarios (pytest, sin llamadas reales de red)
notebooks/02_fundamentos.ipynb → notebook ejecutable del baseline sin RAG
scripts/                → scripts de generación (notebook, actualización del docx)
data/corpus_es_muestra.csv → corpus traducido, persistido
HALLAZGOS.md            → resultados crudos, bitácora de trabajo
TF_Juan_Bautista_Xifro_2026_v4.docx → versión vigente de la tesis
docs/superpowers/       → spec y plan de implementación de cada sub-proyecto
```

## 6. Portabilidad

El código (`src/`, `tests/`, `notebooks/`, `scripts/`) es Python puro y
portable a cualquier máquina con Python 3.11. Lo que **no** viaja con el
repositorio (y hay que rehacer en cada máquina nueva):

- `venv/` — se recrea localmente, nunca se copia entre máquinas.
- `.env` — se recrea a mano con una clave de OpenAI válida para esa máquina/usuario.
- Los modelos de Ollama (`ollama pull llama3.1:8b`, `ollama pull mistral`) — se vuelven a descargar en cada máquina donde se quiera correr el experimento localmente.

Todo lo demás (código, corpus traducido, resultados, tesis) es un conjunto de
archivos de texto/CSV/docx normales — se puede copiar, comprimir o clonar sin
ninguna dependencia oculta.
