"""Traduce el corpus RAG al español con GPT-4o mini y guarda progreso.

Este script realiza llamadas pagas. Reanuda desde el CSV de salida si una
ejecución se interrumpe y registra tokens y costo real en un JSON de auditoría.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


PROYECTO = Path(__file__).resolve().parents[1]
MODELO_TRADUCCION = "gpt-4o-mini-2024-07-18"
PRECIO_ENTRADA_MILLON = 0.15
PRECIO_SALIDA_MILLON = 0.60
PROMPT = (
    "Traducí al español rioplatense neutro la pregunta y la respuesta de "
    "soporte. Conservá sin cambios los marcadores entre llaves dobles, el "
    "sentido, los pasos y el tono. Respondé solamente un objeto JSON con las "
    "claves instruction_es y response_es."
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entrada",
        type=Path,
        default=PROYECTO / "data" / "conocimiento_rag.csv",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=PROYECTO / "data" / "conocimiento_rag_es.csv",
    )
    return parser.parse_args()


def _costo(tokens_in: int, tokens_out: int) -> float:
    return (
        tokens_in / 1_000_000 * PRECIO_ENTRADA_MILLON
        + tokens_out / 1_000_000 * PRECIO_SALIDA_MILLON
    )


def main():
    args = parse_args()
    load_dotenv(PROYECTO / ".env")
    cliente = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    if args.salida.exists():
        corpus = pd.read_csv(args.salida)
    else:
        corpus = pd.read_csv(args.entrada)
        corpus["instruction_es"] = pd.NA
        corpus["response_es"] = pd.NA
        corpus["tokens_traduccion_in"] = 0
        corpus["tokens_traduccion_out"] = 0

    pendientes = corpus["instruction_es"].isna() | corpus["response_es"].isna()
    for posicion, indice in enumerate(corpus.index[pendientes], start=1):
        fila = corpus.loc[indice]
        contenido = json.dumps(
            {
                "instruction": fila["instruction"],
                "response": fila["response"],
            },
            ensure_ascii=False,
        )
        respuesta = cliente.chat.completions.create(
            model=MODELO_TRADUCCION,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": contenido},
            ],
            temperature=0.0,
            max_tokens=1200,
            response_format={"type": "json_object"},
        )
        traduccion = json.loads(respuesta.choices[0].message.content)
        corpus.at[indice, "instruction_es"] = traduccion["instruction_es"]
        corpus.at[indice, "response_es"] = traduccion["response_es"]
        corpus.at[indice, "tokens_traduccion_in"] = respuesta.usage.prompt_tokens
        corpus.at[indice, "tokens_traduccion_out"] = respuesta.usage.completion_tokens
        corpus.at[indice, "texto_rag"] = (
            f"Categoría: {fila['category']}\n"
            f"Intención: {fila['intent']}\n"
            f"Pregunta frecuente: {traduccion['instruction_es']}\n"
            f"Procedimiento recomendado: {traduccion['response_es']}"
        )
        corpus.to_csv(args.salida, index=False)
        print(f"Traducido {posicion}/{int(pendientes.sum())}: {fila['document_id']}")
        time.sleep(0.1)

    tokens_in = int(corpus["tokens_traduccion_in"].sum())
    tokens_out = int(corpus["tokens_traduccion_out"].sum())
    auditoria = {
        "modelo": MODELO_TRADUCCION,
        "documentos": len(corpus),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "precio_entrada_usd_por_millon": PRECIO_ENTRADA_MILLON,
        "precio_salida_usd_por_millon": PRECIO_SALIDA_MILLON,
        "costo_total_usd": round(_costo(tokens_in, tokens_out), 6),
    }
    args.salida.with_name(f"{args.salida.stem}_auditoria.json").write_text(
        json.dumps(auditoria, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(auditoria, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
