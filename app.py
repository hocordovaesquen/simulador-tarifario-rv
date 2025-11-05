"""
🚀 SIMULADOR TARIFARIO RV - STREAMLIT CLOUD
============================================
Versión optimizada para Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Simulador Tarifario RV",
    page_icon="🚀",
    layout="wide"
)

# ==================== CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES ====================
def limpiar_numero(valor):
    """Limpia y convierte valores a float"""
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        valor_str = str(valor).replace('$', '').replace(',', '').strip()
        return float(valor_str) if valor_str else 0.0
    except:
        return 0.0

def calcular_bps(ingreso, monto):
    """Calcula basis points"""
    if monto == 0 or pd.isna(monto):
        return 0.0
    return (ingreso / monto) * 10_000

@st.cache_data
def cargar_datos_negociacion(archivo):
    """Carga datos de A.3 BBDD Neg"""
    try:
        df = pd.read_excel(archivo, sheet_name='A.3 BBDD Neg', header=6)
        
        if 'Cliente estandar' not in df.columns:
            st.error("❌ La hoja 'A.3 BBDD Neg' no tiene la columna 'Cliente estandar'")
            return None
        
        df = df[df['Cliente estandar'].notna()].copy()
        
        columnas_numericas = ['Monto USD', 'Acceso actual', 'Transaccion actual', 
                             'Cobro Acceso', 'Cobro Transacción']
        
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = df[col].apply(limpiar_numero)
        
        df_agrupado = df.groupby(['Cliente estandar', 'Pais'], dropna=True).agg({
            'Monto USD': 'sum',
            'Acceso actual': 'sum',
            'Transaccion actual': 'sum',
            'Cobro Acceso': 'sum',
            'Cobro Transacción': 'sum'
        }).reset_index()
        
        df_agrupado.columns = [
            'Broker', 'Pais', 'Monto_USD',
            'Acceso_Real', 'Trans_Real',
            'Acceso_Propuesta', 'Trans_Propuesta'
        ]
        
        return df_agrupado
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None

@st.cache_data
def cargar_parametros_excel(archivo):
    """Lee parámetros desde columna R"""
    parametros = {
        'Negociacion': {
            'Acceso': {'Colombia': [], 'Peru': [], 'Chile': []},
            'Transaccion': {'Colombia': [], 'Peru': [], 'Chile': []}
        }
    }
    
    try:
        df_params = pd.read_excel(archivo, sheet_name='1. Parametros', header=None)
        
        # ACCESO (filas 99-104) y TRANSACCIÓN (filas 139-145)
        for tipo, filas in [('Acceso', range(99, 104)), ('Transaccion', range(139, 145))]:
            for i in filas:
                try:
                    for pais, cols in [('Colombia', (19,20,21,22)), ('Peru', (23,24,25,26)), ('Chile', (27,28,29,30))]:
                        min_val = limpiar_numero(df_params.iloc[i, cols[0]])
                        max_val = limpiar_numero(df_params.iloc[i, cols[1]])
                        var_val = limpiar_numero(df_params.iloc[i, cols[2]])
                        fija_val = limpiar_numero(df_params.iloc[i, cols[3]])
                        
                        if max_val > 1e15:
                            max_val = float('inf')
                        
                        if min_val > 0 or max_val > 0 or var_val > 0 or fija_val > 0:
                            parametros['Negociacion'][tipo][pais].append({
                                'min': min_val, 'max': max_val, 'var': var_val, 'fija': fija_val
                            })
                except:
                    pass
        
        # Defaults si vacío
        for producto in ['Acceso', 'Transaccion']:
            for pais in ['Colombia', 'Peru', 'Chile']:
                if not parametros['Negociacion'][producto][pais]:
                    parametros['Negociacion'][producto][pais] = [
                        {'min': 0, 'max': 5_000_000, 'var': 0, 'fija': 500},
                        {'min': 5_000_001, 'max': 15_000_000, 'var': 0, 'fija': 1500},
                        {'min': 15_000_001, 'max': float('inf'), 'var': 0, 'fija': 3000}
                    ]
        
        return parametros
        
    except Exception as e:
        st.warning(f"⚠️ Usando parámetros por defecto")
        for producto in ['Acceso', 'Transaccion']:
            for pais in ['Colombia', 'Peru', 'Chile']:
                parametros['Negociacion'][producto][pais] = [
                    {'min': 0, 'max': 5_000_000, 'var': 0, 'fija': 500},
                    {'min': 5_000_001, 'max': 15_000_000, 'var': 0, 'fija': 1500},
                    {'min': 15_000_001, 'max': float('inf'), 'var': 0, 'fija': 3000}
                ]
        return parametros

def calcular_ingreso(monto, tramos):
    """Calcula ingreso según tramos"""
    if not tramos:
        return 0.0
    
    for tramo in tramos:
        if tramo['min'] <= monto < tramo['max'] or (tramo['max'] == float('inf') and monto >= tramo['min']):
            return (monto * tramo['var'] / 100) + tramo['fija']
    
    ultimo = tramos[-1]
    return (monto * ultimo['var'] / 100) + ultimo['fija']

def simular_con_parametros(df_datos, parametros):
    """Simula ingresos"""
    resultados = []
    
    for _, row in df_datos.iterrows():
        pais_key = 'Peru' if row['Pais'] == 'Perú' else row['Pais']
        
        tramos_acc = parametros['Negociacion']['Acceso'].get(pais_key, [])
        tramos_trans = parametros['Negociacion']['Transaccion'].get(pais_key, [])
        
        acc_sim = calcular_ingreso(row['Monto_USD'], tramos_acc)
        trans_sim = calcular_ingreso(row['Monto_USD'], tramos_trans)
        
        total_real = row['Acceso_Real'] + row['Trans_Real']
        total_sim = acc_sim + trans_sim
        
        resultados.append({
            'Broker': row['Broker'],
            'Pais': row['Pais'],
            'Monto_USD': row['Monto_USD'],
            'Total_Real': total_real,
            'Total_Simulado': total_sim,
            'Diferencia': total_sim - total_real,
            'BPS_Simulado': calcular_bps(total_sim, row['Monto_USD'])
        })
    
    return pd.DataFrame(resultados)

# ==================== MAIN ====================
def main():
    st.markdown('<h1 class="main-header">🚀 SIMULADOR TARIFARIO RV</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        archivo = st.file_uploader("📁 Cargar Excel", type=['xlsx'])
        
        if not archivo:
            st.info("👆 Carga tu Excel")
            st.stop()
        
        with st.spinner("🔄 Cargando..."):
            df_datos = cargar_datos_negociacion(archivo)
            if df_datos is None:
                st.stop()
            parametros = cargar_parametros_excel(archivo)
        
        st.success(f"✅ {len(df_datos)} brokers")
        st.markdown("---")
        
        paises = ['Todos'] + sorted(df_datos['Pais'].unique().tolist())
        pais_filtro = st.selectbox("🌎 País", paises)
    
    df_filtrado = df_datos if pais_filtro == 'Todos' else df_datos[df_datos['Pais'] == pais_filtro]
    
    with st.spinner("🔄 Calculando..."):
        df_resultados = simular_con_parametros(df_filtrado, parametros)
    
    # KPIs
    st.markdown("### 💰 KPIs")
    total_monto = df_resultados['Monto_USD'].sum()
    total_real = df_resultados['Total_Real'].sum()
    total_sim = df_resultados['Total_Simulado'].sum()
    var_pct = ((total_sim - total_real) / total_real * 100) if total_real > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Monto", f"${total_monto/1e6:.2f}M")
    col2.metric("📊 Real", f"${total_real/1e6:.2f}M")
    col3.metric("🎯 Simulado", f"${total_sim/1e6:.2f}M", f"{var_pct:+.1f}%")
    col4.metric("📈 BPS", f"{calcular_bps(total_sim, total_monto):.2f}")
    
    st.markdown("---")
    
    # Gráfico
    fig = go.Figure([
        go.Bar(name='Real', x=['Total'], y=[total_real], marker_color='#e74c3c', 
               text=[f'${total_real/1e6:.2f}M'], textposition='outside'),
        go.Bar(name='Simulado', x=['Total'], y=[total_sim], marker_color='#27ae60',
               text=[f'${total_sim/1e6:.2f}M'], textposition='outside')
    ])
    fig.update_layout(height=400, barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown("### 📋 Detalle")
    df_display = df_resultados.sort_values('Diferencia', ascending=False).copy()
    df_display['Monto_USD'] = df_display['Monto_USD'].apply(lambda x: f"${x:,.0f}")
    df_display['Total_Real'] = df_display['Total_Real'].apply(lambda x: f"${x:,.2f}")
    df_display['Total_Simulado'] = df_display['Total_Simulado'].apply(lambda x: f"${x:,.2f}")
    df_display['Diferencia'] = df_display['Diferencia'].apply(lambda x: f"${x:,.2f}")
    df_display['BPS_Simulado'] = df_display['BPS_Simulado'].apply(lambda x: f"{x:.2f}")
    st.dataframe(df_display, use_container_width=True, height=500)
    
    # Exportar
    st.markdown("---")
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "resultados.csv", use_container_width=True)

if __name__ == "__main__":
    main()
