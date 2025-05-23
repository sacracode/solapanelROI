import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Solar ROI - Profesional", layout="centered")
st.title("☀️ Simulador de Ahorro con Paneles Solares – Profesional")

tipo_usuario = st.selectbox("Selecciona el tipo de usuario:", ["Residencial", "Comercial"])
IVA = 0.16

# Tarifas residenciales por bloque
tarifa_fija = {
    "basico": 1.0,
    "intermedio": 1.3,
    "excedente": 3.0,
}

def calcular_bloques_fijos(consumo):
    bloques = [0, 0, 0]
    if consumo <= 150:
        bloques[0] = consumo
    elif consumo <= 350:
        bloques[0] = 150
        bloques[1] = consumo - 150
    else:
        bloques[0] = 150
        bloques[1] = 200
        bloques[2] = consumo - 350

    costos = [
        bloques[0] * tarifa_fija["basico"],
        bloques[1] * tarifa_fija["intermedio"],
        bloques[2] * tarifa_fija["excedente"],
    ]
    subtotal = sum(costos)
    total = subtotal * (1 + IVA)
    return bloques, costos, subtotal, total

def calcular_roi_mensual(consumo_bimestral, tarifa_kwh, costo_panel, anios=25):
    ahorro_mensual = (consumo_bimestral / 2) * tarifa_kwh
    ahorro_acumulado = []
    meses = anios * 12
    saldo = 0
    roi_mes = None
    for mes in range(1, meses + 1):
        saldo += ahorro_mensual
        ahorro_acumulado.append(saldo)
        if roi_mes is None and saldo >= costo_panel:
            roi_mes = mes
    return ahorro_acumulado, roi_mes

# Entradas generales
consumo = st.number_input("Ingresa tu consumo bimestral en kWh:", min_value=0, step=1)
costo_panel = st.number_input("Costo total del sistema solar (MXN):", min_value=10000, step=1000, value=120000)

# Modo Residencial
if tipo_usuario == "Residencial":
    if st.button("Calcular Residencial"):
        bloques, costos, subtotal, total = calcular_bloques_fijos(consumo)

        st.subheader("📊 Desglose estilo CFE:")
        df = pd.DataFrame({
            "Bloque": ["Básico (1.00)", "Intermedio (1.30)", "Excedente (3.00)"],
            "Consumo (kWh)": bloques,
            "Costo (MXN)": [round(c, 2) for c in costos]
        })
        st.table(df)
        st.write(f"**Subtotal (sin IVA):** ${subtotal:.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:.2f} MXN")

        tarifa_aplicada = subtotal / consumo if consumo > 0 else 0
        ahorro, roi_mes = calcular_roi_mensual(consumo, tarifa_aplicada, costo_panel)

        st.subheader("📈 Proyección de Retorno de Inversión (ROI)")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
