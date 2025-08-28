# main.py
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# --- Data Structures (Translated from script.js) ---

# Mapeo de ciclos por potencia (HP)
ciclos_por_potencia = {
    '1.0': [30, 2],
    '3.0': [25, 2.4],
    '5.0': [22, 2.7],
    '7.5': [20, 3],
    '10.0': [20, 3],
    '20.0': [15, 4],
    '30.0': [12, 5],
    '50.0': [10, 6],
    '50.1': [6, 10]
}

# Datos de la tabla comercial de tanques
commercial_tanks_data = [
    {'code': 'US010361CS000000', 'capacity': 10, 'pressure': 10, 'connection': '3/4"', 'dimensions': '250X500', 'packaging': 0.05, 'pallet_qty': 20},
    {'code': 'US015361CS000000', 'capacity': 15, 'pressure': 10, 'connection': '3/4"', 'dimensions': '280X550', 'packaging': 0.065, 'pallet_qty': 20},
    {'code': 'US020361CS000000', 'capacity': 20, 'pressure': 10, 'connection': '3/4"', 'dimensions': '300X600', 'packaging': 0.075, 'pallet_qty': 18},
    {'code': 'US025361CS000000', 'capacity': 25, 'pressure': 10, 'connection': '1"', 'dimensions': '310X650', 'packaging': 0.09, 'pallet_qty': 18},
    {'code': 'US030361CS000000', 'capacity': 30, 'pressure': 10, 'connection': '1"', 'dimensions': '320X700', 'packaging': 0.1, 'pallet_qty': 15},
    {'code': 'US040361CS000000', 'capacity': 40, 'pressure': 10, 'connection': '1"', 'dimensions': '328X757', 'packaging': 0.12, 'pallet_qty': 15},
    {'code': 'US050361CS000000', 'capacity': 50, 'pressure': 10, 'connection': '1"', 'dimensions': '379X759', 'packaging': 0.126, 'pallet_qty': 15},
    {'code': 'US060361CS000000', 'capacity': 60, 'pressure': 10, 'connection': '1"', 'dimensions': '379X825', 'packaging': 0.131, 'pallet_qty': 15},
    {'code': 'US080361CS000000', 'capacity': 80, 'pressure': 10, 'connection': '1"', 'dimensions': '450X789', 'packaging': 0.17, 'pallet_qty': 15},
    {'code': 'US100361CS000000', 'capacity': 100, 'pressure': 10, 'connection': '1"', 'dimensions': '450X910', 'packaging': 0.2, 'pallet_qty': 15},
    {'code': 'US150461CS000000', 'capacity': 150, 'pressure': 10, 'connection': '1"1/2', 'dimensions': '554X1040', 'packaging': 0.34, 'pallet_qty': 8},
    {'code': 'US200461CS000000', 'capacity': 200, 'pressure': 10, 'connection': '1"1/2', 'dimensions': '554X1250', 'packaging': 0.407, 'pallet_qty': 8},
    {'code': 'US300461CS000000', 'capacity': 300, 'pressure': 10, 'connection': '1"1/2', 'dimensions': '624X1370', 'packaging': 0.596, 'pallet_qty': 6},
    {'code': 'US500461CS000000', 'capacity': 500, 'pressure': 10, 'connection': '1"1/2', 'dimensions': '790X1460', 'packaging': 0.9, 'pallet_qty': 1},
    {'code': 'US750461CS000000*', 'capacity': 750, 'pressure': 10, 'connection': '1"1/2', 'dimensions': '786X1925', 'packaging': 1.3, 'pallet_qty': 1},
    {'code': 'USN101161CS000000*', 'capacity': 1000, 'pressure': 9.5, 'connection': '2"', 'dimensions': '945X1912', 'packaging': 1.9, 'pallet_qty': 1},
    {'code': 'USN201161CS000000*', 'capacity': 2000, 'pressure': 9.5, 'connection': '2"', 'dimensions': '1280X2080', 'packaging': 3.72, 'pallet_qty': 1},
]

