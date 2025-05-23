import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Solares – Profesional", layout="centered")
st.title("☀️ Simulador de Ahorro con Paneles Solares – Profesional")

tipo_usuario = st.selectbox("Selecciona el tipo de usuario:", ["Residencial", "Comercial"])
IVA = 0.16

# Tarifas oficiales CFE residenciales por zona
tarifas_residenciales = {
    "1": {"basico": 100, "intermedio": 150},
    "1A": {"basico": 140, "intermedio": 210},
    "1B": {"basico": 170, "intermedio": 280},
    "1C": {"basico": 180, "intermedio": 300},
    "1D": {"basico": 200, "intermedio": 400},
    "1E": {"basico": 250, "intermedio": 450},
    "1F": {"basico": 300, "intermedio": 900},
}
precios_bloques = {"basico": 1.0, "intermedio": 1.3, "excedente": 3.0}

def calcular_bloques_tarifa(consumo, tarifa_tipo):
    limites = tarifas_residenciales[tarifa_tipo]
    bloques = [0, 0, 0]
    if consumo <= limites["basico"]:
        bloques[0] = consumo
    elif consumo <= limites["basico"] + limites["intermedio"]:
        bloques[0] = limites["basico"]
        bloques[1] = consumo - limites["basico"]
    else:
        bloques[0] = limites["basico"]
        bloques[1] = limites["intermedio"]
        bloques[2] = consumo - (limites["basico"] + limites["intermedio"])

    costos = [
        bloques[0] * precios_bloques["basico"],
        bloques[1] * precios_bloques["intermedio"],
        bloques[2] * precios_bloques["excedente"],
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

# Entradas comunes
consumo = st.number_input("Ingresa tu consumo bimestral en kWh:", min_value=0, step=1)
costo_panel = st.number_input("Costo total del sistema solar (MXN):", min_value=10000, step=1000, value=120000)

# 🏡 Residencial
if tipo_usuario == "Residencial":
    tarifa_sel = st.selectbox("Selecciona tu tarifa residencial:", list(tarifas_residenciales.keys()))
    if st.button("Calcular Residencial"):
        bloques, costos, subtotal, total = calcular_bloques_tarifa(consumo, tarifa_sel)

        st.subheader("📊 Desglose estilo CFE:")
        df = pd.DataFrame({
            "Bloque": ["Básico (1.00)", "Intermedio (1.30)", "Excedente (3.00)"],
            "Consumo (kWh)": [int(kwh) for kwh in bloques],
            "Costo (MXN)": [f"${c:.2f}" for c in costos]
        })
        st.table(df)
        st.write(f"**Subtotal (sin IVA):** ${subtotal:,.2f} MXN")
        st.write(f"**Total con IVA (16%):** ${total:,.2f} MXN")

        tarifa_aplicada = subtotal / consumo if consumo > 0 else 0
        ahorro, roi_mes = calcular_roi_mensual(consumo, tarifa_aplicada, costo_panel)

        st.subheader("📈 Proyección de Retorno de Inversión (ROI)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(ahorro)+1)),
            y=ahorro,
            mode="lines+markers",
            name="Ahorro Acumulado",
            line=dict(color="green", width=4),
            marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=[0, len(ahorro)],
            y=[costo_panel, costo_panel],
            mode="lines",
            name="Costo del Panel",
            line=dict(color="orange", dash="dash")
        ))
        if roi_mes:
            fig.add_vline(x=roi_mes, line_width=2, line_dash="dot", line_color="blue")
            fig.add_annotation(
                x=roi_mes,
                y=max(ahorro),
                text=f"ROI en mes {roi_mes} ({roi_mes // 12} años)",
                showarrow=True,
                arrowhead=2,
                yshift=10
            )
        fig.update_layout(
            title="Ahorro Acumulado vs Inversión Inicial",
            xaxis_title="Meses",
            yaxis_title="MXN",
            template="plotly_white",
            font=dict(family="Arial", size=14),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

# 🏢 Comercial
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
        st.write(f"Energía: {consumo} kWh × ${datos['costo_kwh']} = ${energia:,.2f}")
        st.write(f"Demanda: {demanda_kw} kW × ${datos['costo_demanda']} = ${demanda:,.2f}")
        st.write(f"**Subtotal:** ${subtotal:,.2f} MXN")
        st.write(f"**Total {'(incluye IVA)' if incluye_iva else 'con IVA (16%)'}:** ${total:,.2f} MXN")

        tarifa_aplicada = datos["costo_kwh"]
        ahorro, roi_mes = calcular_roi_mensual(consumo, tarifa_aplicada, costo_panel)

        st.subheader("📈 Proyección de Retorno de Inversión (ROI)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(ahorro)+1)),
            y=ahorro,
            mode="lines+markers",
            name="Ahorro Acumulado",
            line=dict(color="#00a896", width=4),
            marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=[0, len(ahorro)],
            y=[costo_panel, costo_panel],
            mode="lines",
            name="Costo del Panel",
            line=dict(color="#f4a261", dash="dash")
        ))
        if roi_mes:
            fig.add_vline(x=roi_mes, line_width=2, line_dash="dot", line_color="#264653")
            fig.add_annotation(
                x=roi_mes,
                y=max(ahorro),
                text=f"ROI en mes {roi_mes} ({roi_mes // 12} años)",
                showarrow=True,
                arrowhead=2,
                yshift=10
            )
        fig.update_layout(
            title="Ahorro Acumulado vs Inversión Inicial",
            xaxis_title="Meses",
            yaxis_title="MXN",
            template="plotly_white",
            font=dict(family="Arial", size=14),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

st.caption("💡 Este simulador es una herramienta educativa. Consulta tus tarifas oficiales en tu recibo CFE o con tu proveedor de energía.")
