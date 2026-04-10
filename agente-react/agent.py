# agent.py — Corazón del agente: implementa el loop ReAct desde cero
#
# Patrón ReAct:
#   1. REASON  → El LLM razona sobre qué hacer
#   2. ACT     → Decide y llama una herramienta (tool_call)
#   3. OBSERVE → Recibe el resultado de la herramienta
#   4. REPEAT  → Repite hasta tener suficiente información para responder

import json

from config import client, MODEL
from tools import TOOLS_MAP
from schemas import tools_schema


# ═══════════════════════════════════════════════════════════════
# SYSTEM PROMPT — Instrucciones de comportamiento del agente
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Eres un agente investigador experto en inteligencia artificial y tecnología.
Tu misión es investigar temas en profundidad y producir reportes completos y bien fundamentados.

## Tu flujo de trabajo obligatorio:

1. **Planifica** mentalmente los pasos necesarios antes de actuar.
2. **Consulta la fecha** usando `fecha_actual` para contextualizar tu investigación.
3. **Investiga exhaustivamente** usando `buscar_web` con al menos 2 queries diferentes
   para obtener perspectivas complementarias sobre el tema.
4. **Sintetiza** la información recopilada de forma coherente y estructurada.
5. **Guarda un reporte** usando `guardar_nota` con título descriptivo y contenido
   completo en Markdown.
6. **Responde al usuario** con un resumen ejecutivo en español, usando formato Markdown
   con encabezados, listas y negritas para mejorar la legibilidad.

## Reglas importantes:
- Siempre responde en **español**.
- Usa formato **Markdown** en tu respuesta final.
- Haz **mínimo 2 búsquedas** antes de sintetizar.
- El reporte guardado debe ser **completo y detallado**.
- Si el usuario hace una pregunta simple (no requiere investigación), responde directamente
  sin usar herramientas innecesarias.
"""


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN: execute_tool
# Despacha la llamada a la herramienta correcta
# ═══════════════════════════════════════════════════════════════

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Busca la función en TOOLS_MAP y la ejecuta con los argumentos dados.
    Retorna el resultado como string para enviarlo de vuelta al LLM.
    """
    if tool_name not in TOOLS_MAP:
        return f"❌ Error: La herramienta '{tool_name}' no existe. Herramientas disponibles: {list(TOOLS_MAP.keys())}"

    funcion = TOOLS_MAP[tool_name]

    try:
        resultado = funcion(**arguments)
        return str(resultado)
    except TypeError as e:
        return f"❌ Error de argumentos al llamar '{tool_name}': {e}"
    except Exception as e:
        return f"❌ Error inesperado en '{tool_name}': {e}"


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL: run_agent
# Implementa el loop ReAct completo
# ═══════════════════════════════════════════════════════════════

def run_agent(user_message: str, verbose: bool = True) -> str:
    """
    Ejecuta el agente con el mensaje del usuario.
    Implementa elLoop ReAct: Reason → Act → Observe → Repeat

    Args:
        user_message: La pregunta o tarea del usuario.
        verbose: Si True, imprime el progreso en cada iteración.

    Returns:
        La respuesta final del agente como string.
    """
    if verbose:
        print("\n" + "═" * 60)
        print("🤖 AGENTE INVESTIGADOR ReAct — Iniciando")
        print("═" * 60)
        print(f"📝 Tarea: {user_message}")
        print("═" * 60 + "\n")

    # ── Inicializar historial de mensajes ──────────────────────
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    MAX_ITERACIONES = 10
    iteracion = 0

    # ── Loop ReAct ─────────────────────────────────────────────
    while iteracion < MAX_ITERACIONES:
        iteracion += 1

        if verbose:
            print(f"🔄 Iteración {iteracion}/{MAX_ITERACIONES} — Consultando al modelo...")

        # ── REASON: El modelo razona y decide qué hacer ────────
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools_schema,
            # tool_choice="auto" es el default: el modelo decide si usar tools o no
        )

        choice = response.choices[0]
        finish_reason = choice.finish_reason
        assistant_message = choice.message

        if verbose:
            print(f"💭 finish_reason: {finish_reason}")

        # ── STOP: El modelo tiene suficiente información ───────
        # Ya no necesita más herramientas → retorna la respuesta final
        if finish_reason == "stop":
            respuesta_final = assistant_message.content or ""
            if verbose:
                print("\n" + "═" * 60)
                print("✅ Agente completó la investigación")
                print("═" * 60)
            return respuesta_final

        # ── ACT: El modelo quiere ejecutar herramientas ────────
        if finish_reason == "tool_calls":
            tool_calls = assistant_message.tool_calls

            # Agregar el mensaje del assistant (con sus tool_calls) al historial
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,  # puede ser None
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })

            # ── OBSERVE: Ejecutar cada tool y guardar resultado ─
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments

                if verbose:
                    print(f"\n⚡ Ejecutando tool: '{tool_name}'")
                    print(f"   Argumentos: {tool_args_str}")

                # Parsear argumentos JSON
                try:
                    arguments = json.loads(tool_args_str)
                except json.JSONDecodeError:
                    arguments = {}

                # Ejecutar la herramienta
                resultado = execute_tool(tool_name, arguments)

                if verbose:
                    # Mostrar solo las primeras 200 chars del resultado para no saturar
                    preview = resultado[:200] + "..." if len(resultado) > 200 else resultado
                    print(f"   📤 Resultado: {preview}\n")

                # Agregar el resultado de la tool al historial (rol "tool")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": resultado,
                })

            # Continuar el loop → el modelo procesa los resultados (REPEAT)
            continue

        # ── Caso inesperado: finish_reason desconocido ─────────
        if verbose:
            print(f"⚠️  finish_reason inesperado: '{finish_reason}'. Deteniendo.")
        break

    # Si se agotaron las iteraciones sin respuesta final
    if verbose:
        print(f"⚠️  Se alcanzó el límite de {MAX_ITERACIONES} iteraciones.")

    return "⚠️ El agente alcanzó el límite máximo de iteraciones sin completar la tarea."
