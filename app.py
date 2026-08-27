import os
import unicodedata
import pandas as pd
import plotly.graph_objects as go
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

# --- FILTRADO 100% ESTRICTO DE DATOS (EVITA MEZCLAS) ---
df_jugador = df_raw[df_raw[columna_nombre] == jugador_seleccionado]

# --- BÚSQUEDA ESTRICTA DE FOTO (EVITA CRUCES) ---
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

  nombre_limpio = limpiar_texto(jugador_seleccionado)
  partes_nombre = [p for p in nombre_limpio.split() if len(p) > 2]

  for archivo in archivos_fotos:
    archivo_limpio = limpiar_texto(archivo)
    if partes_nombre and all(
        parte in archivo_limpio for parte in partes_nombre
    ):
      archivo_encontrado = archivo
      break

  if archivo_encontrado:
    ruta_foto = os.path.join(carpeta_fotos_real, archivo_encontrado)

if not ruta_foto or not os.path.exists(ruta_foto):
  ruta_foto = "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80"

# --- INTERFAZ VISUAL PRINCIPAL ---
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
  if not archivo_encontrado:
    st.info("Sin fotografía oficial registrada.")
  else:
    st.success("Fotografía sincronizada.")

with col2:
  st.markdown("### **📊 Perfil de Rendimiento y Métricas**")

  if not df_jugador.empty:
    cols_numericas = df_jugador.select_dtypes(
        include=["float64", "int64"]
    ).columns.tolist()

    # CORRECCIÓN DE LA COMA INVALIDA AQUÍ:
    cols_radar = [
        c
        for c in cols_numericas
        if not any(
            x in str(c).lower() for x in ["id", "fecha", "partido", "jornada"]
        )
    ]

    if len(cols_radar) >= 3:
      valores_jugador = df_jugador[cols_radar].mean().tolist()
      categorias = cols_radar

      fig = go.Figure()
      fig.add_trace(
          go.Scatterpolar(
              r=valores_jugador,
              theta=categorias,
              fill="toself",
              name=jugador_seleccionado,
              line_color="#B22222",
              fillcolor="rgba(178, 34, 34, 0.4)",
          )
      )

      fig.update_layout(
          polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
          showlegend=False,
          margin=dict(t=30, b=30, l=30, r=30),
          height=350,
      )

      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info(
          "Se muestran las métricas detalladas en tabla (métricas numéricas"
          " insuficientes para radar automático)."
      )

    st.markdown("#### **Historial de Registros Individuales**")
    st.dataframe(df_jugador, use_container_width=True)
  else:
    st.warning("No hay registros disponibles para este jugador.")