# 🎬 Traductor de Subtítulos Cinematográficos con IA Local

Herramienta educativa para traducir archivos de subtítulos `.srt` del español a otros idiomas usando un modelo de inteligencia artificial que corre **en tu propio ordenador**, sin enviar datos a ningún servidor externo.

Desarrollada como práctica para el curso de lingüística computacional aplicada a la traducción audiovisual.

---

## ¿Qué hace este proyecto?

Lee un archivo de subtítulos en español (`.srt`), traduce cada línea de diálogo al idioma que elijas y genera un nuevo archivo `.srt` listo para usar — respetando intactos los tiempos y la numeración originales.

---

## Requisitos de hardware

No cualquier PC puede ejecutar este script sin problemas. El modelo de inteligencia artificial ocupa aproximadamente **3.3 GB** y necesita cargarse completo en memoria, así que tu ordenador debe cumplir unos mínimos.

### Memoria (RAM / VRAM)

| Recurso | Mínimo | Recomendado |
|---|---|---|
| **Espacio en disco** | 3.3 GB libres (para descargar el modelo) | 5 GB o más |
| **RAM del sistema** | 8 GB | 16 GB |
| **VRAM (memoria de la GPU)** | — | 4 GB o más (para que quepa el modelo entero) |

- **8 GB de RAM**: puede funcionar, pero el sistema irá justo y la traducción será muy lenta.
- **16 GB de RAM**: el escenario ideal para que el modelo y el sistema operativo convivan sin problemas.
- **Menos de 8 GB de RAM**: no se recomienda. El modelo no podrá cargarse correctamente.

### GPU (tarjeta gráfica) — opcional pero muy recomendada

El script viene configurado para cargar el modelo entero en la GPU (`num_gpu = 99`, línea 94 de `traductor-subtitulos.py`), lo que da la máxima velocidad. El autor desarrolló y probó el código con una **GPU RTX 4070**.

**Si no tienes GPU dedicada**, el script seguirá funcionando, pero usará la CPU y será bastante más lento. Puedes modificar el parámetro `num_gpu` en esa misma línea para que el modelo no intente cargarse en una GPU que no existe (aunque el script ya intenta caer en CPU automáticamente si no encuentra una GPU compatible).

### Procesador

Cualquier CPU moderna sirve. La diferencia de velocidad la marca tener o no tener GPU.

### Tabla resumen de escenarios

| Tu PC... | ¿Funciona? | ¿Qué esperar? |
|---|---|---|
| Tiene GPU dedicada (RTX 4070 o similar) | ✅ Sí | Rápido. Traduce un archivo de película en pocos minutos |
| Tiene 16 GB de RAM, sin GPU | ✅ Sí | Lento pero usable. Puedes dejar el script corriendo y hacer otra cosa |
| Tiene 8 GB de RAM, sin GPU | ⚠️ Posible | Muy lento. El ordenador puede ir justo de recursos |
| Tiene 4 GB de RAM o menos | ❌ No | El modelo no cabe en memoria. No lo intentes |

---

## Requisitos previos

Antes de ejecutar el script necesitas tener instalado en tu ordenador:

### 1. Python 3.10 o superior

Comprueba si ya lo tienes abriendo una terminal y escribiendo:
```
python --version
```
Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/).

---

### 2. Ollama

Ollama es el programa que carga y ejecuta el modelo de IA en tu máquina.

