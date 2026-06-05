import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mysql.connector import connect, Error

# Configuracion
st.set_page_config(
    page_title="COMPARATIVA POR ESTADOS",
    layout="wide",
)


# Cargar datos
@st.cache_data
def cargar_datos():
    try:
        conexion = connect(
            host = "127.0.0.1",
            user = "root",
            password = "12345",
            database = "ProyectoSuicidio",
            port = 3306
        )
        if conexion:
            df = pd.read_sql("SELECT * FROM SuicidiosMexico", conexion)
            conexion.close()
            return df
    except Error as e:
        st.error(f"Error de conexion a la base de datos: {e}")
        return pd.DataFrame()

df = cargar_datos()

# ============================================
# TITULO Y FILTROS
# ============================================
st.title("Comparativa por Estados")
st.markdown("Analisis de tasas de suicidio por entidad federativa")
st.markdown("---")

# Filtro de año
años_disponibles = sorted(df['anio'].unique())
año_seleccionado = st.selectbox("Selecciona un año", años_disponibles, index=len(años_disponibles) - 1)

st.markdown("---")

# ============================================
# FILTRAR DATOS DEL AÑO SELECCIONADO
# ============================================
df_anio = df[df['anio'] == año_seleccionado].copy()
df_estados = df_anio[df_anio['estado'] != 'NACIONAL'].copy()
df_estados = df_estados.sort_values('tasa_suicidio', ascending=False).reset_index(drop=True)

