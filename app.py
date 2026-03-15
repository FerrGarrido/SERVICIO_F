import streamlit as st
import mysql.connector
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns

# === 0. Configuración de Estilo y Paleta de Colores ===
# Paleta de colores profesional y sobria
COLOR_PRIMARIO = "#264A6A"  # Azul oscuro/Gris azulado para títulos y botones
COLOR_FONDO_CLARO = "#F5F5F5" # Fondo claro general
COLOR_GRIS_OSCURO = "#333333" # Texto principal
COLOR_GRIS_SUAVE = "#AAAAAA"  # Texto secundario/Líneas

# Configuración de Seaborn/Matplotlib para un estilo profesional
sns.set_theme(
    style="whitegrid", 
    rc={
        'axes.edgecolor': COLOR_GRIS_SUAVE,
        'axes.labelcolor': COLOR_GRIS_OSCURO,
        'xtick.color': COLOR_GRIS_OSCURO,
        'ytick.color': COLOR_GRIS_OSCURO,
        'text.color': COLOR_GRIS_OSCURO,
        'grid.color': COLOR_FONDO_CLARO,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'patch.edgecolor': 'none', # Quitar bordes de barras
    }
)

# RUTA DE TU IMAGEN (Ajustada para Python/Streamlit)
RUTA_IMAGEN = "fudepa.png" 

# INSTRUCCIÓN CLAVE PARA EL TAMAÑO:
# Streamlit usa 'width' para controlar el tamaño. Aumentar este valor hará 
# que la imagen sea MÁS ANCHA y MÁS ALTA, manteniendo su proporción.
# MODIFICA ESTE VALOR (en píxeles) al tamaño que desees:
ANCHO_IMAGEN = 150 

# === 1. Conexión a la base de datos ===
@st.cache_data(ttl=600)
def cargar_datos():
    conexion = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=st.secrets["DB_PORT"]
    )
    
    consulta = """
    SELECT
        p.Nombre_pais AS Pais,
        d.Nombre_division_admin AS Division_Administrativa,
        i.Nombre_institucion AS Institucion,
        i.tipoInstitucion AS Tipo_Institucion,
        c.ID_carrera,
        c.Nombre_carrera AS Carrera,
        c.creditos_totales AS Creditos_Totales,
        c.area_de_conocimiento AS Area_Conocimiento,
        c.cantidad_alumnos AS Alumnos,
        c.Nombre_titulo AS Titulo_Obtenido,
        v.ID_version_mapa_curricular AS Version_Malla,
        v.starting_year AS Año_Inicio,
        v.ending_year AS Año_Fin,
        a.ID_asignatura,
        a.Nombre_asignatura AS Asignatura,
        a.Horas_teoricas,
        a.Horas_practicas,
        a.cantidad_creditos AS Creditos_Asignatura,
        ta.nombre_tipo_asignatura AS Tipo_Asignatura,
        tc.Nombre_tipo_creditos AS Tipo_Credito,
        pa.Numero_periodo AS Periodo,
        pa.duracion_periodo AS Duracion,
        pa.etapa AS Etapa
    FROM Carrera c
    JOIN Institucion_Carrera ic ON c.ID_carrera = ic.ID_carrera
    JOIN Institucion i ON ic.ID_institucion = i.ID_institucion
    JOIN Division_Administrativa d ON i.ID_division_administrativa = d.ID_division_administrativa
    JOIN Pais p ON d.ID_pais = p.ID_pais
    LEFT JOIN Version_Mapa_Curricular v ON c.ID_carrera = v.ID_carrera
    LEFT JOIN Contenido_Mapa_Curricular cmc ON v.ID_version_mapa_curricular = cmc.ID_version_mapa_curricular
    LEFT JOIN Mapa_Curricular_Asignatura mca ON cmc.ID_cont_mapa_curricular = mca.ID_cont_mapa_curricular
    LEFT JOIN Asignatura a ON mca.ID_asignatura = a.ID_asignatura
    LEFT JOIN Tipo_Asignatura ta ON a.ID_tipo_asignatura = ta.ID_tipo_asignatura
    LEFT JOIN Tipo_de_Creditos tc ON a.ID_tipo_creditos = tc.ID_tipo_creditos
    LEFT JOIN Periodo_Academico pa ON a.ID_periodo_academico = pa.ID_periodo_academico
    ORDER BY p.Nombre_pais, i.Nombre_institucion, c.Nombre_carrera, a.Nombre_asignatura;
    """
    
    try:
        df = pd.read_sql(consulta, conexion)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error al conectar o cargar datos de MySQL: {err}")
        return pd.DataFrame()
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


