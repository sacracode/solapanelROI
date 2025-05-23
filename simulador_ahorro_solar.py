import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Ahorro Solar con ROI", layout="centered")
st.title("☀️ Simulador de Ahorro con Paneles Solares – México (CFE)")

tipo_usuario = st.selectbox("Selecciona el tipo de usuario:", ["Residencial", "Comercial"])
IVA = 0.16

# Tarifas residenciales con bloques por tarifa de CFE
tarifas_residenciales = {
    "1":  {"costos": [0.793, 0.956, 3.367], "limites": [150, 280]},
    "1A": {"costos": [0.793, 0.956, 3.367], "limites": [300, 600]},
    "1B": {"costos": [0.793, 0.956, 3.367], "limites": [400, 800]},
    "1C": {"costos": [0.793, 0.956, 3.367], "limites": [850, 1000]},
    "1D": {"costos": [0.793, 0.956, 3.367], "limites": [1000, 1200]},
    "1E": {"costos": [0.793, 0.956, 3.367], "limites": [2000, 2500]},
    "1F": {"costos": [0.793, 0.956, 3.367], "limites": [2500, 3000]},
}

# Tarifas comerciales estimadas
tarifas_comerciales = {
    "PDBT": {"costo_kwh": 4.0, "costo_demanda": 150},
    "GDBT": {"costo_kwh": 2.5, "costo_demanda": 300},
    "GDMTO": {"costo_kwh": 1.8, "costo_demanda": 500},
}

def calcular_desglose(consumo, tarifa_key):
    limites = tarifas_residenciales[tarifa_key]["limites"]
    costos = tarifas_residenciales[tarifa_key]["costos"]
    bloques = [0, 0, 0]

    if consumo <= limites[0]:
        bloques[0] = consumo
    elif consumo <= limites[1]:
        bloques[0] = limites[0]
        bloques[1] = consumo - limites[0]
    else:
        bloques[0] = limites[0]
        bloques[1] = limites[1] - limites[0]
        bloques[2] = consumo - limites[1]

    costos_bloques = [bloques[i] * costos[i] for i in range(3)]
    subtotal = sum(costos_bloques)
    total = subtotal * (1 + IVA)

    return bloques, costos_bloques, subtotal, total

def calcular_roi(consumo_bimestral, tarifa_kwh, costo_panel, mensualidad_panel, anios=25):
    ahorro_mensual = consumo_bimestral * tarifa_kwh / 2
    ahorro_acumulado, costo_acumulado = [], []
    saldo = 0
    roi_year = None

    for anio in range(1, anios + 1):
        saldo += ahorro_mensual * 12
        costo = mensualidad_panel * 12 * anio
        ahorro_acumulado.append(saldo)
        costo_acumulado.append(costo)
        if roi_year is None and saldo >= costo_panel:
            roi_year = anio

    return ahorro_acumulado, costo_acumulado, roi_year

# Entradas comunes
consumo = st.number_input("Ingresa tu consumo bimestral en kWh:", min_value=0, step=1)
costo_panel = st.number_input("Costo total del sistema solar (MXN):", min_value=10000, step=1000, value=120000)
mensualidad = st.number_input("Pago mensual estimado del panel solar (MXN):", min_value=0, step=100, value=3000)
tarifa_kwh_manual = st.number_input("Tarifa promedio por kWh actual (MXN):", min_value=0.5, step=0.1, value=2.8)

if tipo_usuario == "Residencial":
    tarifa = st.selectbox("Selecciona tu tarifa:", list(tarifas_residenciales.keys()))

    if st.button("Calcular Residencial"):
        bloques, costos_bloques, subtotal, total = calcular_desglose(consumo, tarifa)

        st.subheader("📊 Desglose estilo CFE:")
        df = pd.DataFrame({
            "Bloque": ["Básico", "Intermedio", "Excedente"],
            "Consumo (kWh)": bloques,
            "Costo (MXN)": [round(c, 2) for c in costos_bloques]
        })
        st.table(df)
        st.write(f"**Subtotal (sin IVA):** ${subtotal:.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:.2f} MXN")

        ahorro, pagos, roi_year = calcular_roi(consumo, tarifa_kwh_manual, costo_panel, mensualidad)

        st.subheader("🔁 Proyección de Ahorro vs Costo del Panel:")
        fig, ax = plt.subplots()
        ax.plot(range(1, 26), ahorro, label="Ahorro Acumulado", linewidth=2)
        ax.plot(range(1, 26), pagos, label="Pagos del Sistema", linestyle="--")
        if roi_year:
            ax.axvline(x=roi_year, color='green', linestyle=':', label=f"ROI en año {roi_year}")
        ax.set_xlabel("Año")
        ax.set_ylabel("MXN")
        ax.set_title("Retorno de Inversión (ROI)")
        ax.legend()
        st.pyplot(fig)

elif tipo_usuario == "Comercial":
    tarifa = st.selectbox("Selecciona tu tarifa:", list(tarifas_comerciales.keys()))
    demanda_kw = st.number_input("Demanda máxima registrada (kW):", min_value=0.0, step=1.0)

    if st.button("Calcular Comercial"):
        datos = tarifas_comerciales[tarifa]
        energia = consumo * datos["costo_kwh"]
        demanda = demanda_kw * datos["costo_demanda"]
        subtotal = energia + demanda
        total = subtotal * (1 + IVA)

        st.subheader("📊 Cálculo Comercial:")
        st.write(f"Energía: {consumo} kWh × ${datos['costo_kwh']} = ${energia:.2f}")
        st.write(f"Demanda: {demanda_kw} kW × ${datos['costo_demanda']} = ${demanda:.2f}")
        st.write(f"**Subtotal (sin IVA):** ${subtotal:.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:.2f} MXN")

        ahorro, pagos, roi_year = calcular_roi(consumo, datos["costo_kwh"], costo_panel, mensualidad)

        st.subheader("🔁 Proyección de Ahorro vs Costo del Panel:")
        fig, ax = plt.subplots()
        ax.plot(range(1, 26), ahorro, label="Ahorro Acumulado", linewidth=2)
        ax.plot(range(1, 26), pagos, label="Pagos del Sistema", linestyle="--")
        if roi_year:
            ax.axvline(x=roi_year, color='green', linestyle=':', label=f"ROI en año {roi_year}")
        ax.set_xlabel("Año")
        ax.set_ylabel("MXN")
        ax.set_title("Retorno de Inversión (ROI)")
        ax.legend()
        st.pyplot(fig)

st.caption("💡 Estos son estimados basados en tarifas públicas de CFE. Consulta tu recibo para información precisa.")
