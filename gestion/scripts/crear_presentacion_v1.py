"""Genera gestion/presentacion/sub-proyecto-1-fundamentos.pptx con python-pptx.

Herramienta interna de una sola vez (no es una dependencia del TF en sí,
por eso no está en proyecto/requirements.txt). Para volver a correrlo:

    pip install python-pptx
    python3 gestion/scripts/crear_presentacion_v1.py

El contenido reproduce gestion/presentacion/sub-proyecto-1-fundamentos.md
(la fuente "de verdad" del contenido); este script solo lo da vuelta a un
.pptx real, autocontenido, sin depender de ningún servicio externo.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.normpath(os.path.join(AQUI, '..', 'presentacion',
                                         'sub-proyecto-1-fundamentos.pptx'))

# --- Paleta simple y consistente ---
NEGRO = RGBColor(0x1A, 0x1A, 0x1A)
GRIS_OSCURO = RGBColor(0x4A, 0x4A, 0x4A)
GRIS_CLARO = RGBColor(0xF5, 0xF5, 0xF5)
AMARILLO = RGBColor(0xFF, 0xE6, 0x00)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
VERDE = RGBColor(0x2E, 0x99, 0x42)
ROJO = RGBColor(0xE5, 0x59, 0x40)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def _fondo(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _texto(slide, x, y, w, h, texto, size=18, bold=False, color=NEGRO,
           align=PP_ALIGN.LEFT, font='Calibri'):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = texto
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    return box


def _bullets(slide, x, y, w, h, items, size=16, color=NEGRO):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f'•  {item}'
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(10)
    return box


def _header(slide, titulo, subtitulo=None):
    _fondo(slide, BLANCO)
    barra = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, Inches(1.1))
    barra.fill.solid()
    barra.fill.fore_color.rgb = NEGRO
    barra.line.fill.background()
    _texto(slide, 0.5, 0.18, 12.3, 0.6, titulo, size=26, bold=True, color=AMARILLO)
    if subtitulo:
        _texto(slide, 0.5, 0.65, 12.3, 0.4, subtitulo, size=14, color=BLANCO)


def _tabla(slide, x, y, w, h, filas, col_widths=None, header=True):
    n_filas = len(filas)
    n_cols = len(filas[0])
    shape = slide.shapes.add_table(n_filas, n_cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tabla = shape.table
    if col_widths:
        for i, cw in enumerate(col_widths):
            tabla.columns[i].width = Inches(cw)
    for i, fila in enumerate(filas):
        for j, val in enumerate(fila):
            celda = tabla.cell(i, j)
            celda.text = str(val)
            for p in celda.text_frame.paragraphs:
                p.font.size = Pt(13 if i == 0 else 12)
                p.font.bold = (i == 0 and header)
                p.font.color.rgb = BLANCO if (i == 0 and header) else NEGRO
            if i == 0 and header:
                celda.fill.solid()
                celda.fill.fore_color.rgb = NEGRO
            else:
                celda.fill.solid()
                celda.fill.fore_color.rgb = GRIS_CLARO if i % 2 == 0 else BLANCO
    return tabla


# ============================================================ Slide 1 — Título
s = prs.slides.add_slide(BLANK)
_fondo(s, NEGRO)
_texto(s, 1, 2.3, 11.3, 1.2, 'Sub-proyecto 1: Fundamentos', size=40, bold=True, color=AMARILLO)
_texto(s, 1, 3.5, 11.3, 0.7, 'Evaluación de LLMs para Soporte al Cliente Automatizado',
       size=20, color=BLANCO)
_texto(s, 1, 4.9, 11.3, 0.5, 'Trabajo Final — Juan Bautista Xifro — UAI 2026', size=16, color=GRIS_CLARO)
_texto(s, 1, 5.6, 11.3, 0.5, 'Baseline sin RAG: 3 modelos, 20 consultas, corrida real, 0 errores.',
       size=14, color=AMARILLO)

# ============================================================ Slide 2 — Objetivo
s = prs.slides.add_slide(BLANK)
_header(s, 'Objetivo de esta etapa')
_bullets(s, 0.6, 1.5, 12, 5, [
    'Entorno reproducible (Ollama local + Python 3.11)',
    'Modelo de costo defendible para los modelos open-source',
    'Corpus en español (no en inglés, para alinear con el alcance del TF)',
    'Corrida real contra los 3 modelos, sin errores',
    'Primeros resultados volcados a la tesis (Cap. 3.4, 4, 5, 6-parcial)',
], size=18)
_texto(s, 0.6, 5.8, 12, 1, 'No busca resultados definitivos — busca validar que la cadena funciona antes de escalar.',
       size=14, bold=True, color=GRIS_OSCURO)

# ============================================================ Slide 3 — Pipeline
s = prs.slides.add_slide(BLANK)
_header(s, 'Pipeline del notebook — 7 pasos')
pasos = [
    '1. Setup — carga .env, verifica que Ollama está corriendo',
    '2. Dataset — Bitext (HuggingFace), muestra estratificada de 20 (semilla=42), traducida al español',
    '3. Generación — 20 consultas a los 3 modelos, mismo prompt, temperatura=0, semilla=42',
    '4. Calidad — BERTScore F1 (español) + ROUGE-L, respuesta vs. referencia',
    '5. Costo — dual: electricidad estimada (piso) + instancia cloud amortizada (oficial)',
    '6. Índice compuesto — normaliza calidad/costo/latencia a [0,1], promedio con igual peso',
    '7. Guardado — CSV con una fila por consulta (no solo promedios)',
]
_bullets(s, 0.6, 1.4, 12, 5.8, pasos, size=15)

# ============================================================ Slide 4 — Modelos
s = prs.slides.add_slide(BLANK)
_header(s, 'Modelos evaluados')
_tabla(s, 0.6, 1.5, 12.1, 2.0, [
    ['Modelo', 'Proveedor', 'Tipo', 'Cómo corre'],
    ['gpt-4o-mini', 'OpenAI (API)', 'Propietario', 'Nube, paga por token'],
    ['llama-3.1-8b', 'Ollama (llama3.1:8b)', 'Código abierto', 'Local, en tu Mac (M3)'],
    ['mistral', 'Ollama (mistral)', 'Código abierto', 'Local, en tu Mac (M3)'],
], col_widths=[2.6, 3.2, 2.6, 3.7])
_texto(s, 0.6, 4.0, 12, 1.2,
       'Los dos modelos open-source ya no usan Groq — corren 100% localmente, para que '
       'costo y latencia se midan sobre la misma infraestructura real.', size=15, color=GRIS_OSCURO)

# ============================================================ Slide 5 — Costo dual
s = prs.slides.add_slide(BLANK)
_header(s, 'El costo de los modelos "gratuitos" — no es cero')
_tabla(s, 0.6, 1.5, 12.1, 1.7, [
    ['Métrica', 'Qué mide', 'Rol'],
    ['costo_electricidad_usd', 'Consumo eléctrico estimado (TDP × latencia real)', 'Piso — 100% medible'],
    ['costo_instancia_usd', 'Amortización de instancia cloud / consultas·hora', 'Oficial — usada en H2/H3'],
], col_widths=[3.6, 5.5, 3.0])
_texto(s, 0.6, 3.6, 12, 1.5,
       '⚠️ Los parámetros (CONSUMO_W, PRECIO_KWH_USD, PRECIO_INSTANCIA_HORA) son '
       'placeholders todavía sin cotización real citada — documentado explícitamente '
       'en el código, en HALLAZGOS.md y en la tesis.', size=15, bold=True, color=ROJO)

# ============================================================ Slide 6 — Costos reales
s = prs.slides.add_slide(BLANK)
_header(s, 'Resultados reales — costo promedio por consulta')
_tabla(s, 0.6, 1.5, 12.1, 1.7, [
    ['Modelo', 'Costo electricidad', 'Costo instancia (oficial)', 'Latencia media'],
    ['gpt-4o-mini', '— (no aplica)', 'USD 0.000071', '1.30 s'],
    ['llama-3.1-8b', 'USD 0.000005', 'USD 0.001328', '6.38 s'],
    ['mistral', 'USD 0.000008', 'USD 0.001926', '9.25 s'],
], col_widths=[3.0, 3.2, 3.4, 2.5])
_texto(s, 0.6, 3.7, 12, 1.4,
       'Costo total de la corrida completa (60 consultas): gpt-4o-mini USD 0.0014 · '
       'llama USD 0.0266 · mistral USD 0.0385 — la corrida entera costó menos de 7 '
       'centavos de dólar en total.', size=16, bold=True, color=VERDE)

# ============================================================ Slide 7 — Tabla completa
s = prs.slides.add_slide(BLANK)
_header(s, 'Resultados reales — tabla completa')
_tabla(s, 0.6, 1.6, 12.1, 1.9, [
    ['Modelo', 'BERTScore F1', 'Latencia', 'Costo oficial', 'Índice compuesto'],
    ['gpt-4o-mini', '0.7120', '1.30 s', 'USD 0.000071', '0.797'],
    ['llama-3.1-8b', '0.7154', '6.38 s', 'USD 0.001328', '0.562'],
    ['mistral', '0.7103', '9.25 s', 'USD 0.001926', '0.425'],
], col_widths=[2.8, 2.4, 2.2, 2.5, 2.2])
_texto(s, 0.6, 4.0, 12, 0.6, '60 consultas totales (3 modelos × 20), 0 errores.',
       size=15, color=GRIS_OSCURO)

# ============================================================ Slide 8 — Hallazgo 1
s = prs.slides.add_slide(BLANK)
_header(s, 'Hallazgo 1 — La calidad no discrimina')
_texto(s, 0.6, 1.8, 12, 1.2,
       'BERTScore F1 queda prácticamente empatado: 0.7103 – 0.7154 (diferencia de ~0.005 '
       'entre el mejor y el peor).', size=20, bold=True)
_texto(s, 0.6, 3.2, 12, 2,
       'En este baseline sin RAG, ningún modelo responde mejor que otro de forma '
       'relevante — el índice compuesto termina decidido casi enteramente por costo y '
       'latencia, no por calidad.', size=17, color=GRIS_OSCURO)

# ============================================================ Slide 9 — Hallazgo 2
s = prs.slides.add_slide(BLANK)
_header(s, 'Hallazgo 2 (riesgo a vigilar) — El costo favorece a GPT-4o mini')
_texto(s, 0.6, 1.6, 12, 1.1,
       'Bajo el modelo de costo oficial, los open-source salen 18.6x (llama) y 27x '
       '(mistral) más caros por consulta que GPT-4o mini — lo opuesto a lo que predice H2.',
       size=18, bold=True, color=ROJO)
_bullets(s, 0.6, 3.0, 12, 2.5, [
    'Por qué: la fórmula divide el precio de instancia entre consultas/hora; la '
    'latencia real de Ollama local (6-9s) es mucho mayor que la de la API de OpenAI (1.3s)',
    'No invalida nada todavía — las hipótesis se contrastan solo con la condición CON RAG',
    'A vigilar en el Sub-proyecto 2: si el patrón se repite con RAG, es un resultado '
    'válido a discutir, no algo para forzar ajustando la metodología',
], size=15)

# ============================================================ Slide 10 — Complejidad
s = prs.slides.add_slide(BLANK)
_header(s, 'Qué fue complejo en esta primera iteración')
_bullets(s, 0.6, 1.4, 12, 5.8, [
    'Diseñar un modelo de costo defendible para algo que "no cuesta nada" (open-source) '
    '— terminamos con 2 métricas paralelas, no 1',
    'Bug real de índices en el muestreo estratificado (filas duplicadas silenciosas) '
    '— encontrado y corregido con test de regresión',
    'Bug real de doble redondeo en el texto de la tesis — el costo de GPT-4o mini se '
    'mostraba ~40% más alto de lo real',
    'Bug real de NaN vs. None al mezclar costos de distintos modelos en un DataFrame',
    'Fricción operativa: cuenta OpenAI sin crédito, confusión ChatGPT Plus vs. API '
    '(productos separados), un incidente de seguridad (clave pegada en el chat, '
    'resuelto revocándola al instante)',
], size=15)

# ============================================================ Slide 11 — Costo iteración
s = prs.slides.add_slide(BLANK)
_header(s, 'Qué costó (tiempo y dinero) en esta iteración')
_tabla(s, 0.6, 1.6, 12.1, 2.4, [
    ['Recurso', 'Costo real'],
    ['Llamadas a OpenAI (traducción + generación + tests)', '< USD 0.10 en total'],
    ['Modelos Ollama descargados', '~10 GB de disco, gratis'],
    ['Crédito cargado en OpenAI', 'USD 5 (alcanza para 500 consultas)'],
    ['Tiempo de desarrollo', '8 tareas + revisión final + 1 ronda de fix, 2 bugs reales corregidos'],
], col_widths=[7.5, 4.6])
_texto(s, 0.6, 4.5, 12, 1,
       'El costo económico de correr el experimento es prácticamente nulo — el costo '
       'real de esta etapa fue tiempo de diseño e ingeniería, no cómputo.', size=15,
       bold=True, color=GRIS_OSCURO)

# ============================================================ Slide 12 — Roadmap
s = prs.slides.add_slide(BLANK)
_header(s, 'Qué falta — Roadmap')
_tabla(s, 0.6, 1.5, 12.1, 3.0, [
    ['#', 'Sub-proyecto', 'Qué agrega'],
    ['2', 'RAG', 'FAISS + LangChain, vía el parámetro contexto que generar() ya acepta'],
    ['3', 'Escalar la muestra', 'De 20 a 300-500 consultas (Spark si el volumen lo justifica)'],
    ['4', 'Pruebas estadísticas', 'Shapiro-Wilk → paramétrica o no paramétrica, contraste H1/H2/H3'],
    ['5', 'Dashboard', 'Streamlit sobre los CSV de resultados'],
    ['6', 'Cierre de la tesis', 'Conclusiones, Líneas Futuras, Anexos'],
], col_widths=[0.8, 3.3, 8.0])
_texto(s, 0.6, 4.8, 12, 0.6, 'Completitud estimada del TF hoy: ~35-40%.',
       size=16, bold=True, color=NEGRO)

# ============================================================ Slide 13 — Cierre
s = prs.slides.add_slide(BLANK)
_fondo(s, NEGRO)
_texto(s, 1, 2.3, 11.3, 1, 'Próximo paso: Sub-proyecto 2 — RAG', size=32, bold=True, color=AMARILLO)
_texto(s, 1, 3.6, 11.3, 1.8,
       'Construir la base de conocimiento vectorial y correr las configuraciones con '
       'contexto recuperado, para poder finalmente contrastar H1, H2 y H3 (las hipótesis '
       'solo se prueban con RAG; esto fue únicamente la línea base de control).',
       size=17, color=BLANCO)
_texto(s, 1, 5.6, 11.3, 0.6, 'Mismo proceso: brainstorming → spec → plan → ejecución con revisión.',
       size=14, color=GRIS_CLARO)

os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
prs.save(DESTINO)
print(f'Presentación creada: {DESTINO}')
print(f'Diapositivas: {len(prs.slides.__iter__.__self__._sldIdLst)}')
