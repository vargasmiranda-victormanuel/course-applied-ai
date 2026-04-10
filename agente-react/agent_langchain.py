# agent_langchain.py — Agente investigador de IA usando LangChain/LangGraph (API moderna)
#
# ⚠️  Nota sobre la API:
#   - La API antigua (create_tool_calling_agent + AgentExecutor) fue deprecada.
#   - `from langchain.agents import create_agent` NO existe en ninguna versión publicada.
#   - La API moderna CORRECTA es `create_react_agent` de `langgraph.prebuilt`, que
#     reemplaza por completo al stack anterior con una sintaxis más limpia.
#
# Dependencias:
#   pip install langchain langchain-openai langgraph python-dotenv

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# ── API moderna de LangGraph ──────────────────────────────────────────────────
# create_react_agent es el reemplazo oficial de AgentExecutor + create_tool_calling_agent
from langgraph.prebuilt import create_react_agent

# Decorador @tool: convierte una función Python en una herramienta para el LLM
# El docstring es CRUCIAL: LangChain lo envía al LLM como descripción de la tool
from langchain_core.tools import tool


# ═══════════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS DEL AGENTE
# Cada herramienta tiene un docstring detallado que el LLM usa para entender
# cuándo y cómo llamar a cada función.
# ═══════════════════════════════════════════════════════════════════════════════

# Base de conocimiento interna (simula respuestas de búsqueda web)
_BASE_DE_CONOCIMIENTO = {
    "agentes ia": (
        "🤖 **Tendencias en Agentes de IA (2025-2026)**\n\n"
        "Los agentes de IA están evolucionando rápidamente:\n"
        "- **MCP (Model Context Protocol)**: Protocolo de Anthropic para conectar LLMs "
        "con herramientas y fuentes de datos externas. Se está convirtiendo en estándar de la industria.\n"
        "- **OpenAI Agents SDK**: Framework oficial de OpenAI para construir agentes "
        "con handoffs, guardrails y trazabilidad nativa.\n"
        "- **CrewAI**: Framework multi-agente donde agentes especializados colaboran "
        "como un equipo con roles, tareas y objetivos definidos.\n"
        "- **Computer Use**: Capacidad de Claude (Anthropic) para controlar interfaces "
        "gráficas de usuario como lo haría un humano.\n"
        "- **Agentic Workflows**: Los LLMs toman decisiones en múltiples pasos autónomos, "
        "no solo responden preguntas en una sola ronda.\n"
        "El mercado de agentes IA supera los $5B USD en 2026."
    ),
    "frameworks": (
        "🛠️ **Frameworks para Agentes de IA en 2026**\n\n"
        "- **LangChain / LangGraph**: El ecosistema más popular; LangGraph agrega "
        "flujos de trabajo stateful con grafos para agentes complejos.\n"
        "- **CrewAI**: Especializado en sistemas multi-agente con roles. "
        "Ideal para pipelines de trabajo colaborativo.\n"
        "- **AutoGen (Microsoft)**: Framework para conversaciones multi-agente "
        "con soporte nativo para ejecución de código.\n"
        "- **LlamaIndex**: Enfocado en RAG e indexación de documentos. "
        "Excelente para búsqueda semántica sobre datos propios.\n"
        "- **MCP (Model Context Protocol)**: Protocolo abierto para integrar "
        "herramientas externas con cualquier LLM compatible.\n"
        "- Tendencia 2026: frameworks convergiendo hacia interfaces de grafos y MCP."
    ),
}


@tool
def buscar_web(query: str) -> str:
    """Busca información actualizada en internet sobre un tema específico de IA o tecnología.

    Útil cuando necesitas investigar tendencias, comparar frameworks, conocer herramientas
    emergentes o encontrar datos sobre el ecosistema de inteligencia artificial.
    Retorna un resumen con los resultados más relevantes encontrados en la web.
    """
    print(f"🔍 Buscando en web: '{query}'")

    query_lower = query.lower()

    # Búsqueda por coincidencia parcial en la base de conocimiento
    for clave, respuesta in _BASE_DE_CONOCIMIENTO.items():
        # Coincide si la clave está en la query O si alguna palabra de la clave está en la query
        palabras_clave = clave.split()
        if clave in query_lower or any(p in query_lower for p in palabras_clave):
            print(f"   ✅ Resultado encontrado para clave: '{clave}'")
            return respuesta

    # Respuesta genérica si no hay coincidencia con la base de conocimiento
    return (
        f"📰 Resultados de búsqueda para '{query}':\n\n"
        f"No se encontró información específica en la base de conocimiento local para este tema. "
        f"El área de consulta '{query}' es relevante en el contexto de IA y tecnología emergente. "
        f"Para información más detallada y actualizada se recomienda consultar:\n"
        f"- arxiv.org (artículos académicos)\n"
        f"- papers.ai (resúmenes de papers)\n"
        f"- Blogs oficiales de Anthropic, OpenAI y Google DeepMind"
    )


