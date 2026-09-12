import re, html, zipfile, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'TF_Juan_Bautista_Xifro_2026_v2.docx')
WORK = os.path.join(BASE, '_tmp_tf')
OUT = os.path.join(BASE, 'TF_Juan_Bautista_Xifro_2026_v3.docx')

if os.path.exists(WORK):
    shutil.rmtree(WORK)
os.makedirs(WORK)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)
    ORDEN = z.namelist()          # preservar el orden original de entradas

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


def reemplazar_texto(fragmento, nuevo, tag):
    """Reemplaza el contenido del <w:t> que contiene `fragmento`."""
    global x
    for m in PARA_RE.finditer(x):
        p = m.group(0)
        ts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, re.S)
        if len(ts) == 1 and fragmento in ts[0]:
            nuevo_p = p.replace(f'>{ts[0]}<', f'>{esc(nuevo)}<')
            x = x[:m.start()] + nuevo_p + x[m.end():]
            print(f'  ok  {tag}')
            return
    raise SystemExit(f'NO ENCONTRADO [{tag}]: {fragmento[:50]}')


def insertar_despues(fragmento, nuevo_xml, tag):
    global x
    for m in PARA_RE.finditer(x):
        t = ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', m.group(0), re.S))
        if fragmento in t:
            x = x[:m.end()] + nuevo_xml + x[m.end():]
            print(f'  ok  {tag}')
            return
    raise SystemExit(f'NO ENCONTRADO [{tag}]: {fragmento[:50]}')


print('Aplicando ediciones:')

# 1. Cierre de hipotesis: aclarar que datos las contrastan
insertar_despues(
    'Las tres hipótesis serán sometidas a prueba empírica',
    body('Cabe precisar que las tres hipótesis se contrastan exclusivamente sobre los datos '
         'obtenidos en la condición con RAG, dado que esa es la configuración en la que una '
         'organización efectivamente desplegaría el sistema. La condición sin RAG no interviene '
         'en el contraste de hipótesis: cumple la función de línea base de control, según se '
         'detalla en el apartado 3.2.'),
    'aclaración tras hipótesis')

# 2. Objetivo especifico 3: explicitar el rol de control
reemplazar_texto(
    'en modo zero-shot y con RAG, midiendo BERTScore',
    '3.Evaluar comparativamente al menos tres modelos LLM (GPT-4o mini, LLaMA 3, Mistral) en la '
    'condición con RAG, midiendo BERTScore, ROUGE, latencia y costo operativo por consulta, '
    'utilizando la condición sin RAG (zero-shot) como línea base de control que permita aislar '
    'el aporte de la recuperación sobre el desempeño de cada modelo.',
    'objetivo específico 3')

# 3. Diseno 3.2: reformular el rol de cada condicion
reemplazar_texto(
    'El diseño es experimental comparativo. Se define un experimento controlado',
    'El diseño es experimental comparativo con línea base de control. La variable independiente '
    'es el tipo de modelo LLM (GPT-4o mini, LLaMA 3, Mistral) y la condición de uso (con RAG / '
    'sin RAG). Las variables dependientes son las métricas de calidad semántica (BERTScore, '
    'ROUGE), el costo operativo por consulta y la latencia de respuesta. Cada combinación modelo '
    '× condición constituye una celda experimental, resultando en un diseño de 3 modelos × 2 '
    'condiciones = 6 configuraciones a evaluar.',
    'diseño 3.2')

insertar_despues(
    'El diseño es experimental comparativo con línea base de control',
    body('Ambas condiciones cumplen funciones metodológicas distintas. La condición con RAG '
         'constituye la configuración de interés: es la que replica el escenario real de '
         'implementación organizacional y sobre la cual se contrastan las tres hipótesis. La '
         'condición sin RAG, en cambio, opera como línea base de control y no participa del '
         'contraste de hipótesis.')
    + body('La inclusión de esta línea base responde a dos razones. En primer lugar, permite '
           'responder la segunda pregunta secundaria de la investigación, referida al impacto '
           'de la incorporación de RAG sobre la calidad de respuesta de cada modelo, lo que '
           'exige necesariamente un punto de comparación previo. En segundo lugar, y de manera '
           'más relevante para la validez interna del estudio, permite discriminar entre dos '
           'explicaciones alternativas ante un eventual resultado de equivalencia entre modelos '
           'en la condición con RAG: que los modelos sean efectivamente equivalentes en calidad, '
           'o que la recuperación domine el resultado y enmascare las diferencias entre ellos. '
           'Sin línea base, esa ambigüedad resultaría irresoluble.')
    + body('Cabe señalar que la mejora asociada al RAG no constituye un supuesto garantizado. '
           'Gao et al. (2023) advierten que la calidad final del sistema depende de manera '
           'conjunta de la etapa de recuperación y de la capacidad generativa del modelo, de '
           'modo que una recuperación deficiente puede introducir ruido contextual y degradar '
           'la respuesta. La línea base permite verificar empíricamente que la implementación '
           'de RAG desarrollada en este trabajo aporta valor, en lugar de asumirlo.'),
    'fundamentación del control')

# 4. Procedimiento 3.5, paso 3
reemplazar_texto(
    'Ejecución de los 6 experimentos (3 modelos × 2 condiciones)',
    '3.Ejecución de las 6 configuraciones experimentales (3 modelos × 2 condiciones): cada '
    'consulta del conjunto de prueba se envía a cada modelo en la condición con RAG y en la '
    'condición sin RAG, esta última en carácter de línea base de control.',
    'procedimiento paso 3')

# 5. Procedimiento 3.5, paso 5
reemplazar_texto(
    'Análisis estadístico: selección y aplicación de pruebas estadísticas apropiadas',
    '5.Análisis estadístico: selección y aplicación de pruebas estadísticas apropiadas según la '
    'distribución de los datos, para verificar las hipótesis formuladas sobre la condición con '
    'RAG y para cuantificar, mediante contraste con la línea base, el aporte de la recuperación '
    'en cada modelo.',
    'procedimiento paso 5')

open(P, 'w', encoding='utf-8').write(x)

# Reempaquetado preservando orden de entradas
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for nombre in ORDEN:
        z.write(os.path.join(WORK, nombre), nombre)

print(f'\nGenerado: {OUT}')

shutil.rmtree(WORK, ignore_errors=True)
print('Carpeta temporal eliminada.')
print('Listo. Abri TF_Juan_Bautista_Xifro_2026_v3.docx')
