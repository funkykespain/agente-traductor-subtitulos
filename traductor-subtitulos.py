##############################################################################
##############################################################################
###                                                                        ###
###                                                                        ###
###   ███████╗██╗   ██╗███╗   ██╗██╗  ██╗██╗   ██╗██╗  ██╗███████╗         ###
###   ██╔════╝██║   ██║████╗  ██║██║ ██╔╝╚██╗ ██╔╝██║ ██╔╝██╔════╝         ###
###   █████╗  ██║   ██║██╔██╗ ██║█████╔╝  ╚████╔╝ █████╔╝ █████╗           ###
###   ██╔══╝  ██║   ██║██║╚██╗██║██╔═██╗   ╚██╔╝  ██╔═██╗ ██╔══╝           ###
###   ██║     ╚██████╔╝██║ ╚████║██║  ██╗   ██║   ██║  ██╗███████╗         ###
###   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝         ###
###                                                                        ###
###   · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·      ###
###                                                                        ###
###   Enrique Aranda  |  @funkykespain                                     ###
###   Data Scientist · Marketing-to-ML Bridge Builder · AI Storyteller 	   ###
###                                                                        ###
###   gh  https://github.com/funkykespain                                  ###
###   li  https://www.linkedin.com/in/earanda                              ###
###   ko  https://ko-fi.com/funkykespain                                   ###
###   ph  +34 665 65 64 04                                                 ###
###                                                                        ###
##############################################################################
##############################################################################




# =============================================================================
#  PIPELINE SIMPLE DE TRADUCCIÓN CINEMATOGRÁFICA CON IA LOCAL
# =============================================================================
#
#  ¿Qué hace este script?
#  ─────────────────────
#  1. Lee un archivo de subtítulos en español (.srt).
#  2. Traduce cada subtítulo completo al idioma elegido con TranslateGemma,
#     manteniendo el contexto de los subtítulos anteriores para mayor coherencia.
#  3. Divide las traducciones largas en dos líneas equilibradas (máx. 42 CPL),
#     respetando las unidades lógicas del texto (no separa preposiciones, etc.)
#
#  Stack tecnológico:
#  ─────────────────
#  • Python          → orquesta todo el flujo
#  • LangChain       → conecta el prompt con el modelo
#  • Ollama          → sirve el modelo de IA en tu máquina (GPU RTX 4070)
#  • TranslateGemma  → modelo de traducción especializado (4B parámetros, ~3.3 GB)
#
#  Requisitos previos (instalar una sola vez en el terminal):
#  ──────────────────────────────────────────────────────────
#  pip install langchain langchain-ollama langchain-core
#  ollama pull translategemma
#
# =============================================================================


# ── SECCIÓN 1: IMPORTACIONES ──────────────────────────────────────────────────
# Le decimos a Python qué librerías externas vamos a usar en este script.

from langchain_ollama import ChatOllama                   # Conecta con Ollama (modelo local)
from langchain_core.prompts import ChatPromptTemplate     # Plantilla para construir el prompt
from langchain_core.output_parsers import StrOutputParser # Extrae solo el texto de la respuesta


# ── SECCIÓN 2: CONFIGURACIÓN ──────────────────────────────────────────────────
# Variables que definen el comportamiento del script.
# Si quieres cambiar el modelo, el idioma o el tamaño de la ventana de contexto,
# solo tienes que tocar esta sección.

MODELO_SLM        = "translategemma:latest"  # Nombre del modelo instalado en Ollama
OLLAMA_API_URL    = "http://localhost:11434" # Dirección donde Ollama escucha (no cambiar)
IDIOMA_ORIGEN     = "Spanish"                # Nombre completo del idioma original
CODIGO_ORIGEN     = "es"                     # Código ISO del idioma original
IDIOMA_DESTINO    = "English"                # Nombre completo del idioma destino
CODIGO_DESTINO    = "en"                     # Código ISO del idioma destino
ARCHIVO_SRT       = "subtitulos.srt"         # Nombre del archivo de subtítulos a traducir

# Cuántos subtítulos anteriores se incluyen como contexto en cada traducción.
# Con 3 el modelo "recuerda" los últimos 3 intercambios al traducir el actual.
# Subir este número mejora la coherencia pero hace cada llamada más lenta.
VENTANA_CONTEXTO  = 3

# Máximo de caracteres por línea (CPL) en el archivo de salida.
# El estándar internacional para alfabetos latinos es entre 37 y 42 caracteres.
CPL_MAXIMO        = 42


