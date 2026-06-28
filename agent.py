from dotenv import load_dotenv
from groq import Groq
import os
from simple_memory import SimpleMemory
import json
from tools import Tools
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

MEMORY_MAX_MESSAGES = 10

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
memory = SimpleMemory(max_messages=MEMORY_MAX_MESSAGES)
now = datetime.now(ZoneInfo("America/Lima"))
SYSTEM_PROMPT = f"""
Eres un asistente que habla español y responde de manera muy breve y concisa.

Reglas:
- Antes de crear una reunión, SIEMPRE debes pedir confirmación explicita al usuario.
- Si el usuario no confirma, NO llames create_event.
- Sí el usuario te pide borrar un evento, SIEMPRE debes pedir confirmación explicita al usuario.
- Si el usuario no confirma, NO llames delete_event.
- Si el usuario te pide borrar un evento, PRIMERO debes listar los eventos con list_events debido a que este método retornara el event_id que es necesario para borrar el evento.

Fecha y hora actual:
{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC-5, Lima, Perú)
"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Revisa si el calendario del usuario está disponible entre time_ini y time_end "
                "usando Google Calendar. los datos time_ini y time_end DEBEN estar en el formato "
                "RFC3339 (con offset para la zona horaria). Por ejemplo: "
                "2026-06-20T08:00:00-05:00"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_ini": {
                        "type": "string",
                        "description": "la fecha de inicio para revisar disponibilidad en formato RFC3339"
                    },
                    "time_end": {
                        "type": "string",
                        "description": "la fecha fin para revisar disponibilidad en formato RFC3339"
                    }
                },
                "required": ["time_ini", "time_end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": (
                "Crea un evento en el calendario del usuario usando Google Calendar. "
                "start y end DEBEN estar en el formato RFC3339 (con offset para la zona horaria). "
                "Por ejemplo: 2026-06-20T08:00:00-05:00"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "el título del evento"
                    },
                    "description": {
                        "type": "string",
                        "description": "la descripción del evento (opcional)"
                    },
                    "start": {
                        "type": "string",
                        "description": "la fecha y hora de inicio del evento en formato RFC3339"
                    },
                    "end": {
                        "type": "string",
                        "description": "la fecha y hora de fin del evento en formato RFC3339"
                    }
                }
            },
            "required": ["summary", "start", "end"]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": (
                "Lista los eventos del calendario del usuario entre time_ini y time_end "
                "usando Google Calendar. Los datos time_ini y time_end DEBEN estar en el formato "
                "RFC3339 (con offset para la zona horaria). Por ejemplo: "
                "2026-06-20T08:00:00-05:00"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_ini": {
                        "type": "string",
                        "description": "la fecha de inicio para revisar disponibilidad en formato RFC3339"
                    },
                    "time_end": {
                        "type": "string",
                        "description": "la fecha fin para revisar disponibilidad en formato RFC3339"
                    }
                },
                "required": ["time_ini", "time_end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": (
                "Elimina un evento del calendario del usuario usando Google Calendar. "
                "Se requiere el event_id del evento a eliminar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "el ID del evento a eliminar"
                    }
                },
                "required": ["event_id"]
            }
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

            if name == "check_availability":
                tools = Tools()
                result = tools.check_availability(
                    time_ini=args["time_ini"],
                    time_end=args["time_end"]
                )
            elif name == "create_event":
                tools = Tools()
                result = tools.create_event(
                    summary=args["summary"],
                    start=args["start"],
                    end=args["end"],
                    description=args.get("description", "")
                )
            elif name == "list_events":
                tools = Tools()
                result = tools.list_events(
                    time_ini=args["time_ini"],
                    time_end=args["time_end"]
                )
            elif name == "delete_event":
                tools = Tools()
                result = tools.delete_event(
                    event_id=args["event_id"]
                )
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