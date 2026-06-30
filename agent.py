from dotenv import load_dotenv
from groq import Groq
import os
from gemini_embedder import GeminiEmbedder
from simple_memory import SimpleMemory
import json
from supabase_doc_store import SupabaseDocStore
from tools import Tools
from datetime import datetime
from zoneinfo import ZoneInfo
from long_term_memory import LongTermMemory

load_dotenv()

MEMORY_MAX_MESSAGES = 10

api_key = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=api_key)
memory = SimpleMemory(max_messages=MEMORY_MAX_MESSAGES)
now = datetime.now(ZoneInfo("America/Lima"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

embedder = GeminiEmbedder(api_key=GEMINI_API_KEY)
store = SupabaseDocStore(database_url=DATABASE_URL)


SYSTEM_PROMPT = f"""
# ROL
Eres un agente de servicio al cliente del área de devoluciones.

Los usuarios te contactarán con dudas relacionadas a las devoluciones.
Para cualquier consulta relacionada a devoluciones de todo tipo,
debes consultar la información actualizada utilizando
la herramienta "politicas_de_devoluciones"

# HERRAMIENTAS
## politicas_de_devoluciones
Esta herramienta debes llamarla siempre que el usuario desee saber algo
relacionado a las devoluciones. Si no está claro según la pregunta,
entonces también utiliza la herramienta.

# REGLAS
- No debes inventar información de ningún tipo. Solo utiliza lo que se te
proporciona como parte de la herramienta.
- Puedes ser amigable pero eres del área de devoluciones, por lo que sé servicial
pero no intentes ayudar más allá de dar la información explícita que te solicitan,
basado en la información de las políticas de devoluciones en la herramienta.

"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "politicas_de_devoluciones",
            "description": (
                "Obtiene información importante y actualizada acerca de las Políticas de Devoluciones"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La pregunta del usuario"
                    }
                }
            },
            "required": ["query"]
        }
    }
]

print("Agente de IA")

def process_response(client:Groq, memory_messages:list[dict], user_text:str):
    
    # Obtener la memoria
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory_messages)
    messages.append({"role": "user", "content": user_text})

    while True:
        resp = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=messages,
            tools=TOOLS
        )

        msg = resp.choices[0].message

        # Si no hay llamadas a tools, entonces regresamos las respuestas
        if not getattr(msg, "tool_calls", None):
            return msg.content or ""
        
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or {})

            if name == "politicas_de_devoluciones":
                query = args["query"]
                print(f"Llamando función politicas_de_devoluciones con {query}")
                emb = embedder.embed_query(query)
                hits = store.search(query_emb=emb)

                result = {
                    "query": query,
                    "matches": hits
                }
            else:
                print(f"Se intentó llamar a una tool desconocida {name}")
                result = {"error": f"Herramienta desconocida: {name}" }

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

while True:

    user_text = input("Tú: ").strip()
    if not user_text:
        continue

    if user_text.lower() in ("exit", "salir"):
        print("See you!")
        break
    
    assistant_text = process_response(client, memory.messages(), user_text)
    print(f"Asistente: {assistant_text}") 

    # Actualizar memoria
    memory.add("user", user_text)
    memory.add("assistant", assistant_text)