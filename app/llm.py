# Este archivo centralizará las llamadas a Ollama. Así evitamos repetir la conexión en cada agente.


import os
import re

import httpx


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:4b",
)


def generate_response(
    system_prompt: str,
    user_message: str,
    response_format=None,
) -> str:

    # 1. Preparamos la solicitud para Ollama.
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0},
    }

    # 2. Si necesitamos una respuesta JSON,
    # agregamos su formato.
    if response_format is not None:
        payload["format"] = response_format

    # 3. Enviamos la solicitud a Ollama.
    with httpx.Client(
    timeout=httpx.Timeout(
        connect=10.0,
        read=180.0,
        write=30.0,
        pool=10.0,
    )
) as client:
        response = client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
        )

        response.raise_for_status()

    # 4. Extraemos el contenido de la respuesta.
    data = response.json()
    message = data["message"]
    content = message.get("content", "")

    # 5. Eliminamos bloques completos <think>.
    content = re.sub(
        r"<think>.*?</think>",
        "",
        content,
        flags=re.DOTALL,
    )

    # 6. Si solo aparece la etiqueta de cierre,
    # conservamos el texto posterior.
    if "</think>" in content:
        content = content.rsplit("</think>", 1)[-1]

    # 7. Devolvemos únicamente la respuesta final.
    return content.strip()
