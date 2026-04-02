import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
import os

# ------------------ FUNCIONES HISTORIAL ------------------

def cargar_historial():
    if os.path.exists("historial.json"):
        with open("historial.json", "r") as f:
            return json.load(f)
    return []

def guardar_historial(data):
    with open("historial.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------ ESTADO ------------------

if "historial" not in st.session_state:
    st.session_state.historial = cargar_historial()

if "codigo_generado" not in st.session_state:
    st.session_state.codigo_generado = ""

# ------------------ CLASE IA ------------------

class DemianIA:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generar_codigo(self, prompt, lenguaje):
        try:
            system_prompt = f"""
Eres Demian IA, experto en programación.
Genera código {lenguaje} limpio, funcional y bien comentado.

Incluye:
- Explicación
- Manejo de errores
- Buenas prácticas
- Ejemplo de uso

NO generes hacks ni cosas ilegales.
"""

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            respuesta = ""
            placeholder = st.empty()

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    respuesta += chunk.choices[0].delta.content
                    placeholder.code(respuesta, language=lenguaje)

            return respuesta

        except Exception as e:
            return f"Error: {str(e)}"

# ------------------ CONFIG APP ------------------

st.set_page_config(
    page_title="Demian IA",
    page_icon="🤖",
    layout="wide"
)

# Modo oscuro simple
st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Demian IA")
st.markdown("---")

# ------------------ SIDEBAR ------------------

with st.sidebar:
    st.header("⚙️ Configuración")

    api_key = st.text_input("API Key:", type="password")

    lenguaje = st.selectbox(
        "Lenguaje:",
        ["python", "javascript", "java", "cpp", "html-css", "react", "flutter"]
    )

    ejemplos = {
        "Calculadora": "Crea una calculadora científica completa",
        "API REST": "Servidor Flask con CRUD y JWT",
        "Juego": "Juego Snake en Pygame",
        "Bot": "Bot de Telegram que responde mensajes"
    }

    ejemplo = st.selectbox("Ejemplo:", list(ejemplos.keys()))

# Validar API
if not api_key:
    st.warning("⚠️ Pon tu API Key")
    st.stop()

demian = DemianIA(api_key)

# ------------------ MAIN ------------------

col1, col2 = st.columns([2, 1])

with col1:
    st.header("✨ Generar Código")

    prompt = st.text_area("Describe lo que quieres:")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🚀 Generar"):
            if prompt:
                resultado = demian.generar_codigo(prompt, lenguaje)
                st.session_state.codigo_generado = resultado

                nuevo = {
                    "prompt": prompt,
                    "lenguaje": lenguaje,
                    "codigo": resultado,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                st.session_state.historial.append(nuevo)
                guardar_historial(st.session_state.historial)

    with c2:
        if st.button("🔥 Ejemplo"):
            prompt = ejemplos[ejemplo]
            resultado = demian.generar_codigo(prompt, lenguaje)
            st.session_state.codigo_generado = resultado

# ------------------ HISTORIAL ------------------

with col2:
    st.header("📋 Historial")

    for item in st.session_state.historial[-5:]:
        with st.expander(f"{item['lenguaje']} - {item['fecha']}"):
            st.code(item["codigo"], language=item["lenguaje"])

# ------------------ RESULTADO ------------------

if st.session_state.codigo_generado:
    st.header("💻 Resultado")

    extensiones = {
        "python": "py",
        "javascript": "js",
        "java": "java",
        "cpp": "cpp",
        "html-css": "html",
        "react": "jsx",
        "flutter": "dart"
    }

    ext = extensiones.get(lenguaje, "txt")

    st.download_button(
        "💾 Descargar",
        st.session_state.codigo_generado,
        file_name=f"demian_{datetime.now().strftime('%H%M')}.{ext}"
    )

    st.code(st.session_state.codigo_generado, language=lenguaje)

    if st.button("🔄 Limpiar"):
        st.session_state.codigo_generado = ""

# ------------------ FOOTER ------------------

st.markdown("---")
st.markdown("Demian IA ⚡ Generación de código inteligente")
