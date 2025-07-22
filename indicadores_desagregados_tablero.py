import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

# ---------------- TÍTULO GENERAL ----------------
st.markdown(
    "<h2 style='text-align: center; color: #2e6e4c;'>"
    "Indicadores desagregados del mercado laboral - SIPG"
    "</h2>",
    unsafe_allow_html=True
)

# ---------------- CARGA DE DATOS ----------------
df = pd.read_excel("SERIE TRIMESTRAL.xlsx")
df.columns = [col.strip() for col in df.columns]

df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
df["valor grafico"] = pd.to_numeric(df["valor grafico"], errors="coerce")
df["indicador"] = df["indicador"].replace("-", "Total")

# ---------------- FILTROS ----------------
st.sidebar.title("Selección")
pestanas = sorted(df["pestaña"].dropna().unique().tolist())
pestana_sel = st.sidebar.selectbox("Indicador", pestanas)

df_base = df[df["pestaña"] == pestana_sel].copy()
df_base["Año"] = df_base["Fecha"].dt.year
df_base["Trimestre"] = df_base["Fecha"].dt.quarter

anios = sorted(df_base["Año"].dropna().unique().tolist(), reverse=True)
anio_sel = st.sidebar.selectbox("Año", ["(Todos)"] + anios)

trimestres = sorted(df_base["Trimestre"].dropna().unique())
trim_sel = st.sidebar.selectbox("Trimestre", ["(Todos)"] + trimestres)

if anio_sel != "(Todos)":
    df_base = df_base[df_base["Año"] == anio_sel]
if trim_sel != "(Todos)":
    df_base = df_base[df_base["Trimestre"] == trim_sel]

# ---------------- TABLA ----------------
df_tabla = df_base[df_base["dato"].str.lower() == "tabla"].copy()
df_tabla["valor"] = pd.to_numeric(df_tabla["valor"], errors="coerce")
df_tabla = df_tabla.dropna(subset=["valor"])
df_tabla["indicador"] = df_tabla["indicador"].replace("-", "Total")
df_tabla["Año"] = df_tabla["Fecha"].dt.year
df_tabla["Trimestre"] = df_tabla["Fecha"].dt.quarter

# Título dinámico centrado
titulo_tabla = df_tabla["Titulo"].dropna().unique()
if len(titulo_tabla) > 0:
    st.markdown(f"<h5 style='text-align: center;'> {titulo_tabla[0]}</h5>", unsafe_allow_html=True)
else:
    st.markdown("<h5 style='text-align: center;'> Tabla</h5>", unsafe_allow_html=True)

if not df_tabla.empty:
    posibles_segmentadores = ["Año", "Trimestre", "Sexo", "Grupo de edad", "Edad", "Nivel educativo", "indicador"]
    segmentadores = [col for col in posibles_segmentadores if col in df_tabla.columns and df_tabla[col].notna().any()]

    tabla_pivot = pd.pivot_table(
        df_tabla,
        values="valor",
        index=segmentadores,
        aggfunc="sum",
        sort=False
    )
    tabla_pivot = tabla_pivot.sort_index()

    # Formatear con punto como separador de miles
    tabla_formateada = tabla_pivot.copy()
    for col in tabla_formateada.columns:
        tabla_formateada[col] = tabla_formateada[col].apply(
            lambda x: f"{int(x):,}".replace(",", ".") if pd.notnull(x) else ""
        )

    tabla_formateada = tabla_formateada.reset_index()

    # Estilo del encabezado
    styled_table = tabla_formateada.style.set_table_styles([
        {"selector": "th.col_heading", "props": [
            ("background-color", "#d9ead3"),
            ("color", "black"),
            ("border", "1px solid lightgray"),
            ("text-align", "center"),
            ("font-weight", "bold")
        ]}
    ])

    st.dataframe(styled_table)
else:
    st.warning("No hay datos de tabla disponibles para esta combinación de filtros.")

# ---------------- GRÁFICO ----------------
df_grafico = df_base[df_base["dato"] == "gráfico"].copy()
df_grafico = df_grafico.dropna(subset=["valor grafico", "Fecha"])

titulo_grafico = df_grafico["Titulo_grafico"].dropna().unique()
titulo_grafico = titulo_grafico[0] if len(titulo_grafico) > 0 else f"Evolución: {pestana_sel}"

st.markdown(f"<h5 style='text-align: center;'> {titulo_grafico}</h5>", unsafe_allow_html=True)

if not df_grafico.empty:
    fig, ax = plt.subplots(figsize=(10, 5))

    agrupador = ["indicador", "Sexo"] if df_grafico["indicador"].nunique() > 1 else ["Sexo"]
    grupos = list(df_grafico.groupby(agrupador))

    cmap = get_cmap("Greens")
    colors = cmap(np.linspace(0.4, 0.9, len(grupos)))

    for i, (claves, grupo) in enumerate(grupos):
        grupo = grupo.sort_values("Fecha")
        etiqueta = " - ".join(str(k) for k in claves) if isinstance(claves, tuple) else str(claves)
        ax.plot(grupo["Fecha"], grupo["valor grafico"], marker="o", label=etiqueta, color=colors[i])

    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor gráfico")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Fuente debajo del gráfico
    st.markdown(
        "<div style='font-size: 0.85em; color: gray; text-align: center; margin-top: 0.5em;'>"
        "Fuente: Elaboración propia a partir de la Encuesta Permanente de Hogares del INDEC."
        "</div>",
        unsafe_allow_html=True
    )
else:
    st.info("No hay datos de gráfico para esta combinación de filtros.")

st.markdown(
    """
        <div style="
            border: 1px solid #ccc;
            padding: 12px 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
            font-size: 0.9em;
            text-align: center;
            max-width: 600px;
            margin: auto;
        ">
            Visualización desarrollada por <strong>Hilario Ferrea</strong><br>
            <strong>Contacto:</strong> hiloferrea@gmail.com — hferrea@estadistica.ec.gba.gov.ar
        </div>
        """,
        unsafe_allow_html=True
)

# Enlace al documento de definiciones
url_definiciones = "https://github.com/HiloFerrea/SIPG_Indicadores_desagregados_del_ML/blob/main/definiciones.txt"

st.markdown(
    f"<div style='text-align: center; margin-top: 2em;'>"
    f"<a href='{url_definiciones}' target='_blank' style='font-size: 0.95em;'>"
    f"📄 Ver definiciones de los indicadores</a></div>",
    unsafe_allow_html=True
)

