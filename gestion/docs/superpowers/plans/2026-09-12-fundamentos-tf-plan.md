# Sub-proyecto 1 "Fundamentos" — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dejar corriendo, de punta a punta, el baseline sin RAG (GPT-4o mini +
LLaMA 3.1 8B + Mistral) sobre una muestra en español, con un modelo de costo dual
defendible para los modelos open-source, y volcar los resultados tanto a
`HALLAZGOS.md` (crudo) como a las secciones correspondientes del `.docx` de la
tesis (redacción APA 7).

**Architecture:** Módulo compartido `src/framework_tf.py` (cliente unificado de
modelos + modelo de costo) y `src/corpus.py` (muestreo + traducción), ambos
cubiertos con tests unitarios usando clientes falsos (sin llamadas reales de red
en el test suite). Un notebook de orquestación (`notebooks/02_fundamentos.ipynb`,
generado programáticamente con `nbformat`) hace la corrida real contra Ollama y
OpenAI. Un script de edición XML (análogo a `aplicar_cambios.py`) actualiza el
`.docx` con los resultados reales.

**Tech Stack:** Python 3.11, `pytest`, `pandas`, `openai`, `ollama` (paquete
Python), `bert-score`, `rouge-score`, `nbformat`, `python-dotenv`. Ollama corriendo
localmente (`llama3.1:8b`, `mistral`) vía Homebrew.

**Spec:** `docs/superpowers/specs/2026-09-12-fundamentos-tf.md`

## Global Constraints

- Python del venv: 3.11 (`/opt/homebrew/bin/python3.11`), no 3.14.
- Modelos Ollama: `llama3.1:8b` y `mistral`, descargados vía `ollama pull`.
- Temperatura = 0.0, semilla = 42 (fijadas, no cambian).
- Costo open-source: se reportan **dos** columnas —
  `costo_electricidad_usd` (sensibilidad/piso) y `costo_instancia_usd` (oficial,
  usada para H2/H3). Nunca una reemplaza a la otra.
- Corpus: `instruction`/`response` originales en inglés se preservan; se agregan
  `instruction_es`/`response_es`. Si `data/corpus_es_muestra.csv` ya existe, no se
  retraduce.
- No hay repositorio git en esta carpeta (`git: false`). Se omite el paso de
  "commit" en cada tarea — en su lugar, cada tarea termina con una verificación
  explícita de que el artefacto quedó guardado en disco. Si más adelante se
  quiere versionar, inicializar git es una tarea aparte, fuera de este plan.
- Redacción del `.docx`: español, APA 7ma edición, mismo mecanismo de edición XML
  que `aplicar_cambios.py` (buscar fragmento de texto en `word/document.xml`,
  reemplazar o insertar párrafo después).

---

### Task 1: Generar la v3 pendiente del documento (prerrequisito ya existente)

`CONTEXTO.md` indica que `aplicar_cambios.py` todavía no se corrió — solo existe
`TF_Juan_Bautista_Xifro_2026_v2.docx`. Antes de agregar nuestras propias ediciones
hay que generar la v3 que ya estaba escrita y pendiente.

**Files:**
- Ejecuta (sin modificar): `aplicar_cambios.py`
- Produce: `TF_Juan_Bautista_Xifro_2026_v3.docx`

**Interfaces:**
- Produces: `TF_Juan_Bautista_Xifro_2026_v3.docx` (input para el Task 8, que
  generará la v4).

- [ ] **Step 1: Correr el script existente**

```bash
cd "/Users/jxifro/Desktop/Trabajo Final"
python3 aplicar_cambios.py
```

Expected: imprime `ok` para cada una de las 5 ediciones y termina con
`Listo. Abri TF_Juan_Bautista_Xifro_2026_v3.docx`. Si falla con
`NO ENCONTRADO [...]`, el v2 fue editado manualmente después de escribir el
script — avisar y no continuar hasta resolverlo.

- [ ] **Step 2: Verificar que el texto se insertó correctamente**

```bash
python3 -c "
import zipfile, re, html
with zipfile.ZipFile('TF_Juan_Bautista_Xifro_2026_v3.docx') as z:
    xml = z.read('word/document.xml').decode('utf-8')
texto = ''.join(html.unescape(t) for t in re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml, re.S))
assert 'línea base de control' in texto, 'No se encontró el texto insertado'
print('OK: v3 contiene las ediciones esperadas')
"
```

Expected: `OK: v3 contiene las ediciones esperadas`

- [ ] **Step 3: Checkpoint**

Confirmar que `TF_Juan_Bautista_Xifro_2026_v3.docx` existe en la carpeta del
proyecto. No hay commit (no hay repo git).

---

### Task 2: Entorno — Ollama + venv + dependencias

**Files:**
- Create: `venv/` (entorno virtual, no se versiona)
- Create: `.env` (con placeholder, la clave real la completa el usuario a mano)
- Modify: `requirements.txt` (agregar `ollama`)

**Interfaces:**
- Produces: un intérprete Python en `venv/bin/python` con todas las dependencias,
  y Ollama sirviendo `llama3.1:8b` + `mistral` en `localhost:11434`. Todas las
  tareas siguientes asumen que este entorno está activo.

- [ ] **Step 1: Instalar y arrancar Ollama**

```bash
brew install ollama
brew services start ollama
```

- [ ] **Step 2: Descargar los dos modelos open-source**

```bash
ollama pull llama3.1:8b
ollama pull mistral
```

Expected: ambos comandos terminan con `success`. Verificar con:

```bash
ollama list
```

Expected: la salida incluye `llama3.1:8b` y `mistral`.

- [ ] **Step 3: Agregar el paquete `ollama` a requirements.txt**

Modificar `requirements.txt`, agregando bajo la sección "Clientes de modelos":

```
ollama>=0.3.0
```

- [ ] **Step 4: Crear el venv con Python 3.11 e instalar dependencias**

```bash
cd "/Users/jxifro/Desktop/Trabajo Final"
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 --version
```

Expected: `Python 3.11.x`