# Definir ciclos_df y commercial_df globalmente
ciclos_df = pd.DataFrame([
    {"Rango de Potencia (HP)": "Hasta 1.0", "Máximo Número de Ciclos por Hora": 20, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 1.1 a 3.0", "Máximo Número de Ciclos por Hora": 20, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 3.1 a 5.0", "Máximo Número de Ciclos por Hora": 20, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 5.1 a 7.5", "Máximo Número de Ciclos por Hora": 20, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 7.6 a 10.0", "Máximo Número de Ciclos por Hora": 20, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 10.1 a 20.0", "Máximo Número de Ciclos por Hora": 15, "Tiempo Mínimo (minutos)": 4},
    {"Rango de Potencia (HP)": "De 20.1 a 30.0", "Máximo Número de Ciclos por Hora": 12, "Tiempo Mínimo (minutos)": 5},
    {"Rango de Potencia (HP)": "De 30.1 a 50.0", "Máximo Número de Ciclos por Hora": 10, "Tiempo Mínimo (minutos)": 6},
    {"Rango de Potencia (HP)": "Desde 50.1", "Máximo Número de Ciclos por Hora": 6, "Tiempo Mínimo (minutos)": 10},
])

commercial_df = pd.DataFrame(commercial_tanks_data)

# --- Helper Functions ---
def create_pdf():
    # Verificar que se haya realizado un cálculo
    if 'calculated_volume' not in st.session_state:
        return None
        
    pdf = FPDF()
    pdf.add_page()
    
    # Configurar fuente
    pdf.set_font('Arial', 'B', 16)
    
    # Título
    pdf.cell(0, 10, 'SISTEMA HIDRONEUMÁTICO', 0, 1, 'C')
    pdf.ln(5)
    
    # Fecha en español
    pdf.set_font('Arial', '', 12)
    meses_es = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    now = datetime.now()
    fecha_actual = f"{now.day} de {meses_es[now.month-1]} de {now.year}"
    pdf.cell(0, 10, f'Fecha: {fecha_actual}', 0, 1, 'L')
    pdf.ln(5)
    
    # Información del proyecto
    proyecto = st.session_state.get('proyecto_nombre', '')
    disenado = st.session_state.get('disenado_por', '')
    pdf.cell(0, 10, f'Proyecto: {proyecto}', 0, 1, 'L')
    pdf.cell(0, 10, f'Diseño: {disenado}', 0, 1, 'L')
    pdf.ln(5)
    
    # Parámetros de entrada
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Parámetros de Entrada:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    qb = st.session_state.get('qb', 0)
    p_off = st.session_state.get('p_off', 0)
    p_on = st.session_state.get('p_on', 0)
    r_aire_text = st.session_state.get('r_aire_text', '')
    potencia_text = st.session_state.get('potencia_selected_text', '')
    n_ciclos = st.session_state.get('n_ciclos', 0)
    n_bombas = st.session_state.get('n_bombas', 0)
    
    pdf.cell(0, 8, f'Caudal de Bombeo: {qb} l/min', 0, 1, 'L')
    pdf.cell(0, 8, f'Presión Apagado: {p_off} mca', 0, 1, 'L')
    pdf.cell(0, 8, f'Presión Encendido: {p_on} mca', 0, 1, 'L')
    pdf.cell(0, 8, f'Coeficiente de Aire: {r_aire_text}', 0, 1, 'L')
    pdf.cell(0, 8, f'Potencia de la Bomba: {potencia_text}', 0, 1, 'L')
    pdf.cell(0, 8, f'Número de Ciclos: {n_ciclos}', 0, 1, 'L')
    pdf.cell(0, 8, f'Número de Bombas: {n_bombas}', 0, 1, 'L')
    pdf.ln(5)
    
    # Resultados del cálculo
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Resultados del Cálculo:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    w_thn_liters = st.session_state.get('w_thn_liters', 0)
    w_thn_gallons = st.session_state.get('w_thn_gallons', 0)
    commercial_liters = st.session_state.get('commercial_liters', 0)
    commercial_gallons = st.session_state.get('commercial_gallons', 0)
    
    pdf.cell(0, 8, f'Volumen Calculado: {w_thn_liters:.2f} L', 0, 1, 'L')
    pdf.cell(0, 8, f'Volumen Calculado: {w_thn_gallons:.2f} gal', 0, 1, 'L')
    pdf.cell(0, 8, f'Volumen Comercial Sugerido: {commercial_liters} L ({commercial_gallons:.2f} gal)', 0, 1, 'L')
    pdf.ln(5)
    
    # Tanque comercial seleccionado
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Tanque Comercial Seleccionado:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    if 'suggested_commercial_tank' in st.session_state and st.session_state['suggested_commercial_tank']:
        tank = st.session_state['suggested_commercial_tank']
        pdf.cell(0, 8, f'Capacidad: {tank["capacity"]} L', 0, 1, 'L')
        pdf.cell(0, 8, f'Presión: {tank["pressure"]} bar', 0, 1, 'L')
        pdf.cell(0, 8, f'Conexión: {tank["connection"]}', 0, 1, 'L')
        pdf.cell(0, 8, f'Dimensiones: {tank["dimensions"]}', 0, 1, 'L')
    pdf.ln(10)

    # Hoja 2: Tabla de Ciclos por Hora y Selección de Tanque Comercial
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Tabla de Ciclos por Hora', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    pdf.cell(65, 8, 'Rango de Potencia (HP)', 1, 0, 'C')
    pdf.cell(65, 8, 'Máximo Número de Ciclos por Hora', 1, 0, 'C')
    pdf.cell(50, 8, 'Tiempo Mínimo (minutos)', 1, 1, 'C')
    for _, row in ciclos_df.iterrows():
        pdf.cell(65, 8, str(row['Rango de Potencia (HP)']), 1, 0, 'C')
        pdf.cell(65, 8, str(row['Máximo Número de Ciclos por Hora']), 1, 0, 'C')
        pdf.cell(50, 8, str(row['Tiempo Mínimo (minutos)']), 1, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Selección de Tanque Comercial', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 9)
    pdf.cell(35, 8, 'Código', 1, 0, 'C')
    pdf.cell(25, 8, 'Capacidad (L)', 1, 0, 'C')
    pdf.cell(20, 8, 'Presión', 1, 0, 'C')
    pdf.cell(25, 8, 'Conexión', 1, 0, 'C')
    pdf.cell(35, 8, 'Dimensiones', 1, 0, 'C')
    pdf.cell(25, 8, 'Embalaje', 1, 0, 'C')
    pdf.cell(25, 8, 'Cantidad/Pallet', 1, 1, 'C')
    for _, row in commercial_df.iterrows():
        pdf.cell(35, 8, str(row['code']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['capacity']), 1, 0, 'C')
        pdf.cell(20, 8, str(row['pressure']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['connection']), 1, 0, 'C')
        pdf.cell(35, 8, str(row['dimensions']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['packaging']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['pallet_qty']), 1, 1, 'C')
    
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Sistema Hidroneumático")

# CSS mejorado para el centrado de tablas
st.markdown('''
<style>
    /* Estilos generales */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        background-color: #F0F8FF;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Estilos específicos para centrar contenido de tablas */
    .stDataFrame > div {
        overflow-x: auto;
    }
    
    .stDataFrame table {
        width: 100% !important;
    }
    
    .stDataFrame th {
        text-align: center !important;
        vertical-align: middle !important;
        font-weight: bold !important;
        background-color: #f0f2f6 !important;
    }
    
    .stDataFrame td {
        text-align: center !important;
        vertical-align: middle !important;
    }
    
    /* Asegurar que las celdas numéricas también estén centradas */
    .stDataFrame .col_heading {
        text-align: center !important;
    }
    
    .stDataFrame .data {
        text-align: center !important;
    }
</style>
''', unsafe_allow_html=True)

st.title("SISTEMA HIDRONEUMÁTICO")
st.subheader("Sistema de Presurización")

# Información del Proyecto (spanning columns 2 and 3, vertically stacked)
st.header("Información del Proyecto")
col1_info, col2_info = st.columns([1, 1])
with col1_info:
    proyecto_nombre = st.text_input("Proyecto:", placeholder="Nombre del Proyecto")
with col2_info:
    disenado_por = st.text_input("Diseño:", placeholder="Tu Nombre")

# 4-column layout
col1, col2, col3, col4 = st.columns([1, 4, 4, 3])

# Column 1: Unidades de Caudal
with col1:
    st.markdown("### Unidades de Caudal")
    unidad_caudal = st.toggle("Cambiar a l/s", value=False, key="unidad_caudal_switch")

# Column 2: Cálculo del Tanque Hidroneumático, Results, and PDF Export
with col2:
    st.header("Cálculo del Tanque Hidroneumático")
    with st.form("calculation_form"):
        col2a, col2b = st.columns(2)
        with col2a:
            if st.session_state.get("unidad_caudal_switch", False):
                qb = st.number_input("Caudal de Bombeo (l/s)", value=2.75, step=0.01, key="qb_ls")
                qb_lmin = qb * 60
            else:
                qb = st.number_input("Caudal de Bombeo (l/min)", value=165.00, step=0.01, key="qb_lmin")
                qb_lmin = qb
            p_off = st.number_input("Presión Apagado (mca)", value=55.33, step=0.01)
            p_on = st.number_input("Presión Encendido (mca)", value=25.33, step=0.01)
        with col2b:
            r_aire_options = {"1.0 (Membrana)": 1.0, "1.5 (Compresor automático)": 1.5, "2.0 (Inyección manual)": 2.0}
            r_aire_selected = st.selectbox("Coeficiente de Aire", list(r_aire_options.keys()))
            r_aire = r_aire_options[r_aire_selected]

            potencia_labels = [row["Rango de Potencia (HP)"] for row in ciclos_df.to_dict('records')]
            potencia_selected_label = st.selectbox("Potencia de la Bomba (HP)", potencia_labels, index=potencia_labels.index("De 7.6 a 10.0"))

            potencia_row = next((row for row in ciclos_df.to_dict('records') if row["Rango de Potencia (HP)"] == potencia_selected_label), None)
            n_ciclos_available = potencia_row["Máximo Número de Ciclos por Hora"] if potencia_row else 20
            n_ciclos = st.selectbox("Número de Ciclos", [n_ciclos_available], key="n_ciclos_select")

            n_bombas = st.number_input("Número de Bombas", value=1, min_value=1, step=1)

        submitted = st.form_submit_button("Calcular Tanque")

        if submitted:
            if p_off <= p_on or qb_lmin <= 0 or n_bombas <= 0 or n_ciclos <= 0:
                st.error("Error: Verifique que la Presión de Apagado sea mayor que la de Encendido y que todos los valores sean positivos.")
            else:
                w_thn_liters = (19 * r_aire * qb_lmin * (p_off + 10.33)) / (n_bombas * n_ciclos * (p_off - p_on))
                w_thn_gallons = w_thn_liters / 3.785

                st.subheader("Resultados del Cálculo")
                st.metric("Volumen Calculado (litros)", f"{w_thn_liters:.2f} L")
                st.metric("Volumen Calculado (galones)", f"{w_thn_gallons:.2f} gal")
                st.metric("Caudal usado en cálculo", f"{qb_lmin:.2f} l/min")

                suggested_commercial_tank = next((tank for tank in commercial_tanks_data if tank['capacity'] >= w_thn_liters), None)
                commercial_liters = suggested_commercial_tank['capacity'] if suggested_commercial_tank else 'N/A'
                commercial_gallons = (commercial_liters / 3.785) if isinstance(commercial_liters, (int, float)) else 'N/A'
                
                st.metric("Volumen Comercial Sugerido", f"{commercial_liters} L ({float(commercial_gallons):.2f} gal)" if commercial_gallons != 'N/A' else f"{commercial_liters} L (N/A gal)")

                # Guardar en session state
                st.session_state['calculated_volume'] = w_thn_liters
                st.session_state['suggested_commercial_tank'] = suggested_commercial_tank
                st.session_state['proyecto_nombre'] = proyecto_nombre
                st.session_state['disenado_por'] = disenado_por
                st.session_state['qb'] = qb_lmin
                st.session_state['p_off'] = p_off
                st.session_state['p_on'] = p_on
                st.session_state['r_aire_text'] = r_aire_selected
                st.session_state['n_bombas'] = n_bombas
                st.session_state['n_ciclos'] = n_ciclos
                st.session_state['w_thn_liters'] = w_thn_liters
                st.session_state['w_thn_gallons'] = w_thn_gallons
                st.session_state['commercial_liters'] = commercial_liters
                st.session_state['commercial_gallons'] = commercial_gallons
                st.session_state['potencia_selected_text'] = potencia_selected_label

    # Separador y botón de descarga PDF
    st.markdown("---")
    
    # Botón para generar el PDF y guardarlo en session_state
    if 'calculated_volume' in st.session_state:
        if st.button("📄 Generar Reporte PDF", use_container_width=True):
            pdf_data = create_pdf()
            if pdf_data:
                st.session_state['pdf_data_for_download'] = pdf_data

        # Botón de descarga que aparece si hay datos de PDF en session_state
        if 'pdf_data_for_download' in st.session_state:
            proyecto_name = st.session_state.get('proyecto_nombre', 'Sistema_Hidroneumatico')
            filename = f"{proyecto_name.replace(' ', '_')}_Reporte.pdf" if proyecto_name else "Sistema_Hidroneumatico_Reporte.pdf"
            
            st.download_button(
                label="📥 Descargar PDF",
                data=st.session_state['pdf_data_for_download'].getvalue(),
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("💡 Realice primero un cálculo para habilitar la descarga del PDF")


# Column 3: Tabla de Ciclos por Hora y Selección de Tanque Comercial
with col3:
    st.header("Tabla de Ciclos por Hora")
    
    def highlight_ciclos_row(row):
        if 'potencia_selected_text' in st.session_state:
            selected_potencia = st.session_state['potencia_selected_text']
            current_potencia = row['Rango de Potencia (HP)']
            
            if current_potencia == selected_potencia:
                return ['background-color: #E3F2FD; font-weight: bold; text-align: center;'] * len(row)
        return ['text-align: center;'] * len(row)

    ciclos_table_styles = [
    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f0f2f6'), ('border', '1px solid #ddd')]},
    {'selector': 'td', 'props': [('text-align', 'center'), ('border', '1px solid #ddd'), ('padding', '8px')]},
    {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]}
    ]
    
    ciclos_styled = ciclos_df.style.apply(highlight_ciclos_row, axis=1).set_table_styles(ciclos_table_styles)
    st.dataframe(ciclos_styled, use_container_width=True, hide_index=True)

    st.header("Selección de Tanque Comercial")
    st.markdown("Esta tabla muestra opciones de tanques comerciales **MAXIVAREM LS CE**. Las filas resaltadas cumplen o superan el volumen comercial mínimo sugerido.")
    
    def highlight_commercial_row(row):
        if 'calculated_volume' in st.session_state and row['Capacidad (L)'] >= st.session_state['calculated_volume']:
            return ['background-color: #E3F2FD; font-weight: bold; text-align: center;'] * len(row)
        return ['text-align: center;'] * len(row)

    commercial_table_styles = [
    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f0f2f6'), ('border', '1px solid #ddd'), ('font-size', '12px')]},
    {'selector': 'td', 'props': [('text-align', 'center'), ('border', '1px solid #ddd'), ('padding', '6px'), ('font-size', '11px')]},
        {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]}
    ]
    
    commercial_display_df = commercial_df.rename(columns={
        'code': 'Código',
        'capacity': 'Capacidad (L)',
        'pressure': 'Presión (bar)',
        'connection': 'Conexión',
        'dimensions': 'Dimensiones (mm)',
        'packaging': 'Embalaje (m³)',
        'pallet_qty': 'Cantidad/Pallet'
    })
    
    if 'calculated_volume' in st.session_state:
        commercial_styled = commercial_display_df.style.apply(highlight_commercial_row, axis=1).set_table_styles(commercial_table_styles)
    else:
        commercial_styled = commercial_display_df.style.set_table_styles(commercial_table_styles)
    
    st.dataframe(commercial_styled, use_container_width=True, hide_index=True)

# Column 4: Criterios, Accesorios, and Fórmula
with col4:
    st.header("Criterios de Diseño")
    st.markdown(r'''
    La presurización para el abastecimiento de agua potable se realiza por medio de un **tanque hidroneumático**. El caudal para el dimensionamiento debe ser el mínimo, igual al caudal máximo probable empleado para el dimensionamiento del distribuidor y columnas del sistema de distribución. Este diseño se basa en la **NORMA NEC 11 CAPÍTULO 16**.

    El sistema deberá operar con un máximo de 20 ciclos por hora para bombas de hasta 10HP.
    ''')

    st.header("Accesorios Mínimos Indispensables")
    st.markdown(r'''
    *   Manómetro
    *   Presostato
    *   Válvula de seguridad
    *   Dispositivo para reposición de aire
    *   Instalaciones electro mecánicas automáticas de arranque y parada
    ''')

    st.header("Fórmula de Cálculo")
    st.latex(r'''
    V_{thn} = \frac{19 \times R_{\text{aire}} \times Q_b \times (P_{\text{off}} + 10.33)}
    {N_{\text{bombas}} \times N_{\text{ciclos}} \times (P_{\text{off}} - P_{\text{on}})}
    ''')
    st.markdown(r'''
    **Donde:**
    * **$V_{thn}$**: Capacidad total del tanque, en litros (L).
    * **$Q_b$**: Caudal de bombeo medio, en litros por minuto (l/min).
    * **$N_{	ext{bombas}}$**: Número de bombas en funcionamiento.
    * **$N_{	ext{ciclos}}$**: Número de ciclos por hora.
    * **$P_{	ext{on}}$**: Presión de encendido, en metros de columna de agua (mca).
    * **$P_{	ext{off}}$**: Presión de apagado, en metros de columna de agua (mca).
    * **$R_{	ext{aire}}$**: Coeficiente que depende del tipo de renovación de aire (1.0, 1.5, 2.0).
    ''')

st.markdown("---")
st.markdown('''
<div style='text-align: center;'>
    <p>Aplicación basada en la <strong>NORMA NEC 11 CAPÍTULO 16</strong>.</p>
    <p>Desarrollado por Patricio Sarmiento Reinoso | Maestría HS 2025.</p>
</div>
''', unsafe_allow_html=True)
