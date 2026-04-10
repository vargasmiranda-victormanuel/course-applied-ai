# tools.py — Herramientas disponibles para el agente ReAct
# Cada función es una "tool" que el agente puede decidir ejecutar

import os
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# HERRAMIENTA 1: Búsqueda web simulada
# ═══════════════════════════════════════════════════════════════

# Base de conocimiento simulada (reemplaza una API de búsqueda real)
_BASE_DE_CONOCIMIENTO = {
    "agentes ia": (
        "🤖 **Tendencias en Agentes de IA (2025-2026)**\n\n"
        "Los agentes de IA están evolucionando rápidamente:\n"
        "- **MCP (Model Context Protocol)**: Protocolo de Anthropic para conectar LLMs "
        "con herramientas y fuentes de datos externas. Se está convirtiendo en estándar.\n"
        "- **OpenAI Agents SDK**: Framework oficial de OpenAI para construir agentes "
        "con handoffs, guardrails y trazabilidad nativa.\n"
        "- **CrewAI**: Framework multi-agente donde agentes especializados colaboran "
        "como un equipo con roles definidos.\n"
        "- **Computer Use**: Capacidad de Claude (Anthropic) para controlar interfaces "
        "gráficas como un humano.\n"
        "- **Agentic Workflows**: Los LLMs toman decisiones en múltiples pasos, "
        "no solo responden preguntas.\n"
        "El mercado de agentes IA supera los $5B USD en 2026."
    ),
    "frameworks": (
        "🛠️ **Frameworks para Agentes de IA en 2026**\n\n"
        "- **LangChain**: El más popular, ofrece chains, agents y RAG. "
        "Gran ecosistema pero puede ser complejo.\n"
        "- **CrewAI**: Especializado en sistemas multi-agente con roles. "
        "Ideal para flujos de trabajo complejos.\n"
        "- **AutoGen (Microsoft)**: Framework para conversaciones multi-agente "
        "con soporte para código.\n"
        "- **LlamaIndex**: Enfocado en RAG e indexación de documentos. "
        "Excelente para búsqueda semántica.\n"
        "- **MCP (Model Context Protocol)**: Protocolo abierto para integrar "
        "herramientas con cualquier LLM compatible.\n"
        "- **OpenAI Swarm**: Framework experimental para orquestación ligera de agentes.\n"
        "Tendencia: migración hacia frameworks más ligeros y control directo de APIs."
    ),
    "patrones diseño": (
        "📐 **Patrones de Diseño para Agentes de IA**\n\n"
        "- **ReAct (Reason + Act)**: El agente razona, actúa con herramientas "
        "y observa resultados en un loop. Patrón fundamental.\n"
        "- **Plan-and-Execute**: El agente primero genera un plan completo, "
        "luego lo ejecuta paso a paso. Mejor para tareas largas.\n"
        "- **Multi-agente / Supervisor**: Un agente orquestador delega subtareas "
        "a agentes especializados. Escala bien.\n"
        "- **RAG (Retrieval-Augmented Generation)**: El agente recupera contexto "
        "relevante antes de responder. Reduce alucinaciones.\n"
        "- **Reflexion**: El agente evalúa y critica sus propias respuestas "
        "para mejorarlas iterativamente.\n"
        "- **Tool-use con Function Calling**: Patrón nativo de OpenAI donde "
        "el modelo decide qué funciones ejecutar."
    ),
    "openai": (
        "🔬 **OpenAI en 2026**\n\n"
        "- **GPT-4o**: Modelo multimodal rápido, soporta texto, imágenes y audio.\n"
        "- **o3/o4**: Modelos de razonamiento extendido con 'chain-of-thought' interno.\n"
        "- **Realtime API**: Conversaciones de voz en tiempo real con baja latencia.\n"
        "- **Assistants API v2**: Gestión de threads, archivos y herramientas integradas.\n"
        "- **Fine-tuning**: Disponible para GPT-4o con datos propios.\n"
        "Precio promedio: $2.50/1M tokens de entrada, $10/1M tokens de salida (GPT-4o)."
    ),
    "inteligencia artificial": (
        "🧠 **Estado del Arte en IA (2026)**\n\n"
        "- Los modelos de lenguaje superan benchmarks humanos en múltiples tareas.\n"
        "- La IA multimodal (texto + imagen + audio + video) se vuelve estándar.\n"
        "- Crecimiento explosivo en aplicaciones de IA agentica (autónoma).\n"
        "- Regulación: EU AI Act en vigor, EE.UU. con ejecutivas sectoriales.\n"
        "- Hardware: GPUs H100/H200 de NVIDIA dominan el entrenamiento.\n"
        "- Inversión global en IA supera $300B USD en 2025."
    ),
}


