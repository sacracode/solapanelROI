import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Ahorro Solar", layout="centered")

st.title("☀️ Simulador de Ahorro con Paneles Solares")
st.markdown("Calcula tu ahorro estimado a lo largo de 25 años al instalar un sistema solar en casa o negocio.")

# Entradas del usuario
with st.form("solar_form"):
    ubicacion = st.text_input("Ubicación", "Jalisco")
    consumo_kwh_bimestral = st.number_input("Consumo bimestral (kWh)", min_value=100, max_value=4000, value=1000)
    tarifa_kwh = st.number_input("Tarifa actual por kWh (MXN)", min_value=0.5, max_value=10.0, value=2.8)
    costo_sistema = st.number_input("Costo total del sistema solar (MXN)", min_value=20000, max_value=1000000, value=120000)
    inflacion_energetica = st.slider("Inflación energética estimada (%)", min_value=0.0, max_value=15.0, value=7.0) / 100
    submit = st.form_submit_button("Calcular ahorro")

if submit:
    vida_util_anios = 25

    # Cálculo de costo bimestral y anual
    costo_bimestral = consumo_kwh_bimestral * tarifa_kwh
    ahorro_anual_sin_inflacion = (costo_bimestral * 6)  # 6 bimestres en un año

    ahorro_acumulado = []
    ahorro_anual = ahorro_anual_sin_inflacion
    recuperacion_anio = None
    ahorro_total = 0

    for year in range(1, vida_util_anios + 1):
        ahorro_total += ahorro_anual
        ahorro_acumulado.append(ahorro_total)
        if not recuperacion_anio and ahorro_total >= costo_sistema:
            recuperacion_anio = year
        ahorro_anual *= (1 + inflacion_energetica)

    roi = ahorro_total / costo_sistema
    tiempo_recuperacion = recuperacion_anio if recuperacion_anio else vida_util_anios

    # Mostrar resultados
    st.subheader("Resultados estimados:")
    st.write(f"**Ubicación:** {ubicacion}")
    st.write(f"**Costo bimestral actual de luz:** ${costo_bimestral:,.2f} MXN")
    st.write(f"**Ahorro total estimado en 25 años:** ${ahorro_total:,.2f} MXN")
    st.write(f"**Retorno sobre inversión (ROI):** {roi:.2f}x")
    st.write(f"**Años estimados para recuperar la inversión:** {tiempo_recuperacion} años")

    # Tabla y gráfica
    df_ahorro = pd.DataFrame({
        'Año': list(range(1, vida_util_anios + 1)),
        'Ahorro acumulado (MXN)': ahorro_acumulado
    })

    fig, ax = plt.subplots()
    ax.plot(df_ahorro['Año'], df_ahorro['Ahorro acumulado (MXN)'], label="Ahorro acumulado")
    ax.axhline(y=costo_sistema, color='red', linestyle='--', label='Costo del sistema')
    if recuperacion_anio:
        ax.axvline(x=recuperacion_anio, color='green', linestyle=':', label=f"ROI se paga en año {recuperacion_anio}")
    ax.set_xlabel("Año")
    ax.set_ylabel("MXN")
    ax.set_title("Proyección de Ahorro Acumulado")
    ax.legend()

    st.pyplot(fig)

    st.caption("Esta herramienta es una estimación educativa. Para un análisis exacto, consulta a tu proveedor solar.")