- [ ] **Step 5: Crear `.env` con placeholder**

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=reemplazar_con_tu_clave_real
EOF
```

Avisar al usuario que reemplace el valor a mano — nunca escribir la clave real
en un archivo generado por un agente.

- [ ] **Step 6: Verificar que el entorno funciona de punta a punta**

```bash
source venv/bin/activate
python3 -c "
import openai, ollama, dotenv, pandas, bert_score, rouge_score
print('Todas las dependencias importan correctamente')
"
python3 -c "
import ollama
r = ollama.Client(host='http://localhost:11434').list()
nombres = [m['name'] for m in r['models']]
assert any('llama3.1' in n for n in nombres), 'Falta llama3.1:8b'
assert any('mistral' in n for n in nombres), 'Falta mistral'
print('Ollama sirve los dos modelos esperados:', nombres)
"
```

Expected: ambos scripts terminan sin error e imprimen los mensajes de éxito.

- [ ] **Step 7: Checkpoint**

Entorno listo: venv activo, Ollama corriendo con los dos modelos, `.env` con
placeholder a completar por el usuario.

---

### Task 3: Modelo de costo dual — `src/framework_tf.py` (parte 1)

**Files:**
- Create: `src/__init__.py` (vacío)
- Create: `src/framework_tf.py`
- Test: `tests/test_costo.py`

**Interfaces:**
- Produces: `costo_electricidad(latencia_s) -> float`,
  `costo_instancia(latencia_s) -> float`,
  `costo_consulta(fila: dict) -> dict` con claves
  `costo_usd`, `costo_electricidad_usd`, `costo_instancia_usd`,
  `costo_oficial(fila: dict) -> float`.
  Task 4 y el notebook (Task 6) consumen estas cuatro funciones.

- [ ] **Step 1: Crear la carpeta de tests y el paquete `src`**

```bash
mkdir -p src tests
touch src/__init__.py
```

- [ ] **Step 2: Escribir los tests (deben fallar — el módulo no existe todavía)**

Crear `tests/test_costo.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src import framework_tf as ftf


def test_costo_electricidad_formula():
    ftf.CONSUMO_W = 20
    ftf.PRECIO_KWH_USD = 0.15
    costo = ftf.costo_electricidad(latencia_s=3600)  # 1 hora exacta
    esperado = (20 / 1000) * (3600 / 3600) * 0.15
    assert round(costo, 8) == round(esperado, 8)


def test_costo_instancia_formula():
    ftf.PRECIO_INSTANCIA_HORA = 0.75
    costo = ftf.costo_instancia(latencia_s=1.0)  # 3600 consultas/hora
    esperado = 0.75 / 3600
    assert round(costo, 8) == round(esperado, 8)


def test_costo_consulta_propietario():
    fila = {'modelo': 'gpt-4o-mini', 'tokens_in': 1000, 'tokens_out': 500, 'latencia_s': 1.2}
    r = ftf.costo_consulta(fila)
    esperado = 1000 / 1_000_000 * 0.150 + 500 / 1_000_000 * 0.600
    assert round(r['costo_usd'], 8) == round(esperado, 8)
    assert r['costo_electricidad_usd'] is None
    assert r['costo_instancia_usd'] is None


def test_costo_consulta_open_source():
    fila = {'modelo': 'llama-3.1-8b', 'tokens_in': 50, 'tokens_out': 80, 'latencia_s': 2.0}
    r = ftf.costo_consulta(fila)
    assert r['costo_usd'] is None
    assert r['costo_electricidad_usd'] > 0
    assert r['costo_instancia_usd'] > 0


def test_costo_oficial_selecciona_columna_correcta():
    fila_propietario = {'costo_usd': 0.001, 'costo_instancia_usd': None}
    fila_open_source = {'costo_usd': None, 'costo_instancia_usd': 0.0002}
    assert ftf.costo_oficial(fila_propietario) == 0.001
    assert ftf.costo_oficial(fila_open_source) == 0.0002
```

- [ ] **Step 3: Correr los tests y confirmar que fallan**

```bash
source venv/bin/activate
pip install pytest
pytest tests/test_costo.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.framework_tf'` (o
similar, porque el archivo todavía no existe).

- [ ] **Step 4: Crear `src/framework_tf.py` con el modelo de costo**

```python
"""Cliente unificado de modelos y modelo de costo — Sub-proyecto 1 (Fundamentos)."""

# --- Modelo de costo: propietarios ---
PRECIOS_API = {
    'gpt-4o-mini': {'in': 0.150, 'out': 0.600},  # USD por 1M tokens
}

# --- Modelo de costo: open-source, columna de sensibilidad (electricidad real) ---
CONSUMO_W = 20          # TDP aprox. Apple M3 bajo carga (fuente: specs Apple — citar fecha real al usar)
PRECIO_KWH_USD = 0.15   # tarifa eléctrica a citar con fuente y fecha real

# --- Modelo de costo: open-source, columna oficial (instancia cloud amortizada) ---
PRECIO_INSTANCIA_HORA = 0.75  # cotización cloud a reemplazar por una real, citada


def costo_electricidad(latencia_s):
    """Costo marginal de electricidad para una consulta de `latencia_s` segundos."""
    return (CONSUMO_W / 1000) * (latencia_s / 3600) * PRECIO_KWH_USD


def costo_instancia(latencia_s):
    """Costo si se amortiza una instancia cloud con GPU sobre las consultas/hora
    que permite `latencia_s`."""
    consultas_por_hora = 3600 / latencia_s
    return PRECIO_INSTANCIA_HORA / consultas_por_hora


def costo_consulta(fila):
    """Costo(s) en USD de una fila de resultado. Devuelve las tres columnas;
    las que no aplican quedan en None."""
    m = fila['modelo']
    if m in PRECIOS_API:
        p = PRECIOS_API[m]
        costo = (fila['tokens_in'] / 1_000_000 * p['in'] +
                 fila['tokens_out'] / 1_000_000 * p['out'])
        return {'costo_usd': costo, 'costo_electricidad_usd': None, 'costo_instancia_usd': None}

    return {
        'costo_usd': None,
        'costo_electricidad_usd': costo_electricidad(fila['latencia_s']),
        'costo_instancia_usd': costo_instancia(fila['latencia_s']),
    }


def costo_oficial(fila):
    """Costo usado para el contraste de H2/H3 y el índice compuesto: tarifa
    oficial para propietarios, costo de instancia amortizada para open-source."""
    if fila.get('costo_usd') is not None:
        return fila['costo_usd']
    return fila['costo_instancia_usd']
```

- [ ] **Step 5: Correr los tests y confirmar que pasan**

```bash
pytest tests/test_costo.py -v
```

Expected: 5 PASSED

- [ ] **Step 6: Checkpoint**

Modelo de costo dual implementado y testeado. No hay commit (no hay repo git).

---

### Task 4: Cliente unificado de modelos — `src/framework_tf.py` (parte 2)

**Files:**
- Modify: `src/framework_tf.py` (agregar `MODELOS`, `_cliente()`, `verificar_ollama()`, `generar()`)
- Test: `tests/test_generar.py`

**Interfaces:**
- Consumes: nada de tareas anteriores dentro de este módulo (usa las constantes
  de costo solo indirectamente, no en `generar()`).
