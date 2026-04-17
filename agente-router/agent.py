# agent.py — Sistema multiagente con patrón Router usando LangGraph
#
# ARQUITECTURA:
#   cliente → [clasificador] → router → [ventas | tecnico | facturacion] → END
#
#   El nodo "clasificador" usa un LLM para detectar la intención del mensaje.
#   La función router() dirige el flujo al agente especializado correspondiente.
#   Cada agente especializado genera una respuesta con tono y contexto propios.
#
# Dependencias:
#   pip install langchain langchain-openai langgraph python-dotenv

import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────

# Cargar variables de entorno desde el archivo .env (debe contener OPENAI_API_KEY)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ ERROR: No se encontró OPENAI_API_KEY en las variables de entorno.")
    print("   Crea un archivo .env con: OPENAI_API_KEY=sk-...")
    sys.exit(1)

# Inicializar el LLM compartido (gpt-4o-mini: rápido y económico)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ═══════════════════════════════════════════════════════════════════════════════
# DEFINICIÓN DEL STATE
# TypedDict define los campos que el grafo transporta entre nodos.
# Cada nodo recibe el state completo y retorna solo los campos que modifica.
# ═══════════════════════════════════════════════════════════════════════════════

class State(TypedDict):
    message: str   # mensaje original del cliente
    category: str  # categoría detectada: "ventas" | "tecnico" | "facturacion"
    response: str  # respuesta final generada por el agente especializado


# ═══════════════════════════════════════════════════════════════════════════════
# NODO 1: CLASIFICADOR
# Analiza el mensaje del cliente y determina su categoría de intención.
# ═══════════════════════════════════════════════════════════════════════════════

def clasificador(state: State) -> dict:
    """
    Clasifica el mensaje del cliente en una de tres categorías:
    - ventas: interés en comprar, precios, planes, promociones
    - tecnico: problemas de funcionamiento, errores, soporte técnico
    - facturacion: cobros, facturas, pagos, reembolsos
    """
    print(f"\n🔍 [clasificador] Analizando mensaje: '{state['message']}'")

    prompt = f"""Eres un clasificador de intenciones para un sistema de atención al cliente.

Analiza el siguiente mensaje y clasifícalo en UNA de estas tres categorías:
- ventas: el cliente pregunta por productos, precios, planes, descuentos o quiere comprar
- tecnico: el cliente tiene un problema técnico, error, fallo o necesita soporte técnico
- facturacion: el cliente pregunta por facturas, cobros, pagos, reembolsos o estados de cuenta

IMPORTANTE: Responde ÚNICAMENTE con una de estas tres palabras exactas (en minúsculas):
ventas | tecnico | facturacion

Mensaje del cliente: "{state['message']}"

Categoría:"""

    resultado = llm.invoke(prompt)

    # Normalizar la respuesta: minúsculas, sin espacios ni puntuación
    categoria_raw = resultado.content.strip().lower()
    categoria_raw = categoria_raw.replace(".", "").replace(",", "").replace("'", "")

    # Validar que sea una categoría conocida; si no, usar fallback
    categorias_validas = {"ventas", "tecnico", "facturacion"}
    if categoria_raw in categorias_validas:
        categoria = categoria_raw
    else:
        # Buscar la primera coincidencia dentro de la respuesta
        categoria = "ventas"  # fallback por defecto
        for cat in categorias_validas:
            if cat in categoria_raw:
                categoria = cat
                break

    print(f"   → Categoría detectada: {categoria}")
    return {"category": categoria}


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN ROUTER (conditional edge)
# Decide el siguiente nodo a ejecutar según la categoría detectada.
# ═══════════════════════════════════════════════════════════════════════════════

def router(state: State) -> str:
    """
    Retorna el nombre del nodo destino según state["category"].
    Esta función es usada por add_conditional_edges para el enrutamiento.
    """
    categoria = state.get("category", "ventas")
    print(f"\n🔀 [router] Enrutando a agente: {categoria}")

    if categoria == "ventas":
        return "ventas"
    elif categoria == "tecnico":
        return "tecnico"
    elif categoria == "facturacion":
        return "facturacion"
    else:
        # Fallback de seguridad
        return "ventas"


# ═══════════════════════════════════════════════════════════════════════════════
# NODO 2: AGENTE DE VENTAS
# Especializado en consultas comerciales con tono persuasivo.
# ═══════════════════════════════════════════════════════════════════════════════

def agente_ventas(state: State) -> dict:
    """
    Responde consultas de ventas con tono persuasivo y orientado a cerrar negocios.
    """
    print(f"\n💼 [agente_ventas] Procesando consulta comercial...")

    prompt = f"""Eres un asesor de ventas experto y entusiasta de una empresa de tecnología.
Tu objetivo es ayudar al cliente a encontrar la solución perfecta para sus necesidades
y motivarlo a tomar una decisión de compra.

Tono: persuasivo, cercano, positivo y orientado a cerrar ventas.
Responde de forma concisa (máximo 3-4 oraciones).
Incluye siempre un llamado a la acción al final.

Mensaje del cliente: "{state['message']}"

Tu respuesta:"""

    respuesta = llm.invoke(prompt)
    print(f"   → Respuesta generada (ventas)")
    return {"response": respuesta.content.strip()}


