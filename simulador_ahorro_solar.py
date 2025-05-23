import streamlit as st
import pandas as pd

# Configuración
st.set_page_config(page_title="Simulador de Ahorro Solar CFE", layout="centered")
st.title("☀️ Simulador de Ahorro con Paneles Solares – México (CFE)")

# Tipos de usuario
tipo_usuario = st.selectbox("Selecciona el tipo de usuario:", ["Residencial", "Comercial"])

# Tarifas residenciales extendidas (MXN por kWh)
tarifas_residenciales = {
    "1":  {"limites": [150, 280],  "costos": [0.793, 0.956, 3.367]},
    "1A": {"limites": [300, 600],  "costos": [0.793, 0.956, 3.367]},
    "1B": {"limites": [400, 800],  "costos": [0.793, 0.956, 3.367]},
    "1C": {"limites": [850, 1000], "costos": [0.793, 0.956, 3.367]},
    "1D": {"limites": [1000, 1200],"costos": [0.793, 0.956, 3.367]},
    "1E": {"limites": [2000, 2500],"costos": [0.793, 0.956, 3.367]},
    "1F": {"limites": [2500, 3000],"costos": [0.793, 0.956, 3.367]},
}

# Tarifas comerciales estimadas
tarifas_comerciales = {
    "PDBT":  {"costo_kwh": 4.0, "costo_demanda": 150},
    "GDBT":  {"costo_kwh": 2.5, "costo_demanda": 300},
    "GDMTO": {"costo_kwh": 1.8, "costo_demanda": 500},
}

IVA = 0.16

# Función residencial
def calcular_costo_residencial(consumo, tarifa):
    limites = tarifas_residenciales[tarifa]["limites"]
    costos = tarifas_residenciales[tarifa]["costos"]
    consumo_bloques = [0, 0, 0]
    costos_bloques = [0, 0, 0]

    if consumo <= limites[0]:
        consumo_bloques[0] = consumo
    elif consumo <= limites[1]:
        consumo_bloques[0] = limites[0]
        consumo_bloques[1] = consumo - limites[0]
    else:
        consumo_bloques[0] = limites[0]
        consumo_bloques[1] = limites[1] - limites[0]
        consumo_bloques[2] = consumo - limites[1]

    for i in range(3):
        costos_bloques[i] = consumo_bloques[i] * costos[i]

    subtotal = sum(costos_bloques)
    total = subtotal * (1 + IVA)
    return consumo_bloques, costos_bloques, subtotal, total

# ENTRADAS
if tipo_usuario == "Residencial":
    tarifa = st.selectbox("Selecciona tu tarifa:", list(tarifas_residenciales.keys()))
    consumo = st.number_input("Ingresa tu consumo bimestral en kWh:", min_value=0, step=1)

    if st.button("Calcular"):
        consumo_bloques, costos_bloques, subtotal, total = calcular_costo_residencial(consumo, tarifa)
        st.subheader("Desglose estilo CFE:")
        df = pd.DataFrame({
            "Bloque": ["Básico", "Intermedio", "Excedente"],
            "Consumo (kWh)": consumo_bloques,
            "Costo (MXN)": [round(x, 2) for x in costos_bloques]
        })
        st.table(df)
        st.write(f"**Subtotal (sin IVA):** ${subtotal:.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:.2f} MXN")
        st.caption("💡 Estos son estimados con base en las tarifas públicas de CFE. El precio real será el que indique tu recibo actual.")

elif tipo_usuario == "Comercial":
    tarifa = st.selectbox("Selecciona tu tarifa:", list(tarifas_comerciales.keys()))
    consumo = st.number_input("Ingresa tu consumo mensual en kWh:", min_value=0, step=1)
    demanda_real_kw = st.number_input("Demanda máxima registrada (kW):", min_value=0.0, step=1.0)

    if st.button("Calcular"):
        datos = tarifas_comerciales[tarifa]
        energia_total = consumo * datos["costo_kwh"]
        demanda_total = demanda_real_kw * datos["costo_demanda"]
        subtotal = energia_total + demanda_total
        total = subtotal * (1 + IVA)

        st.subheader("Desglose comercial:")
        st.write(f"🔌 Energía: {consumo} kWh × ${datos['costo_kwh']:.2f} = ${energia_total:.2f}")
        st.write(f"⚡ Demanda: {demanda_real_kw} kW × ${datos['costo_demanda']:.2f} = ${demanda_total:.2f}")
        st.write(f"**Subtotal (sin IVA):** ${subtotal:.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:.2f} MXN")
        st.caption("💡 Estos son estimados con base en las tarifas públicas de CFE. El precio real será el que indique tu recibo actual.")
