import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(1, len(ahorro) + 1), ahorro, label="Ahorro Acumulado", color="#007f5f", linewidth=2)
        ax.axhline(y=costo_panel, color="#ffa500", linestyle="--", label=f"Costo Panel (${costo_panel})")
        if roi_mes:
            ax.axvline(x=roi_mes, color="#38b000", linestyle=":", label=f"ROI en mes {roi_mes} ({roi_mes // 12} años)")

        ax.set_xlabel("Meses", fontsize=12)
        ax.set_ylabel("MXN", fontsize=12)
        ax.set_title("📊 Ahorro Acumulado vs Inversión Inicial", fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${int(x):,}"))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
        ax.set_facecolor('#f5f5f5')
        st.pyplot(fig)

# Modo Comercial
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
        ahorro, roi_mes = calcular_roi_mensual(consumo, tarifa_aplicada, costo_panel)

        st.subheader("📈 Proyección de Retorno de Inversión (ROI)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(1, len(ahorro) + 1), ahorro, label="Ahorro Acumulado", color="#007f5f", linewidth=2)
        ax.axhline(y=costo_panel, color="#ffa500", linestyle="--", label=f"Costo Panel (${costo_panel})")
        if roi_mes:
            ax.axvline(x=roi_mes, color="#38b000", linestyle=":", label=f"ROI en mes {roi_mes} ({roi_mes // 12} años)")

        ax.set_xlabel("Meses", fontsize=12)
        ax.set_ylabel("MXN", fontsize=12)
        ax.set_title("📊 Ahorro Acumulado vs Inversión Inicial", fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${int(x):,}"))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
        ax.set_facecolor('#f5f5f5')
        st.pyplot(fig)

st.caption("💡 Este simulador es una herramienta educativa. Consulta tus tarifas oficiales en tu recibo CFE o con tu proveedor de energía.")