def buscar_web(query: str) -> str:
    """
    Simula una búsqueda web y retorna información relevante.
    En producción, esta función llamaría a una API real (Serper, Tavily, etc.)
    """
    print(f"🔍 Buscando en la web: '{query}'")

    query_lower = query.lower()

    # Buscar coincidencia parcial en las claves del diccionario
    for clave, respuesta in _BASE_DE_CONOCIMIENTO.items():
        if any(palabra in query_lower for palabra in clave.split()):
            return respuesta

    # Respuesta genérica si no hay coincidencia
    return (
        f"📄 Información general encontrada sobre '{query}':\n\n"
        "Se encontraron múltiples fuentes relevantes. Los expertos coinciden en que "
        "este tema está experimentando un crecimiento significativo en 2026. "
        "Las principales tendencias incluyen automatización, integración con IA "
        "y nuevos paradigmas de desarrollo. Se recomienda profundizar con búsquedas "
        "más específicas para obtener datos concretos."
    )


# ═══════════════════════════════════════════════════════════════
# HERRAMIENTA 2: Guardar notas en archivos Markdown
# ═══════════════════════════════════════════════════════════════

def guardar_nota(titulo: str, contenido: str) -> str:
    """
    Guarda una nota de investigación como archivo Markdown en la carpeta 'notas/'.
    """
    # Crear carpeta 'notas/' si no existe
    carpeta = "notas"
    os.makedirs(carpeta, exist_ok=True)

    # Generar nombre de archivo limpio (sin caracteres especiales)
    nombre_archivo = titulo.lower()
    nombre_archivo = nombre_archivo.replace(" ", "_")
    # Remover caracteres no permitidos en nombres de archivo
    caracteres_invalidos = r'\/:*?"<>|'
    for char in caracteres_invalidos:
        nombre_archivo = nombre_archivo.replace(char, "")
    nombre_archivo = f"{nombre_archivo}.md"

    ruta = os.path.join(carpeta, nombre_archivo)

    # Fecha actual para el encabezado del archivo
    fecha = datetime.now().strftime("%d de %B de %Y, %H:%M")

    # Contenido del archivo Markdown
    contenido_md = f"""# {titulo}

**Fecha de creación:** {fecha}
**Generado por:** Agente Investigador ReAct

---

{contenido}

---
*Nota generada automáticamente por el agente de IA.*
"""

    # Escribir el archivo
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido_md)

    print(f"💾 Nota guardada: {ruta}")
    return f"✅ Nota '{titulo}' guardada exitosamente en '{ruta}'"


# ═══════════════════════════════════════════════════════════════
# HERRAMIENTA 3: Fecha y hora actual
# ═══════════════════════════════════════════════════════════════

# Mapas para formatear la fecha en español
_MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

_DIAS_ES = {
    0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
    4: "viernes", 5: "sábado", 6: "domingo",
}


def fecha_actual() -> str:
    """
    Retorna la fecha y hora actual formateada en español.
    """
    ahora = datetime.now()
    dia_semana = _DIAS_ES[ahora.weekday()]
    mes = _MESES_ES[ahora.month]

    fecha_formateada = (
        f"{dia_semana.capitalize()}, {ahora.day} de {mes} de {ahora.year} "
        f"— {ahora.strftime('%H:%M:%S')}"
    )

    print(f"🗓️ Consultando fecha y hora actual")
    return fecha_formateada


# ═══════════════════════════════════════════════════════════════
# REGISTRO DE HERRAMIENTAS
# El agente usa este mapa para ejecutar la tool correcta por nombre
# ═══════════════════════════════════════════════════════════════

TOOLS_MAP = {
    "buscar_web": buscar_web,
    "guardar_nota": guardar_nota,
    "fecha_actual": fecha_actual,
}