- Produces: `MODELOS: dict`, `generar(modelo_key: str, consulta: str, contexto: str | None = None) -> dict`
  con claves `respuesta`, `latencia_s`, `tokens_in`, `tokens_out`, `error`.
  `verificar_ollama() -> None` (lanza `RuntimeError` si Ollama no responde).
  El notebook (Task 6) y el módulo de corpus (Task 5, indirectamente vía el
  cliente OpenAI) consumen estas funciones.

- [ ] **Step 1: Escribir los tests (deben fallar — `generar` no existe todavía)**

Crear `tests/test_generar.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src import framework_tf as ftf


class _FakeMsg:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMsg(content)


class _FakeUsage:
    def __init__(self, tin, tout):
        self.prompt_tokens = tin
        self.completion_tokens = tout


class _FakeOpenAIResponse:
    def __init__(self, content, tin, tout):
        self.choices = [_FakeChoice(content)]
        self.usage = _FakeUsage(tin, tout)


class _FakeOpenAIClient:
    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                return _FakeOpenAIResponse(' Hola, ¿en qué puedo ayudarte? ', 12, 8)


class _FakeOllamaClient:
    def chat(self, **kwargs):
        return {
            'message': {'content': ' Claro, te ayudo. '},
            'total_duration': 2_500_000_000,  # 2.5 s en nanosegundos
            'prompt_eval_count': 30,
            'eval_count': 40,
        }


def test_generar_openai_dispatch(monkeypatch):
    monkeypatch.setitem(ftf._clientes, 'openai', _FakeOpenAIClient())
    out = ftf.generar('gpt-4o-mini', 'hola')
    assert out['error'] is None
    assert out['respuesta'] == 'Hola, ¿en qué puedo ayudarte?'
    assert out['tokens_in'] == 12
    assert out['tokens_out'] == 8


def test_generar_ollama_dispatch(monkeypatch):
    monkeypatch.setitem(ftf._clientes, 'ollama', _FakeOllamaClient())
    out = ftf.generar('llama-3.1-8b', 'hola')
    assert out['error'] is None
    assert out['respuesta'] == 'Claro, te ayudo.'
    assert out['latencia_s'] == 2.5
    assert out['tokens_in'] == 30
    assert out['tokens_out'] == 40


def test_generar_modelo_desconocido():
    try:
        ftf.generar('modelo-inexistente', 'hola')
        assert False, 'Debería haber lanzado KeyError'
    except KeyError:
        pass


def test_generar_captura_error_del_proveedor(monkeypatch):
    class _ClienteQueFalla:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    raise ConnectionError('timeout simulado')

    monkeypatch.setitem(ftf._clientes, 'openai', _ClienteQueFalla())
    out = ftf.generar('gpt-4o-mini', 'hola')
    assert out['error'] is not None
    assert 'timeout simulado' in out['error']
    assert out['respuesta'] is None
```

- [ ] **Step 2: Correr los tests y confirmar que fallan**

```bash
pytest tests/test_generar.py -v
```

Expected: FAIL — `AttributeError: module 'src.framework_tf' has no attribute 'generar'`

- [ ] **Step 3: Agregar el cliente unificado a `src/framework_tf.py`**

Agregar al final del archivo (después del modelo de costo del Task 3):

```python
import os
import time

TEMPERATURA = 0.0
MAX_TOKENS = 300

MODELOS = {
    'gpt-4o-mini':  {'proveedor': 'openai', 'id': 'gpt-4o-mini', 'tipo': 'propietario'},
    'llama-3.1-8b': {'proveedor': 'ollama', 'id': 'llama3.1:8b', 'tipo': 'open-source'},
    'mistral':      {'proveedor': 'ollama', 'id': 'mistral',     'tipo': 'open-source'},
}

PROMPT_SISTEMA = (
    'Sos un agente de soporte al cliente. Respondé la consulta de forma clara, '
    'concisa y profesional. No inventes datos que no tengas. '
    'Respondé en el mismo idioma en que se te consulta.'
)

_clientes = {}


def _cliente(proveedor):
    """Devuelve (y cachea) el cliente del proveedor indicado."""
    if proveedor not in _clientes:
        if proveedor == 'openai':
            from openai import OpenAI
            _clientes[proveedor] = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        elif proveedor == 'ollama':
            import ollama
            _clientes[proveedor] = ollama.Client(host='http://localhost:11434')
        else:
            raise ValueError(f'Proveedor desconocido: {proveedor}')
    return _clientes[proveedor]


def verificar_ollama():
    """Lanza RuntimeError con mensaje claro si Ollama no está corriendo."""
    import ollama
    try:
        ollama.Client(host='http://localhost:11434').list()
    except Exception as e:
        raise RuntimeError(
            'Ollama no responde en localhost:11434. Iniciá el servicio con '
            '`brew services start ollama` (o `ollama serve`) antes de continuar.'
        ) from e


def generar(modelo_key, consulta, contexto=None):
    """Envía una consulta al modelo y devuelve respuesta + métricas operativas.

    Devuelve dict con: respuesta, latencia_s, tokens_in, tokens_out, error.
    contexto=None -> condición sin RAG. Este parámetro ya existe para que
    agregar RAG en el Sub-proyecto 2 no obligue a cambiar la firma.
    """
    cfg = MODELOS[modelo_key]
    cli = _cliente(cfg['proveedor'])

    user_msg = consulta if contexto is None else (
        f'Contexto relevante de la organización:\n{contexto}\n\n'
        f'Consulta del cliente: {consulta}'
    )
    mensajes = [
        {'role': 'system', 'content': PROMPT_SISTEMA},
        {'role': 'user',   'content': user_msg},
    ]

    t0 = time.perf_counter()
    try:
        if cfg['proveedor'] == 'openai':
            r = cli.chat.completions.create(
                model=cfg['id'], messages=mensajes,
                temperature=TEMPERATURA, max_tokens=MAX_TOKENS,
            )
            return {
                'respuesta':  r.choices[0].message.content.strip(),
                'latencia_s': round(time.perf_counter() - t0, 3),
                'tokens_in':  r.usage.prompt_tokens,
                'tokens_out': r.usage.completion_tokens,
                'error':      None,
            }
        elif cfg['proveedor'] == 'ollama':
            r = cli.chat(
                model=cfg['id'], messages=mensajes,
                options={'temperature': TEMPERATURA, 'num_predict': MAX_TOKENS},
            )
            return {
                'respuesta':  r['message']['content'].strip(),
                'latencia_s': round(r['total_duration'] / 1e9, 3),
                'tokens_in':  r.get('prompt_eval_count', 0),
                'tokens_out': r.get('eval_count', 0),
                'error':      None,
            }
        else:
            raise ValueError(f"Proveedor desconocido: {cfg['proveedor']}")
    except Exception as e:
        return {
            'respuesta':  None,
            'latencia_s': round(time.perf_counter() - t0, 3),
            'tokens_in':  0,
            'tokens_out': 0,
            'error':      f'{type(e).__name__}: {e}',
        }
```

