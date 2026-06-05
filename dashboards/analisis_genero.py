import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuracion
st.set_page_config(
    page_title="Analisis por Genero",
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
# DATOS NACIONALES
# ============================================
df_nacional = df[df['estado'] == 'NACIONAL'].copy()

# ============================================
# CALCULOS CLAVE
# ============================================
tasa_hombres_1990 = df_nacional[df_nacional['anio'] == 1990]['tasa_hombres'].values[0]
tasa_hombres_2024 = df_nacional[df_nacional['anio'] == 2024]['tasa_hombres'].values[0]
tasa_mujeres_1990 = df_nacional[df_nacional['anio'] == 1990]['tasa_mujeres'].values[0]
tasa_mujeres_2024 = df_nacional[df_nacional['anio'] == 2024]['tasa_mujeres'].values[0]

aumento_hombres = ((tasa_hombres_2024 - tasa_hombres_1990) / tasa_hombres_1990) * 100
aumento_mujeres = ((tasa_mujeres_2024 - tasa_mujeres_1990) / tasa_mujeres_1990) * 100

brecha_1990 = tasa_hombres_1990 / tasa_mujeres_1990
brecha_2024 = tasa_hombres_2024 / tasa_mujeres_2024

total_hombres = df_nacional['suicidios_hombres'].sum()
total_mujeres = df_nacional['suicidios_mujeres'].sum()
proporcion = total_hombres / total_mujeres

# ============================================
# CALCULOS PARA MULTIPLES METRICAS DE BRECHA
# ============================================
# Para 2024
razon_2024 = brecha_2024
diferencia_puntos_2024 = tasa_hombres_2024 - tasa_mujeres_2024
porcentaje_mas_2024 = ((tasa_hombres_2024 - tasa_mujeres_2024) / tasa_mujeres_2024) * 100
casos_extra_por_millon_2024 = diferencia_puntos_2024 * 10

# Para 1990
razon_1990 = brecha_1990
diferencia_puntos_1990 = tasa_hombres_1990 - tasa_mujeres_1990
porcentaje_mas_1990 = ((tasa_hombres_1990 - tasa_mujeres_1990) / tasa_mujeres_1990) * 100
casos_extra_por_millon_1990 = diferencia_puntos_1990 * 10

# Cambio general
cambio_brecha = ((brecha_2024 - brecha_1990) / brecha_1990) * 100

# ============================================
# TITULO
# ============================================
st.title("Análisis por Género")
st.markdown("Comparativa de tasas de suicidio entre hombres y mujeres")
st.markdown("---")

# ============================================
# METRICAS CLAVE
# ============================================
st.subheader("Indicadores por Genero")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Hombres 1990", f"{tasa_hombres_1990:.2f}")
with col2:
    st.metric("Hombres 2024", f"{tasa_hombres_2024:.2f}", delta=f"{aumento_hombres:+.1f}%")
with col3:
    st.metric("Mujeres 1990", f"{tasa_mujeres_1990:.2f}")
with col4:
    st.metric("Mujeres 2024", f"{tasa_mujeres_2024:.2f}", delta=f"{aumento_mujeres:+.1f}%")

st.markdown("---")

# ============================================
# GRAFICO 1: EVOLUCION COMPARATIVA (LINEAS)
# ============================================
st.subheader("Evolucion comparativa: Hombres vs Mujeres")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df_nacional['anio'],
    y=df_nacional['tasa_hombres'],
    mode='lines+markers',
    name='Hombres',
    line=dict(color='#3498db', width=3),
    marker=dict(size=8, color='#3498db'),
    fill='tozeroy',
    fillcolor='rgba(52, 152, 219, 0.15)'
))

fig1.add_trace(go.Scatter(
    x=df_nacional['anio'],
    y=df_nacional['tasa_mujeres'],
    mode='lines+markers',
    name='Mujeres',
    line=dict(color='#e91e63', width=3),
    marker=dict(size=8, color='#e91e63'),
    fill='tozeroy',
    fillcolor='rgba(233, 30, 99, 0.15)'
))