# === Streamlit Interface ===
st.set_page_config(
    page_title="Plataforma de Mallas Curriculares", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS para el Encabezado y estilo profesional ---
st.markdown("""
    <style>
    /* Estilo para el contenedor del encabezado */
    .header-container {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 2px solid #DDDDDD;
        margin-bottom: 20px;
    }
    /* Estilo para el título principal */
    .main-title {
        color: """ + COLOR_GRIS_OSCURO + """;
        margin: 0;
        font-size: 2.5em;
        font-weight: 300;
        padding-left: 20px;
    }
    /* Estilo para el subtitulo */
    .subtitle {
        color: """ + COLOR_GRIS_SUAVE + """;
        margin: 0;
        font-size: 1.1em;
        padding-left: 20px;
        font-style: italic;
    }
    /* Ocultar el pie de página de Streamlit */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# --- Encabezado de Fundación con Imagen ---
# Usamos [0.2, 0.8] en las columnas para dar más espacio al logo grande
encabezado_cols = st.columns([0.2, 0.8]) 
with encabezado_cols[0]:
    try:
        # Aquí se usa el valor de la variable ANCHO_IMAGEN
        st.image(RUTA_IMAGEN, width=ANCHO_IMAGEN) 
    except FileNotFoundError:
        # Placeholder de error si la imagen no se encuentra
        st.markdown(f'<div style="width: {ANCHO_IMAGEN}px; height: {ANCHO_IMAGEN}px; background-color: #A93226; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.0em; text-align: center;">🚫 Logo no encontrado</div>', unsafe_allow_html=True)

with encabezado_cols[1]:
    st.markdown(f'<p class="main-title">Plataforma de Análisis Curricular</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Fundación Pro-Educación Global</p>', unsafe_allow_html=True)

# --- Carga de Datos ---
df = cargar_datos()

if df.empty:
    st.warning("No se pudo cargar la data. Por favor, verifica tu conexión a la base de datos.")
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("⚙️ Opciones de Filtrado")
st.sidebar.markdown("---")
universidad = st.sidebar.multiselect("🎓 Institución", options=df['Institucion'].unique())
carrera = st.sidebar.multiselect("📚 Carrera", options=df['Carrera'].unique())
pais = st.sidebar.multiselect("🌎 País", options=df['Pais'].unique())
st.sidebar.markdown("---")

# --- Buscador global ---
st.markdown("## Búsqueda General")
busqueda = st.text_input("🔎 Ingrese palabra clave (ej: Ingeniería, Obligatoria, UNAM)", placeholder="Buscar en todos los campos...")
st.markdown("---")

df_filtrado = df.copy()

# Aplicar filtros
if universidad:
    df_filtrado = df_filtrado[df_filtrado['Institucion'].isin(universidad)]
if carrera:
    df_filtrado = df_filtrado[df_filtrado['Carrera'].isin(carrera)]
if pais:
    df_filtrado = df_filtrado[df_filtrado['Pais'].isin(pais)]

# Aplicar buscador
if busqueda:
    busqueda_lower = busqueda.lower()
    df_filtrado = df_filtrado[
        df_filtrado.apply(lambda row: row.astype(str).str.lower().str.contains(busqueda_lower, na=False).any(), axis=1)
    ]

# --- Sección de Resultados ---
st.subheader(f"Tabla de Resultados ({len(df_filtrado)} registros)")

with st.container(border=True):
    st.dataframe(df_filtrado, use_container_width=True)

    # Botón para descargar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Datos filtrados')
    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Descargar Resultados en Excel",
        data=excel_data,
        file_name="mallas_filtradas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

st.markdown("---")

# === Sección de gráficos ===
st.header("📈 Visualización y Análisis")

opciones_graficos = ["Análisis de Aspirantes por Carrera (Muestra)", "Distribución de Carreras por País", "Créditos por Tipo de Asignatura"]
grafico_seleccionado = st.selectbox("Selecciona un Gráfico para Visualizar", opciones_graficos)

# --- Gráfico 1: Aspirantes por Carrera (Modificado con colores sobrios) ---
if grafico_seleccionado == "Análisis de Aspirantes por Carrera (Muestra)":
    
    df_aspirantes = df_filtrado.groupby('Carrera').agg(
        total_aceptados=pd.NamedAgg(column='Creditos_Totales', aggfunc='sum'),
        total_rechazados=pd.NamedAgg(column='Alumnos', aggfunc='sum')
    ).reset_index().nlargest(10, 'total_aceptados', keep='all')
    
    if not df_aspirantes.empty:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        COLOR_ACEPTADOS = "#6D9F71" 
        COLOR_RECHAZADOS = "#C67D6F" 

        ax.bar(df_aspirantes['Carrera'], df_aspirantes['total_aceptados'], label='Aceptados (Proxy)', color=COLOR_ACEPTADOS)
        ax.bar(df_aspirantes['Carrera'], df_aspirantes['total_rechazados'], bottom=df_aspirantes['total_aceptados'], label='Rechazados (Proxy)', color=COLOR_RECHAZADOS)
        
        ax.set_xlabel("Carrera", fontsize=12)
        ax.set_ylabel("Número de Aspirantes (Proxy)", fontsize=12)
        ax.set_title("Top 10 Carreras - Aspirantes (Datos Placeholder)", fontsize=14, color=COLOR_PRIMARIO, pad=15)
        ax.legend(frameon=False)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        
        with st.container(border=True):
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            st.download_button(
                label="⬇️ Descargar Gráfico de Aspirantes",
                data=buf,
                file_name="aspirantes_por_carrera.png",
                mime="image/png",
                type="secondary"
            )
        plt.close(fig)
    else:
        st.info("No hay datos filtrados para generar este gráfico.")


# --- Gráfico 2: Cantidad de Carreras por País ---
if grafico_seleccionado == "Distribución de Carreras por País":
    df_paises = df_filtrado.groupby('Pais').agg(
        cantidad_carreras=pd.NamedAgg(column='Carrera', aggfunc='nunique')
    ).reset_index().sort_values(by='cantidad_carreras', ascending=False)
    
    if not df_paises.empty:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        ax.bar(df_paises['Pais'], df_paises['cantidad_carreras'], color=COLOR_PRIMARIO)
        
        ax.set_xlabel("País", fontsize=12)
        ax.set_ylabel("Número Único de Carreras", fontsize=12)
        ax.set_title("Distribución de Carreras Únicas por País", fontsize=14, color=COLOR_PRIMARIO, pad=15)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        
        for i, v in enumerate(df_paises['cantidad_carreras']):
            ax.text(i, v + (max(df_paises['cantidad_carreras'])*0.01), str(v), color=COLOR_GRIS_OSCURO, ha='center', fontsize=10)

        plt.tight_layout()
        
        with st.container(border=True):
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            st.download_button(
                label="⬇️ Descargar Gráfico de Carreras por País",
                data=buf,
                file_name="carreras_por_pais.png",
                mime="image/png",
                type="secondary"
            )
        plt.close(fig)
    else:
        st.info("No hay datos filtrados para generar este gráfico.")

# --- Gráfico 3: Créditos por Tipo de Asignatura ---
if grafico_seleccionado == "Créditos por Tipo de Asignatura":
    df_creditos = df_filtrado.groupby('Tipo_Asignatura')['Creditos_Asignatura'].sum().reset_index()
    
    if not df_creditos.empty:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colores_pie = ["#506784", "#98AABF", "#C6CEDA", "#E0E3E8"]
        
        ax.pie(
            df_creditos['Creditos_Asignatura'], 
            labels=df_creditos['Tipo_Asignatura'], 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colores_pie,
            wedgeprops={"edgecolor": "white", 'linewidth': 1}
        )
        ax.axis('equal')
        ax.set_title("Distribución de Créditos por Tipo de Asignatura", fontsize=14, color=COLOR_PRIMARIO, pad=15)
        
        with st.container(border=True):
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            st.download_button(
                label="⬇️ Descargar Gráfico de Créditos por Asignatura",
                data=buf,
                file_name="creditos_por_tipo_asignatura.png",
                mime="image/png",
                type="secondary"
            )
        plt.close(fig)
    else:
        st.info("No hay datos filtrados o la información de tipo de asignatura es insuficiente.")
