import os
import zipfile
import streamlit as st
import mammoth

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="CARVIMSA - PLANTA MOLINO",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS REFORZADOS (ESTILO CARVIMSA ORIGINAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1b2a !important; color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: #1b263b !important; border-right: 1px solid #415a77; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stButton > button { background-color: #1e293b !important; color: #e2e8f0 !important; border: 1px solid #415a77 !important; text-align: left !important; display: block !important; width: 100% !important; padding: 10px !important; font-size: 13px !important; border-radius: 6px !important; }
    .stButton > button:hover { border-color: #38bdf8 !important; background-color: #0f172a !important; color: #38bdf8 !important; }
    .banner-principal { background: linear-gradient(135deg, #0077b6, #0096c7); padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .contenedor-vista-previa { background-color: #ffffff !important; color: #1e293b !important; padding: 30px; border-radius: 10px; border: 3px solid #0077b6; min-height: 500px; font-family: 'Segoe UI', sans-serif; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-top: 15px; overflow-y: auto; max-height: 750px; }
    .contenedor-vista-previa h1, .contenedor-vista-previa h2, .contenedor-vista-previa h3 { color: #0f172a !important; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; margin-top: 15px; }
    .contenedor-vista-previa p, .contenedor-vista-previa li, .contenedor-vista-previa td, .contenedor-vista-previa tr { font-size: 16px !important; line-height: 1.6 !important; color: #1e293b !important; }
    .contenedor-vista-previa table { border-collapse: collapse; width: 100%; margin-top: 15px; }
    .contenedor-vista-previa th, .contenedor-vista-previa td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE PESTAÑAS Y MAPEO DE ZIPs ---
opciones_zip = {
    "🔴 Prioridad 1": ("1parte.zip", "2parte.zip"),
    "🟠 Prioridad 2": ("PRIORIDAD 2.zip",),
    "🟡 Prioridad 3": ("PRIORIDAD 3.zip",),
    "🟢 Prioridad 4": ("PRIORIDAD 4.zip",),
    "🟣 Prioridad 5": ("PRIORIDAD 5.zip",)
}

pestanas = list(opciones_zip.keys())
pestana_seleccionada = st.radio("📁 SELECCIONA LA PRIORIDAD A CONSULTAR:", pestanas, horizontal=True)
archivos_zip_a_leer = opciones_zip[pestana_seleccionada]

if "archivo_activo_zip" not in st.session_state:
    st.session_state.archivo_activo_zip = None
if "ultima_pestana" not in st.session_state:
    st.session_state.ultima_pestana = pestana_seleccionada

if st.session_state.ultima_pestana != pestana_seleccionada:
    st.session_state.archivo_activo_zip = None
    st.session_state.ultima_pestana = pestana_seleccionada

# --- LECTURA PROFUNDA DE SUB-CARPETAS Y ARCHIVOS ---
subcarpetas_detectadas = set()
mapa_archivos_origen = {}
todos_los_archivos_zip = []

for zip_file_name in archivos_zip_a_leer:
    if os.path.exists(zip_file_name):
        try:
            with zipfile.ZipFile(zip_file_name, 'r') as z:
                for f in z.namelist():
                    if f.lower().endswith('.docx') and not f.startswith('__MACOSX') and not os.path.basename(f).startswith('.') and not os.path.basename(f).startswith('~$'):
                        todos_los_archivos_zip.append(f)
                        mapa_archivos_origen[f] = zip_file_name
                        partes_ruta = f.split('/')
                        if len(partes_ruta) > 1:
                            subcarpetas_detectadas.add(partes_ruta[-2])
        except Exception as e:
            st.sidebar.error(f"Error al leer {zip_file_name}: {str(e)}")

todos_los_archivos_zip.sort()

# --- 1. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom:0;'>CARVIMSA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#94a3b8; text-align:center; margin-top:0;'>GRUPO COMECA - PERÚ</p>", unsafe_allow_html=True)
    st.write("---")
    
    if subcarpetas_detectadas:
        lista_carpetas_sidebar = ["📁 Ver todas las carpetas"] + sorted(list(subcarpetas_detectadas))
        carpeta_seleccionada = st.selectbox("📂 Clasificación por subcarpetas:", lista_carpetas_sidebar)
    else:
        carpeta_seleccionada = "📁 Ver todas las carpetas"
        
    st.write("---")
    buscar = st.text_input("🔍 Filtrar por nombre en esta lista:", placeholder="Escribe aquí para buscar...")
    st.write("---")
    
    if carpeta_seleccionada != "📁 Ver todas las carpetas":
        archivos_filtrados = [f for f in todos_los_archivos_zip if len(f.split('/')) > 1 and f.split('/')[-2] == carpeta_seleccionada]
    else:
        archivos_filtrados = todos_los_archivos_zip
        
    if buscar:
        archivos_mostrar = [f for f in archivos_filtrados if buscar.strip().lower() in os.path.basename(f).lower()]
    else:
        archivos_mostrar = archivos_filtrados

    st.markdown(f"### 📂 DOCUMENTOS ENCONTRADOS ({len(archivos_mostrar)})")
    
    if archivos_mostrar and st.session_state.archivo_activo_zip not in archivos_mostrar:
        st.session_state.archivo_activo_zip = archivos_mostrar[0]
        
    for f_path in archivos_mostrar:
        f_name_clean = os.path.basename(f_path)
        marca = "▶️ " if f_path == st.session_state.archivo_activo_zip else "📄 "
        if st.button(f"{marca}{f_name_clean}", key=f"btn_lista_{f_path}", use_container_width=True):
            st.session_state.archivo_activo_zip = f_path
            st.rerun()

# --- 2. CONTENEDOR DE VISTA PREVIA PRINCIPAL ---
st.markdown("""
    <div class="banner-principal">
        <span style="background-color:#ffffff; color:#0077b6; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold;">📌 CATÁLOGO DE PLANTA • VISTA PREVIA</span>
        <h1 style="color:white; margin-top:10px; margin-bottom:0; font-size:32px;">CARVIMSA - PLANTA MOLINO</h1>
        <p style="color:#e0e1dd; margin-top:5px; font-size:14px;">Consulta en tiempo real de documentos técnicos en pantalla.</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.archivo_activo_zip:
    archivo_actual = st.session_state.archivo_activo_zip
    nombre_limpio_pantalla = os.path.basename(archivo_actual)
    zip_origen = mapa_archivos_origen.get(archivo_actual)
    subcarpeta_origen = archivo_actual.split('/')[-2] if len(archivo_actual.split('/')) > 1 else "Raíz"
    
    st.markdown(f"<h3 style='color: #38bdf8;'>👁️ Vista Previa Activa: <span style='color: white;'>{nombre_limpio_pantalla}</span> <br><span style='font-size: 13px; color: #94a3b8;'>(Origen: 🗜️ {zip_origen} • Ubicación: 📁 {subcarpeta_origen})</span></h3>", unsafe_allow_html=True)
    
    if zip_origen and os.path.exists(zip_origen):
        try:
            with zipfile.ZipFile(zip_origen, 'r') as z:
                with z.open(archivo_actual) as docx_file:
                    resultado = mammoth.convert_to_html(docx_file, ignore_empty_paragraphs=True)
                    html_contenido = resultado.value
                    html_contenido = html_contenido.replace("<li>1. ", "<li style='list-style-type: none; margin-left: -15px;'>🔹 <b>")
                    if not html_contenido.strip():
                        html_contenido = "<p style='color: #64748b; font-style: italic;'>El documento seleccionado está vacío o no contiene texto legible.</p>"
                    st.download_button(label="📥 Descargar Word original", data=z.read(archivo_actual), file_name=nombre_limpio_pantalla, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dl_main_{archivo_actual}")
                    st.markdown(f'<div class="contenedor-vista-previa">{html_contenido}</div>', unsafe_allow_html=True)
        except Exception as err_lectura:
            st.error(f"Error: {str(err_lectura)}")
else:
    st.info("👈 Selecciona un archivo de la barra izquierda.")