# ============================================
# METRICAS CLAVE DEL TEMA 2
# ============================================
st.subheader("Indicadores por Estado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    estado_max = df_estados.iloc[0]['estado']
    tasa_max = df_estados.iloc[0]['tasa_suicidio']
    st.metric("Estado con mayor tasa", estado_max, delta=f"{tasa_max:.2f}")

with col2:
    estado_min = df_estados.iloc[-1]['estado']
    tasa_min = df_estados.iloc[-1]['tasa_suicidio']
    st.metric("Estado con menor tasa", estado_min, delta=f"{tasa_min:.2f}")

with col3:
    promedio_estados = df_estados['tasa_suicidio'].mean()
    st.metric("Promedio nacional", f"{promedio_estados:.2f}")

with col4:
    desviacion = df_estados['tasa_suicidio'].std()
    st.metric("Desviacion estandar", f"{desviacion:.2f}")

st.markdown("---")

# ============================================
# GRAFICO 1: TOP 10 ESTADOS
# ============================================
st.subheader("Top 10 estados con mayor tasa")

top10 = df_estados.head(10).copy()

fig1 = px.bar(
    top10,
    x='tasa_suicidio',
    y='estado',
    orientation='h',
    title=f"Estados con tasa mas alta ({año_seleccionado})",
    color='tasa_suicidio',
    color_continuous_scale='Reds',
    text='tasa_suicidio',
    labels={'tasa_suicidio': 'Tasa por 100,000 hab', 'estado': 'Estado'}
)
fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig1.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 2: BOTTOM 10 ESTADOS
# ============================================
st.subheader("Bottom 10 estados con menor tasa")

bottom10 = df_estados.tail(10).copy()
bottom10 = bottom10.sort_values('tasa_suicidio', ascending=True)

fig2 = px.bar(
    bottom10,
    x='tasa_suicidio',
    y='estado',
    orientation='h',
    title=f"Estados con tasa mas baja ({año_seleccionado})",
    color='tasa_suicidio',
    color_continuous_scale='Greens',
    text='tasa_suicidio',
    labels={'tasa_suicidio': 'Tasa por 100,000 hab', 'estado': 'Estado'}
)
fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 3: MAPA DE CALOR
# ============================================
st.subheader("Mapa de calor: Evolucion por estado")

df_heatmap = df[df['estado'] != 'NACIONAL'].pivot_table(
    index='estado',
    columns='anio',
    values='tasa_suicidio'
)

años_recientes = sorted(df_heatmap.columns)[-10:]
df_heatmap_reciente = df_heatmap[años_recientes]

fig3 = px.imshow(
    df_heatmap_reciente,
    labels={'x': 'Año', 'y': 'Estado', 'color': 'Tasa'},
    title="Tasa de suicidio por estado y año (ultimos 10 años)",
    color_continuous_scale='Viridis',
    aspect='auto',
    height=800
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 4: COMPARATIVA TOP VS BOTTOM
# ============================================
st.subheader("Comparativa: Estados extremos")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Tasa mas alta: {estado_max}")
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #e74c3c;'>{tasa_max:.2f}</p>",
                unsafe_allow_html=True)
    st.markdown(f"por cada 100,000 habitantes")

    datos_max = df_estados[df_estados['estado'] == estado_max].iloc[0]
    st.markdown(f"""
    <div style="background: #fdf2e9; border-radius: 10px; padding: 15px; margin-top: 15px;">
        <b>Datos de {estado_max}:</b><br>
        Total suicidios: {datos_max['suicidios_total']:,}<br>
        Tasa hombres: {datos_max['tasa_hombres']:.2f}<br>
        Tasa mujeres: {datos_max['tasa_mujeres']:.2f}<br>
        Poblacion: {datos_max['poblacion']:,.0f}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"### Tasa mas baja: {estado_min}")
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #27ae60;'>{tasa_min:.2f}</p>",
                unsafe_allow_html=True)
    st.markdown(f"por cada 100,000 habitantes")

    datos_min = df_estados[df_estados['estado'] == estado_min].iloc[0]
    st.markdown(f"""
    <div style="background: #e8f8f5; border-radius: 10px; padding: 15px; margin-top: 15px;">
        <b>Datos de {estado_min}:</b><br>
        Total suicidios: {datos_min['suicidios_total']:,}<br>
        Tasa hombres: {datos_min['tasa_hombres']:.2f}<br>
        Tasa mujeres: {datos_min['tasa_mujeres']:.2f}<br>
        Poblacion: {datos_min['poblacion']:,.0f}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# TABLA COMPLETA
# ============================================
with st.expander("Ver todos los estados"):
    tabla_estados = df_estados[
        ['estado', 'tasa_suicidio', 'suicidios_total', 'tasa_hombres', 'tasa_mujeres', 'poblacion']]
    tabla_estados.columns = ['Estado', 'Tasa Total', 'Suicidios', 'Tasa Hombres', 'Tasa Mujeres', 'Poblacion']
    tabla_estados['Tasa Total'] = tabla_estados['Tasa Total'].map(lambda x: f"{x:.2f}")
    tabla_estados['Tasa Hombres'] = tabla_estados['Tasa Hombres'].map(lambda x: f"{x:.2f}")
    tabla_estados['Tasa Mujeres'] = tabla_estados['Tasa Mujeres'].map(lambda x: f"{x:.2f}")
    tabla_estados['Suicidios'] = tabla_estados['Suicidios'].map(lambda x: f"{x:,}")
    tabla_estados['Poblacion'] = tabla_estados['Poblacion'].map(lambda x: f"{x:,.0f}")
    st.dataframe(tabla_estados, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================
# INTERPRETACION
# ============================================
st.subheader("Interpretacion")

brecha = tasa_max - tasa_min
ratio = tasa_max / tasa_min

st.markdown(f"""
**1. Disparidad entre estados**  
La diferencia entre el estado con mayor tasa ({estado_max}: {tasa_max:.2f}) y el de menor tasa ({estado_min}: {tasa_min:.2f})  
es de **{brecha:.2f} puntos**. El estado con mayor tasa tiene una tasa **{ratio:.1f} veces mas alta**.

**2. Analisis regional**  
- Los estados con tasas mas altas son: **{', '.join(top10.head(3)['estado'].tolist())}**
- Los estados con tasas mas bajas son: **{', '.join(bottom10.tail(3)['estado'].tolist())}**

**3. Conclusion**  
Existe una marcada desigualdad regional en las tasas de suicidio. Algunos estados tienen tasas significativamente mas altas que el promedio nacional, mientras que otros se mantienen por debajo.
""")

st.markdown("---")
st.caption(f"Fuente: Datamx.io | Datos del año {año_seleccionado} | Tasas por cada 100,000 habitantes")