import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tendencia_nacional as tn
from mysql.connector import connect, Error

st.set_page_config(
    page_title="Dashboard - Suicidios Mexico",
    layout="wide",
)

st.markdown("""
<style>
    /* Fondo principal - gris claro suave */
    .stApp {
        background-color: #F0F2F6;
    }

    /* Fondo principal alternativo - blanco hueso */
    /* .stApp {
        background-color: #F8F9FA;
    } */

    /* Fondo principal alternativo - azul muy claro */
    /* .stApp {
        background-color: #E8F0FE;
    } */

    /* Fondo de los contenedores principales */
    .main > div {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Tarjetas de metricas */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #E8E8E8;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }

    .metric-card h4 {
        color: #6C5B7B;
        margin-bottom: 10px;
        font-size: 14px;
        letter-spacing: 1px;
    }

    .metric-card h2 {
        color: #2C3E50;
        font-size: 32px;
        margin: 10px 0;
        font-weight: 700;
    }

    .metric-card p {
        color: #7f8c8d;
        font-size: 13px;
    }

    /* Tarjeta de emergencia */
    .emergencia-card {
        background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
    }

    .emergencia-card h3 {
        color: white !important;
        margin: 0 0 8px 0;
        font-size: 18px;
    }

    .emergencia-card h2 {
        color: white !important;
        font-size: 28px;
        margin: 8px 0;
        letter-spacing: 2px;
    }

    .emergencia-card p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 12px;
        margin: 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C3E50 0%, #1A252F 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 8px;
    }

    [data-testid="stSidebar"] .stRadio label {
        padding: 6px 12px;
    }

    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #6C5B7B 0%, #4A3B5C 100%);
        color: white;
        border-radius: 25px;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108, 91, 123, 0.4);
    }

    /* Títulos */
    h1, h2, h3 {
        color: #2C3E50 !important;
        font-weight: 600 !important;
    }

    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.8rem !important;
    }

    h3 {
        font-size: 1.4rem !important;
    }

    hr {
        margin: 24px 0;
        border-color: #E8E8E8;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #F8F9FA;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Dataframe */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Select boxes */
    .stSelectbox > div, .stSlider > div {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# BARRA LATERAL - NAVEGACION
# ============================================
st.sidebar.title("📊 Menu")
tema = st.sidebar.radio(
    "Selecciona una seccion",
    ["Tendencia Nacional", "Comparativa por Estados", "Analisis por Genero"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Tasas por cada 100,000 habitantes")
st.sidebar.markdown("""
<div style="
    background: rgba(255,255,255,0.1); 
    border-radius: 12px; 
    padding: 12px; 
    margin-top: 20px;
    text-align: center;
">
    <div style="font-size: 12px;">📞 ¿Necesitas ayuda?</div>
    <div style="font-size: 14px; font-weight: bold;">800 911 2000</div>
    <div style="font-size: 10px;">Línea de la Vida • 24/7</div>
</div>
""", unsafe_allow_html=True)



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
df_nacional = df[df['estado'] == 'NACIONAL'].copy()

# TENDENCIA NACIONAL
# ============================================
if tema == "Tendencia Nacional":
    tn.render()

# ============================================
# COMPARATIVA POR ESTADOS
# ============================================
elif tema == "Comparativa por Estados":
    st.title("Comparativa por Estados")
    st.markdown("Analisis interactivo de tasas de suicidio por entidad federativa")
    st.markdown("---")

    df_estados = df[df['estado'] != 'NACIONAL'].copy()
    años_disponibles = sorted(df_estados['anio'].unique())
    estados_disponibles = sorted(df_estados['estado'].unique())

    default_estados = []
    estados_comunes = ["CIUDAD DE MEXICO", "JALISCO", "NUEVO LEON", "Estado de Mexico", "Veracruz", "Puebla"]
    for estado in estados_comunes:
        if estado in estados_disponibles:
            default_estados.append(estado)
            if len(default_estados) >= 3:
                break

    if not default_estados:
        default_estados = estados_disponibles[:3]

    with st.form("filtros_comparativa"):
        col1, col2 = st.columns(2)
        with col1:
            año_seleccionado = st.slider(
                "Selecciona un año",
                min(años_disponibles),
                max(años_disponibles),
                step=5,
                value=2024
            )
        with col2:
            estados_seleccionados = st.multiselect(
                "Selecciona estados para comparar",
                estados_disponibles,
                default=default_estados
            )
        submit = st.form_submit_button("Aplicar Filtros", use_container_width=True)

    if submit and len(estados_seleccionados) > 0:
        df_filtrado = df_estados[
            (df_estados['anio'] == año_seleccionado) &
            (df_estados['estado'].isin(estados_seleccionados))
            ].copy()

        if len(df_filtrado) > 0:
            st.subheader("Indicadores por Estado")
            df_filtrado_sorted = df_filtrado.sort_values('tasa_suicidio', ascending=False)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                estado_max = df_filtrado_sorted.iloc[0]['estado']
                tasa_max = df_filtrado_sorted.iloc[0]['tasa_suicidio']
                st.markdown(f"""
                <div class="metric-card">
                    <h4>⚠️ Estado con mayor tasa</h4>
                    <h2>{estado_max}</h2>
                    <p>{tasa_max:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                estado_min = df_filtrado_sorted.iloc[-1]['estado']
                tasa_min = df_filtrado_sorted.iloc[-1]['tasa_suicidio']
                st.markdown(f"""
                <div class="metric-card">
                    <h4>✅ Estado con menor tasa</h4>
                    <h2>{estado_min}</h2>
                    <p>{tasa_min:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                promedio = df_filtrado['tasa_suicidio'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Promedio</h4>
                    <h2>{promedio:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                total_suicidios = df_filtrado['suicidios_total'].sum()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>💔 Total suicidios</h4>
                    <h2>{total_suicidios:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Tasa de suicidio por estado")

            fig_barras = px.bar(
                df_filtrado_sorted,
                x='estado',
                y='tasa_suicidio',
                color='tasa_suicidio',
                title=f"Tasa de suicidio en {año_seleccionado}",
                text='tasa_suicidio',
                labels={'tasa_suicidio': 'Tasa por 100,000 hab', 'estado': 'Estado'},
                color_continuous_scale=['#FFE66D', '#FF9F6B', '#FF6B6B']
            )
            fig_barras.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_barras.update_layout(
                showlegend=False,
                height=450,
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_size=16
            )
            st.plotly_chart(fig_barras, use_container_width=True)

            with st.expander("Ver datos completos de los estados seleccionados"):
                tabla = df_filtrado[[
                    'estado', 'tasa_suicidio', 'suicidios_total',
                    'tasa_hombres', 'tasa_mujeres', 'poblacion'
                ]].copy()
                tabla.columns = [
                    'Estado', 'Tasa Total', 'Total Suicidios',
                    'Tasa Hombres', 'Tasa Mujeres', 'Poblacion'
                ]
                tabla['Tasa Total'] = tabla['Tasa Total'].map(lambda x: f"{x:.2f}")
                tabla['Tasa Hombres'] = tabla['Tasa Hombres'].map(lambda x: f"{x:.2f}")
                tabla['Tasa Mujeres'] = tabla['Tasa Mujeres'].map(lambda x: f"{x:.2f}")
                tabla['Total Suicidios'] = tabla['Total Suicidios'].map(lambda x: f"{x:,}")
                tabla['Poblacion'] = tabla['Poblacion'].map(lambda x: f"{x:,.0f}")
                st.dataframe(tabla, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Interpretacion")
            brecha_max = df_filtrado['tasa_suicidio'].max() - df_filtrado['tasa_suicidio'].min()
            ratio_max = df_filtrado['tasa_suicidio'].max() / df_filtrado['tasa_suicidio'].min()
            st.markdown(f"""
            *1. Disparidad entre estados seleccionados*  
            - Estado con tasa mas alta: *{estado_max}* ({tasa_max:.2f})
            - Estado con tasa mas baja: *{estado_min}* ({tasa_min:.2f})
            - Diferencia: *{brecha_max:.2f} puntos* por 100,000 habitantes
            - El estado con tasa mas alta tiene una tasa *{ratio_max:.1f} veces mas alta*

            *2. Comparativa por genero*  
            En promedio, la tasa en hombres es significativamente mas alta que en mujeres.
            """)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados")
    elif submit and len(estados_seleccionados) == 0:
        st.error("Por favor selecciona al menos un estado para comparar")

    # Numero de emergencia al final de la pagina
    st.markdown("---")
    st.markdown("""
    <div class="emergencia-card">
        <h3>Línea de Ayuda</h3>
        <h2>800 911 2000</h2>
        <p>Línea de la Vida - 24/7 - Confidencial - Gratuito</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ANALISIS POR GENERO
# ============================================
else:
    st.title("Analisis por Genero")
    st.markdown("Comparativa de tasas de suicidio entre hombres y mujeres")
    st.markdown("---")

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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>👤 Hombres 1990</h4>
            <h2>{tasa_hombres_1990:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>👤 Hombres 2024</h4>
            <h2>{tasa_hombres_2024:.2f}</h2>
            <p>{aumento_hombres:+.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>👩 Mujeres 1990</h4>
            <h2>{tasa_mujeres_1990:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>👩 Mujeres 2024</h4>
            <h2>{tasa_mujeres_2024:.2f}</h2>
            <p>{aumento_mujeres:+.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Evolucion comparativa")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_nacional['anio'], y=df_nacional['tasa_hombres'], mode='lines+markers',
                              name='Hombres', line=dict(color='#3498db', width=3), fill='tozeroy',
                              fillcolor='rgba(52,152,219,0.15)'))
    fig1.add_trace(go.Scatter(x=df_nacional['anio'], y=df_nacional['tasa_mujeres'], mode='lines+markers',
                              name='Mujeres', line=dict(color='#e74c3c', width=3), fill='tozeroy',
                              fillcolor='rgba(231,76,60,0.15)'))
    fig1.update_layout(height=500, xaxis_title='Año', yaxis_title='Tasa por 100,000 habitantes',
                       hovermode='x unified', plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")

    st.subheader("Brecha de genero")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 1990</h4>
            <h2>{brecha_1990:.1f}x</h2>
            <p>Hombres vs Mujeres</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 2024</h4>
            <h2>{brecha_2024:.1f}x</h2>
            <p>Hombres vs Mujeres</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        cambio_brecha = ((brecha_2024 - brecha_1990) / brecha_1990) * 100
        flecha = "↑" if cambio_brecha > 0 else "↓"
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Cambio</h4>
            <h2 style="color: {'#e74c3c' if cambio_brecha > 0 else '#27ae60'}">{flecha} {abs(cambio_brecha):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Proporcion de suicidios (1990-2024)")
    fig_dona = go.Figure(data=[go.Pie(labels=['Hombres', 'Mujeres'], values=[total_hombres, total_mujeres],
                                      hole=0.4, marker=dict(colors=['#3498db', '#e74c3c']), textinfo='label+percent')])
    fig_dona.update_layout(height=450, plot_bgcolor='white', paper_bgcolor='white',
                           annotations=[dict(text=f'{proporcion:.1f}:1', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig_dona, use_container_width=True)
    st.markdown("---")

    st.subheader("Brecha de genero por estado")
    años_disp = sorted(df['anio'].unique())
    año_gen = st.selectbox("Selecciona un año", años_disp, index=len(años_disp) - 1)
    df_año = df[(df['anio'] == año_gen) & (df['estado'] != 'NACIONAL')].copy()
    df_año['brecha_estado'] = df_año['tasa_hombres'] / df_año['tasa_mujeres']
    df_año = df_año.sort_values('brecha_estado', ascending=False).head(15)
    fig_brecha = px.bar(df_año, x='brecha_estado', y='estado', orientation='h',
                        title=f"Estados con mayor brecha ({año_gen})", color='brecha_estado',
                        color_continuous_scale='RdYlBu_r', text='brecha_estado')
    fig_brecha.update_traces(texttemplate='%{text:.1f}x', textposition='outside')
    fig_brecha.update_layout(height=500, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_brecha, use_container_width=True)
    st.markdown("---")

    with st.expander("Ver datos completos por estado"):
        tabla_genero = df_año[
            ['estado', 'tasa_hombres', 'tasa_mujeres', 'brecha_estado', 'suicidios_hombres', 'suicidios_mujeres']]
        tabla_genero.columns = ['Estado', 'Tasa Hombres', 'Tasa Mujeres', 'Brecha', 'Suicidios Hombres',
                                'Suicidios Mujeres']
        tabla_genero['Tasa Hombres'] = tabla_genero['Tasa Hombres'].map(lambda x: f"{x:.2f}")
        tabla_genero['Tasa Mujeres'] = tabla_genero['Tasa Mujeres'].map(lambda x: f"{x:.2f}")
        tabla_genero['Brecha'] = tabla_genero['Brecha'].map(lambda x: f"{x:.1f}x")
        tabla_genero['Suicidios Hombres'] = tabla_genero['Suicidios Hombres'].map(lambda x: f"{x:,}")
        tabla_genero['Suicidios Mujeres'] = tabla_genero['Suicidios Mujeres'].map(lambda x: f"{x:,}")
        st.dataframe(tabla_genero, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Interpretacion")
    st.markdown(f"""
    *1. Brecha de genero nacional*  
    En 2024, la tasa en hombres es *{brecha_2024:.1f} veces mas alta* que en mujeres.

    *2. Total historico*  
    Hombres: *{total_hombres:,.0f}* suicidios | Mujeres: *{total_mujeres:,.0f}* | Proporcion: *{proporcion:.1f}:1*

    *3. Conclusion*  
    Los hombres presentan tasas consistentemente mas altas. Se requieren politicas especificas.
    """)

    # Numero de emergencia al final de la pagina
    st.markdown("---")
    st.markdown("""
    <div class="emergencia-card">
        <h3>Línea de Ayuda</h3>
        <h2>800 911 2000</h2>
        <p>Línea de la Vida - 24/7 - Confidencial - Gratuito</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Fuente: Datamx.io | Tasas por cada 100,000 habitantes")