# 🎓 Prompts para Crear los Agentes con IA

## Instrucciones para los estudiantes

Copien **UN** prompt en su herramienta de IA favorita (GitHub Copilot, ChatGPT, Claude, Cursor)
y la IA les generará el proyecto completo.

**Antes de empezar**, preparen el entorno:

```bash
mkdir practica-agente
cd practica-agente
python3 -m venv .venv
source .venv/bin/activate
pip install openai langchain langchain-openai python-dotenv
```

Creen un archivo `.env` con su API key:
```
OPENAI_API_KEY=sk-tu-api-key-aqui
```

---

## 🤖 PROMPT A — Agente desde Cero (sin frameworks)

> Copien todo el bloque y péguenlo en la IA.

```
Creame un proyecto completo en Python de un agente investigador de IA usando
SOLO la API de OpenAI (sin frameworks como LangChain). El agente debe implementar
el patrón ReAct (Reason → Act → Observe → Repeat) desde cero.

El proyecto debe tener estos archivos, todos en la misma carpeta:

═══ ARCHIVO 1: config.py ═══
- Usa python-dotenv para cargar OPENAI_API_KEY desde un archivo .env
- Crea un cliente de OpenAI (from openai import OpenAI)
- Define MODEL = "gpt-4o"
- Si se ejecuta directamente, verifica la conexión con una llamada simple

═══ ARCHIVO 2: tools.py ═══
Crea 3 herramientas (funciones Python normales):

1. buscar_web(query: str) -> str
   - SIMULA búsqueda web (no necesita API real, usa un diccionario interno)
   - Tiene respuestas simuladas para: "agentes ia" (habla de MCP, OpenAI Agents SDK,
     CrewAI, Computer Use), "frameworks" (LangChain, CrewAI, AutoGen, LlamaIndex, MCP),
     "patrones diseño" (ReAct, Plan-and-Execute, Multi-agente, RAG)
   - Si la query coincide parcialmente con alguna clave, retorna esa respuesta
   - Si no, retorna "Información general encontrada sobre el tema"
   - Imprime 🔍 con la query

2. guardar_nota(titulo: str, contenido: str) -> str
   - Crea carpeta "notas/" si no existe
   - Guarda un archivo .md con título, fecha, contenido
   - Retorna confirmación con la ruta

3. fecha_actual() -> str
   - Retorna fecha y hora actual formateada en español

Al final crea: TOOLS_MAP = {"buscar_web": buscar_web, "guardar_nota": guardar_nota, "fecha_actual": fecha_actual}

═══ ARCHIVO 3: schemas.py ═══
Una lista tools_schema con el formato JSON Schema de OpenAI para function calling.
Cada tool: {"type": "function", "function": {"name", "description", "parameters": {"type": "object", "properties": {...}, "required": [...]}}}
- buscar_web: recibe query (string, requerido)
- guardar_nota: recibe titulo y contenido (strings, requeridos)
- fecha_actual: no recibe parámetros (properties vacío, required vacío)
Las descripciones deben ser detalladas porque el LLM las lee para decidir cuándo usar cada tool.

═══ ARCHIVO 4: agent.py ═══
El corazón del agente — implementa el loop ReAct:

- Importa client, MODEL de config.py; TOOLS_MAP de tools.py; tools_schema de schemas.py
- Define un SYSTEM_PROMPT que diga al agente que es un investigador experto:
  planifica → usa fecha_actual → busca con buscar_web (mínimo 2 búsquedas) →
  sintetiza → guarda reporte con guardar_nota → responde en español con markdown
- Función execute_tool(tool_name, arguments): busca en TOOLS_MAP, ejecuta con **arguments, retorna resultado
- Función principal run_agent(user_message, verbose=True):
  • Inicializa messages con system prompt + user message
  • Loop de máximo 10 iteraciones
  • Llama a client.chat.completions.create(model=MODEL, messages=messages, tools=tools_schema)
  • Si finish_reason == "stop" → retorna response.content (terminó)
  • Si finish_reason == "tool_calls" → para cada tool_call:
    - Extrae nombre y argumentos con json.loads(tool_call.function.arguments)
    - Ejecuta con execute_tool
    - Agrega el message del assistant y el resultado del tool a messages
    - Continúa el loop
  • Si verbose=True, imprime cada iteración con emojis

═══ ARCHIVO 5: main.py ═══
- Importa run_agent desde agent.py
- demo(): ejecuta con pregunta predefinida "Investiga las tendencias en agentes de IA para 2026"
- chat_interactivo(): loop pidiendo input, escribe "salir" para terminar
- if __name__ == "__main__": si recibe --chat ejecuta chat_interactivo(), sino demo()

═══ ARCHIVO 6: .env.example ═══
OPENAI_API_KEY=sk-tu-api-key-aqui

═══ ARCHIVO 7: requirements.txt ═══
openai
python-dotenv

═══ EJECUCIÓN ═══
python config.py        → Verificar conexión
python main.py          → Demo
python main.py --chat   → Modo interactivo

Dame el código completo de cada archivo, bien comentado en español, con emojis en los prints.
```