- [ ] **Step 4: Correr los tests y confirmar que pasan**

```bash
pytest tests/test_generar.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Smoke test manual contra servicios reales (no automatizado)**

```bash
source venv/bin/activate
export $(grep -v '^#' .env | xargs)  # carga OPENAI_API_KEY del .env
python3 -c "
import sys; sys.path.insert(0, '.')
from src import framework_tf as ftf

ftf.verificar_ollama()
print('Ollama OK')

for modelo in ['gpt-4o-mini', 'llama-3.1-8b', 'mistral']:
    out = ftf.generar(modelo, '¿Cómo hago para cancelar mi pedido?')
    print(modelo, '->', 'ERROR:' + out['error'] if out['error'] else out['respuesta'][:80])
"
```

Expected: `Ollama OK`, y una respuesta (sin error) para cada uno de los tres
modelos. Si `gpt-4o-mini` falla, revisar que `.env` tenga la clave real (Step 5
del Task 2). Si los modelos Ollama fallan, revisar `ollama list`.

- [ ] **Step 6: Checkpoint**

Cliente unificado funcionando con los 3 modelos, tests unitarios en verde,
verificación manual contra servicios reales exitosa.

---

### Task 5: Corpus en español — `src/corpus.py`

**Files:**
- Create: `src/corpus.py`
- Test: `tests/test_corpus.py`

**Interfaces:**
- Consumes: ningún módulo anterior directamente (recibe un cliente OpenAI ya
  instanciado como parámetro, para poder testearlo con un fake).
- Produces: `muestreo_estratificado(df_full, n_muestra, semilla=42) -> DataFrame`,
  `traducir_muestra(cliente, muestra) -> DataFrame` (agrega `instruction_es`,
  `response_es`), `cargar_o_generar_corpus_es(path, df_full, n_muestra, cliente, semilla=42) -> DataFrame`.
  El notebook (Task 6) consume `cargar_o_generar_corpus_es`.

- [ ] **Step 1: Escribir los tests (deben fallar — el módulo no existe todavía)**

Crear `tests/test_corpus.py`:

```python
import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src import corpus


def _df_fake(n_categorias=3, filas_por_categoria=5):
    filas = []
    for c in range(n_categorias):
        for i in range(filas_por_categoria):
            filas.append({
                'category': f'cat_{c}',
                'instruction': f'pregunta {c}-{i}',
                'response': f'respuesta {c}-{i}',
            })
    return pd.DataFrame(filas)


def test_muestreo_estratificado_cubre_todas_las_categorias():
    df = _df_fake(n_categorias=4, filas_por_categoria=5)
    muestra = corpus.muestreo_estratificado(df, n_muestra=4, semilla=42)
    assert len(muestra) == 4
    assert muestra['category'].nunique() == 4


def test_muestreo_estratificado_completa_con_extra_si_faltan():
    df = _df_fake(n_categorias=2, filas_por_categoria=5)
    muestra = corpus.muestreo_estratificado(df, n_muestra=5, semilla=42)
    assert len(muestra) == 5


class _FakeMsg:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMsg(content)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class _FakeClienteTraductor:
    """Traduce anteponiendo '[ES] ' — alcanza para verificar el flujo sin costo real."""
    class chat:
        class completions:
            @staticmethod
            def create(messages, **kwargs):
                original = messages[-1]['content']
                return _FakeResponse(f'[ES] {original}')


def test_traducir_muestra_agrega_columnas_es():
    muestra = pd.DataFrame({
        'category': ['x'], 'instruction': ['hello'], 'response': ['world'],
    })
    out = corpus.traducir_muestra(_FakeClienteTraductor(), muestra)
    assert out.loc[0, 'instruction_es'] == '[ES] hello'
    assert out.loc[0, 'response_es'] == '[ES] world'
    # las columnas originales se preservan intactas
    assert out.loc[0, 'instruction'] == 'hello'


def test_cargar_o_generar_no_retraduce_si_el_archivo_ya_existe(tmp_path):
    path = tmp_path / 'corpus.csv'
    pd.DataFrame({
        'category': ['x'], 'instruction': ['hola'], 'response': ['chau'],
        'instruction_es': ['hola'], 'response_es': ['chau'],
    }).to_csv(path, index=False)

    llamadas = {'n': 0}

    class _ClienteQueNoDeberiaLlamarse:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    llamadas['n'] += 1
                    raise AssertionError('No debería traducir si el archivo ya existe')

    df = corpus.cargar_o_generar_corpus_es(
        str(path), df_full=None, n_muestra=1,
        cliente=_ClienteQueNoDeberiaLlamarse(),
    )
    assert llamadas['n'] == 0
    assert df.iloc[0]['instruction_es'] == 'hola'


def test_cargar_o_generar_crea_el_archivo_si_no_existe(tmp_path):
    path = tmp_path / 'nuevo' / 'corpus.csv'
    df_full = _df_fake(n_categorias=2, filas_por_categoria=3)

    df = corpus.cargar_o_generar_corpus_es(
        str(path), df_full=df_full, n_muestra=2,
        cliente=_FakeClienteTraductor(),
    )
    assert path.exists()
    assert 'instruction_es' in df.columns
    assert len(df) == 2
```

- [ ] **Step 2: Correr los tests y confirmar que fallan**

```bash
pytest tests/test_corpus.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.corpus'`

- [ ] **Step 3: Crear `src/corpus.py`**

