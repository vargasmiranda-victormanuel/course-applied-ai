"""
╔══════════════════════════════════════════════════════════════╗
║  Ejercicio 2: Pipeline RAG con FAISS                        ║
║  RAG Avanzado — Semana 8                                    ║
║  Universidad Cenfotec — Aplicaciones con IA                 ║
╚══════════════════════════════════════════════════════════════╝

Objetivo: Construir un pipeline RAG completo que:
  1. Cargue y divida un documento en chunks
  2. Genere embeddings con sentence-transformers
  3. Indexe los embeddings en FAISS
  4. Busque documentos relevantes por similitud
  5. Genere respuestas con GPT usando el contexto recuperado

Requisitos:
  pip install faiss-cpu sentence-transformers openai langchain python-dotenv
"""

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

# ═══════════════════════════════════════════
# 1. CARGAR Y DIVIDIR EL DOCUMENTO
# ═══════════════════════════════════════════
print("📄 Paso 1: Cargando y dividiendo documento...")
print("-" * 50)

with open("documentos/politicas.txt", "r", encoding="utf-8") as f:
    texto = f.read()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],
)
chunks = splitter.split_text(texto)
print(f"   ✅ Documento: {len(texto)} caracteres")
print(f"   ✅ Chunks generados: {len(chunks)}")
print()

# ═══════════════════════════════════════════
# 2. GENERAR EMBEDDINGS
# ═══════════════════════════════════════════
print("🧠 Paso 2: Generando embeddings...")
print("-" * 50)

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

print(f"   ✅ Embeddings shape: {embeddings.shape}")
print(f"   ✅ Dimensión: {embeddings.shape[1]} (MiniLM-L6-v2)")
print()

# ═══════════════════════════════════════════
# 3. INDEXAR EN FAISS
# ═══════════════════════════════════════════
print("⚡ Paso 3: Indexando en FAISS...")
print("-" * 50)

dimension = embeddings.shape[1]  # 384 para MiniLM
index = faiss.IndexFlatL2(dimension)  # L2 = distancia euclidiana
index.add(embeddings)

print(f"   ✅ Índice creado: IndexFlatL2")
print(f"   ✅ Vectores indexados: {index.ntotal}")
print()

# ═══════════════════════════════════════════
# 4. FUNCIÓN DE BÚSQUEDA (RETRIEVAL)
# ═══════════════════════════════════════════
def buscar_chunks(pregunta, k=3):
    """Busca los k chunks más similares a la pregunta."""
    query_embedding = model.encode([pregunta]).astype("float32")
    distances, indices = index.search(query_embedding, k)

    resultados = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        resultados.append({
            "chunk": chunks[idx],
            "distancia": float(dist),
            "indice": int(idx),
        })
    return resultados


# ═══════════════════════════════════════════
# 5. FUNCIÓN RAG (RETRIEVAL + GENERATION)
# ═══════════════════════════════════════════
def rag_query(pregunta, k=3, verbose=True):
    """
    Pipeline RAG completo:
    1. Busca chunks relevantes con FAISS
    2. Construye un prompt con el contexto
    3. Genera respuesta con GPT
    """
    # Paso 1: Retrieval
    resultados = buscar_chunks(pregunta, k=k)

    if verbose:
        print(f"\n🔍 Pregunta: {pregunta}")
        print(f"   Chunks recuperados: {len(resultados)}")
        for i, r in enumerate(resultados):
            print(f"   📌 Chunk {r['indice']} (dist: {r['distancia']:.4f}): {r['chunk'][:60]}...")

    # Paso 2: Construir contexto
    contexto = "\n---\n".join([r["chunk"] for r in resultados])

    # Paso 3: Generar respuesta con GPT
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": f"""Eres un asistente que responde preguntas basándose ÚNICAMENTE 
en el contexto proporcionado. 

REGLAS IMPORTANTES:
1. Si la respuesta NO está en el contexto, responde: "No tengo información suficiente para responder."
2. NO inventes información.
3. Cita la fuente entre [corchetes] cuando sea posible.
4. Sé conciso y directo.

CONTEXTO:
{contexto}""",
            },
            {"role": "user", "content": pregunta},
        ],
    )

    respuesta = response.choices[0].message.content

    if verbose:
        print(f"\n💬 Respuesta:\n   {respuesta}")
        print(f"\n   Tokens usados: {response.usage.total_tokens}")

    return respuesta


# ═══════════════════════════════════════════
# 6. PROBAR EL PIPELINE
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("🚀 PROBANDO EL PIPELINE RAG")
print("=" * 60)

# Pregunta 1
print("\n" + "━" * 60)
rag_query("¿Cuál es la política de devoluciones?")

# Pregunta 2
print("\n" + "━" * 60)
rag_query("¿Cuál es el horario de atención los sábados?")

# Pregunta 3
print("\n" + "━" * 60)
rag_query("¿Cómo funciona el programa de puntos de fidelidad?")

# Pregunta 4 — Pregunta que NO está en el documento
print("\n" + "━" * 60)
rag_query("¿Cuál es el precio de los televisores?")

# Pregunta 5
print("\n" + "━" * 60)
rag_query("¿Puedo devolver un producto después de 60 días?")

# ═══════════════════════════════════════════
# 7. MODO INTERACTIVO (opcional)
# ═══════════════════════════════════════════
print("\n\n" + "=" * 60)
print("💬 MODO INTERACTIVO")
print("   Escribe tus preguntas (o 'salir' para terminar)")
print("=" * 60)

while True:
    pregunta = input("\n❓ Tu pregunta: ").strip()
    if pregunta.lower() in ("salir", "exit", "q", "quit", ""):
        print("👋 ¡Hasta luego!")
        break
    rag_query(pregunta)