# ── SECCIÓN 3: INICIALIZACIÓN DEL MODELO ─────────────────────────────────────
# Creamos la conexión con TranslateGemma a través de Ollama.

llm = ChatOllama(
    model       = MODELO_SLM,
    base_url    = OLLAMA_API_URL,
    temperature = 0,   # T=0 hace que el modelo sea determinista:
    		           # siempre elegirá la traducción más probable y no "inventará" ni será creativo.
    num_gpu     = 99,  # Carga el modelo entero en la GPU para máxima velocidad.
)


# ── SECCIÓN 4: PLANTILLA DEL PROMPT ──────────────────────────────────────────
# Definimos el "molde" del mensaje que recibirá el modelo en cada traducción.
# Las llaves {variable} se rellenan automáticamente en cada llamada.
#
# El bloque {context} lleva los últimos subtítulos ya traducidos para que el
# modelo sepa qué se ha dicho antes y mantenga coherencia de nombres, tono, etc.

prompt_template = ChatPromptTemplate.from_messages([
    ("user", (
        # Formato EXACTO de la documentación oficial de TranslateGemma:
        # https://ollama.com/library/translategemma
        # Alterar esta estructura puede degradar la calidad de la traducción.
        #
        # La sección {context} es el "historial" de la sesión: se inyectan aquí
        # los últimos subtítulos (original + traducción) para dar continuidad.
        #
        # Nota: la documentación exige DOS líneas en blanco antes del texto
        # a traducir. Están incluidas justo antes de {text}.
        "You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. "
        "Your goal is to accurately convey the meaning and nuances of the original {source_lang} text "
        "while adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.\n"
        "Produce only the {target_lang} translation, without any additional explanations or commentary.\n\n"
        "For context, here are the previous subtitles already translated:\n"
        "{context}\n\n"
        "Please translate the following {source_lang} text into {target_lang}:\n\n\n"
        "{text}"
    ))
])

# Encadenamos los tres pasos: construir el prompt → pasarlo al modelo → extraer el texto.
# El operador | (pipe) conecta cada paso con el siguiente.
chain = prompt_template | llm | StrOutputParser()
# Esta línea une los tres pasos en un flujo:
# 1. Prepara el mensaje (prompt) -> 2. Lo envía a la IA (llm) -> 3. Limpia la respuesta (parser)


# ── SECCIÓN 5: FUNCIÓN DE TRADUCCIÓN ─────────────────────────────────────────
# Esta función recibe una frase y el historial reciente, y devuelve la traducción.

def traducir(texto: str, historial: list) -> str:
    """
    Traduce un subtítulo completo al idioma definido en SECCIÓN 2,
    usando el historial de subtítulos anteriores como contexto.

    Parámetros:
      texto     (str):  El texto del subtítulo a traducir (ya unificado en una sola frase).
      historial (list): Lista de tuplas (original, traduccion) de subtítulos recientes.

    Devuelve:
      str: La traducción generada por TranslateGemma.
    """
    # Formateamos el historial como un bloque de texto legible para el modelo.
    # Cada entrada muestra el original en español y su traducción, separados por |
    # Ejemplo:  ES: Te amo.  |  EN: I love you.
    if historial:
        contexto_str = "\n".join(
            f"{CODIGO_ORIGEN.upper()}: {orig}  |  {CODIGO_DESTINO.upper()}: {trad}"
            for orig, trad in historial
        )
    else:
        # En el primer subtítulo todavía no hay historial
        contexto_str = "(No previous subtitles)"

    # Llama a la IA: le entrega el "pack" de instrucciones y recibe el texto traducido.
    traduccion = chain.invoke({
        "source_lang": IDIOMA_ORIGEN,
        "source_code": CODIGO_ORIGEN,
        "target_lang": IDIOMA_DESTINO,
        "target_code": CODIGO_DESTINO,
        "context":     contexto_str,
        "text":        texto
    })
    return traduccion


# ── SECCIÓN 6: DIVISIÓN INTELIGENTE DE LÍNEAS ────────────────────────────────
# Tras la traducción, las frases largas se dividen en dos líneas para respetar
# el estándar de legibilidad de 37-42 caracteres por línea (CPL).
#
# Reglas que sigue el algoritmo:
#   1. Si el texto cabe en una línea (≤ CPL_MAXIMO), no se toca.
#   2. Se busca el punto de corte más cercano al centro visual del texto.
#   3. No se corta después de palabras funcionales (preposiciones, artículos,
#      conjunciones) para no separar unidades lógicas como "go to\nthe store".

