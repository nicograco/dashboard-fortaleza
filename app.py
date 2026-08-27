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

col_nombre_candidatas = [
    c
    for c in df_raw.columns
    if any(k in str(c).lower() for k in ["nombre", "jug", "player"])
]
columna_nombre = (
    col_nombre_candidatas[0] if col_nombre_candidatas else df_raw.columns[3]
)


# --- UNIFICACIÓN BLINDADA DE NOMBRES (ELIMINA DUPLICADOS) ---
def armonizar_nombres(nombre):
  n = str(nombre).strip().title()
  n_norm = "".join(
      c
      for c in unicodedata.normalize("NFD", n)
      if unicodedata.category(c) != "Mn"
  ).lower()
  if "adrian mosquera" in n_norm:
    return "Adrian Mosquera Renteria"
  return n


df_raw[columna_nombre] = df_raw[columna_nombre].apply(armonizar_nombres)

lista_jugadores = sorted(df_raw[columna_nombre].dropna().unique())
jugador_seleccionado = st.sidebar.selectbox(
    "Selecciona el Jugador:", lista_jugadores
)

# --- FILTRADO ESTRICTO DE DATOS ---
df_jugador = df_raw[df_raw[columna_nombre] == jugador_seleccionado]


def limpiar_texto(texto):
  return (
      "".join(
          c
          for c in unicodedata.normalize("NFD", str(texto))
          if unicodedata.category(c) != "Mn"
      )
      .lower()
      .replace("-", " ")
      .replace("_", " ")
  )


# --- BÚSQUEDA DE FOTO ---
current_dir = os.getcwd()
ruta_foto = None
archivo_encontrado = None
carpeta_fotos_real = None

for root, dirs, files in os.walk(current_dir):
  for d in dirs:
    if d.strip().lower() in ["fotos", "photo", "photos"]:
      carpeta_fotos_real = os.path.join(root, d)
      break
  if carpeta_fotos_real:
    break

if carpeta_fotos_real:
  archivos_fotos = [
      f
      for f in os.listdir(carpeta_fotos_real)
      if not f.startswith(".")
      and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
  ]

  nombre_limpio_jugador = limpiar_texto(jugador_seleccionado)
  tokens_jugador = [p for p in nombre_limpio_jugador.split() if len(p) >= 3]

  mejor_archivo = None

  for archivo in archivos_fotos:
    nombre_sin_ext = os.path.splitext(archivo)[0]
    nombre_limpio_archivo = limpiar_texto(nombre_sin_ext)
    tokens_archivo = [p for p in nombre_limpio_archivo.split() if len(p) >= 3]

    if nombre_limpio_archivo == nombre_limpio_jugador:
      mejor_archivo = archivo
      break

    match_encontrado = False
    for ta in tokens_archivo:
      for tj in tokens_jugador:
        if (
            ta == tj
            or (
                len(ta) >= 4
                and len(tj) >= 4
                and (ta[:4] == tj[:4] or ta in tj or tj in ta)
            )
            or (len(tokens_archivo) == 1 and ta in tj)
        ):
          match_encontrado = True
          break
      if match_encontrado:
        break

    if match_encontrado:
      mejor_archivo = archivo
      if len(tokens_archivo) == 1:
        break

  if mejor_archivo:
    archivo_encontrado = mejor_archivo
    ruta_foto = os.path.join(carpeta_fotos_real, mejor_archivo)

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

# --- DISEÑO SUPERIOR (FOTO + DATOS PERSONALES Y ACUMULADOS) ---
col_foto, col_info = st.columns([1, 2.3])

