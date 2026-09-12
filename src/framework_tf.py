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