# Palabras tras las cuales NO se debe cortar (van unidas a lo que sigue).
NO_CORTAR_ANTES = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "with",
    "by", "from", "into", "about", "up", "as", "but", "or", "and",
    "that", "which", "who", "whom", "I", "he", "she", "it", "we", "you",
    "my", "your", "his", "her", "its", "our", "not", "no", "so",
}

def partir_subtitulo(texto: str) -> str:
    """
    Divide un texto en dos líneas equilibradas respetando CPL_MAXIMO
    y las unidades lógicas del idioma.

    Parámetros:
      texto (str): El texto traducido en una sola línea.

    Devuelve:
      str: El texto original si cabe en una línea, o partido en dos líneas
           separadas por un salto de línea.
    """
    if len(texto) <= CPL_MAXIMO:
        return texto  # Cabe en una línea, no hace falta partir

    palabras = texto.split()
    mejor_corte      = None
    mejor_puntuacion = float("inf")
    centro           = len(texto) / 2

    for i in range(len(palabras) - 1):
        linea1 = " ".join(palabras[:i+1])
        linea2 = " ".join(palabras[i+1:])

        # Descartamos cortes que generen una línea demasiado larga
        if len(linea1) > CPL_MAXIMO or len(linea2) > CPL_MAXIMO:
            continue

        # Penalizamos cortes tras palabras funcionales (preposición, artículo...)
        # para evitar partidos como "go to\nthe store"
        ultima_palabra = palabras[i].rstrip(",.;:?!").lower()
        penalizacion   = 8 if ultima_palabra in NO_CORTAR_ANTES else 0

        # La puntuación combina: distancia al centro + penalización + desequilibrio.
        # Un valor más bajo = mejor corte.
        puntuacion = (
            abs(len(linea1) - centro) +
            penalizacion +
            abs(len(linea1) - len(linea2)) * 0.3
        )

        if puntuacion < mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_corte      = i + 1

    if mejor_corte is None:
        return texto  # No hay corte posible dentro del límite; dejamos tal cual

    return " ".join(palabras[:mejor_corte]) + "\n" + " ".join(palabras[mejor_corte:])


# ── SECCIÓN 7: INGESTA DEL ARCHIVO SRT ───────────────────────────────────────
# Leemos el archivo y lo dividimos en bloques. Cada bloque es un subtítulo
# completo con su índice, sus tiempos y su texto (que puede ocupar varias líneas).
#
# Un archivo .srt tiene este formato por cada subtítulo:
#   1                            ← número de subtítulo
#   00:00:01,000 --> 00:00:03,000 ← tiempo de entrada y salida
#   Primera línea del texto       ← texto (puede ser una o varias líneas)
#   Segunda línea del texto       ←
#                                 ← línea en blanco (separador entre bloques)

def parsear_srt(ruta_archivo: str) -> list:
    """
    Lee un archivo .srt y devuelve una lista de diccionarios, uno por subtítulo.
    Cada diccionario tiene las claves: 'indice', 'tiempo', 'texto'.

    El texto de cada subtítulo se une en una sola frase, eliminando el problema
    de las líneas partidas (ej. "CONCEBIDO, ESCRITO\nY DIRIGIDO POR" →
    "CONCEBIDO, ESCRITO Y DIRIGIDO POR").
    """
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Dividimos el archivo en bloques usando la línea en blanco como separador
    bloques_raw = contenido.strip().split("\n\n")

    subtitulos = []
    for bloque in bloques_raw:
        lineas = bloque.strip().split("\n")

        # Un bloque válido tiene al menos: índice + tiempo + una línea de texto
        if len(lineas) < 3:
            continue

        indice = lineas[0].strip()
        tiempo = lineas[1].strip()

        # Todo lo que viene a partir de la línea 3 es texto del subtítulo.
        # Lo unimos con un espacio para reconstruir la frase completa.
        # "CONCEBIDO, ESCRITO" + "Y DIRIGIDO POR" → "CONCEBIDO, ESCRITO Y DIRIGIDO POR"
        texto_completo = " ".join(line.strip() for line in lineas[2:])
        # Junta las líneas partidas del archivo original en una sola frase larga. 
	    # Es mejor que la IA traduzca una frase completa que "pedazos" de frases.

        subtitulos.append({
            "indice": indice,
            "tiempo": tiempo,
            "texto":  texto_completo,
        })

    return subtitulos


# ── SECCIÓN 8: TRADUCCIÓN Y ESCRITURA DEL ARCHIVO DE SALIDA ──────────────────
    # ── EJECUCIÓN DEL SCRIPT