```python
"""Muestreo estratificado y traducción del corpus — Sub-proyecto 1 (Fundamentos)."""

import os
import pandas as pd

SEMILLA = 42

PROMPT_TRADUCTOR = (
    'Traducí el siguiente texto de inglés a español rioplatense neutro, '
    'preservando el tono y el registro. Devolvé únicamente la traducción, '
    'sin comentarios adicionales.'
)


def muestreo_estratificado(df_full, n_muestra, semilla=SEMILLA):
    """Al menos 1 registro por categoría, completando al azar hasta `n_muestra`."""
    muestra = (df_full
               .groupby('category', group_keys=False)
               .apply(lambda g: g.sample(1, random_state=semilla))
               .reset_index(drop=True))

    if len(muestra) < n_muestra:
        restantes = df_full[~df_full.index.isin(muestra.index)]
        extra = restantes.sample(n_muestra - len(muestra), random_state=semilla)
        muestra = pd.concat([muestra, extra], ignore_index=True)

    return muestra.head(n_muestra).reset_index(drop=True)


def _traducir_texto(cliente, texto):
    r = cliente.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': PROMPT_TRADUCTOR},
            {'role': 'user', 'content': texto},
        ],
        temperature=0.0,
    )
    return r.choices[0].message.content.strip()


def traducir_muestra(cliente, muestra):
    """Agrega `instruction_es` y `response_es` sin tocar las columnas originales."""
    muestra = muestra.copy()
    muestra['instruction_es'] = muestra['instruction'].apply(lambda t: _traducir_texto(cliente, t))
    muestra['response_es'] = muestra['response'].apply(lambda t: _traducir_texto(cliente, t))
    return muestra


def cargar_o_generar_corpus_es(path, df_full, n_muestra, cliente, semilla=SEMILLA):
    """Reutiliza el CSV persistido si ya existe; si no, muestrea, traduce y guarda."""
    if os.path.exists(path):
        return pd.read_csv(path)

    muestra = muestreo_estratificado(df_full, n_muestra, semilla)
    muestra_es = traducir_muestra(cliente, muestra)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    muestra_es.to_csv(path, index=False)
    return muestra_es
```

- [ ] **Step 4: Correr los tests y confirmar que pasan**

```bash
pytest tests/test_corpus.py -v
```

Expected: 5 PASSED

- [ ] **Step 5: Checkpoint**

Módulo de corpus completo y testeado (sin ninguna llamada real a OpenAI en los
tests automatizados).

---

### Task 6: Notebook de fundamentos — corrida real

**Files:**
- Create: `scripts/crear_notebook_fundamentos.py` (genera el notebook con `nbformat`)
- Create (generado por el script anterior): `notebooks/02_fundamentos.ipynb`
- Produce: `resultados_fundamentos_<sello>.csv`

**Interfaces:**
- Consumes: `src.framework_tf.MODELOS`, `src.framework_tf.generar`,
  `src.framework_tf.verificar_ollama`, `src.framework_tf.costo_consulta`,
  `src.framework_tf.costo_oficial`, `src.corpus.cargar_o_generar_corpus_es`.
- Produces: `resultados_fundamentos_<sello>.csv` con una fila por consulta,
  columnas: `modelo`, `tipo`, `category`, `consulta`, `referencia`, `respuesta`,
  `latencia_s`, `tokens_in`, `tokens_out`, `error`, `bertscore_f1`, `rouge_l`,
  `costo_usd`, `costo_electricidad_usd`, `costo_instancia_usd`,
  `costo_oficial_usd`, `indice`. Consumido por el Task 7 (`HALLAZGOS.md`) y el
  Task 8 (actualización del `.docx`).

Se genera el notebook con `nbformat` (en vez de escribirlo a mano en la UI de
Jupyter) para que la construcción sea reproducible y scripteable.

- [ ] **Step 1: Instalar `nbformat` y `ipykernel` en el venv**

```bash
source venv/bin/activate
pip install nbformat
```

(`ipykernel` ya está en `requirements.txt`.)

- [ ] **Step 2: Crear `scripts/crear_notebook_fundamentos.py`**

