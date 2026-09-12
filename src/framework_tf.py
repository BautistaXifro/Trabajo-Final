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


# --- Cliente unificado de modelos ---
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