if __name__ == "__main__":
    # Esta condición asegura que el proceso de traducción solo arranque si el
    # archivo se ejecuta directamente y no cuando se importan sus funciones.

    print(f"Leyendo '{ARCHIVO_SRT}'...")
    subtitulos = parsear_srt(ARCHIVO_SRT)
    print(f"Se encontraron {len(subtitulos)} subtítulos.\n")
    print(f"Traduciendo al {IDIOMA_DESTINO} con ventana de contexto = {VENTANA_CONTEXTO}...\n")

    lineas_salida = []  # Aquí construimos el contenido del nuevo archivo .srt
    historial     = []  # Lista de tuplas (original, traduccion) de los últimos subtítulos

    for i, sub in enumerate(subtitulos, start=1):

        texto_original = sub["texto"]

        # Mostramos el progreso en la terminal
        print(f"  [{i}/{len(subtitulos)}] ES: {texto_original}")

        # Pasamos solo los últimos N subtítulos como contexto (ventana deslizante)
        contexto_reciente = historial[-VENTANA_CONTEXTO:]
        # Toma solo los últimos N subtítulos del historial para no saturar la memoria de la IA, 
	    # pero manteniendo el hilo de la conversación.

        # Traducimos el subtítulo completo de una sola vez
        traduccion = traducir(texto_original, contexto_reciente)
        print(f"           {CODIGO_DESTINO.upper()}: {traduccion}\n")

        # Añadimos este par al historial para los siguientes subtítulos
        historial.append((texto_original, traduccion))

        # Dividimos la traducción en dos líneas si supera el límite de CPL
        traduccion_formateada = partir_subtitulo(traduccion)

        # Reconstruimos el bloque .srt con el formato estándar:
        # índice, tiempo, texto traducido (en 1 o 2 líneas), línea en blanco
        lineas_salida.append(f"{sub['indice']}\n")
        lineas_salida.append(f"{sub['tiempo']}\n")
        lineas_salida.append(f"{traduccion_formateada}\n")
        lineas_salida.append("\n")

    # Guardamos el resultado como un nuevo archivo .srt
    nombre_salida = ARCHIVO_SRT.replace(".srt", f"_{CODIGO_DESTINO}.srt")
    # Si el original es 'cine.srt' y traduces a inglés, crea automáticamente 'cine_en.srt'.
    with open(nombre_salida, "w", encoding="utf-8") as archivo_salida:
        archivo_salida.writelines(lineas_salida)

    print(f"✓ Traducción completada. Archivo guardado como: {nombre_salida}")
    

# =============================================================================
#  REPASO FINAL Y CONCEPTOS CLAVE
# =============================================================================
#
#  CONCEPTOS TÉCNICOS:
#  ─────────────────
#  • SLM (Small Language Model): Modelos como TranslateGemma que, a diferencia de 
#    ChatGPT, son lo suficientemente pequeños para correr en tu propia GPU.
#
#  • TEMPERATURE (0): Controla la aleatoriedad. En traducción usamos 0 para que 
#    el modelo sea "serio" y no invente palabras o estilos innecesarios.
#
#  • CPL (Characters Per Line): Estándar de la industria (37-42) para que el ojo 
#    humano pueda leer el subtítulo sin mover demasiado la cabeza.
#
#  • PROMPT: El conjunto de instrucciones y reglas que le damos a la IA para
#    moldear su comportamiento antes de entregarle el texto a traducir.
#
#  FLUJO DE DATOS (EL CAMINO DEL SUBTÍTULO):
#  ────────────────────────────────────────
#  1. PARSEAR: El script "limpia" el archivo .srt y une frases cortadas.
#  2. CONTEXTO: Se recuperan los últimos subtítulos para que la IA no pierda el hilo.
#  3. INVOKE: Se dispara la llamada a la IA (TranslateGemma) mediante Ollama.
#  4. PARTIR: Si la traducción es muy larga, el algoritmo busca el mejor lugar
#     para hacer un salto de línea sin romper unidades lógicas (preposiciones).
#  5. GUARDAR: Se reconstruye el formato .srt y se exporta el archivo final.
#
#  CONSEJO FINAL:
#  ─────────────
#  Si notas que la IA confunde géneros (él/ella) o términos técnicos, aumenta la 
#  variable VENTANA_CONTEXTO en la SECCIÓN 2. Esto le da más "memoria", aunque
#  el proceso tardará un poco más por cada subtítulo.
#
# =============================================================================
