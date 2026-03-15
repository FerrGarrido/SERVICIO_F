
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