---

## 🦜 PROMPT B — Agente con LangChain

> Copien todo el bloque y péguenlo en la IA.

```
Creame un agente investigador de IA en Python usando LangChain 1.x en un solo archivo.

Usa la API nueva de LangChain 1.x (NO uses la API vieja de create_tool_calling_agent ni AgentExecutor,
esas ya no existen). La API correcta es:

  from langchain.agents import create_agent
  from langchain_core.tools import tool

El archivo se llama agent_langchain.py y debe tener todo:

═══ TOOLS ═══
Define 3 tools usando el decorador @tool de LangChain.
Los docstrings son CRUCIALES porque LangChain los usa como descripción para el LLM:

1. @tool
   def buscar_web(query: str) -> str:
   """Busca información actualizada en internet..."""
   - SIMULA búsqueda web con un diccionario interno
   - Tiene respuestas para: "agentes ia" (MCP, OpenAI Agents SDK, CrewAI, Computer Use),
     "frameworks" (LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, MCP)
   - Si coincide parcialmente, retorna esa respuesta. Si no, respuesta genérica.
   - Imprime 🔍

2. @tool
   def guardar_nota(titulo: str, contenido: str) -> str:
   """Guarda una nota de investigación en markdown..."""
   - Crea carpeta notas/ y guarda archivo .md
   - Imprime 📝

3. @tool
   def fecha_actual() -> str:
   """Retorna la fecha y hora actual..."""
   - Imprime 📅

═══ SYSTEM PROMPT ═══
Un string SYSTEM_PROMPT que indique: eres investigador experto, planifica,
usa fecha_actual, busca con buscar_web, sintetiza, guarda con guardar_nota,
responde en español con markdown.

═══ CREAR AGENTE ═══
agent = create_agent(
    model="openai:gpt-4o",
    tools=[buscar_web, guardar_nota, fecha_actual],
    system_prompt=SYSTEM_PROMPT,
)

═══ EJECUTAR ═══
En if __name__ == "__main__":
- Usa python-dotenv para cargar .env con OPENAI_API_KEY
- Define pregunta: "Investiga las tendencias en agentes de IA para 2026..."
- Ejecuta: result = agent.invoke({"messages": [{"role": "user", "content": pregunta}]})
- Respuesta: result["messages"][-1].content
- Muestra con formato bonito (emojis, líneas separadoras)

═══ DEPENDENCIAS ═══
openai, langchain, langchain-openai, python-dotenv

Dame el código completo, bien comentado en español, con emojis en los prints.
```

---

## ▶️ Cómo Ejecutar

```bash
# Agente desde cero
python config.py          # Verificar conexión
python main.py            # Demo automática
python main.py --chat     # Chat interactivo

# Agente LangChain
python agent_langchain.py
```

---

## 💡 Tips

- Si algo no funciona, peguen el error en el chat de IA y pidan que lo corrija
- Modifiquen el SYSTEM_PROMPT para cambiar la personalidad del agente
- Agreguen más tools (calculadora, traductor, generador de código...)
- Comparen ambas versiones: ¿cuál es más fácil? ¿cuál da más control?