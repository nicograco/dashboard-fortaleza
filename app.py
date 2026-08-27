import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="Ficha Técnica - Fortaleza F.C.", initial_sidebar_state="expanded")

st.markdown("""
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
    .header-box p { color: #ffcccc; font-size: 13px; margin: 5px 0 0 0; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

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

col_nombre_candidatas = [c for c in df_raw.columns if any(k in str(c).lower() for k in ['nombre', 'jug', 'player'])]
columna_nombre = col_nombre_candidatas[0] if col_nombre_candidatas else df_raw.columns[3]

lista_jugadores = df_raw[columna_nombre].dropna().unique()
jugador_seleccionado = st.sidebar.selectbox("Seleccionar Jugador", lista_jugadores)

df_jugador = df_raw[df_raw[columna_nombre] == jugador_seleccionado]

def buscar_col(df, palabras):
    for col in df.columns:
        col_str = str(col).strip().lower()
        for p in palabras:
            if p.lower() in col_str:
                return col
    return None

c_min = buscar_col(df_jugador, ['min', 'min_jug', 'jugados'])
c_goles = buscar_col(df_jugador, ['goles', 'gol'])
c_autogoles = buscar_col(df_jugador, ['autogoles', 'autogol'])
c_asist = buscar_col(df_jugador, ['asist', 'asistencia'])

primera_fila = df_jugador.iloc[0]
def get_dato_fijo(palabras, defecto="N/A"):
    c = buscar_col(df_jugador, palabras)
    if c and pd.notna(primera_fila[c]):
        return primera_fila[c]
    return defecto

posicion = get_dato_fijo(['posición', 'posicion', 'pos'])
departamento = get_dato_fijo(['departamento', 'dept'])
talla = get_dato_fijo(['talla', 'altura'])
peso = get_dato_fijo(['peso'])
f_nac = get_dato_fijo(['fecha de nac', 'nacimiento', 'f_nac'])
a_nac = get_dato_fijo(['año', 'ano'], '')
valoracion = get_dato_fijo(['valoracion', 'valoración'])

total_min = df_jugador[c_min].sum() if c_min and pd.api.types.is_numeric_dtype(df_jugador[c_min]) else len(df_jugador)*90
total_goles = df_jugador[c_goles].sum() if c_goles and pd.api.types.is_numeric_dtype(df_jugador[c_goles]) else 0
total_autogoles = df_jugador[c_autogoles].sum() if c_autogoles and pd.api.types.is_numeric_dtype(df_jugador[c_autogoles]) else 0
total_asist = df_jugador[c_asist].sum() if c_asist and pd.api.types.is_numeric_dtype(df_jugador[c_asist]) else 0

def promedio_gps(palabras):
    c = buscar_col(df_jugador, palabras)
    if c and pd.api.types.is_numeric_dtype(df_jugador[c]):
        return df_jugador[c].mean()
    return 0.0

pl = promedio_gps(['pl'])
td = promedio_gps(['td'])
m_min = promedio_gps(['m_min'])
hsr = promedio_gps(['hsr'])
sprints = promedio_gps(['sprint25', 'sprint'])
acc = promedio_gps(['acc'])
dec = promedio_gps(['dec'])
maxvel = df_jugador[buscar_col(df_jugador, ['maxvel'])].max() if buscar_col(df_jugador, ['maxvel']) else 0.0

st.sidebar.markdown("---")
st.sidebar.info(f"🟢 **Fechas analizadas:** {len(df_jugador)} partidos")

st.markdown("""
    <div class="header-box">
        <h1>PERFIL DE RENDIMIENTO DEL JUGADOR</h1>
        <p>DEPARTAMENTO DE RENDIMIENTO | FORTALEZA F.C.</p>
    </div>
""", unsafe_allow_html=True)

# BUSCADOR DINÁMICO E INDIVIDUAL PARA CADA JUGADOR SELECCIONADO
current_dir = os.getcwd()
contenido_directorio = os.listdir(current_dir)

ruta_foto = None
mensaje_estado = ""

carpeta_fotos_real = None
for d in contenido_directorio:
    if d.strip().lower() == "fotos":
        carpeta_fotos_real = os.path.join(current_dir, d)
        break

if carpeta_fotos_real:
    archivos_fotos = [f for f in os.listdir(carpeta_fotos_real) if not f.startswith('.')]
    
    # Extraemos las palabras significativas del jugador que está seleccionado en el menú (ignorando palabras cortas)
    palabras_jugador = [p.lower() for p in str(jugador_seleccionado).split() if len(p) > 2]
    
    archivo_encontrado = None
    for archivo in archivos_fotos:
        archivo_lower = archivo.lower()
        # Verificamos si alguna de las palabras del jugador (nombre o apellido) coincide con este archivo
        if any(palabra in archivo_lower for palabra in palabras_jugador):
            archivo_encontrado = archivo
            break
            
    if archivo_encontrado:
        ruta_foto = os.path.join(carpeta_fotos_real, archivo_encontrado)
        mensaje_estado = f"¡Foto cargada para {jugador_seleccionado} ({archivo_encontrado})!"
    else:
        mensaje_estado = f"No hay foto en FOTOS para {jugador_seleccionado}."
else:
    mensaje_estado = "No se encontró la carpeta FOTOS."

if not ruta_foto or not os.path.exists(ruta_foto):
    ruta_foto = "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80"

col_foto, col_datos, col_competicion = st.columns([1.2, 1.8, 2.2])

with col_foto:
    st.image(ruta_foto, width=170)
    st.markdown(f"<h4 style='text-align: center; margin-top: 8px; color: #111;'>{jugador_seleccionado}</h4>", unsafe_allow_html=True)
    st.caption(f"🔍 {mensaje_estado}")

with col_datos:
    st.markdown("### 👤 Datos Personales")
    st.markdown(f"**Posición:** {posicion} &nbsp;|&nbsp; **Depto:** {departamento}")
    st.markdown(f"**Talla:** {talla} cm &nbsp;|&nbsp; **Peso:** {peso} kg")
    st.markdown(f"**Nacimiento:** {f_nac} (Año: {a_nac})")
    st.markdown(f"**Valoración:** {valoracion}")

with col_competicion:
    st.markdown("### 🏆 Acumulado Temporada (17 Fechas)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Min. Jugados", f"{int(total_min)}")
    c2.metric("Goles", f"{int(total_goles)}")
    c3.metric("Asistencias", f"{int(total_asist)}")
    c4.metric("Autogoles", f"{int(total_autogoles)}")

st.markdown("---")

col_radar, col_gps = st.columns([1, 1.2])

with col_radar:
    st.markdown("### 🧬 Perfil Físico y Carga (Promedio)")
    cats = ['Player Load (PL)', 'Distancia (TD)/100', 'HSR', 'Sprints']
    vals = [float(pl), float(td)/100 if td else 0, float(hsr), float(sprints)*10]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals, theta=cats, fill='toself', line_color='#8B0000', fillcolor='rgba(139, 0, 0, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=320)
    st.plotly_chart(fig, use_container_width=True)

with col_gps:
    st.markdown("### 📡 Métricas de Carga GPS (Promedio per Partido)")
    g1, g2 = st.columns(2)
    with g1:
        st.metric("Player Load (PL)", f"{pl:.1f}")
        st.metric("Distancia Total (TD)", f"{td:.1f} m")
        st.metric("Metros / Minuto", f"{m_min:.1f} m/min")
        st.metric("Velocidad Máx", f"{maxvel:.1f} km/h")
    with g2:
        st.metric("Alta Intensidad (HSR)", f"{hsr:.1f} m")
        st.metric("Sprints (>25km/h)", f"{sprints:.1f}")
        st.metric("Aceleraciones (acc)", f"{acc:.1f}")
        st.metric("Desaceleraciones (dec)", f"{dec:.1f}")