```python
"""Genera notebooks/02_fundamentos.ipynb con nbformat, de forma reproducible."""

import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
celdas = []

celdas.append(nbf.v4.new_markdown_cell(
    "# Fundamentos — baseline sin RAG (3 modelos, corpus en español)\n\n"
    "Sub-proyecto 1 del Trabajo Final. Corre GPT-4o mini (OpenAI), "
    "LLaMA 3.1 8B y Mistral (ambos vía Ollama local) sobre la muestra "
    "estratificada traducida al español, sin RAG."
))

celdas.append(nbf.v4.new_code_cell(
    "import sys, os\n"
    "sys.path.insert(0, '..')\n"
    "from dotenv import load_dotenv\n"
    "load_dotenv()\n"
    "from src import framework_tf as ftf\n"
    "from src import corpus\n\n"
    "ftf.verificar_ollama()\n"
    "print('Ollama OK')"
))

celdas.append(nbf.v4.new_markdown_cell("## 1. Dataset y muestra en español"))
celdas.append(nbf.v4.new_code_cell(
    "from datasets import load_dataset\n"
    "import pandas as pd\n\n"
    "N_MUESTRA = 20\n"
    "ds = load_dataset('bitext/Bitext-customer-support-llm-chatbot-training-dataset', split='train')\n"
    "df_full = ds.to_pandas()\n\n"
    "from openai import OpenAI\n"
    "cliente_traductor = OpenAI(api_key=os.environ['OPENAI_API_KEY'])\n\n"
    "muestra = corpus.cargar_o_generar_corpus_es(\n"
    "    '../data/corpus_es_muestra.csv', df_full, N_MUESTRA, cliente_traductor,\n"
    ")\n"
    "print(f'Muestra: {len(muestra)} filas, {muestra[\"category\"].nunique()} categorías')\n"
    "muestra[['category', 'instruction_es', 'response_es']].head(3)"
))

celdas.append(nbf.v4.new_markdown_cell("## 2. Generación sobre los 3 modelos"))
celdas.append(nbf.v4.new_code_cell(
    "from tqdm.auto import tqdm\n"
    "import time\n\n"
    "def correr_experimento(modelo_key, df):\n"
    "    filas = []\n"
    "    for i, fila in tqdm(df.iterrows(), total=len(df), desc=modelo_key):\n"
    "        out = ftf.generar(modelo_key, fila['instruction_es'])\n"
    "        filas.append({\n"
    "            'modelo': modelo_key,\n"
    "            'tipo': ftf.MODELOS[modelo_key]['tipo'],\n"
    "            'category': fila['category'],\n"
    "            'consulta': fila['instruction_es'],\n"
    "            'referencia': fila['response_es'],\n"
    "            **out,\n"
    "        })\n"
    "        if ftf.MODELOS[modelo_key]['proveedor'] == 'openai':\n"
    "            time.sleep(0.5)\n"
    "    return pd.DataFrame(filas)\n\n"
    "resultados = pd.concat(\n"
    "    [correr_experimento(m, muestra) for m in ftf.MODELOS],\n"
    "    ignore_index=True,\n"
    ")\n"
    "n_err = resultados['error'].notna().sum()\n"
    "print(f'Completadas: {len(resultados) - n_err}/{len(resultados)}')\n"
    "if n_err:\n"
    "    print(resultados[resultados['error'].notna()][['modelo', 'error']])"
))

celdas.append(nbf.v4.new_markdown_cell("## 3. Métricas de calidad (BERTScore en español + ROUGE-L)"))
celdas.append(nbf.v4.new_code_cell(
    "from bert_score import score as bertscore\n"
    "from rouge_score import rouge_scorer\n\n"
    "ok = resultados[resultados['error'].isna()].copy()\n\n"
    "P, R, F1 = bertscore(cands=ok['respuesta'].tolist(), refs=ok['referencia'].tolist(),\n"
    "                     lang='es', verbose=False)\n"
    "ok['bertscore_f1'] = F1.numpy().round(4)\n\n"
    "rs = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)\n"
    "ok['rouge_l'] = [round(rs.score(ref, cand)['rougeL'].fmeasure, 4)\n"
    "                 for ref, cand in zip(ok['referencia'], ok['respuesta'])]\n\n"
    "ok.groupby('modelo')[['bertscore_f1', 'rouge_l', 'latencia_s']].mean().round(4)"
))

celdas.append(nbf.v4.new_markdown_cell("## 4. Costo dual e índice compuesto"))
celdas.append(nbf.v4.new_code_cell(
    "import numpy as np\n\n"
    "costos = ok.apply(lambda f: pd.Series(ftf.costo_consulta(f)), axis=1)\n"
    "ok = pd.concat([ok, costos], axis=1)\n"
    "ok['costo_oficial_usd'] = ok.apply(ftf.costo_oficial, axis=1)\n\n"
    "def normalizar(s, invertir=False):\n"
    "    rango = s.max() - s.min()\n"
    "    if rango == 0:\n"
    "        return pd.Series(0.5, index=s.index)\n"
    "    n = (s - s.min()) / rango\n"
    "    return 1 - n if invertir else n\n\n"
    "ok['n_calidad'] = normalizar(ok['bertscore_f1'])\n"
    "ok['n_costo'] = normalizar(ok['costo_oficial_usd'], invertir=True)\n"
    "ok['n_latencia'] = normalizar(ok['latencia_s'], invertir=True)\n"
    "ok['indice'] = ((ok['n_calidad'] + ok['n_costo'] + ok['n_latencia']) / 3).round(4)\n\n"
    "resumen = ok.groupby('modelo').agg(\n"
    "    n=('category', 'count'),\n"
    "    bertscore_f1=('bertscore_f1', 'mean'),\n"
    "    rouge_l=('rouge_l', 'mean'),\n"
    "    latencia_s=('latencia_s', 'mean'),\n"
    "    costo_electricidad_usd=('costo_electricidad_usd', 'mean'),\n"
    "    costo_instancia_usd=('costo_instancia_usd', 'mean'),\n"
    "    costo_oficial_usd=('costo_oficial_usd', 'mean'),\n"
    "    indice=('indice', 'mean'),\n"
    ").round(6)\n"
    "resumen"
))

celdas.append(nbf.v4.new_markdown_cell("## 5. Guardado"))
celdas.append(nbf.v4.new_code_cell(
    "from datetime import datetime\n"
    "sello = datetime.now().strftime('%Y%m%d_%H%M')\n"
    "archivo = f'../resultados_fundamentos_{sello}.csv'\n"
    "ok.to_csv(archivo, index=False)\n"
    "print(f'Guardado: {archivo} ({len(ok)} filas)')"
))

nb['cells'] = celdas
os.makedirs('notebooks', exist_ok=True)
with open('notebooks/02_fundamentos.ipynb', 'w') as f:
    nbf.write(nb, f)
print('Notebook creado: notebooks/02_fundamentos.ipynb')
```

- [ ] **Step 2: Generar el notebook**

```bash
mkdir -p scripts
python3 scripts/crear_notebook_fundamentos.py
```

Expected: `Notebook creado: notebooks/02_fundamentos.ipynb`

- [ ] **Step 3: Ejecutar el notebook de punta a punta (corrida real, con costo real de OpenAI y tiempo real de Ollama)**

```bash
source venv/bin/activate
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 02_fundamentos.ipynb
cd ..
```

Expected: termina sin excepción. Puede tardar varios minutos por la inferencia
local de Ollama en CPU/GPU integrada.

- [ ] **Step 4: Verificar el resultado**

```bash
python3 -c "
import pandas as pd, glob
archivo = sorted(glob.glob('resultados_fundamentos_*.csv'))[-1]
df = pd.read_csv(archivo)
assert df['modelo'].nunique() == 3, f'Se esperaban 3 modelos, hay {df[\"modelo\"].nunique()}'
assert df['bertscore_f1'].notna().all(), 'Hay bertscore_f1 nulo'
assert df['costo_oficial_usd'].notna().all(), 'Hay costo_oficial_usd nulo'
print('OK —', archivo)
print(df.groupby('modelo')[['bertscore_f1','latencia_s','costo_oficial_usd','indice']].mean().round(6))
"
```

Expected: `OK — resultados_fundamentos_<sello>.csv` seguido de la tabla resumen
por modelo, sin valores nulos en las columnas clave.

- [ ] **Step 5: Checkpoint**

Baseline sin RAG corrido de punta a punta contra servicios reales (OpenAI +
Ollama local), con resultados persistidos a nivel de consulta individual.

---

### Task 7: `HALLAZGOS.md` — bitácora de resultados

**Files:**
- Create: `HALLAZGOS.md`

**Interfaces:**
- Consumes: `resultados_fundamentos_<sello>.csv` (Task 6).
- Produces: `HALLAZGOS.md` — insumo de prosa para el Task 8.

- [ ] **Step 1: Generar la sección de hallazgos a partir del CSV real**