fig1.update_layout(
    height=500,
    xaxis_title='Año',
    yaxis_title='Tasa por 100,000 habitantes',
    hovermode='x unified',
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#E8E0D5'),
    yaxis=dict(showgrid=True, gridcolor='#E8E0D5')
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 2: BRECHA DE GENERO (MULTIPLES METRICAS)
# ============================================
st.subheader("⚖️ Brecha de género: 4 perspectivas")

# Tarjeta principal destacada
st.markdown(f"""
<div style='background:linear-gradient(135deg, #1e3c72, #2a5298); border-radius:15px; padding:20px; text-align:center; color:white; margin-bottom:25px'>
    <p style='font-size:16px; opacity:0.9; margin:0'>📊 EN 2024</p>
    <p style='font-size:28px; font-weight:bold; margin:5px 0'>La tasa de suicidio en hombres es</p>
    <p style='font-size:56px; font-weight:bold; margin:-5px 0'>{porcentaje_mas_2024:.0f}%</p>
    <p style='font-size:20px; margin:-5px 0'>más alta que en mujeres</p>
</div>
""", unsafe_allow_html=True)

# 4 métricas en columnas
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown(f"""
    <div style='background:#f0f2f6; border-radius:12px; padding:15px; text-align:center; height:140px'>
        <p style='font-size:12px; color:#666; margin:0'>📏 PROPORCIÓN</p>
        <p style='font-size:32px; font-weight:bold; margin:5px 0; color:#3498db'>{razon_2024:.1f}:1</p>
        <p style='font-size:11px; color:#666'>hombres : mujer</p>
        <p style='font-size:10px; color:#999; margin-top:5px'>1990: {razon_1990:.1f}:1</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    color_porcentaje = "#e74c3c" if porcentaje_mas_2024 > porcentaje_mas_1990 else "#27ae60"
    flecha = "▲" if porcentaje_mas_2024 > porcentaje_mas_1990 else "▼"
    st.markdown(f"""
    <div style='background:#f0f2f6; border-radius:12px; padding:15px; text-align:center; height:140px'>
        <p style='font-size:12px; color:#666; margin:0'>📈 PORCENTAJE EXTRA</p>
        <p style='font-size:32px; font-weight:bold; margin:5px 0; color:{color_porcentaje}'>+{porcentaje_mas_2024:.0f}%</p>
        <p style='font-size:11px; color:#666'>más en hombres</p>
        <p style='font-size:10px; color:#999; margin-top:5px'>{flecha} 1990: +{porcentaje_mas_1990:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    color_diferencia = "#e74c3c" if diferencia_puntos_2024 > diferencia_puntos_1990 else "#27ae60"
    st.markdown(f"""
    <div style='background:#f0f2f6; border-radius:12px; padding:15px; text-align:center; height:140px'>
        <p style='font-size:12px; color:#666; margin:0'>🎯 DIFERENCIA EN TASA</p>
        <p style='font-size:32px; font-weight:bold; margin:5px 0; color:#f39c12'>{diferencia_puntos_2024:.1f}</p>
        <p style='font-size:11px; color:#666'>puntos por 100k</p>
        <p style='font-size:10px; color:#999; margin-top:5px'>1990: {diferencia_puntos_1990:.1f}</p>
    </div>
    """, unsafe_allow_html=True)

with col_d:
    st.markdown(f"""
    <div style='background:#f0f2f6; border-radius:12px; padding:15px; text-align:center; height:140px'>
        <p style='font-size:12px; color:#666; margin:0'>👥 IMPACTO REAL</p>
        <p style='font-size:32px; font-weight:bold; margin:5px 0; color:#27ae60'>{casos_extra_por_millon_2024:.0f}</p>
        <p style='font-size:11px; color:#666'>más hombres por millón</p>
        <p style='font-size:10px; color:#999; margin-top:5px'>1990: {casos_extra_por_millon_1990:.0f}</p>
    </div>
    """, unsafe_allow_html=True)

# Explicación expandible
with st.expander("📖 ¿Qué significa cada métrica?"):
    st.markdown("""
    | Métrica | Qué mide | Ejemplo |
    |---------|----------|---------|
    | **Proporción** | Hombres por cada mujer | `5.9:1` = 5.9 hombres por cada mujer |
    | **Porcentaje extra** | % más alta la tasa masculina | `+490%` = Casi 6 veces más |
    | **Diferencia en tasa** | Diferencia por 100,000 hab. | `9.8 puntos` más hombres |
    | **Impacto real** | Hombres extra por millón | `98 hombres` más en 1M de personas |
    """)

    if cambio_brecha > 0:
        st.warning(f"⚠️ La brecha se ha **ampliado {abs(cambio_brecha):.1f}%** desde 1990")
    else:
        st.success(f"✅ La brecha se ha **reducido {abs(cambio_brecha):.1f}%** desde 1990")

st.markdown("---")

# ============================================
# GRAFICO 3: DONA / PASTEL DE PROPORCION
# ============================================
st.subheader("Proporcion de suicidios por genero (historico 1990-2024)")

fig_dona = go.Figure(data=[go.Pie(
    labels=['Hombres', 'Mujeres'],
    values=[total_hombres, total_mujeres],
    hole=0.4,
    marker=dict(colors=['#3498db', '#e91e63']),
    textinfo='label+percent',
    textposition='auto'
)])

fig_dona.update_layout(
    height=450,
    title="Total de suicidios 1990-2024",
    annotations=[dict(text=f'{proporcion:.1f}:1', x=0.5, y=0.5, font_size=20, showarrow=False)]
)

st.plotly_chart(fig_dona, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 4: BRECHA POR ESTADO (BARRAS HORIZONTALES)
# ============================================
st.subheader("Brecha de genero por estado")

# Filtro de año
años_disp = sorted(df['anio'].unique())
año_gen = st.selectbox("Selecciona un año", años_disp, index=len(años_disp) - 1)

df_año = df[(df['anio'] == año_gen) & (df['estado'] != 'NACIONAL')].copy()
df_año['brecha_estado'] = df_año['tasa_hombres'] / df_año['tasa_mujeres']
df_año = df_año.sort_values('brecha_estado', ascending=False).head(15)

fig_brecha = px.bar(
    df_año,
    x='brecha_estado',
    y='estado',
    orientation='h',
    title=f"Estados donde la brecha es mas amplia ({año_gen})",
    color='brecha_estado',
    color_continuous_scale='RdYlBu_r',
    text='brecha_estado',
    labels={'brecha_estado': 'Hombres por cada mujer', 'estado': 'Estado'}
)
fig_brecha.update_traces(texttemplate='%{text:.1f}:1', textposition='outside')
fig_brecha.update_layout(height=500)

st.plotly_chart(fig_brecha, use_container_width=True)

st.markdown("---")

# ============================================
# GRAFICO 5: COMPARATIVA POR ESTADO (BARRAS LATERALES)
# ============================================
st.subheader("Comparativa hombres vs mujeres por estado")

# Obtener lista de estados (excluyendo NACIONAL)
estados_disponibles = sorted(df[df['estado'] != 'NACIONAL']['estado'].unique())
estado_seleccionado = st.selectbox("Selecciona un estado", estados_disponibles)

df_estado = df[(df['estado'] == estado_seleccionado)].copy()

fig_estado = go.Figure()

fig_estado.add_trace(go.Bar(
    x=df_estado['anio'],
    y=df_estado['tasa_hombres'],
    name='Hombres',
    marker_color='#3498db'
))

fig_estado.add_trace(go.Bar(
    x=df_estado['anio'],
    y=df_estado['tasa_mujeres'],
    name='Mujeres',
    marker_color='#e91e63'
))

fig_estado.update_layout(
    title=f'Evolucion en {estado_seleccionado}',
    xaxis_title='Año',
    yaxis_title='Tasa por 100,000 habitantes',
    barmode='group',
    height=450,
    plot_bgcolor='white'
)

st.plotly_chart(fig_estado, use_container_width=True)

st.markdown("---")

# ============================================
# TABLA COMPARATIVA
# ============================================
with st.expander("Ver datos completos por estado"):
    tabla_genero = df_año[
        ['estado', 'tasa_hombres', 'tasa_mujeres', 'brecha_estado', 'suicidios_hombres', 'suicidios_mujeres']].copy()
    tabla_genero.columns = ['Estado', 'Tasa Hombres', 'Tasa Mujeres', 'Hombres por mujer', 'Suicidios Hombres',
                            'Suicidios Mujeres']
    tabla_genero['Tasa Hombres'] = tabla_genero['Tasa Hombres'].map(lambda x: f"{x:.2f}")
    tabla_genero['Tasa Mujeres'] = tabla_genero['Tasa Mujeres'].map(lambda x: f"{x:.2f}")
    tabla_genero['Hombres por mujer'] = tabla_genero['Hombres por mujer'].map(lambda x: f"{x:.1f}:1")
    tabla_genero['Suicidios Hombres'] = tabla_genero['Suicidios Hombres'].map(lambda x: f"{x:,}")
    tabla_genero['Suicidios Mujeres'] = tabla_genero['Suicidios Mujeres'].map(lambda x: f"{x:,}")
    st.dataframe(tabla_genero, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================
# INTERPRETACION
# ============================================
st.subheader("Interpretacion")

if len(df_año) > 0:
    estado_max_brecha = df_año.iloc[0]['estado']
    brecha_max = df_año.iloc[0]['brecha_estado']
else:
    estado_max_brecha = "No disponible"
    brecha_max = 0

st.markdown(f"""
**1. Brecha de genero nacional**  
En 2024, la tasa de suicidio en hombres es **{porcentaje_mas_2024:.0f}% más alta** que en mujeres.  
Esto equivale a **{razon_2024:.1f} hombres por cada mujer**.

**2. Evolucion por genero**  
- Hombres: aumento de {tasa_hombres_1990:.2f} a {tasa_hombres_2024:.2f} ({aumento_hombres:+.1f}%)
- Mujeres: aumento de {tasa_mujeres_1990:.2f} a {tasa_mujeres_2024:.2f} ({aumento_mujeres:+.1f}%)

**3. Total historico**  
Entre 1990 y 2024:
- Hombres: **{total_hombres:,.0f}** suicidios
- Mujeres: **{total_mujeres:,.0f}** suicidios
- Proporcion: **{proporcion:.1f} hombres por cada mujer**

**4. Estado con mayor brecha**  
**{estado_max_brecha}** tiene la brecha mas amplia con **{brecha_max:.1f} hombres por cada mujer**.

**5. Conclusion**  
Los hombres presentan consistentemente tasas mas altas. Se requieren politicas de prevencion especificas para la poblacion masculina.
""")

st.markdown("---")
st.caption(f"Fuente: Datamx.io | Datos del año {año_gen} | Tasas por cada 100,000 habitantes")