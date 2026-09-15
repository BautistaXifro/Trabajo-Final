# Evaluación de LLMs para soporte al cliente

Primera iteración del Trabajo Final de Juan Bautista Xifro (UAI, 2026). Compara GPT-4o mini, LLaMA 3.1 8B y Mistral sobre consultas de atención al cliente, midiendo calidad, latencia y costo.

El corpus proviene de [Bitext Customer Support LLM Chatbot Training Dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset). La muestra persistida en `data/` contiene 20 consultas traducidas al español.

## Contenido

- `src/`: carga y traducción del corpus, clientes de OpenAI/Ollama y cálculo de costos.
- `tests/`: 16 pruebas unitarias sin llamadas reales a APIs.
- `notebooks/02_fundamentos.ipynb`: experimento reproducible del baseline sin RAG.
- `data/corpus_es_muestra.csv`: muestra traducida para evitar repetir costo y tiempo.
- `resultados_fundamentos_20260913_1422.csv`: resultados de la primera corrida.
- `TF_Juan_Bautista_Xifro_2026.docx`: única versión vigente de la tesis.
- `requirements.txt`: dependencias Python reproducibles.

El contexto de desarrollo, planes, hallazgos, presentación y referencias están en `../gestion/`.

## Requisitos

- Windows 10/11.
- Python 3.11 (las versiones muy nuevas pueden ser incompatibles con `torch`/`bert-score`).
- Ollama con `llama3.1:8b` y `mistral` descargados.
- Una API key de OpenAI con crédito disponible.
- Aproximadamente 10–12 GB libres para modelos y cachés.

## Instalación en PowerShell

Ejecutar desde esta carpeta (`proyecto/`):

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

ollama pull llama3.1:8b
ollama pull mistral

Copy-Item .env.example .env
```

Luego editar `.env` y reemplazar el valor de ejemplo por una clave válida. `.env` y `venv/` son locales y Git los ignora.

## Verificación

```powershell
.\venv\Scripts\python.exe -m pytest tests -v
ollama list
```

El resultado esperado es `16 passed`. Antes de ejecutar el experimento, Ollama debe estar activo en `http://localhost:11434`.

## Ejecutar el notebook

En VS Code:

1. Abrir `notebooks/02_fundamentos.ipynb`.
2. Seleccionar como kernel `proyecto\venv\Scripts\python.exe`.
3. Ejecutar las celdas en orden.

También se puede ejecutar completo desde PowerShell:

```powershell
Set-Location notebooks
..\venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace 02_fundamentos.ipynb
Set-Location ..
```

La ejecución completa realiza llamadas pagas a OpenAI y usa los modelos locales de Ollama. El corpus ya traducido evita repetir la traducción mientras `data/corpus_es_muestra.csv` exista.

## Portabilidad

Al clonar en otra computadora se deben recrear `venv/` y `.env`, instalar Ollama y volver a descargar sus modelos. No se deben copiar ni versionar el entorno virtual, las credenciales ni los cachés: todo lo necesario para reconstruirlos está declarado en este repositorio.
