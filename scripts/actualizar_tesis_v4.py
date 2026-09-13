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
# Nota: el fragmento comienza con "Para" (mayúscula) en el v3 real, a
# diferencia de la minúscula asumida originalmente en el brief.
insertar_despues(
    'Para la base de conocimiento RAG se utilizará un subconjunto de documentos de '
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
    costo_electricidad_usd=('costo_electricidad_usd', 'mean'),
)
n_por_modelo = df.groupby('modelo').size()
n_muestra = int(n_por_modelo.iloc[0])
assert (n_por_modelo == n_muestra).all(), 'Cantidad de consultas por modelo distinta entre modelos'
# Nota: no se redondea `resumen` aquí. costo_oficial_usd/costo_electricidad_usd
# se muestran con 6 decimales (`:.6f`) más abajo; redondear a 4 decimales antes
# de formatear con 6 mostraría precisión falsa sobre un valor ya truncado. Cada
# campo se redondea únicamente al formatearse (":.4f", ":.2f", ":.6f").

texto_resultados = (
    f'Los resultados del baseline sin RAG, calculados sobre una muestra de '
    f'{n_muestra} consultas por modelo (muestra estratificada traducida al '
    'español), se presentan a continuación. GPT-4o mini alcanzó un '
    f"BERTScore F1 medio de {resumen.loc['gpt-4o-mini', 'bertscore_f1']:.4f}, con una "
    f"latencia media de {resumen.loc['gpt-4o-mini', 'latencia_s']:.2f} segundos y un "
    f"costo medio de USD {resumen.loc['gpt-4o-mini', 'costo_oficial_usd']:.6f} por "
    'consulta. LLaMA 3.1 8B, servido localmente mediante Ollama, obtuvo un BERTScore '
    f"F1 medio de {resumen.loc['llama-3.1-8b', 'bertscore_f1']:.4f}, con una latencia "
    f"media de {resumen.loc['llama-3.1-8b', 'latencia_s']:.2f} segundos y un costo de "
    f"instancia amortizada de USD {resumen.loc['llama-3.1-8b', 'costo_oficial_usd']:.6f} "
    'por consulta (frente a una cota inferior de USD '
    f"{resumen.loc['llama-3.1-8b', 'costo_electricidad_usd']:.6f} por electricidad). "
    'Mistral presentó un BERTScore F1 medio de '
    f"{resumen.loc['mistral', 'bertscore_f1']:.4f}, con una latencia media de "
    f"{resumen.loc['mistral', 'latencia_s']:.2f} segundos y un costo equivalente de "
    f"USD {resumen.loc['mistral', 'costo_oficial_usd']:.6f} por consulta (frente a una "
    f"cota inferior de USD {resumen.loc['mistral', 'costo_electricidad_usd']:.6f} por "
    'electricidad). Estos resultados corresponden exclusivamente a la condición sin '
    'RAG, que opera como línea base de control; la condición con RAG se incorpora en '
    'la siguiente etapa de este trabajo. Cabe aclarar que los parámetros de costo '
    'utilizados para estas estimaciones (consumo eléctrico del hardware, tarifa '
    'eléctrica y precio de instancia cloud) son valores provisionales, pendientes de '
    'reemplazo por una cotización real y citada; en consecuencia, la magnitud '
    'absoluta de las cifras en USD reportadas es provisoria, aunque la comparación '
    'relativa entre modelos se mantiene válida al calcularse con los mismos '
    'parámetros para los tres.'
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
