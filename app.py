import os
import unicodedata
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Perfil de Rendimiento - Fortaleza F.C.",
    initial_sidebar_state="expanded",
)

# Estilos CSS idénticos al diseño original
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(90deg, #990000 0%, #B22222 100%);
        padding: 18px;
        border-radius: 6px;
        color: white;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 25px;
    }
    .header-box h1 { color: white; font-size: 24px; margin: 0; font-weight: 700; letter-spacing: 1px; }
    .header-box p { color: #f0f0f0; font-size: 12px; margin: 5px 0 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .player-name {
        font-size: 20px;
        font-weight: 800;
        text-align: center;
        margin-top: 10px;
        color: #111;
        text-transform: uppercase;
    }
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

# Detección de columna de nombres
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

# --- BÚSQUEDA SEGURA DE FOTO (BLINDADA CONTRA CRUCES) ---
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
  tokens_jugador = set(
      [p for p in limpiar_texto(jugador_seleccionado).split() if len(p) > 1]
  )

  for archivo in archivos_fotos:
    nombre_archivo_sin_ext = os.path.splitext(archivo)[0]
    tokens_archivo = set(
        [p for p in limpiar_texto(nombre_archivo_sin_ext).split() if len(p) > 1]
    )
    if tokens_archivo and tokens_archivo.issubset(tokens_jugador):
      archivo_encontrado = archivo
      ruta_foto = os.path.join(carpeta_fotos_real, archivo)
      break

if not ruta_foto or not os.path.exists(ruta_foto):
  ruta_foto = "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80"

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    """
    <div class="header-box">
        <h1>PERFIL DE RENDIMIENTO DEL JUGADOR</h1>
        <p>DEPARTAMENTO DE RENDIMIENTO | FORTALEZA F.C.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- EXTRACCIÓN SEGURA DE DATOS PERSONALES Y ACUMULADOS ---
row_p = df_jugador.iloc[0] if not df_jugador.empty else {}


def get_val(keywords, default="-"):
  for col in df_jugador.columns:
    if any(k in str(col).lower() for k in keywords):
      val = row_p.get(col, default)
      return val if pd.notna(val) else default
  return default


posicion = get_val(["pos", "posición"])
depto = get_val(["depto", "departamento"])
talla = get_val(["talla", "altura"])
peso = get_val(["peso"])
nacimiento = get_val(["nacimiento", "mes"])
valoracion = get_val(["valoración", "valoracion", "nota"])

total_fechas = len(df_jugador)


def get_sum(keywords):
  for col in df_jugador.columns:
    if any(k in str(col).lower() for k in keywords):
      try:
        return int(df_jugador[col].sum())
      except:
        pass
  return 0


min_jugados = get_sum(["min", "minutos"])
goles = get_sum(["gol", "goles"])
asistencias = get_sum(["asist"])
autogoles = get_sum(["autogol"])

# --- DISEÑO SUPERIOR (FOTO + DATOS PERSONALES + ACUMULADO) ---
col_foto, col_info = st.columns([1, 2.3])

with col_foto:
  st.image(ruta_foto, use_container_width=True)
  st.markdown(
      f'<div class="player-name">{jugador_seleccionado}</div>',
      unsafe_allow_html=True,
  )

with col_info:
  st.markdown("### 👤 Datos Personales &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 🏆 Acumulado Temporada")
  
  c_dat, c_acu = st.columns(2)
  
  with c_dat:
    st.markdown(f"**Posición:** {posicion} &nbsp;|&nbsp; **Depto:** {depto}")
    st.markdown(f"**Talla:** {talla} &nbsp;|&nbsp; **Peso:** {peso}")
    st.markdown(f"**Nacimiento:** {nacimiento}")
    st.markdown(f"**Valoración:** {valoracion}")
    
  with c_acu:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Min. Jugados", min_jugados)
    m2.metric("Goles", goles)
    m3.metric("Asistencias", asistencias)
    m4.metric("Autogoles", autogoles)

st.markdown("---")

# --- DISEÑO INFERIOR (RADAR + MÉTRICAS GPS) ---
col_radar, col_gps = st.columns([1, 1.2])

with col_radar:
  st.markdown("### 🧬 Perfil Físico y Carga (Promedio)")
  
  # Selección de métricas numéricas para el radar estilo araña
  cols_numericas = df_jugador.select_dtypes(include=["float64", "int64"]).columns.tolist()
  cols_radar = [
      c for c in cols_numericas
      if not any(x in str(c).lower() for x in ["id", "fecha", "partido", "jornada", "año", "talla", "peso", "número", "numero"])
  ]

  if len(cols_radar) >= 3 and not df_jugador.empty:
    valores_jugador = df_jugador[cols_radar].mean().tolist()
    categorias = cols_radar

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=valores_jugador,
            theta=categorias,
            fill="toself",
            name=jugador_seleccionado,
            line_color="#990000",
            fillcolor="rgba(153, 0, 0, 0.35)",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(100, max(valores_jugador) * 1.1 if valores_jugador else 100)])),
        showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.info("Métricas suficientes para generar el radar físico no disponibles.")

with col_gps:
  st.markdown("### 🛰️ Métricas de Carga GPS (Promedio por Partido)")
  
  if not df_jugador.empty:
    # Cálculo de promedios para métricas comunes de GPS
    def get_promedio(keywords):
      for col in df_jugador.columns:
        if any(k in str(col).lower() for k in keywords):
          try:
            val = df_jugador[col].mean()
            return f"{val:.1f}"
          except:
            pass
      return "0.0"

    pl = get_promedio(["player load", "pl"])
    hsr = get_promedio(["hsr", "alta intensidad", "high speed"])
    td = get_promedio(["distancia total", "td"])
    sprints = get_promedio(["sprint"])
    min_km = get_promedio(["min/min", "metros/minuto", "m_min"])
    acc = get_promedio(["aceleracion", "acc"])
    vel_max = get_promedio.get("velocidad", get_promedio(["maxvel", "velocidad"]))
    dec = get_promedio(["desaceleracion", "dec"])

    g1, g2 = st.columns(2)
    with g1:
      st.metric("Player Load (PL)", pl)
      st.metric("Distancia Total (TD)", td + " m" if td != "0.0" else "0.0")
      st.metric("Metros / Minuto", min_km)
      st.metric("Velocidad Máx", vel_max + " km/h" if vel_max != "0.0" else "0.0")
    with g2:
      st.metric("Alta Intensidad (HSR)", hsr + " m" if hsr != "0.0" else "0.0")
      st.metric("Sprints (>25km/h)", sprints)
      st.metric("Aceleraciones (acc)", acc)
      st.metric("Desaceleraciones (dec)", dec)
  else:
    st.warning("Sin datos GPS registrados.")

st.markdown("---")
with st.expander("📋 Ver Historial Detallado de Registros (Todas las Fechas)"):
  if not df_jugador.empty:
    st.dataframe(df_jugador, use_container_width=True)
  else:
    st.warning("No hay registros disponibles.")