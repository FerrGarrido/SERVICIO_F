import streamlit as st
import mysql.connector
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns

# === 0. Configuración de Estilo y Paleta de Colores ===

COLOR_PRIMARIO = "#264A6A"
COLOR_FONDO_CLARO = "#F5F5F5"
COLOR_GRIS_OSCURO = "#333333"
COLOR_GRIS_SUAVE = "#AAAAAA"

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
        'patch.edgecolor': 'none',
    }
)

# === CONFIGURACIÓN DE LA APP ===

st.set_page_config(
    page_title="Mallas Curriculares",
    layout="wide"
)

# === LOGO ===

RUTA_IMAGEN = "fudepa.png"
ANCHO_IMAGEN = 150

try:
    st.image(RUTA_IMAGEN, width=ANCHO_IMAGEN)
except:
    pass

st.title("Sistema de Análisis de Mallas Curriculares")

st.write("Exploración de carreras, asignaturas y estructuras curriculares.")

# === FUNCIÓN PARA CARGAR DATOS ===

@st.cache_data(ttl=600)
def cargar_datos():

    try:
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

        df = pd.read_sql(consulta, conexion)
        conexion.close()

        return df

    except mysql.connector.Error as err:
        st.error(f"Error al conectar con MySQL: {err}")
        return pd.DataFrame()

# === CARGAR DATOS ===

df = cargar_datos()

# === VALIDACIÓN ===

if df.empty:

    st.warning("No se pudieron cargar datos desde la base de datos.")

else:

    st.success(f"Datos cargados correctamente: {len(df)} registros")

    # === TABLA ===

    st.subheader("Vista de Datos")

    st.dataframe(df, use_container_width=True)

    # === DESCARGA EXCEL ===

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        label="Descargar datos en Excel",
        data=buffer.getvalue(),
        file_name="mallas_curriculares.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # === GRÁFICA ===

    st.subheader("Distribución de Carreras por Área de Conocimiento")

    conteo = df["Area_Conocimiento"].value_counts().head(10)

    fig, ax = plt.subplots()

    sns.barplot(
        x=conteo.values,
        y=conteo.index,
        ax=ax
    )

    ax.set_xlabel("Cantidad")
    ax.set_ylabel("Área de conocimiento")

    st.pyplot(fig)
