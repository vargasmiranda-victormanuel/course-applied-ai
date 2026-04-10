# main.py — Punto de entrada del agente investigador ReAct
#
# Uso:
#   python main.py          → Ejecuta la demo con pregunta predefinida
#   python main.py --chat   → Modo conversacional interactivo

import sys
from agent import run_agent


# ═══════════════════════════════════════════════════════════════
# MODO DEMO
# Ejecuta el agente con una pregunta predefinida de ejemplo
# ═══════════════════════════════════════════════════════════════

def demo():
    """Ejecuta una investigación de ejemplo para demostrar el agente."""
    pregunta = "Investiga las tendencias en agentes de IA para 2026"

    print("\n🚀 Iniciando modo DEMO")
    print(f"📌 Pregunta de investigación: {pregunta}\n")

    respuesta = run_agent(pregunta, verbose=True)

    print("\n" + "═" * 60)
    print("📋 RESPUESTA FINAL DEL AGENTE:")
    print("═" * 60)
    print(respuesta)
    print("═" * 60 + "\n")


# ═══════════════════════════════════════════════════════════════
# MODO CHAT INTERACTIVO
# El usuario puede hacer múltiples preguntas en sesión
# ═══════════════════════════════════════════════════════════════

def chat_interactivo():
    """Modo conversacional: el usuario escribe preguntas en bucle."""
    print("\n" + "═" * 60)
    print("💬 AGENTE INVESTIGADOR — Modo Interactivo")
    print("═" * 60)
    print("Escribe tu pregunta y presiona Enter.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            # Leer input del usuario
            user_input = input("👤 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 ¡Hasta luego!")
            break

        # Comando de salida
        if user_input.lower() in ("salir", "exit", "quit", "q"):
            print("👋 ¡Hasta luego!")
            break

        # Ignorar inputs vacíos
        if not user_input:
            print("⚠️  Por favor, escribe una pregunta.\n")
            continue

        # Ejecutar el agente
        respuesta = run_agent(user_input, verbose=True)

        print("\n" + "─" * 60)
        print("🤖 Agente:")
        print(respuesta)
        print("─" * 60 + "\n")


# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Verificar si se pasó el flag --chat
    if "--chat" in sys.argv:
        chat_interactivo()
    else:
        demo()