```bash
source venv/bin/activate
python3 -c "
import pandas as pd, glob

archivo = sorted(glob.glob('resultados_fundamentos_*.csv'))[-1]
df = pd.read_csv(archivo)
resumen = df.groupby('modelo').agg(
    bertscore_f1=('bertscore_f1', 'mean'),
    rouge_l=('rouge_l', 'mean'),
    latencia_s=('latencia_s', 'mean'),
    costo_electricidad_usd=('costo_electricidad_usd', 'mean'),
    costo_instancia_usd=('costo_instancia_usd', 'mean'),
    costo_oficial_usd=('costo_oficial_usd', 'mean'),
    indice=('indice', 'mean'),
).round(6)

with open('HALLAZGOS.md', 'w') as f:
    f.write('# Hallazgos — Trabajo Final\n\n')
    f.write('Bitácora cruda de resultados y decisiones metodológicas. Este documento es '
            'el insumo directo para redactar las secciones correspondientes de la tesis '
            '(ver `.docx`), pero NO reemplaza la redacción formal.\n\n')
    f.write('## Sub-proyecto 1 — Fundamentos\n\n')
    f.write(f'**Archivo de resultados:** `{archivo}`\n\n')
    f.write('### Decisiones metodológicas\n\n')
    f.write('- Costo open-source medido en dos columnas: `costo_electricidad_usd` '
            '(piso, energía real medida en Apple M3) y `costo_instancia_usd` (oficial, '
            'usada para H2/H3, amortización de instancia cloud con la latencia real '
            'medida en Ollama).\n')
    f.write('- Modelos open-source servidos localmente vía Ollama, reemplazando Groq, '
            'para que costo y latencia se midan sobre la misma infraestructura real.\n')
    f.write('- Corpus: subconjunto de Bitext traducido al español (instrucción + '
            'referencia), persistido en `data/corpus_es_muestra.csv`.\n\n')
    f.write('### Resultados — baseline sin RAG\n\n')
    f.write(resumen.to_markdown() + '\n\n')
    f.write('### Observaciones\n\n')
    f.write('- [completar tras inspeccionar manualmente los resultados: outliers, '
            'errores de generación, respuestas vacías, etc.]\n\n')
    f.write('### Pendiente\n\n')
    f.write('- Condición con RAG (Sub-proyecto 2).\n')
    f.write('- Escalado a 300-500 consultas (Sub-proyecto 3).\n')
    f.write('- Pruebas estadísticas (Sub-proyecto 4).\n')
    f.write('- Dashboard (Sub-proyecto 5).\n')
print('HALLAZGOS.md generado')
"
```

Nota: la sección "Observaciones" queda con un ítem para completar a mano —
requiere criterio humano (revisar las respuestas generadas), no es un dato que
se pueda derivar automáticamente del CSV. Todo lo demás en este documento sale
de datos reales, no de contenido inventado.

- [ ] **Step 2: Verificar que el archivo se generó con la tabla de resultados**

```bash
grep -q "costo_oficial_usd" HALLAZGOS.md && echo "OK: tabla de resultados presente"
```

Expected: `OK: tabla de resultados presente`

- [ ] **Step 3: Checkpoint**

`HALLAZGOS.md` creado con resultados reales del Task 6.

---

### Task 8: Actualización de la tesis — `TF_Juan_Bautista_Xifro_2026_v3.docx` → `v4`

**Files:**
- Create: `scripts/actualizar_tesis_v4.py` (análogo a `aplicar_cambios.py`)
- Produce: `TF_Juan_Bautista_Xifro_2026_v4.docx`

**Interfaces:**
- Consumes: `TF_Juan_Bautista_Xifro_2026_v3.docx` (Task 1),
  `resultados_fundamentos_<sello>.csv` (Task 6).
- Produces: `TF_Juan_Bautista_Xifro_2026_v4.docx`.

- [ ] **Step 1: Crear `scripts/actualizar_tesis_v4.py`**