Descárgalo desde [ollama.com](https://ollama.com) e instálalo como cualquier otra aplicación.

Una vez instalado, descarga el modelo de traducción abriendo una terminal y ejecutando:
```
ollama pull translategemma
```
> ⚠️ El modelo ocupa aproximadamente **3.3 GB**. Asegúrate de tener espacio en disco y conexión estable antes de descargarlo.

Ya podrías chatear con este modelo ejecutando:
```
ollama run translategemma
```
---

### 3. Descargar (o actualizar) el proyecto desde GitHub

El código de este proyecto está alojado en GitHub. Para obtenerlo en tu ordenador:

**Primera vez — clonar el repositorio:**
```
git clone https://github.com/funkykespain/agente-traductor-subtitulos.git
```
Esto crea una carpeta llamada `agente-traductor-subtitulos` con todos los archivos del proyecto. A partir de ahora trabaja siempre **dentro de esa carpeta**.

**Para actualizar el proyecto (si ya lo tenías descargado):**
```
cd agente-traductor-subtitulos
git pull
```
Haz esto cada vez que quieras recibir las últimas mejoras o correcciones.

> 💡 **¿No tienes Git instalado?** Descárgalo desde [git-scm.com](https://git-scm.com/downloads) e instálalo como cualquier otro programa. Durante la instalación puedes dejar todas las opciones por defecto. Una vez instalado, abre una terminal nueva y escribe `git --version` para comprobar que funciona.

---

### 4. Las librerías de Python

Las librerías son extensiones que añaden funcionalidades extra a Python. Este proyecto usa tres:

| Librería | ¿Para qué sirve? |
|---|---|
| `langchain` | Orquesta la comunicación entre el prompt y el modelo |
| `langchain-ollama` | Conecta LangChain con Ollama |
| `langchain-core` | Componentes base de LangChain (prompts, parsers) |

Instálalas todas de una vez ejecutando este comando en la terminal, **dentro de la carpeta del proyecto**:

```
pip install -r requirements.txt
```

---

## Estructura del proyecto

```
agente-traductor-subtitulos/
│
├── traductor-subtitulos.py     ← el script principal (empieza aquí)
│
├── subtitulos.srt              ← tu archivo de subtítulos en español (lo pones tú)
│
├── requirements.txt            ← lista de librerías necesarias
├── pyproject.toml              ← metadatos del proyecto
├── .gitignore                  ← archivos que no se suben a GitHub
└── LICENSE                     ← licencia MIT
```

---

## Cómo usarlo

**Paso 1.** Coloca tu archivo de subtítulos en español en la carpeta raíz del proyecto y asegúrate de que se llama `subtitulos.srt` (o cambia el nombre en el script).

**Paso 2.** Abre `traductor-subtitulos.py` y edita las cuatro variables de la **Sección 2** según el idioma que necesites:

```python
IDIOMA_ORIGEN  = "Spanish"   # No cambiar si el original es en español
CODIGO_ORIGEN  = "es"        # No cambiar si el original es en español
IDIOMA_DESTINO = "English"   # Cambia aquí el nombre del idioma destino
CODIGO_DESTINO = "en"        # Cambia aquí el código ISO del idioma destino
```

Algunos ejemplos de idiomas soportados por TranslateGemma:

| Idioma | Código |
|---|---|
| English | `en` |
| French | `fr` |
| Italian | `it` |
| German | `de` |
| Russian | `ru` |
| Hindi | `hi` |
| Korean | `ko` |
| Ukrainian | `uk` |
| Serbian | `sr` |

**Paso 3.** Asegúrate de que Ollama está en marcha (en macOS y Windows arranca solo al instalarse; en Linux ejecuta `ollama serve` en una terminal aparte).

**Paso 4.** Ejecuta el script desde la terminal, **desde la carpeta raíz del proyecto**:
```
python traductor-subtitulos.py
```

El resultado se guardará automáticamente como `subtitulos_en.srt` (o el código del idioma que hayas elegido).

---

## Problemas frecuentes

**`ModuleNotFoundError: No module named 'langchain'`**
→ Las librerías no están instaladas. Ejecuta `pip install -r requirements.txt`.

**`Connection refused` o error al conectar con Ollama**
→ Ollama no está en marcha. Ábrelo como aplicación o ejecuta `ollama serve` en la terminal.

**`model 'translategemma' not found`**
→ El modelo no se ha descargado todavía. Ejecuta `ollama pull translategemma`.

---

## Licencia

MIT License — © 2026 Enrique Aranda Varela.
Consulta el archivo [LICENSE](LICENSE) para más detalles.
