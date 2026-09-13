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