# ═══════════════════════════════════════════════════════════════════════════════
# NODO 3: AGENTE TÉCNICO
# Especializado en soporte técnico con tono claro y paso a paso.
# ═══════════════════════════════════════════════════════════════════════════════

def agente_tecnico(state: State) -> dict:
    """
    Responde problemas técnicos con instrucciones claras y estructuradas.
    """
    print(f"\n🔧 [agente_tecnico] Procesando consulta técnica...")

    prompt = f"""Eres un ingeniero de soporte técnico especializado con amplia experiencia
en resolución de problemas de software y hardware.

Tono: claro, preciso y empático. Usa pasos numerados cuando sea necesario.
Responde de forma concisa (máximo 4-5 oraciones o pasos).
Valida siempre que el cliente entienda los próximos pasos.

Mensaje del cliente: "{state['message']}"

Tu respuesta:"""

    respuesta = llm.invoke(prompt)
    print(f"   → Respuesta generada (tecnico)")
    return {"response": respuesta.content.strip()}


# ═══════════════════════════════════════════════════════════════════════════════
# NODO 4: AGENTE DE FACTURACIÓN
# Especializado en cobros, facturas y pagos con tono formal y preciso.
# ═══════════════════════════════════════════════════════════════════════════════

def agente_facturacion(state: State) -> dict:
    """
    Responde consultas de facturación con tono formal, preciso y confiable.
    """
    print(f"\n🧾 [agente_facturacion] Procesando consulta de facturación...")

    prompt = f"""Eres un especialista en facturación y cobros de una empresa de tecnología.
Gestionas consultas sobre facturas, pagos, cargos incorrectos, reembolsos y estados de cuenta.

Tono: formal, preciso y tranquilizador. El cliente confía en ti para resolver
problemas financieros con prontitud y exactitud.
Responde de forma concisa (máximo 3-4 oraciones).
Indica siempre el plazo estimado de resolución cuando aplique.

Mensaje del cliente: "{state['message']}"

Tu respuesta:"""

    respuesta = llm.invoke(prompt)
    print(f"   → Respuesta generada (facturacion)")
    return {"response": respuesta.content.strip()}


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL GRAFO
# ═══════════════════════════════════════════════════════════════════════════════

def construir_grafo() -> StateGraph:
    """
    Construye y compila el StateGraph con el patrón Router.

    Topología:
        START → clasificador → router → ventas    → END
                                      → tecnico   → END
                                      → facturacion → END
    """
    # Crear el StateGraph con el esquema de estado definido
    graph = StateGraph(State)

    # ── Registrar nodos ───────────────────────────────────────────────────────
    graph.add_node("clasificador", clasificador)
    graph.add_node("ventas", agente_ventas)
    graph.add_node("tecnico", agente_tecnico)
    graph.add_node("facturacion", agente_facturacion)

    # ── Definir el nodo de entrada ────────────────────────────────────────────
    graph.set_entry_point("clasificador")

    # ── Routing condicional: clasificador → agente especializado ──────────────
    # add_conditional_edges ejecuta router(state) para determinar el siguiente nodo
    graph.add_conditional_edges(
        "clasificador",  # nodo origen
        router,          # función que decide el destino
        {
            "ventas":      "ventas",
            "tecnico":     "tecnico",
            "facturacion": "facturacion",
        }
    )

    # ── Cada agente termina el flujo en END ───────────────────────────────────
    graph.add_edge("ventas", END)
    graph.add_edge("tecnico", END)
    graph.add_edge("facturacion", END)

    # Compilar el grafo (valida la estructura y prepara la ejecución)
    app = graph.compile()
    print("✅ Grafo compilado correctamente")
    return app


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL — Chat interactivo
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  SISTEMA MULTIAGENTE CON PATRÓN ROUTER — LangGraph")
    print("=" * 65)
    print("  Escribe tu consulta y el sistema la enrutará al agente")
    print("  correspondiente. Escribe 'salir' para terminar.")
    print("=" * 65)

    # Construir el grafo una sola vez (se reutiliza en cada consulta)
    app = construir_grafo()

    # ── Bucle interactivo ─────────────────────────────────────────────────────
    while True:
        print()
        try:
            mensaje = input("📨 Tu mensaje: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C o Ctrl+D cierran el programa limpiamente
            print("\n\nHasta luego 👋")
            break

        if not mensaje:
            print("   ⚠️  Escribe un mensaje para continuar.")
            continue

        if mensaje.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego 👋")
            break

        print("─" * 65)

        # El estado inicial solo requiere el campo "message"
        estado_inicial = {
            "message": mensaje,
            "category": "",
            "response": "",
        }

        # Ejecutar el grafo
        resultado = app.invoke(estado_inicial)

        # Mostrar resultado final
        print(f"\n📋 RESULTADO FINAL:")
        print(f"   Categoría : {resultado['category']}")
        print(f"   Respuesta : {resultado['response']}")
        print("─" * 65)


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
