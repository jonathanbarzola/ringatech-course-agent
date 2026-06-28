# ringatech-course-agent

Agente de IA para interactuar con Google Calendar mediante herramientas del modelo.

## Funcionalidades
- Revisar disponibilidad del calendario.
- Crear eventos en Google Calendar.
- Mantener una memoria simple de la conversación.

## Requisitos
- Python 3.11+
- Dependencias del proyecto instaladas en un entorno virtual.

## Ejecución
1. Crear y activar un entorno virtual:
   ```bash
   python -m venv env
   .\env\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar el agente:
   ```bash
   python agent.py
   ```

## Archivos importantes
- `agent.py`: lógica principal del agente y llamadas al modelo.
- `tools.py`: integración con Google Calendar.
- `simple_memory.py`: memoria simple de mensajes.
- `.gitignore`: archivos que no deben subirse a Git.