@tool
def guardar_nota(titulo: str, contenido: str) -> str:
    """Guarda una nota de investigación en formato Markdown en el sistema de archivos local.

    Útil para persistir hallazgos importantes, resúmenes de investigación y reportes finales.
    El título se convierte en nombre de archivo y el contenido se escribe como cuerpo Markdown.
    Siempre guarda en la carpeta 'notas/' relativa al directorio de trabajo actual.
    """
    print(f"📝 Guardando nota: '{titulo}'")

    # Crear carpeta notas/ si no existe
    carpeta_notas = Path("notas")
    carpeta_notas.mkdir(exist_ok=True)

    # Construir nombre de archivo seguro (sin caracteres especiales ni espacios)
    nombre_seguro = titulo.lower().replace(" ", "_").replace("/", "-").replace("\\", "-")
    nombre_seguro = "".join(c for c in nombre_seguro if c.isalnum() or c in "_-")
    ruta_archivo = carpeta_notas / f"{nombre_seguro}.md"

    # Agregar cabecera con metadatos al documento
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    documento = f"# {titulo}\n\n*Generado automáticamente el {timestamp}*\n\n---\n\n{contenido}"

    ruta_archivo.write_text(documento, encoding="utf-8")
    print(f"   ✅ Archivo guardado en: {ruta_archivo}")

    return f"✅ Nota guardada exitosamente en: {ruta_archivo}"


@tool
def fecha_actual() -> str:
    """Retorna la fecha y hora actual del sistema operativo.

    Útil para contextualizar reportes e investigaciones con la fecha correcta,
    o para determinar qué información puede considerarse 'actual' o 'reciente'.
    """
    print("📅 Consultando fecha actual...")

    ahora = datetime.now()
    # Formato legible en español
    fecha_formateada = ahora.strftime("%A %d de %B de %Y, %H:%M:%S")
    return f"Fecha y hora actual del sistema: {fecha_formateada}"


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# Define el comportamiento, rol y flujo de trabajo del agente
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Eres un investigador experto en inteligencia artificial y tecnología de vanguardia.
Tu misión es producir reportes exhaustivos, bien fundamentados y claramente estructurados.

## Flujo de trabajo obligatorio:

1. **Planifica**: Antes de actuar, identifica mentalmente qué información necesitas reunir.
2. **Fecha**: Usa `fecha_actual` para contextualizar tu investigación con la fecha correcta.
3. **Investiga**: Usa `buscar_web` con al menos 2 queries diferentes para obtener perspectivas
   complementarias. No te limites a una sola búsqueda.
4. **Sintetiza**: Analiza la información recopilada, busca patrones y saca conclusiones propias.
5. **Guarda**: Usa `guardar_nota` para persistir el reporte completo con un título descriptivo.
6. **Responde**: Presenta un resumen ejecutivo claro al usuario.

## Estilo de respuesta:
- Siempre en **español**.
- Formato **Markdown** con encabezados (##), listas (-) y negritas (**texto**).
- Incluye conclusiones y recomendaciones prácticas.
- El reporte guardado debe ser completo y detallado; el resumen al usuario puede ser más conciso.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# CREAR EL AGENTE
# create_react_agent de LangGraph implementa el loop Reason-Act-Observe
# internamente, sin necesidad de AgentExecutor ni bucles manuales.
# ═══════════════════════════════════════════════════════════════════════════════

# El string "openai:gpt-4o" usa init_chat_model internamente (requiere langchain-openai)
agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[buscar_web, guardar_nota, fecha_actual],
    prompt=SYSTEM_PROMPT,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Cargar OPENAI_API_KEY desde archivo .env
    load_dotenv()

    # Validar que la API key está presente antes de invocar el agente
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: No se encontró OPENAI_API_KEY.")
        print("💡 Crea un archivo .env en este directorio con:")
        print("   OPENAI_API_KEY=sk-...")
        raise SystemExit(1)

    print("=" * 62)
    print("🤖  AGENTE INVESTIGADOR DE IA  —  LangChain + LangGraph")
    print("=" * 62)
    print("⚙️  Agente inicializado con modelo: gpt-4o")
    print(f"🛠️  Herramientas: buscar_web | guardar_nota | fecha_actual")

    # Pregunta de investigación que se enviará al agente
    pregunta = (
        "Investiga las tendencias en agentes de IA para 2026. "
        "Incluye los principales frameworks, herramientas emergentes y casos de uso. "
        "Guarda un reporte completo con tus hallazgos."
    )

    print(f"\n❓ Pregunta:\n   {pregunta}")
    print("\n" + "─" * 62)
    print("🔄 Ejecutando investigación...\n")

    # Invocar el agente con el formato de mensajes estándar de LangChain
    # El agente ejecuta el loop ReAct internamente hasta completar la tarea
    resultado = agent.invoke({
        "messages": [{"role": "user", "content": pregunta}]
    })

    # El último mensaje en la lista es siempre la respuesta final del LLM
    respuesta_final = resultado["messages"][-1].content

    # Mostrar resultado con formato visual claro
    print("\n" + "=" * 62)
    print("📊  RESULTADO DE LA INVESTIGACIÓN")
    print("=" * 62)
    print(respuesta_final)
    print("=" * 62)
    print("✅  ¡Investigación completada con éxito!")
