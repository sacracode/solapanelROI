import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Ahorro Solar con ROI", layout="centered")
st.title("☀️ Simulador de Ahorro con Paneles Solares – México (CFE)")

tipo_usuario = st.selectbox("Selecciona el tipo de usuario:", ["Residencial", "Comercial"])
IVA = 0.16

# Tarifas por bloque fijas
tarifa_fija = {
    "basico": 1.0,
    "intermedio": 1.3,
    "excedente": 3.0,
}

def calcular_bloques_fijos(consumo):
    bloques = [0, 0, 0]  # básico, intermedio, excedente

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

def calcular_roi(consumo_bimestral, tarifa_aplicada, costo_panel, bimestralidad, anios=25):
    ahorro_bimestral = consumo_bimestral * tarifa_aplicada
    ahorro_acumulado, pagos_acumulados = [], []
    saldo = 0
    roi_year = None

    for anio in range(1, anios + 1):
        saldo += ahorro_bimestral * 6
        pago = bimestralidad * 6 * anio
        ahorro_acumulado.append(saldo)
        pagos_acumulados.append(pago)
        if roi_year is None and saldo >= costo_panel:
            roi_year = anio

    return ahorro_acumulado, pagos_acumulados, roi_year

# Entradas comunes
consumo = st.number_input("Ingresa tu consumo bimestral en kWh:", min_value=0, step=1)
costo_panel = st.number_input("Costo total del sistema solar (MXN):", min_value=10000, step=1000, value=120000)
bimestralidad = st.number_input("Pago bimestral estimado del panel solar (MXN):", min_value=0, step=100, value=3000)

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

        tarifa_aplicada = (subtotal / consumo) if consumo > 0 else 0
        ahorro, pagos, roi_year = calcular_roi(consumo, tarifa_aplicada, costo_panel, bimestralidad)

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
    tarifas_comerciales = {
        "PDBT": {"costo_kwh": 5.3, "costo_demanda": 150},
        "GDBT": {"costo_kwh": 4.1, "costo_demanda": 300},
        "GDMTO": {"costo_kwh": 3.8, "costo_demanda": 500},
    }

    tarifa = st.selectbox("Selecciona tu tarifa:", list(tarifas_comerciales.keys()))
    demanda_kw = st.number_input("Demanda máxima registrada (kW):", min_value=0.0, step=1.0)
    incluye_iva = st.checkbox("¿La tarifa por kWh ya incluye IVA?", value=True)

    if st.button("Calcular Comercial"):
        datos = tarifas_comerciales[tarifa]
        energia = consumo * datos["costo_kwh"]
        demanda = demanda_kw * datos["costo_demanda"]
        subtotal = energia + demanda
        total = subtotal if incluye_iva else subtotal * (1 + IVA)

        st.subheader("📊 Cálculo Comercial:")
        st.write(f"Energía: {consumo} kWh × ${datos['costo_kwh']} = ${energia:.2f}")
        st.write(f"Demanda: {demanda_kw} kW × ${datos['costo_demanda']} = ${demanda:.2f}")
        st.write(f"**Subtotal:** ${subtotal:.2f} MXN")
        st.write(f"**Total {'(incluye IVA)' if incluye_iva else 'con IVA (16%)'}:** ${total:.2f} MXN")

        tarifa_aplicada = datos["costo_kwh"]
        ahorro, pagos, roi_year = calcular_roi(consumo, tarifa_aplicada, costo_panel, bimestralidad)

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

st.caption("💡 Estos son estimados basados en estructuras de tarifas públicas de CFE. Consulta tu recibo para información precisa.")
