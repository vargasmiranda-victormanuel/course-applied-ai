"""
╔══════════════════════════════════════════════════════════════╗
║  Ejercicio 1: Chunking Inteligente                          ║
║  RAG Avanzado — Semana 8                                    ║
║  Universidad Cenfotec — Aplicaciones con IA                 ║
╚══════════════════════════════════════════════════════════════╝

Objetivo: Implementar diferentes estrategias de chunking y comparar
cómo cada una divide un documento real.

Conceptos clave:
  - Fixed-Size chunking: divide por cantidad fija de caracteres
  - Recursive chunking: divide respetando separadores jerárquicos
  - Overlap: superposición entre chunks para no perder contexto
"""

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ═══════════════════════════════════════════
# 1. CARGAR DOCUMENTO
# ═══════════════════════════════════════════
with open("documentos/politicas.txt", "r", encoding="utf-8") as f:
    texto = f.read()

print(f"📄 Documento cargado: {len(texto)} caracteres")
print(f"   Líneas: {texto.count(chr(10))}")
print("=" * 60)

# ═══════════════════════════════════════════
# 2. ESTRATEGIA 1: FIXED-SIZE CHUNKING
# ═══════════════════════════════════════════
print("\n✂️  ESTRATEGIA 1: Fixed-Size Chunking")
print("-" * 40)

splitter_fixed = CharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separator="\n",
)
chunks_fixed = splitter_fixed.split_text(texto)

print(f"   Chunks generados: {len(chunks_fixed)}")
print(f"   Overlap: 50 caracteres\n")

for i, chunk in enumerate(chunks_fixed[:3]):
    print(f"   📌 Chunk {i + 1} ({len(chunk)} chars):")
    print(f"      {chunk[:100]}...")
    print()

# ═══════════════════════════════════════════
# 3. ESTRATEGIA 2: RECURSIVE CHUNKING
# ═══════════════════════════════════════════
print("\n🧩 ESTRATEGIA 2: Recursive Chunking")
print("-" * 40)

splitter_recursive = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],
)
chunks_recursive = splitter_recursive.split_text(texto)

print(f"   Chunks generados: {len(chunks_recursive)}")
print(f"   Separadores: ['\\n\\n', '\\n', '. ', ' ']")
print(f"   Overlap: 50 caracteres\n")

for i, chunk in enumerate(chunks_recursive[:3]):
    print(f"   📌 Chunk {i + 1} ({len(chunk)} chars):")
    print(f"      {chunk[:100]}...")
    print()

# ═══════════════════════════════════════════
# 4. COMPARACIÓN
# ═══════════════════════════════════════════
print("\n📊 COMPARACIÓN DE ESTRATEGIAS")
print("=" * 60)
print(f"{'Métrica':<30} {'Fixed-Size':>12} {'Recursive':>12}")
print("-" * 60)
print(f"{'Cantidad de chunks':<30} {len(chunks_fixed):>12} {len(chunks_recursive):>12}")

avg_fixed = sum(len(c) for c in chunks_fixed) / len(chunks_fixed)
avg_recursive = sum(len(c) for c in chunks_recursive) / len(chunks_recursive)
print(f"{'Tamaño promedio (chars)':<30} {avg_fixed:>12.0f} {avg_recursive:>12.0f}")

min_fixed = min(len(c) for c in chunks_fixed)
min_recursive = min(len(c) for c in chunks_recursive)
print(f"{'Chunk más pequeño (chars)':<30} {min_fixed:>12} {min_recursive:>12}")

max_fixed = max(len(c) for c in chunks_fixed)
max_recursive = max(len(c) for c in chunks_recursive)
print(f"{'Chunk más grande (chars)':<30} {max_fixed:>12} {max_recursive:>12}")

# ═══════════════════════════════════════════
# 5. EXPERIMENTAR CON DIFERENTES PARÁMETROS
# ═══════════════════════════════════════════
print("\n\n🔬 EXPERIMENTO: Efecto del tamaño de chunk y overlap")
print("=" * 60)

configuraciones = [
    (200, 0),    # Chunks pequeños, sin overlap
    (200, 40),   # Chunks pequeños, 20% overlap
    (500, 50),   # Chunks medianos, 10% overlap
    (500, 100),  # Chunks medianos, 20% overlap
    (800, 100),  # Chunks grandes, ~12% overlap
]

print(f"{'Chunk Size':>12} {'Overlap':>10} {'% Overlap':>12} {'# Chunks':>10}")
print("-" * 50)

for size, overlap in configuraciones:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_text(texto)
    pct = (overlap / size) * 100
    print(f"{size:>12} {overlap:>10} {pct:>11.0f}% {len(chunks):>10}")

# ═══════════════════════════════════════════
# PREGUNTAS PARA REFLEXIONAR
# ═══════════════════════════════════════════
print("\n\n💡 PREGUNTAS PARA REFLEXIONAR:")
print("=" * 60)
print("  1. ¿Cuál estrategia respeta mejor la estructura del documento?")
print("  2. ¿Cuál produce chunks más coherentes semánticamente?")
print("  3. ¿Qué pasa si el overlap es 0? ¿Y si es 50%?")
print("  4. ¿Cuál sería el tamaño ideal de chunk para este documento?")
print("  5. ¿Cómo afecta el tamaño de chunk al costo de la API de OpenAI?")