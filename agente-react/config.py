# config.py — Configuración central del agente ReAct
# Carga variables de entorno e inicializa el cliente de OpenAI

import os
from dotenv import load_dotenv
from openai import OpenAI

# 📦 Cargar variables del archivo .env
load_dotenv()

# 🔑 Obtener la API Key desde el entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "❌ No se encontró OPENAI_API_KEY. "
        "Crea un archivo .env con tu clave. "
        "Consulta .env.example para el formato."
    )

# 🤖 Inicializar el cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 Modelo a utilizar
MODEL = "gpt-4o"


# ─────────────────────────────────────────────────────────────────
# Verificación de conexión (se ejecuta al correr: python config.py)
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔌 Verificando conexión con OpenAI...")
    try:
        respuesta = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": "Responde solo con: 'Conexión exitosa'"}
            ],
            max_tokens=20,
        )
        print(f"✅ {respuesta.choices[0].message.content.strip()}")
        print(f"📡 Modelo usado: {MODEL}")
    except Exception as e:
        print(f"❌ Error al conectar con OpenAI: {e}")
