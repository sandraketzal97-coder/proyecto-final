from mysql.connector import connect, Error
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuracion
st.set_page_config(
    page_title="Tendencia Nacional",
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


def render():
    df = cargar_datos()
    df_nacional = df[df['estado'] == 'NACIONAL'].copy()

    # ============================================
    # CALCULOS
    # ============================================
    tasa_1990 = df_nacional[df_nacional['anio'] == 1990]['tasa_suicidio'].values[0]
    tasa_2024 = df_nacional[df_nacional['anio'] == 2024]['tasa_suicidio'].values[0]
    aumento = ((tasa_2024 - tasa_1990) / tasa_1990) * 100
    año_max = df_nacional.loc[df_nacional['tasa_suicidio'].idxmax(), 'anio']
    tasa_max = df_nacional['tasa_suicidio'].max()
    año_min = df_nacional.loc[df_nacional['tasa_suicidio'].idxmin(), 'anio']
    tasa_min = df_nacional['tasa_suicidio'].min()
    total_suicidios = df_nacional['suicidios_total'].sum()
    promedio_anual = df_nacional['tasa_suicidio'].mean()

    # Promedios por decada
    df_nacional['decada'] = (df_nacional['anio'] // 10) * 10
    promedio_decadas = df_nacional.groupby('decada')['tasa_suicidio'].mean().round(2)

    # TITULO
    st.title("Tendencia Nacional de la tasa del suicidio ")
    st.markdown(
        "La tasa de suicidio en México mostró una tendencia creciente entre 1994 y 2010. De acuerdo con datos de mortalidad del Instituto Nacional de Estadística y Geografía (INEGI), la tasa pasó de 2.9 suicidios por cada 100 mil habitantes en 1994 a 4.3–4.6 por cada 100 mil habitantes en 2010, lo que representa un aumento aproximado de entre 48% y 59% en ese periodo.")
    st.markdown("---")

    # METRICAS
    st.subheader("Indicadores Clave")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Tasa 1990", f"{tasa_1990:.2f}")
    with col2:
        st.metric("Tasa 2024", f"{tasa_2024:.2f}")
    with col3:
        st.metric("Año mas critico", f"{int(año_max)}")
    with col4:
        st.metric("Total suicidios", f"{total_suicidios:,.0f}")
    with col5:
        st.metric("Promedio anual", f"{promedio_anual:.2f}")

    st.markdown("---")
    st.subheader("Evolucion historica")

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df_nacional['anio'],
        y=df_nacional['tasa_suicidio'],
        mode='lines+markers',
        name='Tasa nacional',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8, color='#FF6B6B'),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.2)'
    ))

    # Tendencia lineal - requiere numpy pero se puede calcular sin importar
    # Como se eliminó numpy, usamos una aproximación simple
    coef = (df_nacional['tasa_suicidio'].iloc[-1] - df_nacional['tasa_suicidio'].iloc[0]) / (
                df_nacional['anio'].iloc[-1] - df_nacional['anio'].iloc[0])
    intercept = df_nacional['tasa_suicidio'].iloc[0] - coef * df_nacional['anio'].iloc[0]
    tendencia_lineal = coef * df_nacional['anio'] + intercept

    fig1.add_trace(go.Scatter(
        x=df_nacional['anio'],
        y=tendencia_lineal,
        mode='lines',
        name='Tendencia lineal',
        line=dict(color='#4ECDC4', width=2, dash='dash')
    ))

    fig1.add_trace(go.Scatter(
        x=[año_max],
        y=[tasa_max],
        mode='markers+text',
        name='Pico maximo',
        marker=dict(size=18, color='#FFE66D', symbol='star', line=dict(width=2, color='#FF6B6B')),
        text=[f'  {tasa_max:.2f}'],
        textposition='top center'
    ))

    fig1.add_trace(go.Scatter(
        x=[año_min],
        y=[tasa_min],
        mode='markers+text',
        name='Valor minimo',
        marker=dict(size=12, color='#1A535C', symbol='circle'),
        text=[f'  {tasa_min:.2f}'],
        textposition='bottom center'
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
    # GRAFICO 2: PROMEDIO POR DECADA
    # ============================================
    st.subheader("Comparativa por decadas")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig2 = px.bar(
            promedio_decadas.reset_index(),
            x='decada',
            y='tasa_suicidio',
            title="Tasa promedio por decada",
            color='tasa_suicidio',
            color_continuous_scale=['#FFE66D', '#FF9F6B', '#FF6B6B', '#4ECDC4'],
            text='tasa_suicidio',
            labels={'decada': 'Decada', 'tasa_suicidio': 'Tasa promedio'}
        )
        fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("### Crecimiento por decada")
        decadas_lista = list(promedio_decadas.index)
        for i in range(len(decadas_lista) - 1):
            valor_ant = promedio_decadas[decadas_lista[i]]
            valor_sig = promedio_decadas[decadas_lista[i + 1]]
            crecimiento = ((valor_sig - valor_ant) / valor_ant) * 100
            color = "#FF6B6B" if crecimiento > 0 else "#4ECDC4"
            flecha = "↑" if crecimiento > 0 else "↓"
            st.markdown(f"""
            <div style="margin-bottom: 15px; padding: 10px; background: #F5F0E8; border-radius: 10px;">
                <b>{decadas_lista[i]}s → {decadas_lista[i + 1]}s</b><br>
                <span style="color: {color}; font-size: 20px;">{flecha} {abs(crecimiento):.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ============================================
    # GRAFICO 3: TOP AÑOS
    # ============================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Años con mayor tasa")
        top_años = df_nacional.nlargest(5, 'tasa_suicidio')[['anio', 'tasa_suicidio']]
        fig3 = px.bar(
            top_años,
            x='anio',
            y='tasa_suicidio',
            title="Top 5 años mas altos",
            color='tasa_suicidio',
            color_continuous_scale=['#FFE66D', '#FF9F6B', '#FF6B6B'],
            text='tasa_suicidio',
            labels={'anio': 'Año', 'tasa_suicidio': 'Tasa'}
        )
        fig3.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("Años con menor tasa")
        bottom_años = df_nacional.nsmallest(5, 'tasa_suicidio')[['anio', 'tasa_suicidio']]
        fig4 = px.bar(
            bottom_años,
            x='anio',
            y='tasa_suicidio',
            title="Top 5 años mas bajos",
            color='tasa_suicidio',
            color_continuous_scale=['#4ECDC4', '#1A535C'],
            text='tasa_suicidio',
            labels={'anio': 'Año', 'tasa_suicidio': 'Tasa'}
        )
        fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ============================================
    # TABLAS
    # ============================================
    with st.expander("Ver datos historicos completos"):
        tabla = df_nacional[['anio', 'tasa_suicidio', 'suicidios_total']].sort_values('anio', ascending=False)
        tabla.columns = ['Año', 'Tasa por 100,000 hab', 'Total de suicidios']
        tabla['Tasa por 100,000 hab'] = tabla['Tasa por 100,000 hab'].map(lambda x: f"{x:.2f}")
        tabla['Total de suicidios'] = tabla['Total de suicidios'].map(lambda x: f"{x:,}")
        st.dataframe(tabla, use_container_width=True, hide_index=True)

    with st.expander("Datos por decada"):
        tabla_decadas = promedio_decadas.reset_index()
        tabla_decadas.columns = ['Decada', 'Tasa promedio']
        tabla_decadas['Tasa promedio'] = tabla_decadas['Tasa promedio'].map(lambda x: f"{x:.2f}")
        st.dataframe(tabla_decadas, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ============================================
    # INTERPRETACION
    # ============================================
    st.subheader("Interpretacion")

    st.markdown(f"""
    *1. La tasa de suicidio ha aumentado significativamente*  
    Paso de *{tasa_1990:.2f}* en 1990 a *{tasa_2024:.2f}* en 2024, un *aumento del {aumento:.1f}%*.  
    Esto significa que la tasa se ha {"mas que duplicado" if aumento > 100 else "incrementado notablemente"} en 35 años.

    *2. Puntos criticos*  
    - Año con tasa mas alta: *{int(año_max)}* ({tasa_max:.2f})  
    - Año con tasa mas baja: *{int(año_min)}* ({tasa_min:.2f})

    *3. Tendencia por decadas*  
    Cada decada ha superado a la anterior:
    - 1990s: {promedio_decadas[1990]:.2f}
    - 2000s: {promedio_decadas[2000]:.2f}
    - 2010s: {promedio_decadas[2010]:.2f}
    - 2020s: {promedio_decadas[2020]:.2f}

    *4. Conclusion general*  
    La tendencia muestra un *crecimiento sostenido* en las ultimas tres decadas.
    """)

    st.markdown("---")
    st.caption("Fuente: Datamx.io | Tasas calculadas por cada 100,000 habitantes")