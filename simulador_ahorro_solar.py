import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Simulador de Ahorro Solar", layout="centered")

st.title("☀️ Simulador de Ahorro con Paneles Solares")
st.markdown("Calcula tu ahorro estimado a lo largo de 25 años al instalar un sistema solar en casa o negocio.")

# Entradas del usuario
ubicacion = st.text_input("Ubicación", "Jalisco")
consumo_kwh_mensual = st.number_input("Consumo mensual (kWh)", min_value=100, max_value=2000, value=500)
tarifa_kwh = st.number_input("Tarifa actual por kWh (MXN)", min_value=0.5, max_value=10.0, value=2.8)
costo_sistema = st.number_input("Costo total del sistema solar (MXN)", min_value=20000, max_value=300000, value=120000)
inflacion_energetica = st.slider("Inflación energética estimada (%)", min_value=0.0, max_value=15.0, value=7.0) / 100
vida_util_anios = 25

# Cálculos
costo_mensual = consumo_kwh_mensual * tarifa_kwh
ahorro_anual_sin_inflacion = costo_mensual * 12

ahorro_acumulado = []
ahorro_anual = ahorro_anual_sin_inflacion

for year in range(1, vida_util_anios + 1):
    ahorro_acumulado.append(ahorro_anual)
    ahorro_anual *= (1 + inflacion_energetica)

total_ahorro = sum(ahorro_acumulado)
roi = total_ahorro / costo_sistema
tiempo_recuperacion = costo_sistema / ahorro_acumulado[0]

# Mostrar resultados
st.subheader("Resultados estimados:")
st.write(f"**Ubicación:** {ubicacion}")
st.write(f"**Costo mensual actual de luz:** ${costo_mensual:,.2f} MXN")
st.write(f"**Ahorro total estimado en 25 años:** ${total_ahorro:,.2f} MXN")
st.write(f"**Retorno sobre inversión (ROI):** {roi:.2f}x")
st.write(f"**Años estimados para recuperar la inversión:** {tiempo_recuperacion:.1f} años")

# Tabla y gráfica
df_ahorro = pd.DataFrame({
    'Año': list(range(1, vida_util_anios + 1)),
    'Ahorro anual (MXN)': ahorro_acumulado
})

st.subheader("Proyección de Ahorro Anual:")
st.line_chart(df_ahorro.set_index('Año'))

st.caption("Esta herramienta es una estimación educativa. Para un análisis exacto, consulta a tu proveedor solar.")