with col_foto:
  if ruta_foto and os.path.exists(ruta_foto):
    st.image(ruta_foto, use_container_width=True)
  else:
    st.markdown(
        """
        <div style="border: 2px dashed #ccc; border-radius: 8px; padding: 60px 20px; text-align: center; color: #666; background-color: #fff;">
            <b>Sin fotografía oficial registrada</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown(
      f'<div class="player-name">{jugador_seleccionado}</div>',
      unsafe_allow_html=True,
  )
  if archivo_encontrado:
    st.caption(f"📁 Foto oficial: {archivo_encontrado}")

with col_info:
  st.markdown(
      "### 👤 Datos Personales &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
      " 🏆 Acumulado Temporada (Suma Total)"
  )

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

# --- DISEÑO INFERIOR (RADAR COMPARATIVO VS POSICIÓN Y MÉTRICAS GPS) ---
col_radar, col_gps = st.columns([1, 1.2])

with col_radar:
  st.markdown(
      f"### 🧬 Perfil Físico: {jugador_seleccionado} vs Promedio ({posicion})"
  )

  cols_numericas = df_jugador.select_dtypes(
      include=["float64", "int64"]
  ).columns.tolist()
  metricas_objetivo = [
      "pl",
      "td",
      "m_min",
      "hsr",
      "sprint25",
      "acc",
      "dec",
      "maxvel",
  ]
  cols_radar = []

  for c in cols_numericas:
    c_lower = str(c).lower()
    if any(m in c_lower for m in metricas_objetivo):
      cols_radar.append(c)

  if len(cols_radar) >= 3 and not df_jugador.empty:
    col_pos_candidatas = [
        c
        for c in df_raw.columns
        if any(k in str(c).lower() for k in ["pos", "posición", "position"])
    ]
    col_pos = (
        col_pos_candidatas[0] if col_pos_candidatas else df_raw.columns[2]
    )

    df_misma_posicion = df_raw[df_raw[col_pos] == posicion]

    promedios_jugador = df_jugador[cols_radar].mean()
    promedios_posicion = df_misma_posicion[cols_radar].mean()

    valores_jugador_norm = []
    valores_posicion_norm = []
    categorias = []

    for c in cols_radar:
      max_equipo = df_raw[c].max()
      val_jug = promedios_jugador[c] if pd.notna(promedios_jugador[c]) else 0
      val_pos = (
          promedios_posicion[c] if pd.notna(promedios_posicion[c]) else 0
      )

      if max_equipo > 0:
        valores_jugador_norm.append(min((val_jug / max_equipo) * 100, 100))
        valores_posicion_norm.append(min((val_pos / max_equipo) * 100, 100))
      else:
        valores_jugador_norm.append(0)
        valores_posicion_norm.append(0)

      categorias.append(c.upper())

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=valores_posicion_norm,
            theta=categorias,
            fill="toself",
            name=f"Promedio Posición ({posicion})",
            line_color="#2b5c8f",
            fillcolor="rgba(43, 92, 143, 0.2)",
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=valores_jugador_norm,
            theta=categorias,
            fill="toself",
            name=jugador_seleccionado,
            line_color="#990000",
            fillcolor="rgba(153, 0, 0, 0.35)",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")
        ),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1
        ),
        margin=dict(t=40, b=20, l=40, r=40),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.info("Métricas suficientes para generar el radar físico no disponibles.")

with col_gps:
  st.markdown("### 🛰️ Métricas de Carga GPS (Promedio por Partido)")

  if not df_jugador.empty:

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
    vel_max = get_promedio(["maxvel", "velocidad"])
    dec = get_promedio(["desaceleracion", "dec"])

    g1, g2 = st.columns(2)
    with g1:
      st.metric("Player Load (PL)", pl)
      st.metric("Distancia Total (TD)", td + " m" if td != "0.0" else "0.0")
      st.metric("Metros / Minuto", min_km)
      st.metric(
          "Velocidad Máx", vel_max + " km/h" if vel_max != "0.0" else "0.0"
      )
    with g2:
      st.metric("Alta Intensidad (HSR)", hsr + " m" if hsr != "0.0" else "0.0")
      st.metric("Sprints (>25km/h)", sprints)
      st.metric("Aceleraciones (acc)", acc)
      st.metric("Desaceleraciones (dec)", dec)
  else:
    st.warning("Sin datos GPS registrados.")

st.markdown("---")

# --- SECCIÓN: GRÁFICO DE EVOLUCIÓN LONGITUDINAL + ANÁLISIS AUTOMATIZADO ---
st.markdown("### 📈 Evolución Longitudinal y Análisis de Rendimiento")

if not df_jugador.empty and len(cols_numericas) >= 2:
  col_fecha_candidatas = [
      c
      for c in df_jugador.columns
      if any(
          k in str(c).lower() for k in ["fecha", "date", "jornada", "partido"]
      )
  ]
  col_fecha = (
      col_fecha_candidatas[0] if col_fecha_candidatas else df_jugador.columns[0]
  )

  df_jugador_ordenado = df_jugador.sort_values(by=col_fecha)

  c_sel1, c_sel2 = st.columns(2)
  with c_sel1:
    default_m1_idx = 0
    for i, c in enumerate(cols_numericas):
      if any(k in c.lower() for k in ["pl", "load"]):
        default_m1_idx = i
        break
    metrica_1 = st.selectbox(
        "Selecciona Métrica (Eje Izquierdo 🔴):",
        cols_numericas,
        index=default_m1_idx,
    )

  with c_sel2:
    default_m2_idx = 1 if len(cols_numericas) > 1 else 0
    for i, c in enumerate(cols_numericas):
      if any(k in c.lower() for k in ["hsr", "sprint", "dist"]):
        default_m2_idx = i
        break
    metrica_2 = st.selectbox(
        "Selecciona Métrica (Eje Derecho 🔵):",
        cols_numericas,
        index=default_m2_idx,
    )

  fig_tendencia = go.Figure()

  fig_tendencia.add_trace(
      go.Scatter(
          x=df_jugador_ordenado[col_fecha],
          y=df_jugador_ordenado[metrica_1],
          mode="lines+markers",
          name=str(metrica_1).upper(),
          line=dict(color="#990000", width=3),
      )
  )

  fig_tendencia.add_trace(
      go.Scatter(
          x=df_jugador_ordenado[col_fecha],
          y=df_jugador_ordenado[metrica_2],
          mode="lines+markers",
          name=str(metrica_2).upper(),
          line=dict(color="#2b5c8f", width=3),
          yaxis="y2",
      )
  )

  fig_tendencia.update_layout(
      title=f"Progresión Temporal: {str(metrica_1).upper()} vs {str(metrica_2).upper()}",
      xaxis=dict(title="Fecha / Partido", type="category"),
      yaxis=dict(title=str(metrica_1).upper(), title_font=dict(color="#990000")),
      yaxis2=dict(
          title=str(metrica_2).upper(),
          title_font=dict(color="#2b5c8f"),
          overlaying="y",
          side="right",
      ),
      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
      margin=dict(t=40, b=40, l=40, r=40),
      height=400,
  )

  st.plotly_chart(fig_tendencia, use_container_width=True)

  # --- APARTADO DE ANÁLISIS AUTOMATIZADO Y SINTETIZADO ---
  try:
    val_max_1 = df_jugador_ordenado[metrica_1].max()
    prom_1 = df_jugador_ordenado[metrica_1].mean()
    row_pico_1 = df_jugador_ordenado.loc[
        df_jugador_ordenado[metrica_1].idxmax()
    ]
    fecha_pico_1 = row_pico_1[col_fecha]

    val_max_2 = df_jugador_ordenado[metrica_2].max()
    prom_2 = df_jugador_ordenado[metrica_2].mean()
    row_pico_2 = df_jugador_ordenado.loc[
        df_jugador_ordenado[metrica_2].idxmax()
    ]
    fecha_pico_2 = row_pico_2[col_fecha]

    total_partidos = len(df_jugador_ordenado)

    st.markdown(
        f"""
        <div style="background-color: #f1f3f5; border-left: 4px solid #2b5c8f; padding: 18px; border-radius: 6px; margin-top: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #111;">🧠 Análisis Automatizado de Rendimiento (Cuerpo Técnico)</h4>
            <ul style="margin: 0; padding-left: 20px; color: #333; font-size: 14px; line-height: 1.6;">
                <li><b>Participación Registrada:</b> El deportista cuenta con registros en <b>{total_partidos} partidos</b> evaluados en el periodo.</li>
                <li><b>Comportamiento de {str(metrica_1).upper()} (Eje Rojo):</b> Presenta un promedio general de <b>{prom_1:.1f}</b> por partido, alcanzando su rendimiento cumbre de <b>{val_max_1}</b> en la jornada <i>{fecha_pico_1}</i>.</li>
                <li><b>Comportamiento de {str(metrica_2).upper()} (Eje Azul):</b> Mantiene un promedio de <b>{prom_2:.1f}</b> con un pico máximo de <b>{val_max_2}</b> registrado en la fecha <i>{fecha_pico_2}</i>.</li>
                <li><b>Interpretación Analítica:</b> Este cruce permite identificar las semanas de mayor exigencia competitiva. La sincronización de picos en ambas métricas refleja partidos de alta intensidad global, mientras que las variaciones individuales ayudan a calibrar las cargas de trabajo de cara a la planificación semanal.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
  except Exception as err:
    st.info("Generando métricas analíticas...")

else:
  st.warning("No hay suficientes registros numéricos para mostrar la tendencia.")

st.markdown("---")
with st.expander("📋 Ver Historial Detallado de Registros (Todas las Fechas)"):
  if not df_jugador.empty:
    st.dataframe(df_jugador, use_container_width=True)
  else:
    st.warning("No hay registros disponibles.")