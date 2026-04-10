# schemas.py — Definición JSON Schema de las herramientas para OpenAI Function Calling
#
# OpenAI necesita estos esquemas para saber:
#   - Qué tools existen
#   - Cuándo usarlas (description)
#   - Qué argumentos requieren (parameters)
#
# El LLM lee las 'description' para decidir de forma autónoma qué tool invocar.

tools_schema = [

    # ─────────────────────────────────────────────────
    # Tool 1: buscar_web
    # ─────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "buscar_web",
            "description": (
                "Busca información actualizada en internet sobre cualquier tema. "
                "Úsala cuando necesites datos, tendencias, estadísticas, noticias "
                "o información que no está en tu conocimiento base. "
                "Ideal para investigar tecnologías, frameworks, conceptos técnicos, "
                "o cualquier tema que requiera información reciente. "
                "Puedes llamarla múltiples veces con queries diferentes para obtener "
                "perspectivas complementarias sobre el mismo tema."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "La consulta de búsqueda. Debe ser específica y clara. "
                            "Ejemplos: 'agentes IA tendencias 2026', "
                            "'frameworks Python para LLMs', "
                            "'patrón ReAct en inteligencia artificial'."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },

    # ─────────────────────────────────────────────────
    # Tool 2: guardar_nota
    # ─────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "guardar_nota",
            "description": (
                "Guarda una nota o reporte de investigación como archivo Markdown "
                "en la carpeta 'notas/'. Úsala para preservar hallazgos importantes, "
                "resúmenes de investigación, reportes finales o cualquier información "
                "valiosa que el usuario quiera conservar. "
                "El archivo se crea automáticamente con formato profesional. "
                "Llámala al final de una investigación para guardar el reporte completo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": (
                            "Título descriptivo de la nota o reporte. "
                            "Ejemplo: 'Reporte Tendencias IA 2026', "
                            "'Análisis Frameworks Python para Agentes'."
                        ),
                    },
                    "contenido": {
                        "type": "string",
                        "description": (
                            "Contenido completo de la nota en formato Markdown. "
                            "Puede incluir encabezados (##), listas (-), "
                            "negritas (**texto**) y cualquier otro formato Markdown. "
                            "Debe ser un resumen completo y bien estructurado."
                        ),
                    },
                },
                "required": ["titulo", "contenido"],
            },
        },
    },

    # ─────────────────────────────────────────────────
    # Tool 3: fecha_actual
    # ─────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "fecha_actual",
            "description": (
                "Retorna la fecha y hora actual del sistema en español. "
                "Úsala al inicio de una investigación para contextualizar "
                "temporalmente el reporte, o cuando el usuario pregunte "
                "la fecha/hora actual. "
                "No requiere ningún parámetro."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
