# 🚀 Simulador Tarifario RV - Streamlit Edition

Simulador simplificado y funcional para análisis de tarifas de Renta Variable.

## ✨ Características

- ✅ **Compatible con Python 3.13** (sin xlcalculator)
- 🎮 **Editor Interactivo** de parámetros tarifarios
- ✏️ **Edición en tiempo real** sin tocar el Excel
- 📊 **Dashboard interactivo** con KPIs y gráficos
- 🌎 **Filtros por país**: Colombia, Perú, Chile
- 📈 **Comparación Real vs Simulado**
- 🔄 **Múltiples escenarios** de simulación
- 💾 **Exportación a CSV**
- ⚡ **Rápido y confiable**

## 📦 Estructura

```
repo/
├── app.py              # Aplicación Streamlit
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 🚀 Deploy en Streamlit Cloud

### Paso 1: Subir a GitHub

1. Crea un nuevo repositorio en GitHub
2. Sube estos archivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### Paso 2: Deploy

1. Ve a [https://share.streamlit.io](https://share.streamlit.io)
2. Click en "New app"
3. Selecciona tu repositorio
4. Configura:
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click "Deploy"

¡Listo! Tu app estará online en 2-3 minutos.

## 📊 Uso

### Flujo Básico

1. **Cargar Excel**: Sube tu archivo .xlsx
2. **Ver Dashboard**: KPIs, gráficos y tabla
3. **Filtrar** (opcional): Selecciona un país
4. **Exportar**: Descarga resultados en CSV

### Editor Interactivo 🎮

**¡NUEVO!** Ahora puedes editar parámetros tarifarios directamente en la interfaz:

1. **Habilita la edición**: 
   - En el sidebar, activa "🔓 Habilitar Edición"

2. **Selecciona qué editar**:
   - País: Colombia, Perú o Chile
   - Producto: Acceso o Transacción

3. **Modifica los tramos**:
   - Cambia Mínimo, Máximo, Variable % o Fija $
   - Ejemplo: Aumentar tarifa fija de $1,500 a $2,000

4. **Aplica cambios**:
   - Click en "🔄 Aplicar Cambios"
   - La simulación se recalcula automáticamente

5. **Observa el impacto**:
   - KPIs se actualizan
   - Gráficos muestran nuevo resultado
   - Tabla refleja nuevos ingresos

6. **Prueba diferentes escenarios**:
   - Edita, aplica, observa
   - Exporta resultados para cada escenario
   - Compara en Excel

**Ventajas:**
- ✅ Sin editar el Excel original
- ✅ Cambios instantáneos
- ✅ Múltiples pruebas rápidas
- ✅ Ideal para análisis "what-if"

## 📝 Estructura del Excel

### Hoja: "A.3 BBDD Neg" (o "A.3 Negociación")
- Header en fila 6
- Columnas requeridas:
  - `Cliente estandar`: Nombre del broker
  - `Pais`: Colombia / Perú / Chile
  - `Monto USD`: Monto negociado
  - `Cobro Acceso`: Ingreso real por acceso
  - `Cobro Transacción`: Ingreso real por transacción

### Hoja: "1. Parametros"
- Columnas R+ (17+): Nuevo tarifario
- Filas 99-104: Parámetros de Acceso
- Filas 139-145: Parámetros de Transacción

**Distribución por país:**
- Columnas 17-20 (R-U): Colombia
- Columnas 21-24 (V-Y): Perú
- Columnas 25-28 (Z-AC): Chile

## 🎯 Qué Hace la App

1. **Carga** tu Excel
2. **Lee** valores reales de "Cobro Acceso" y "Cobro Transacción"
3. **Simula** nuevos ingresos según parámetros de columna R+
4. **Compara** Real vs Simulado
5. **Muestra** KPIs, gráficos y tabla detallada
6. **Exporta** resultados

## 💡 Fórmulas

### Cálculo de Ingreso por Tramo
```
Ingreso = (Monto × Variable%) + Fija
```

### BPS (Basis Points)
```
BPS = (Ingreso / Monto) × 10,000
```

## 🔧 Ejecución Local (Opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

## 🐛 Solución de Problemas

### Error: "Columna no encontrada"
- Verifica que tu Excel tenga las columnas: `Cliente estandar`, `Pais`, `Monto USD`, `Cobro Acceso`, `Cobro Transacción`
- El header debe estar en la fila 6

### Total_Real en $0
- ✅ SOLUCIONADO: La app usa las columnas correctas (`Cobro Acceso` y `Cobro Transacción`)

### App lenta
- Filtra por un país específico
- Reduce el tamaño del Excel si es muy grande

## ⚡ Diferencias con Versiones Anteriores

Esta versión:
- ❌ **NO usa xlcalculator** (evita problemas de compatibilidad)
- ✅ **Lee valores directos** del Excel
- ✅ **Compatible con Python 3.13**
- ✅ **Más simple y mantenible**
- ✅ **Deploy garantizado en Streamlit Cloud**

## 📚 Ventajas

✅ Sin problemas de compatibilidad  
✅ Deploy rápido y confiable  
✅ Código simple y mantenible  
✅ Performance óptimo  
✅ Funciona con cualquier versión de Python 3.9+  

## 🎉 ¡Listo!

Tu simulador está optimizado para Streamlit Cloud. Sube los archivos a GitHub y haz deploy. ¡Funcionará a la primera!

---

**Made with ❤️ for Streamlit Cloud**