```python
"""Aplica al v3 las secciones correspondientes al Sub-proyecto 1 (Fundamentos)
y genera la v4. Mismo mecanismo de edición XML que aplicar_cambios.py."""

import re, html, zipfile, shutil, os, glob
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'TF_Juan_Bautista_Xifro_2026_v3.docx')
WORK = os.path.join(BASE, '_tmp_tf_v4')
OUT = os.path.join(BASE, 'TF_Juan_Bautista_Xifro_2026_v4.docx')

if os.path.exists(WORK):
    shutil.rmtree(WORK)
os.makedirs(WORK)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)
    ORDEN = z.namelist()

P = os.path.join(WORK, 'word/document.xml')
x = open(P, encoding='utf-8').read()

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" '
       'w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/>'
       '<w:sz w:val="24"/><w:szCs w:val="24"/><w:rtl w:val="0"/></w:rPr>')
TAIL = ('<w:r w:rsidDel="00000000" w:rsidR="00000000" w:rsidRPr="00000000">'
        '<w:rPr><w:rtl w:val="0"/></w:rPr></w:r>')
PARA_RE = re.compile(r'<w:p\b[^>]*>(?:(?!</w:p>).)*?</w:p>', re.S)


def esc(t):
    return html.escape(t, quote=False)


def body(text):
    return ('<w:p><w:pPr><w:spacing w:after="160" w:before="0" w:line="360" '
            'w:lineRule="auto"/><w:jc w:val="both"/><w:rPr/></w:pPr>'
            f'<w:r>{RPR}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
            f'{TAIL}</w:p>')


def insertar_despues(fragmento, nuevo_xml, tag):
    global x
    for m in PARA_RE.finditer(x):
        t = ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', m.group(0), re.S))
        if fragmento in t:
            x = x[:m.end()] + nuevo_xml + x[m.end():]
            print(f'  ok  {tag}')
            return
    raise SystemExit(f'NO ENCONTRADO [{tag}]: {fragmento[:50]}')


print('Aplicando ediciones del Sub-proyecto 1 (Fundamentos):')

# 1. Sección 3.4 — nota sobre la traducción del corpus
insertar_despues(
    'para la base de conocimiento RAG se utilizará un subconjunto de documentos de '
    'política y procedimientos sintéticos, generados a partir del mismo dataset y '
    'almacenados en FAISS.',
    body('Dado que el dataset Bitext se encuentra íntegramente en inglés y el alcance '
         'de este trabajo se orienta a organizaciones hispanohablantes, la muestra '
         'utilizada en la fase experimental fue traducida al español mediante un '
         'modelo de lenguaje (GPT-4o mini), preservando tanto las consultas como las '
         'respuestas de referencia originales a los fines de trazabilidad con el '
         'dataset público. La muestra traducida se persiste en un archivo versionado '
         'del proyecto, de modo que la traducción se realiza una única vez y las '
         'corridas subsiguientes son reproducibles sin costo adicional.'),
    '3.4 nota traducción corpus')

# 2. Capítulo 4 — arquitectura del cliente unificado y modelo de costo dual
insertar_despues(
    'Se incluirá un diagrama de arquitectura y la justificación de cada decisión de '
    'diseño en función del problema planteado. [Contenido a desarrollar en la tesis '
    'completa.]',
    body('El framework implementa un cliente unificado de modelos que expone una '
         'interfaz común independiente del proveedor subyacente: dado un identificador '
         'de modelo y una consulta, devuelve siempre la misma estructura de respuesta '
         '(texto generado, latencia, tokens de entrada y salida, y error si '
         'corresponde). Esta abstracción permite incorporar nuevos modelos agregando '
         'una entrada de configuración, sin modificar el código de generación ni de '
         'evaluación.')
    + body('Una decisión de diseño central es la del modelo de costo aplicado a los '
           'modelos de código abierto. Dado que estos no tienen un precio de API '
           'publicado, se calculan dos métricas de costo con roles diferenciados. La '
           'primera, el costo de electricidad, estima el consumo energético marginal '
           'de ejecutar el modelo localmente, a partir de la potencia térmica de '
           'diseño del hardware utilizado y la duración real de inferencia medida en '
           'cada consulta; constituye una cota inferior estrictamente medible, sin '
           'depender de ninguna cotización externa, aunque subestima el costo total '
           'porque no incorpora la amortización del hardware. La segunda, el costo de '
           'instancia amortizada, estima el costo de servir el modelo desde una '
           'instancia de cómputo en la nube con capacidad de GPU, dividiendo el precio '
           'por hora de dicha instancia por la cantidad de consultas que su latencia '
           'real permite atender en una hora; esta segunda métrica se adopta como '
           'métrica oficial para el contraste de las Hipótesis 2 y 3, por representar '
           'de manera más fiel el escenario de despliegue productivo que dichas '
           'hipótesis describen. Ambas métricas se calculan y documentan en paralelo, '
           'de modo que la robustez de los hallazgos pueda evaluarse frente a ambas '
           'estimaciones.'),
    'capítulo 4 arquitectura y costo')

# 3. Capítulo 5 — stack técnico real
insertar_despues(
    'Este capítulo detalla el stack tecnológico completo (PySpark, LangChain, FAISS, '
    'RAGAS, Streamlit), la configuración de cada modelo LLM evaluado, el proceso de '
    'integración del RAG y la construcción del dashboard interactivo. Se incluirá '
    'código fuente relevante y capturas del prototipo funcional. [Contenido a '
    'desarrollar en la tesis completa.]',
    body('En su fase de fundamentos, el prototipo se implementó en Python 3.11. El '
         'modelo propietario (GPT-4o mini) se accede mediante la API de OpenAI. Los '
         'modelos de código abierto (LLaMA 3.1 8B y Mistral) se ejecutan localmente '
         'mediante Ollama, lo que permite medir de forma directa su latencia real y '
         'derivar de ella un costo operativo defendible, en lugar de estimarlo. Las '
         'métricas de calidad semántica se calculan con las bibliotecas bert-score y '
         'rouge-score. La configuración de credenciales se gestiona mediante variables '
         'de entorno cargadas con python-dotenv, evitando su exposición en el código '
         'fuente.'),
    'capítulo 5 stack técnico')

# 4. Capítulo 6 — resultados del baseline sin RAG (con datos reales)
archivo = sorted(glob.glob(os.path.join(BASE, 'resultados_fundamentos_*.csv')))[-1]
df = pd.read_csv(archivo)
resumen = df.groupby('modelo').agg(
    bertscore_f1=('bertscore_f1', 'mean'),
    latencia_s=('latencia_s', 'mean'),
    costo_oficial_usd=('costo_oficial_usd', 'mean'),
).round(4)

texto_resultados = (
    'Los resultados del baseline sin RAG, calculados sobre la muestra estratificada '
    'traducida al español, se presentan a continuación. GPT-4o mini alcanzó un '
    f"BERTScore F1 medio de {resumen.loc['gpt-4o-mini', 'bertscore_f1']:.4f}, con una "
    f"latencia media de {resumen.loc['gpt-4o-mini', 'latencia_s']:.2f} segundos y un "
    f"costo medio de USD {resumen.loc['gpt-4o-mini', 'costo_oficial_usd']:.6f} por "
    'consulta. LLaMA 3.1 8B, servido localmente mediante Ollama, obtuvo un BERTScore '
    f"F1 medio de {resumen.loc['llama-3.1-8b', 'bertscore_f1']:.4f}, con una latencia "
    f"media de {resumen.loc['llama-3.1-8b', 'latencia_s']:.2f} segundos y un costo de "
    f"instancia amortizada de USD {resumen.loc['llama-3.1-8b', 'costo_oficial_usd']:.6f} "
    'por consulta. Mistral presentó un BERTScore F1 medio de '
    f"{resumen.loc['mistral', 'bertscore_f1']:.4f}, con una latencia media de "
    f"{resumen.loc['mistral', 'latencia_s']:.2f} segundos y un costo equivalente de "
    f"USD {resumen.loc['mistral', 'costo_oficial_usd']:.6f} por consulta. Estos "
    'resultados corresponden exclusivamente a la condición sin RAG, que opera como '
    'línea base de control; la condición con RAG se incorpora en la siguiente etapa '
    'de este trabajo.'
)

insertar_despues(
    'Este capítulo presenta los resultados del experimento comparativo: tablas de '
    'métricas por modelo y condición, análisis estadístico de las hipótesis, '
    'discusión de los hallazgos y la guía de selección de modelo según perfil '
    'organizacional. [Contenido a desarrollar en la tesis completa.]',
    body(texto_resultados),
    'capítulo 6 resultados baseline')

open(P, 'w', encoding='utf-8').write(x)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for nombre in ORDEN:
        z.write(os.path.join(WORK, nombre), nombre)

print(f'\nGenerado: {OUT}')
shutil.rmtree(WORK, ignore_errors=True)
print('Listo.')
```

- [ ] **Step 2: Correr el script**

```bash
python3 scripts/actualizar_tesis_v4.py
```

Expected: imprime `ok` para las 4 ediciones y termina con `Listo.`. Si falla con
`NO ENCONTRADO [...]`, el texto exacto del v3 difiere del esperado — revisar
manualmente el fragmento en cuestión antes de reintentar.

- [ ] **Step 3: Verificar el contenido de la v4**

```bash
python3 -c "
import zipfile, re, html
with zipfile.ZipFile('TF_Juan_Bautista_Xifro_2026_v4.docx') as z:
    xml = z.read('word/document.xml').decode('utf-8')
texto = ''.join(html.unescape(t) for t in re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml, re.S))
for esperado in ['costo de electricidad', 'costo de instancia amortizada',
                 'Ollama', 'python-dotenv', 'BERTScore F1 medio de']:
    assert esperado in texto, f'Falta: {esperado}'
print('OK: v4 contiene las 4 secciones nuevas con datos reales')
"
```

Expected: `OK: v4 contiene las 4 secciones nuevas con datos reales`

- [ ] **Step 4: Checkpoint**

`TF_Juan_Bautista_Xifro_2026_v4.docx` generado con las secciones 3.4, Capítulo 4,
Capítulo 5 y la parte del Capítulo 6 correspondiente al baseline sin RAG,
redactadas en APA 7 con datos reales del experimento. Sub-proyecto 1 completo.
