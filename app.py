import os
import unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Ficha Técnica - Fortaleza F.C.",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #f4f6f9; }
    .header-box {
        background: linear-gradient(90deg, #8B0000 0%, #B22222 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 25px;
    }
    .header-box h1 { color: white; font-size: 26px; margin: 0; font-weight: 700; }
    .header-box p { color: #ffcccc; font-size: 13px; margin: 5px 0 0; text-transform: uppercase; }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_datos():
  try:
    return pd.read_excel("DATOS INDIVIDUALES.xlsx", sheet_name="individual")
  except:
    return pd.read_excel("DATOS INDIVIDUALES.xlsx", sheet_name=0)


try:
  df_raw = cargar_datos()
except Exception as e:
  st.error(f"Error al leer el Excel: {e}")
  st.stop()

st.sidebar.markdown("### ⚙️ Panel de Control")
st.sidebar.markdown("---")

col_nombre_candidatas = [
    c
    for c in df_raw.columns
    if any(k in str(c).lower() for k in ["nombre", "jug", "player"])
]
columna_nombre = (
    col_nombre_candidatas[0] if col_nombre_candidatas else df_raw.columns[3]
)

lista_jugadores = sorted(df_raw[columna_nombre].dropna().unique())
jugador_seleccionado = st.sidebar.selectbox(
    "Selecciona el Jugador:", lista_jugadores
)

# --- FILTRADO 100% ESTRICTO DE DATOS ---
df_jugador = df_raw[df_raw[columna_nombre] == jugador_seleccionado]

# --- BÚSQUEDA INTELIGENTE Y SEGURA DE FOTO ---
current_dir = os.getcwd()
contenido_directorio = os.listdir(current_dir)

ruta_foto = None
carpeta_fotos_real = None
for d in contenido_directorio:
  if d.strip().lower() == "fotos":
    carpeta_fotos_real = os.path.join(current_dir, d)
    break


def limpiar_texto(texto):
  return "".join(
      c
      for c in unicodedata.normalize("NFD", str(texto))
      if unicodedata.category(c) != "Mn"
  ).lower()


archivo_encontrado = None
if carpeta_fotos_real:
  archivos_fotos = [
      f for f in os.listdir(carpeta_fotos_real) if not f.startswith(".")
  ]

  # Palabras clave del jugador seleccionado en el Excel
  tokens_jugador = set(
      [p for p in limpiar_texto(jugador_seleccionado).split() if len(p) > 1]
  )

  for archivo in archivos_fotos:
    nombre_archivo_sin_ext = os.path.splitext(archivo)[0]
    tokens_archivo = set(
        [p for p in limpiar_texto(nombre_archivo_sin_ext).split() if len(p) > 1]
    )

    # Valida que las palabras de la foto correspondan al jugador sin mezclarse con otros
    if tokens_archivo and tokens_archivo.issubset(tokens_jugador):
      archivo_encontrado = archivo
      ruta_foto = os.path.join(carpeta_fotos_real, archivo)
      break

if not ruta_foto or not os.path.exists(ruta_foto):
  ruta_foto = "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80"

# --- INTERFAZ VISUAL LIMPIA ---
st.markdown(
    f"""
    <div class="header-box">
        <h1>FORTALEZA F.C. - SUB-20</h1>
        <p>Ficha Técnica Individual y Rendimiento</p>
    </div>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 2.5])

with col1:
  st.image(ruta_foto, use_container_width=True)
  st.markdown(f"### **{jugador_seleccionado}**")
  if archivo_encontrado:
    st.success(f"Foto oficial: {archivo_encontrado}")
  else:
    st.info("Sin fotografía oficial registrada.")

with col2:
  st.markdown("### **📊 Resumen de Rendimiento y Registros**")

  if not df_jugador.empty:
    st.dataframe(df_jugador, use_container_width=True)
  else:
    st.warning("No hay registros disponibles para este jugador.")