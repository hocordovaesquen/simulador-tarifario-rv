"""
🚀 SIMULADOR TARIFARIO RV - STREAMLIT CLOUD EDITION
===================================================
Versión simplificada y funcional para Streamlit Cloud
SIN xlcalculator - 100% Compatible con Python 3.13
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Simulador Tarifario RV",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILOS ====================
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
    """Carga datos de A.3 BBDD Neg o A.3 Negociación"""
    try:
        # Intentar diferentes nombres
        nombres_hoja = ['A.3 BBDD Neg', 'A.3 Negociacion', 'A.3 Negociación', 'A3. Negociación']
        
        df = None
        for nombre in nombres_hoja:
            try:
                df = pd.read_excel(archivo, sheet_name=nombre, header=6)
                st.success(f"✅ Hoja: '{nombre}'")
                break
            except:
                continue
        
        if df is None:
            st.error("❌ No se encontró hoja de negociación")
            return None
        
        if 'Cliente estandar' not in df.columns:
            st.error("❌ Columna 'Cliente estandar' no encontrada")
            return None
        
        df = df[df['Cliente estandar'].notna()].copy()
        
        if len(df) == 0:
            st.error("❌ Sin datos de clientes")
            return None
        
        # Limpiar valores
        for col in ['Monto USD', 'Cobro Acceso', 'Cobro Transacción']:
            if col in df.columns:
                df[col] = df[col].apply(limpiar_numero)
        
        # Agrupar
        df_agrupado = df.groupby(['Cliente estandar', 'Pais'], dropna=True).agg({
            'Monto USD': 'sum',
            'Cobro Acceso': 'sum',
            'Cobro Transacción': 'sum'
        }).reset_index()
        
        df_agrupado.columns = ['Broker', 'Pais', 'Monto_USD', 'Acceso_Real', 'Trans_Real']
        
        df_agrupado['Total_Real'] = df_agrupado['Acceso_Real'] + df_agrupado['Trans_Real']
        df_agrupado['BPS_Real'] = df_agrupado.apply(
            lambda x: calcular_bps(x['Total_Real'], x['Monto_USD']), axis=1
        )
        
        st.success(f"✅ {len(df_agrupado)} brokers cargados")
        return df_agrupado
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

@st.cache_data
def cargar_parametros(archivo):
    """Carga parámetros desde columna R+"""
    parametros = {
        'Negociacion': {
            'Acceso': {'Colombia': [], 'Peru': [], 'Chile': []},
            'Transaccion': {'Colombia': [], 'Peru': [], 'Chile': []}
        }
    }
    
    try:
        df_params = pd.read_excel(archivo, sheet_name='1. Parametros', header=None)
        
        rangos = {'Acceso': (99, 104), 'Transaccion': (139, 145)}
        columnas_pais = {
            'Colombia': (17, 18, 19, 20),
            'Peru': (21, 22, 23, 24),
            'Chile': (25, 26, 27, 28)
        }
        
        for tipo, (fila_inicio, fila_fin) in rangos.items():
            for fila in range(fila_inicio, fila_fin):
                try:
                    for pais, (col_min, col_max, col_var, col_fija) in columnas_pais.items():
                        min_val = limpiar_numero(df_params.iloc[fila, col_min])
                        max_val = limpiar_numero(df_params.iloc[fila, col_max])
                        var_val = limpiar_numero(df_params.iloc[fila, col_var])
                        fija_val = limpiar_numero(df_params.iloc[fila, col_fija])
                        
                        if max_val > 1e15:
                            max_val = float('inf')
                        
                        if min_val > 0 or max_val > 0 or var_val > 0 or fija_val > 0:
                            parametros['Negociacion'][tipo][pais].append({
                                'min': min_val, 'max': max_val, 'var': var_val, 'fija': fija_val
                            })
                except:
                    pass
        
        # Defaults
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
        st.warning(f"⚠️ Parámetros por defecto")
        for producto in ['Acceso', 'Transaccion']:
            for pais in ['Colombia', 'Peru', 'Chile']:
                parametros['Negociacion'][producto][pais] = [
                    {'min': 0, 'max': 5_000_000, 'var': 0, 'fija': 500},
                    {'min': 5_000_001, 'max': 15_000_000, 'var': 0, 'fija': 1500},
                    {'min': 15_000_001, 'max': float('inf'), 'var': 0, 'fija': 3000}
                ]
        return parametros

def calcular_ingreso_tramo(monto, tramos):
    """Calcula ingreso según tramos"""
    if not tramos:
        return 0.0
    
    for tramo in tramos:
        if tramo['min'] <= monto < tramo['max'] or \
           (tramo['max'] == float('inf') and monto >= tramo['min']):
            return (monto * tramo['var'] / 100) + tramo['fija']
    
    ultimo = tramos[-1]
    return (monto * ultimo['var'] / 100) + ultimo['fija']

def simular_tarifas(df_datos, parametros):
    """Simula ingresos"""
    resultados = []
    
    for _, row in df_datos.iterrows():
        pais_key = 'Peru' if row['Pais'] == 'Perú' else row['Pais']
        
        tramos_acc = parametros['Negociacion']['Acceso'].get(pais_key, [])
        tramos_trans = parametros['Negociacion']['Transaccion'].get(pais_key, [])
        
        acc_sim = calcular_ingreso_tramo(row['Monto_USD'], tramos_acc)
        trans_sim = calcular_ingreso_tramo(row['Monto_USD'], tramos_trans)
        total_sim = acc_sim + trans_sim
        
        diff = total_sim - row['Total_Real']
        var_pct = (diff / row['Total_Real'] * 100) if row['Total_Real'] > 0 else 0
        
        resultados.append({
            'Broker': row['Broker'],
            'Pais': row['Pais'],
            'Monto_USD': row['Monto_USD'],
            'Acceso_Real': row['Acceso_Real'],
            'Trans_Real': row['Trans_Real'],
            'Total_Real': row['Total_Real'],
            'BPS_Real': row['BPS_Real'],
            'Acceso_Simulado': acc_sim,
            'Trans_Simulado': trans_sim,
            'Total_Simulado': total_sim,
            'BPS_Simulado': calcular_bps(total_sim, row['Monto_USD']),
            'Diferencia': diff,
            'Variacion_%': var_pct
        })
    
    return pd.DataFrame(resultados)

def crear_grafico_comparativo(df_resultados):
    """Gráfico comparativo"""
    total_real = df_resultados['Total_Real'].sum()
    total_simulado = df_resultados['Total_Simulado'].sum()
    
    fig = go.Figure(data=[
        go.Bar(name='Real', x=['Total'], y=[total_real], marker_color='#e74c3c',
               text=[f'${total_real/1e6:.2f}M'], textposition='outside'),
        go.Bar(name='Simulado', x=['Total'], y=[total_simulado], marker_color='#27ae60',
               text=[f'${total_simulado/1e6:.2f}M'], textposition='outside')
    ])
    
    fig.update_layout(title='<b>Real vs Simulado</b>', barmode='group', 
                     height=400, template='plotly_white')
    return fig

def crear_grafico_por_pais(df_resultados):
    """Gráfico por país"""
    df_pais = df_resultados.groupby('Pais').agg({
        'Total_Real': 'sum', 'Total_Simulado': 'sum'
    }).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(name='Real', x=df_pais['Pais'], y=df_pais['Total_Real'], marker_color='#3498db'),
        go.Bar(name='Simulado', x=df_pais['Pais'], y=df_pais['Total_Simulado'], marker_color='#e67e22')
    ])
    
    fig.update_layout(title='<b>Por País</b>', barmode='group', 
                     height=400, template='plotly_white')
    return fig

# ==================== MAIN ====================
def main():
    st.markdown('<h1 class="main-header">🚀 SIMULADOR TARIFARIO RV</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        archivo = st.file_uploader("📁 Cargar Excel", type=['xlsx'])
        
        if not archivo:
            st.info("👆 Sube tu Excel")
            st.stop()
        
        with st.spinner("📊 Cargando..."):
            df_datos = cargar_datos_negociacion(archivo)
            if df_datos is None:
                st.stop()
            
            # Cargar parámetros en session_state si no existen
            if 'parametros' not in st.session_state:
                st.session_state.parametros = cargar_parametros(archivo)
        
        st.markdown("---")
        
        # Filtro por país
        paises = ['Todos'] + sorted(df_datos['Pais'].unique().tolist())
        pais_filtro = st.selectbox("🌎 País", paises)
        
        st.markdown("---")
        
        # Editor de parámetros
        st.markdown("### ✏️ Editar Parámetros")
        
        editar = st.checkbox("🔓 Habilitar Edición", value=False)
        
        if editar:
            st.markdown("#### Selecciona qué editar:")
            
            pais_edit = st.selectbox(
                "País",
                ['Colombia', 'Peru', 'Chile'],
                key='pais_editor'
            )
            
            producto_edit = st.selectbox(
                "Producto",
                ['Acceso', 'Transaccion'],
                key='producto_editor'
            )
            
            st.markdown(f"**Tramos para {pais_edit} - {producto_edit}:**")
            
            # Obtener tramos actuales
            tramos_actuales = st.session_state.parametros['Negociacion'][producto_edit][pais_edit]
            
            # Mostrar/editar cada tramo
            tramos_nuevos = []
            for i, tramo in enumerate(tramos_actuales):
                st.markdown(f"**Tramo {i+1}:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    min_val = st.number_input(
                        f"Mínimo",
                        value=float(tramo['min']),
                        step=100000.0,
                        key=f"min_{pais_edit}_{producto_edit}_{i}",
                        format="%.0f"
                    )
                    
                    var_val = st.number_input(
                        f"Variable %",
                        value=float(tramo['var']),
                        step=0.01,
                        key=f"var_{pais_edit}_{producto_edit}_{i}",
                        format="%.2f"
                    )
                
                with col2:
                    max_display = tramo['max'] if tramo['max'] != float('inf') else 999999999999
                    max_val = st.number_input(
                        f"Máximo",
                        value=float(max_display),
                        step=100000.0,
                        key=f"max_{pais_edit}_{producto_edit}_{i}",
                        format="%.0f"
                    )
                    if max_val > 1e12:
                        max_val = float('inf')
                    
                    fija_val = st.number_input(
                        f"Fija $",
                        value=float(tramo['fija']),
                        step=100.0,
                        key=f"fija_{pais_edit}_{producto_edit}_{i}",
                        format="%.2f"
                    )
                
                tramos_nuevos.append({
                    'min': min_val,
                    'max': max_val,
                    'var': var_val,
                    'fija': fija_val
                })
                
                st.markdown("---")
            
            # Actualizar parámetros en session_state
            st.session_state.parametros['Negociacion'][producto_edit][pais_edit] = tramos_nuevos
            
            if st.button("🔄 Aplicar Cambios", use_container_width=True):
                st.success("✅ Cambios aplicados! La simulación se recalculará automáticamente")
                st.rerun()
    
    df_filtrado = df_datos if pais_filtro == 'Todos' else df_datos[df_datos['Pais'] == pais_filtro]
    
    with st.spinner("🎯 Calculando..."):
        df_resultados = simular_tarifas(df_filtrado, st.session_state.parametros)
    
    # KPIs
    st.markdown("### 💰 Métricas")
    col1, col2, col3, col4 = st.columns(4)
    
    total_monto = df_resultados['Monto_USD'].sum()
    total_real = df_resultados['Total_Real'].sum()
    total_sim = df_resultados['Total_Simulado'].sum()
    diff = total_sim - total_real
    var_pct = (diff / total_real * 100) if total_real > 0 else 0
    
    col1.metric("💵 Monto", f"${total_monto/1e6:.2f}M")
    col2.metric("📊 Real", f"${total_real/1e6:.2f}M", f"{calcular_bps(total_real, total_monto):.2f} bps")
    col3.metric("🎯 Simulado", f"${total_sim/1e6:.2f}M", f"{var_pct:+.1f}%")
    col4.metric("📈 Diferencia", f"${diff/1e6:.2f}M")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(crear_grafico_comparativo(df_resultados), use_container_width=True)
    with col2:
        st.plotly_chart(crear_grafico_por_pais(df_resultados), use_container_width=True)
    
    # Tabla
    st.markdown("### 📋 Detalle")
    df_display = df_resultados.sort_values('Diferencia', ascending=False).copy()
    df_display['Monto_USD'] = df_display['Monto_USD'].apply(lambda x: f"${x:,.0f}")
    df_display['Total_Real'] = df_display['Total_Real'].apply(lambda x: f"${x:,.2f}")
    df_display['Total_Simulado'] = df_display['Total_Simulado'].apply(lambda x: f"${x:,.2f}")
    df_display['Diferencia'] = df_display['Diferencia'].apply(lambda x: f"${x:,.2f}")
    df_display['BPS_Real'] = df_display['BPS_Real'].apply(lambda x: f"{x:.2f}")
    df_display['BPS_Simulado'] = df_display['BPS_Simulado'].apply(lambda x: f"{x:.2f}")
    df_display['Variacion_%'] = df_display['Variacion_%'].apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(df_display[['Broker', 'Pais', 'Monto_USD', 'Total_Real', 'BPS_Real',
                            'Total_Simulado', 'BPS_Simulado', 'Diferencia', 'Variacion_%']], 
                use_container_width=True, height=500)
    
    # Exportar
    st.markdown("---")
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "resultados.csv", use_container_width=True)

if __name__ == "__main__":
    main()
