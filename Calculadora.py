import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Estación de Pesaje OTC - Modelos M/M/1 y M/M/C", layout="centered")

# Control de estado de la vista (calculadora, calculadora_general, ayuda)
if "vista" not in st.session_state:
    st.session_state["vista"] = "calculadora"

def cambiar_vista(nueva_vista):
    st.session_state["vista"] = nueva_vista

# Estilos CSS base (Tonos lilas y morados con alto contraste)
st.markdown("""
    <style>
    /* Fondo lila pastel suave */
    .stApp {
        background-color: #E9D5FF;
    }
    
    /* Encabezados en morado oscuro */
    h1, h2, h3, h4, h5 {
        color: #4C1D95 !important;
        font-weight: 700;
    }
    
    /* Asegurar que todos los textos generales sean oscuros y legibles */
    p, label, span, div, li {
        color: #1E1B4B !important;
    }

    /* Estilo para las métricas de resultados */
    [data-testid="stMetricValue"] {
        color: #5B21B6 !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #1E1B4B !important;
        font-weight: 600;
    }

    /* Botón principal de cálculo */
    .stButton>button[kind="primary"] {
        background-color: #6D28D9;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #5B21B6;
    }
    
    /* Pie de página con integrantes */
    .integrantes {
        text-align: center;
        color: #3B0764 !important;
        font-size: 14px;
        margin-top: 50px;
        padding: 12px;
        border-top: 2px solid #C084FC;
    }
    
    /* Contenedores holgados para la vista de ayuda */
    .help-box {
        background-color: #F3E8FF;
        border-left: 5px solid #7E22CE;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .result-card-red {
        background-color: #FEE2E2;
        border-left: 5px solid #DC2626;
        padding: 18px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .result-card-green {
        background-color: #DCFCE7;
        border-left: 5px solid #16A34A;
        padding: 18px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header con Título y Menú de Navegación
col_title, col_btn = st.columns([2.5, 1.5])

with col_title:
    if st.session_state["vista"] == "calculadora":
        st.title("Estación de Pesaje OTC")
    elif st.session_state["vista"] == "calculadora_general":
        st.title("Calculadora General de Colas")
    else:
        st.title(" Manual y Ayuda OTC")

with col_btn:
    st.write("")
    if st.session_state["vista"] == "calculadora":
        btn_col_a, btn_col_b = st.columns(2)
        with btn_col_a:
            st.button("🌐 General", on_click=cambiar_vista, args=("calculadora_general",), key="btn_nav_gen")
        with btn_col_b:
            st.button("🧍 Ayuda", on_click=cambiar_vista, args=("ayuda",), key="btn_nav_ayuda1")
    elif st.session_state["vista"] == "calculadora_general":
        btn_col_a, btn_col_b = st.columns(2)
        with btn_col_a:
            st.button("🚛 Caso OTC", on_click=cambiar_vista, args=("calculadora",), key="btn_nav_otc")
        with btn_col_b:
            st.button("🧍 Ayuda", on_click=cambiar_vista, args=("ayuda",), key="btn_nav_ayuda2")
    else:
        st.button("🔙 Volver a Calculadora", on_click=cambiar_vista, args=("calculadora",), key="btn_nav_volver")

# Función estilizada para generar gráficas avanzadas sin colisión de nodos DOM
def generar_graficas(lam_val, mu_val, c_val, is_otc=True):
    unit_label = "camiones" if is_otc else "unidades"
    rho_val = lam_val / (c_val * mu_val)
    
    # Calcular P0 (Manejo defensivo en caso de resultados negativos matemáticos irreales)
    try:
        if c_val == 1:
            P0_val = 1 - rho_val
        else:
            sumatoria = sum([(lam_val / mu_val)**k / math.factorial(k) for k in range(c_val)])
            termino_c = ((lam_val / mu_val)**c_val / math.factorial(c_val)) * (1 / (1 - rho_val))
            P0_val = 1 / (sumatoria + termino_c)
    except:
        P0_val = 0

    # Métricas base
    try:
        if c_val == 1:
            Lq_val = (lam_val**2) / (mu_val * (mu_val - lam_val))
            Ls_val = lam_val / (mu_val - lam_val)
            Wq_val = lam_val / (mu_val * (mu_val - lam_val))
            Ws_val = 1 / (mu_val - lam_val)
        else:
            Lq_val = (P0_val * ((lam_val / mu_val)**c_val) * rho_val) / (math.factorial(c_val) * ((1 - rho_val)**2))
            Ls_val = Lq_val + (lam_val / mu_val)
            Wq_val = Lq_val / lam_val
            Ws_val = Wq_val + (1 / mu_val)
    except:
        Lq_val, Ls_val, Wq_val, Ws_val = 0, 0, 0, 0

    st.markdown("---")
    st.markdown("### 📈 Panel Visual de Gráficas")

    # Aislamiento DOM mediante contenedor único
    c_graf = st.container()
    with c_graf:
        tab_g1, tab_g2, tab_g3, tab_g4 = st.tabs([
            "📊 Distribución Pn", 
            "⏱️ Tiempos Wq vs Ws", 
            "📦 Cantidad Lq vs Ls", 
            "📈 Sensibilidad λ vs Lq"
        ])

        # Gráfica 1: Distribución Pn
        with tab_g1:
            st.write(f"**Distribución de Probabilidad del número de {unit_label} en el sistema (Pn)**")
            n_arr = list(range(11))
            pn_arr = []
            for n_i in n_arr:
                try:
                    if c_val == 1:
                        pn_arr.append((1 - rho_val) * (rho_val**n_i))
                    else:
                        if n_i < c_val:
                            pn_arr.append(((lam_val / mu_val)**n_i / math.factorial(n_i)) * P0_val)
                        else:
                            pn_arr.append(((lam_val / mu_val)**n_i / (math.factorial(c_val) * (c_val**(n_i - c_val)))) * P0_val)
                except:
                    pn_arr.append(0)

            fig1, ax1 = plt.subplots(figsize=(7, 3.8))
            pct_values = [max(0, p * 100) for p in pn_arr] # Evitar visuales negativos
            colors = ['#A855F7' if i == 0 else '#6D28D9' for i in range(len(n_arr))]
            bars = ax1.bar(n_arr, pct_values, color=colors, edgecolor='#3B0764', linewidth=1.2, width=0.6)
            
            for bar in bars:
                height = bar.get_height()
                if height > 0.5:
                    ax1.annotate(f'{height:.1f}%',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1E1B4B')

            ax1.set_xlabel(f"Número de {unit_label} en el sistema (n)", fontsize=10, fontweight='bold')
            ax1.set_ylabel("Probabilidad (%)", fontsize=10, fontweight='bold')
            ax1.set_xticks(n_arr)
            ax1.set_ylim(0, max(pct_values) * 1.18 if max(pct_values) > 0 else 100)
            ax1.grid(axis='y', linestyle='--', alpha=0.5)
            ax1.set_facecolor('#F3E8FF')
            fig1.patch.set_facecolor('#E9D5FF')
            st.pyplot(fig1)

        # Gráfica 2: Wq vs Ws
        with tab_g2:
            st.write("**Tiempos Promedio: Espera en Cola (Wq) vs. Permanencia Total (Ws)**")
            fig2, ax2 = plt.subplots(figsize=(6.5, 3.2))
            categorias = ['En Cola (Wq)', 'Total Sistema (Ws)']
            tiempos_min = [max(0, Wq_val * 60), max(0, Ws_val * 60)]
            bars2 = ax2.barh(categorias, tiempos_min, color=['#A855F7', '#5B21B6'], height=0.45, edgecolor='#3B0764')
            
            for bar in bars2:
                width = bar.get_width()
                ax2.annotate(f'{width:.2f} min',
                            xy=(width, bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0),
                            textcoords="offset points",
                            ha='left', va='center', fontsize=9, fontweight='bold', color='#1E1B4B')

            ax2.set_xlabel("Tiempo (minutos)", fontsize=10, fontweight='bold')
            ax2.set_xlim(0, max(tiempos_min) * 1.25 if max(tiempos_min) > 0 else 10)
            ax2.grid(axis='x', linestyle='--', alpha=0.5)
            ax2.set_facecolor('#F3E8FF')
            fig2.patch.set_facecolor('#E9D5FF')
            st.pyplot(fig2)

        # Gráfica 3: Lq vs Ls
        with tab_g3:
            st.write(f"**Cantidad Promedio de {unit_label}: En Cola (Lq) vs. En Sistema (Ls)**")
            fig3, ax3 = plt.subplots(figsize=(6.5, 3.5))
            cantidades = [max(0, Lq_val), max(0, Ls_val)]
            labels3 = ['En Cola (Lq)', 'En Sistema (Ls)']
            bars3 = ax3.bar(labels3, cantidades, color=['#C084FC', '#6D28D9'], width=0.4, edgecolor='#3B0764')
            
            for bar in bars3:
                height = bar.get_height()
                ax3.annotate(f'{height:.4f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1E1B4B')

            ax3.set_ylabel(f"Promedio de {unit_label}", fontsize=10, fontweight='bold')
            ax3.set_ylim(0, max(cantidades) * 1.25 if max(cantidades) > 0 else 5)
            ax3.grid(axis='y', linestyle='--', alpha=0.5)
            ax3.set_facecolor('#F3E8FF')
            fig3.patch.set_facecolor('#E9D5FF')
            st.pyplot(fig3)

        # Gráfica 4: Sensibilidad
        with tab_g4:
            st.write(f"**Curva de Desempeño: Impacto del incremento de llegadas (λ) en la Cola (Lq)**")
            capacidad_max = c_val * mu_val
            lam_range = np.linspace(0.1, capacidad_max * 0.95, 60)
            lq_curve = []
            for l_i in lam_range:
                rho_i = l_i / capacidad_max
                if c_val == 1:
                    lq_curve.append((l_i**2) / (mu_val * (mu_val - l_i)))
                else:
                    sum_i = sum([(l_i / mu_val)**k / math.factorial(k) for k in range(c_val)])
                    term_i = ((l_i / mu_val)**c_val / math.factorial(c_val)) * (1 / (1 - rho_i))
                    p0_i = 1 / (sum_i + term_i)
                    lq_i = (p0_i * ((l_i / mu_val)**c_val) * rho_i) / (math.factorial(c_val) * ((1 - rho_i)**2))
                    lq_curve.append(lq_i)

            fig4, ax4 = plt.subplots(figsize=(7, 3.8))
            ax4.plot(lam_range, lq_curve, color='#4C1D95', linewidth=2.8, label='Curva de Cola Lq')
            ax4.fill_between(lam_range, lq_curve, color='#C084FC', alpha=0.3)
            ax4.axvline(x=lam_val, color='#DC2626', linestyle='--', linewidth=1.8, label=f'λ Actual ({lam_val:.1f})')
            ax4.set_xlabel("Tasa de llegadas (λ)", fontsize=10, fontweight='bold')
            ax4.set_ylabel(f"{unit_label.capitalize()} en cola (Lq)", fontsize=10, fontweight='bold')
            ax4.legend(loc='upper left')
            ax4.grid(True, linestyle='--', alpha=0.5)
            ax4.set_facecolor('#F3E8FF')
            fig4.patch.set_facecolor('#E9D5FF')
            st.pyplot(fig4)


# ==============================================================================
# VISTA 1: CALCULADORA CASO REAL OTC
# ==============================================================================
if st.session_state["vista"] == "calculadora":
    
    st.info("📌 **Estación de Pesaje OTC:** Introduce las tasas en camiones/hora y el número de básculas, luego presiona **Calcular Resultados**.")

    modelo = st.radio("Selecciona la configuración de la estación de pesaje:", ("M/M/1", "M/M/C"))

    col1, col2 = st.columns(2)
    with col1:
        lam = st.number_input("Tasa de llegadas (λ) [camiones/hora]:", value=60.0, step=1.0, format="%f")
    with col2:
        mu = st.number_input("Tasa de servicio (μ) [camiones/hora]:", value=66.0, step=1.0, format="%f")

    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        if modelo == "M/M/C":
            c = st.number_input("Número de básculas operativas (c):", value=2, step=1)
        else:
            c = 1
    with col_sub2:
        n_val = st.number_input("Número de camiones en sistema (n) [para Pn]:", value=1, step=1)

    opciones_calculo = [
        "Todos los resultados",
        "Factor de utilización (ρ)",
        "Probabilidad de sistema vacío (P0)",
        "Número promedio en cola (Lq)",
        "Número promedio en sistema (Ls)",
        "Tiempo promedio en cola (Wq)",
        "Tiempo promedio en sistema (Ws)",
        "Probabilidad de n camiones (Pn)",
        "Probabilidad de esperar en cola (Pw)",
        "Uso/Capacidad ocupada del sistema (U)"
    ]

    calculo_seleccionado = st.selectbox(
        "¿Qué métrica de rendimiento deseas analizar?",
        opciones_calculo
    )

    if st.button("Calcular Resultados", type="primary", key="btn_calc_otc"):
        errores = False
        
        if lam is None or mu is None or (modelo == "M/M/C" and c is None) or n_val is None:
            st.error(" Error de datos: Debes ingresar todos los parámetros obligatorios antes de calcular.")
            errores = True

        if not errores:
            if lam < 0 or mu < 0:
                st.error(" Error de datos: Las tasas de llegada (λ) y servicio (μ) no pueden ser números negativos.")
                errores = True
            elif lam == 0 or mu == 0:
                st.error(" Error de datos: Las tasas deben ser estrictamente mayores a cero para que el sistema funcione.")
                errores = True
            elif lam > 100 or mu > 100:
                st.error(" Error de rango: Según las restricciones físicas de la estación de pesaje OTC, no se permiten más de 100 camiones por hora.")
                errores = True
                
            if n_val < 0:
                st.error(" Error de datos: El número de camiones en el sistema (n) no puede ser un número negativo. Debe ser 0 o un entero positivo.")
                errores = True
            elif not isinstance(n_val, int) and not float(n_val).is_integer():
                st.error(" Error de datos: El valor de n para Pn debe ser un número entero (no se permiten decimales ni fracciones de camiones).")
                errores = True

            if modelo == "M/M/C":
                if c < 1 or c > 3:
                    st.error(" Error de infraestructura: El número de básculas (c) debe estar entre 1 y 3 (máximo permitido).")
                    errores = True
                elif not isinstance(c, int) and not float(c).is_integer():
                    st.error(" Error de datos: El número de básculas debe ser obligatoriamente un número entero positivo.")
                    errores = True

        if not errores:
            # Prevención interna para no crashear (ZeroDivisionError) si las tasas son exactamente idénticas
            if modelo == "M/M/1" and lam == mu:
                mu += 0.00001
            elif modelo == "M/M/C" and lam == (c * mu):
                mu += 0.00001

            st.success("✅ Cálculos realizados con éxito (Mostrando resultados analíticos).")
            
            c = int(c)
            n_val = int(n_val)
            
            if modelo == "M/M/1":
                rho = lam / mu
                Lq = (lam**2) / (mu * (mu - lam))
                Ls = lam / (mu - lam)
                Wq = lam / (mu * (mu - lam))
                Ws = 1 / (mu - lam)
                P0 = 1 - rho
                Pn = (1 - rho) * (rho**n_val)
                Pw = rho
                U = rho
                
            elif modelo == "M/M/C":
                rho = lam / (c * mu)
                sumatoria = sum([(lam / mu)**k / math.factorial(k) for k in range(c)])
                termino_c = ((lam / mu)**c / math.factorial(c)) * (1 / (1 - rho))
                P0 = 1 / (sumatoria + termino_c)
                
                Lq = (P0 * ((lam / mu)**c) * rho) / (math.factorial(c) * ((1 - rho)**2))
                Ls = Lq + (lam / mu)
                Wq = Lq / lam
                Ws = Wq + (1 / mu)
                
                if n_val < c:
                    Pn = ((lam / mu)**n_val / math.factorial(n_val)) * P0
                else:
                    Pn = ((lam / mu)**n_val / (math.factorial(c) * (c**(n_val - c)))) * P0
                
                Pw = ((lam / mu)**c / (math.factorial(c) * (1 - rho))) * P0
                U = rho

            rho_pct = rho * 100
            P0_pct = P0 * 100
            Pn_pct = Pn * 100
            Pw_pct = Pw * 100
            U_pct = U * 100
            Wq_min = Wq * 60
            Ws_min = Ws * 60

            st.markdown("### 📊 Resultados de la Estación")

            if calculo_seleccionado == "Todos los resultados":
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric("Factor de utilización básculas (ρ)", f"{rho:.4f}  |  {rho_pct:.2f}%")
                    st.metric("Probabilidad de báscula(s) vacía(s) (P0)", f"{P0:.4f}  |  {P0_pct:.2f}%")
                    st.metric(f"Probab. de {n_val} camiones (P{n_val})", f"{Pn:.4f}  |  {Pn_pct:.2f}%")
                    st.metric("Probab. de esperar en cola (Pw)", f"{Pw:.4f}  |  {Pw_pct:.2f}%")
                    st.metric("Capacidad ocupada / Uso (U)", f"{U:.4f}  |  {U_pct:.2f}%")
                with res_col2:
                    st.metric("Camiones esperando en rampa (Lq)", f"{Lq:.4f} camiones")
                    st.metric("Total camiones en estación (Ls)", f"{Ls:.4f} camiones")
                    st.metric("Tiempo de espera en rampa (Wq)", f"{Wq:.4f} horas", f"~ {Wq_min:.2f} min")
                    st.metric("Tiempo total de pesaje (Ws)", f"{Ws:.4f} horas", f"~ {Ws_min:.2f} min")

            elif calculo_seleccionado == "Factor de utilización (ρ)":
                st.metric("Factor de utilización básculas (ρ)", f"{rho:.4f}", f"{rho_pct:.2f}%")
            elif calculo_seleccionado == "Probabilidad de sistema vacío (P0)":
                st.metric("Probabilidad de báscula(s) vacía(s) (P0)", f"{P0:.4f}", f"{P0_pct:.2f}%")
            elif calculo_seleccionado == "Número promedio en cola (Lq)":
                st.metric("Camiones esperando en rampa (Lq)", f"{Lq:.4f} camiones")
            elif calculo_seleccionado == "Número promedio en sistema (Ls)":
                st.metric("Total camiones en estación (Ls)", f"{Ls:.4f} camiones")
            elif calculo_seleccionado == "Tiempo promedio en cola (Wq)":
                st.metric("Tiempo de espera en rampa (Wq)", f"{Wq:.4f} horas", f"~ {Wq_min:.2f} min")
            elif calculo_seleccionado == "Tiempo promedio en sistema (Ws)":
                st.metric("Tiempo total de pesaje (Ws)", f"{Ws:.4f} horas", f"~ {Ws_min:.2f} min")
            elif calculo_seleccionado == "Probabilidad de n camiones (Pn)":
                st.metric(f"Probabilidad de tener {n_val} camiones (P{n_val})", f"{Pn:.4f}", f"{Pn_pct:.2f}%")
            elif calculo_seleccionado == "Probabilidad de esperar en cola (Pw)":
                st.metric("Probabilidad de esperar en cola (Pw)", f"{Pw:.4f}", f"{Pw_pct:.2f}%")
            elif calculo_seleccionado == "Uso/Capacidad ocupada del sistema (U)":
                st.metric("Capacidad ocupada del sistema (U)", f"{U:.4f}", f"{U_pct:.2f}%")

            # Módulo para explicar la sobrecarga cuando rho >= 1 (Sin usar la palabra colapso)
            if rho >= 1:
                capacidad = c * mu if modelo == "M/M/C" else mu
                camion_inicio = int(math.floor(capacidad)) + 1
                camion_fin = int(math.floor(lam))
                
                st.warning(f"⚠️ **AVISO: FORMACIÓN DE COLA CONTINUA (ρ ≥ 1)**\nEl sistema se mantiene operativo y estable atendiendo a su máxima capacidad ({capacidad:.0f} camiones/hora). Sin embargo, como la tasa de llegadas es mayor a la capacidad de servicio, se forma una fila que acumula tiempo de espera de forma continua.")
                
                if camion_fin >= camion_inicio:
                    st.markdown("📌 **Aumento Acumulado del Tiempo de Espera en la primera hora:**")
                    for i in range(camion_inicio, camion_fin + 1):
                        # Cálculo corregido: El camión i espera a todos los (i-1) camiones que tiene delante
                        t_espera_h = (i - 1) * (1.0 / capacidad)
                        t_espera_m = t_espera_h * 60.0
                        horas_ent = int(t_espera_m // 60)
                        minutos_res = t_espera_m % 60
                        st.write(f"- **Camión {i}:** Tiempo de espera en cola de **{t_espera_h:.4f} horas** (lo que equivale a **{horas_ent} horas y {minutos_res:.2f} minutos**).")

            # Finalmente mostramos gráficas
            if calculo_seleccionado == "Todos los resultados":
                generar_graficas(lam, mu, c, is_otc=True)

# ==============================================================================
# VISTA 2: CALCULADORA GENERAL DE COLAS
# ==============================================================================
elif st.session_state["vista"] == "calculadora_general":
    
    st.info("🌐 **Calculadora General Teórica de Colas:** Introduce las tasas sin límite máximo de capacidad. Se deben ingresar todos los valores obligatoriamente y cumplir la condición de estabilidad.")

    modelo_gen = st.radio("Selecciona el modelo de líneas de espera:", ("M/M/1", "M/M/C"))

    col1, col2 = st.columns(2)
    with col1:
        lam_gen = st.number_input("Tasa de llegadas (λ) [unidades/tiempo]:", value=None, step=1.0, placeholder="Ejemplo: 120.0", format="%f")
    with col2:
        mu_gen = st.number_input("Tasa de servicio (μ) [unidades/tiempo]:", value=None, step=1.0, placeholder="Ejemplo: 150.0", format="%f")

    col_sub1_g, col_sub2_g = st.columns(2)
    with col_sub1_g:
        if modelo_gen == "M/M/C":
            c_gen = st.number_input("Número de servidores (c):", value=2, step=1)
        else:
            c_gen = 1
    with col_sub2_g:
        n_val_gen = st.number_input("Número de clientes en sistema (n) [para Pn]:", value=1, step=1)

    opciones_calculo_gen = [
        "Todos los resultados",
        "Factor de utilización (ρ)",
        "Probabilidad de sistema vacío (P0)",
        "Número promedio en cola (Lq)",
        "Número promedio en sistema (Ls)",
        "Tiempo promedio en cola (Wq)",
        "Tiempo promedio en sistema (Ws)",
        "Probabilidad de n clientes (Pn)",
        "Probabilidad de esperar en cola (Pw)",
        "Uso/Capacidad ocupada del sistema (U)"
    ]

    calculo_sel_gen = st.selectbox(
        "¿Qué métrica deseas realizar?",
        opciones_calculo_gen
    )

    if st.button("Calcular Resultados", type="primary", key="btn_calc_gen"):
        errores_gen = False
        
        if lam_gen is None or mu_gen is None or (modelo_gen == "M/M/C" and c_gen is None) or n_val_gen is None:
            st.error(" Error de datos: Es obligatorio ingresar un valor para la Tasa de Llegadas (λ), Tasa de Servicio (μ), Número de Servidores (c) y n para Pn. Por favor, completa todos los campos.")
            errores_gen = True
            
        if not errores_gen:
            if lam_gen < 0 or mu_gen < 0:
                st.error(" Error de datos: Las tasas de llegada (λ) y servicio (μ) deben ser números reales estrictamente positivos. No se permiten valores negativos.")
                errores_gen = True
            elif lam_gen == 0 or mu_gen == 0:
                st.error(" Error de datos: Las tasas deben ser estrictamente mayores a cero (> 0) para que exista un sistema dinámico.")
                errores_gen = True

            if n_val_gen < 0:
                st.error(" Error de datos: El número de clientes en el sistema (n) no puede ser un número negativo. Debe ser 0 o un entero positivo.")
                errores_gen = True
            elif not isinstance(n_val_gen, int) and not float(n_val_gen).is_integer():
                st.error(" Error de datos: El valor de n para Pn debe ser un número entero (no se permiten fracciones de clientes).")
                errores_gen = True
                
            if modelo_gen == "M/M/C":
                if c_gen < 1:
                    st.error(" Error de infraestructura: El número de servidores (c) debe ser al menos 1 (c ≥ 1).")
                    errores_gen = True
                elif not isinstance(c_gen, int) and not float(c_gen).is_integer():
                    st.error(" Error de datos: El número de servidores debe ser un entero positivo (no se permiten fracciones).")
                    errores_gen = True

        if not errores_gen:
            # Prevención interna para evitar crasheo (ZeroDivisionError)
            if modelo_gen == "M/M/1" and lam_gen == mu_gen:
                mu_gen += 0.00001
            elif modelo_gen == "M/M/C" and lam_gen == (c_gen * mu_gen):
                mu_gen += 0.00001

            st.success("✅ Cálculos realizados con éxito (Mostrando resultados analíticos).")
            
            c_gen = int(c_gen)
            n_val_gen = int(n_val_gen)
            
            if modelo_gen == "M/M/1":
                rho_gen = lam_gen / mu_gen
                Lq_gen = (lam_gen**2) / (mu_gen * (mu_gen - lam_gen))
                Ls_gen = lam_gen / (mu_gen - lam_gen)
                Wq_gen = lam_gen / (mu_gen * (mu_gen - lam_gen))
                Ws_gen = 1 / (mu_gen - lam_gen)
                P0_gen = 1 - rho_gen
                Pn_gen = (1 - rho_gen) * (rho_gen**n_val_gen)
                Pw_gen = rho_gen
                U_gen = rho_gen
                
            elif modelo_gen == "M/M/C":
                rho_gen = lam_gen / (c_gen * mu_gen)
                sumatoria_gen = sum([(lam_gen / mu_gen)**n / math.factorial(n) for n in range(c_gen)])
                termino_c_gen = ((lam_gen / mu_gen)**c_gen / math.factorial(c_gen)) * (1 / (1 - rho_gen))
                P0_gen = 1 / (sumatoria_gen + termino_c_gen)
                
                Lq_gen = (P0_gen * ((lam_gen / mu_gen)**c_gen) * rho_gen) / (math.factorial(c_gen) * ((1 - rho_gen)**2))
                Ls_gen = Lq_gen + (lam_gen / mu_gen)
                Wq_gen = Lq_gen / lam_gen
                Ws_gen = Wq_gen + (1 / mu_gen)
                
                if n_val_gen < c_gen:
                    Pn_gen = ((lam_gen / mu_gen)**n_val_gen / math.factorial(n_val_gen)) * P0_gen
                else:
                    Pn_gen = ((lam_gen / mu_gen)**n_val_gen / (math.factorial(c_gen) * (c_gen**(n_val_gen - c_gen)))) * P0_gen
                
                Pw_gen = ((lam_gen / mu_gen)**c_gen / (math.factorial(c_gen) * (1 - rho_gen))) * P0_gen
                U_gen = rho_gen

            rho_pct_gen = rho_gen * 100
            P0_pct_gen = P0_gen * 100
            Pn_pct_gen = Pn_gen * 100
            Pw_pct_gen = Pw_gen * 100
            U_pct_gen = U_gen * 100
            Wq_min_gen = Wq_gen * 60
            Ws_min_gen = Ws_gen * 60

            st.markdown("### 📊 Resultados Generales")

            if calculo_sel_gen == "Todos los resultados":
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric("Factor de utilización (ρ)", f"{rho_gen:.4f}  |  {rho_pct_gen:.2f}%")
                    st.metric("Probabilidad de sistema vacío (P0)", f"{P0_gen:.4f}  |  {P0_pct_gen:.2f}%")
                    st.metric(f"Probab. de {n_val_gen} clientes (P{n_val_gen})", f"{Pn_gen:.4f}  |  {Pn_pct_gen:.2f}%")
                    st.metric("Probab. de esperar en cola (Pw)", f"{Pw_gen:.4f}  |  {Pw_pct_gen:.2f}%")
                    st.metric("Capacidad ocupada / Uso (U)", f"{U_gen:.4f}  |  {U_pct_gen:.2f}%")
                with res_col2:
                    st.metric("Número promedio en cola (Lq)", f"{Lq_gen:.4f} unidades")
                    st.metric("Número promedio en sistema (Ls)", f"{Ls_gen:.4f} unidades")
                    st.metric("Tiempo promedio en cola (Wq)", f"{Wq_gen:.4f} u.t.", f"~ {Wq_min_gen:.2f} min")
                    st.metric("Tiempo promedio en sistema (Ws)", f"{Ws_gen:.4f} u.t.", f"~ {Ws_min_gen:.2f} min")

            elif calculo_sel_gen == "Factor de utilización (ρ)":
                st.metric("Factor de utilización (ρ)", f"{rho_gen:.4f}", f"{rho_pct_gen:.2f}%")
            elif calculo_sel_gen == "Probabilidad de sistema vacío (P0)":
                st.metric("Probabilidad de sistema vacío (P0)", f"{P0_gen:.4f}", f"{P0_pct_gen:.2f}%")
            elif calculo_sel_gen == "Número promedio en cola (Lq)":
                st.metric("Número promedio en cola (Lq)", f"{Lq_gen:.4f} unidades")
            elif calculo_sel_gen == "Número promedio en sistema (Ls)":
                st.metric("Número promedio en sistema (Ls)", f"{Ls_gen:.4f} unidades")
            elif calculo_sel_gen == "Tiempo promedio en cola (Wq)":
                st.metric("Tiempo promedio en cola (Wq)", f"{Wq_gen:.4f} u.t.", f"~ {Wq_min_gen:.2f} min")
            elif calculo_sel_gen == "Tiempo promedio en sistema (Ws)":
                st.metric("Tiempo promedio en sistema (Ws)", f"{Ws_gen:.4f} u.t.", f"~ {Ws_min_gen:.2f} min")
            elif calculo_sel_gen == "Probabilidad de n clientes (Pn)":
                st.metric(f"Probabilidad de tener {n_val_gen} clientes (P{n_val_gen})", f"{Pn_gen:.4f}", f"{Pn_pct_gen:.2f}%")
            elif calculo_sel_gen == "Probabilidad de esperar en cola (Pw)":
                st.metric("Probabilidad de esperar en cola (Pw)", f"{Pw_gen:.4f}", f"{Pw_pct_gen:.2f}%")
            elif calculo_sel_gen == "Uso/Capacidad ocupada del sistema (U)":
                st.metric("Capacidad ocupada del sistema (U)", f"{U_gen:.4f}", f"{U_pct_gen:.2f}%")

            # Módulo para explicar la sobrecarga cuando rho_gen >= 1
            if rho_gen >= 1:
                cap_gen = c_gen * mu_gen if modelo_gen == "M/M/C" else mu_gen
                unidad_inicio = int(math.floor(cap_gen)) + 1
                unidad_fin = int(math.floor(lam_gen))
                
                st.warning(f"⚠️ **AVISO: FORMACIÓN DE COLA CONTINUA (ρ ≥ 1)**\nEl sistema se mantiene estable atendiendo a su máxima capacidad ({cap_gen:.0f} unidades/tiempo). Al superar la capacidad de servicio, el exceso forma una cola que acumula tiempo de forma progresiva.")
                
                if unidad_fin >= unidad_inicio:
                    st.markdown("📌 **Aumento Acumulado del Tiempo de Espera en el primer periodo:**")
                    for i in range(unidad_inicio, unidad_fin + 1):
                        # Cálculo corregido: La unidad i espera a todas las (i-1) unidades que tiene delante
                        t_espera_h = (i - 1) * (1.0 / cap_gen)
                        t_espera_m = t_espera_h * 60.0
                        horas_ent = int(t_espera_m // 60)
                        minutos_res = t_espera_m % 60
                        st.write(f"- **Unidad {i}:** Tiempo de espera en cola de **{t_espera_h:.4f} u.t.** (lo que equivale a **{horas_ent} horas y {minutos_res:.2f} minutos** si se trata de horas).")

            # Finalmente mostramos gráficas
            if calculo_sel_gen == "Todos los resultados":
                generar_graficas(lam_gen, mu_gen, c_gen, is_otc=False)

# ==============================================================================
# VISTA 3: SECCIÓN COMPLETA DE AYUDA Y EJERCICIO DE EJEMPLO
# ==============================================================================
else:
    st.markdown("###  Guía del Usuario, Conceptos y Manual de Gráficas")
    
    st.write("⚙️ **¿Cómo utilizar la calculadora?**")
    st.write("1. Selecciona la configuración del sistema (M/M/1 para servidor único o M/M/C para múltiples servidores en paralelo).")
    st.write("2. Digita la Tasa de llegadas (λ) y la Tasa de servicio (μ).")
    st.write("3. Especifica el valor de n si deseas consultar la probabilidad de hallar exactamente esa cantidad de entidades (Pn).")
    st.write("4. Selecciona la métrica específica o la vista completa 'Todos los resultados'.")
    st.write("5. Presiona 'Calcular Resultados' para ver los indicadores numéricos y desplegar el panel gráfico interactivo.")
    
    st.markdown("---")
    st.markdown("### 📐 Concepto de Cada Cálculo Matemático")
    st.write("• **Factor de Utilización (ρ):** Mide la fracción promedio de tiempo que los servidores están ocupados.")
    st.write("• **Probabilidad de Sistema Vacío (P0):** Probabilidad de que no haya clientes ni camiones en la instalación (servidores ociosos).")
    st.write("• **Probabilidad de n Unidades (Pn):** Probabilidad exacta de encontrar n clientes/camiones dentro del sistema en un instante dado.")
    st.write("• **Probabilidad de Esperar en Cola (Pw):** Probabilidad de que un cliente recién llegado tenga que hacer fila obligatoriamente al encontrar todos los servidores ocupados.")
    st.write("• **Uso del Sistema (U):** Representa el nivel de carga global o capacidad ocupada del servicio.")
    st.write("• **Número Promedio en Cola (Lq):** Cantidad esperada de unidades haciendo fila sin ser atendidas aún.")
    st.write("• **Número Promedio en Sistema (Ls):** Total de unidades en la instalación (tanto en cola como siendo atendidas en los servidores).")
    st.write("• **Tiempo Promedio en Cola (Wq):** Tiempo medio de espera de una unidad antes de recibir servicio.")
    st.write("• **Tiempo Promedio en Sistema (Ws):** Tiempo total que permanece una unidad desde que llega hasta que finaliza la atención.")

    st.markdown("---")
    st.markdown("### ⚠️ Acumulación de Cola (ρ ≥ 1)")
    st.write("Cuando la tasa de llegadas (λ) es mayor o igual a la capacidad total de servicio (c · μ), el factor de utilización (ρ) supera el 100%. El sistema sigue operando de forma estable atendiendo a su máxima capacidad, pero se genera una cola continua.")
    st.write("• **¿Por qué ocurre el aumento de tiempo acumulado?** El servidor atiende a su máxima velocidad, pero entran más camiones de los que pueden salir. El exceso se acumula hora tras hora de forma determinista. Por ejemplo, si llegan 60 camiones y solo se pueden atender 50, el camión 51 no pasará en esa hora, y su tiempo para pasar se sumará al tiempo de espera de los demás, incrementando la cola constantemente por cada unidad adicional.")
    st.write("• **¿Por qué no se recomienda simular con ρ ≥ 1?** Matemáticamente, las fórmulas de estado estable no aplican a colas que crecen hacia el infinito. En la realidad física, esto significa la acumulación progresiva de la fila, lo que terminaría bloqueando las vías de acceso a largo plazo si no disminuye la tasa de llegadas.")

    st.markdown("---")
    st.markdown("### 📊 Interpretación de las Gráficas del Sistema")
    st.write("1. **Distribución de Probabilidad (Pn) — Gráfico de Barras Discretas:** Muestra la curva estocástica de cuántos clientes/camiones se espera encontrar simultáneamente. La primera barra resaltada (n=0) muestra P0. Permite visualizar si el sistema suele estar casi vacío o con acumulación severa.")
    st.write("2. **Comparativa de Tiempos (Wq 'vs.' Ws) — Barras Horizontales:** Compara directamente la cantidad de tiempo perdida haciendo fila (Wq) frente al tiempo global gastado en el proceso (Ws). Si Wq abarca casi todo el largo de Ws, significa que el cuello de botella está en la cola y no en el tiempo de servicio.")
    st.write("3. **Comparativa de Cantidades (Lq vs. Ls) — Barras Verticales:** Permite observar qué porcentaje de la saturación del sistema proviene de la congestión en fila (Lq) frente a las unidades atendidas en las básculas/servidores (Ls).")
    st.write("4. **Curva de Sensibilidad (λ vs Lq) — Gráfico de Líneas con Sombreado:** Grafica la respuesta del sistema conforme se incrementa el flujo de llegadas (λ). Permite identificar el punto de inflexión donde la cola crece asintóticamente cuando ρ aproxima a 1, ayudando a prevenir congestiones críticas.")

    st.markdown("---")
    st.markdown("### 🛑 Restricciones del Sistema Real")
    st.write("• **Valores Positivos:** Las tasas λ y μ deben ser números reales estrictamente mayores a cero.")
    st.write("• **Cantidad de camiones (n ≥ 0):** Se aceptan enteros mayores o iguales a cero.")
    st.write("• **Límite de Tráfico (Pestaña OTC):** Un máximo de 100 camiones/hora para evitar flujos irreales en la rampa de la autopista.")
    st.write("• **Capacidad de Infraestructura:** El número de básculas (c) debe ser un número entero entre 1 y 3.")
    st.write("• **Formación de colas:** La velocidad total de atención debe ser superior a las llegadas (ρ < 1) para evitar que el tiempo de espera crezca constantemente.")

    st.markdown("---")
    st.markdown("### 🚛 Ejercicio Práctico de Ejemplo (Caso OTC)")
    st.write("La **Ohio Turnpike Commission (OTC)** opera una estación de pesaje para camiones. A continuación se presentan los datos del caso de estudio y la comparación entre la situación actual y la propuesta de expansión:")
    
    st.markdown("""
    <div class="help-box">
        <h4> Parámetros de Entrada del Caso</h4>
        <ul>
            <li><b>Tasa de llegadas de camiones (λ):</b> 60 camiones / hora</li>
            <li><b>Tasa de servicio por báscula (μ):</b> 66 camiones / hora</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📊 Comparativa de Resultados del Ejemplo")
    
    col_ex1, col_ex2 = st.columns(2)
    
    with col_ex1:
        st.markdown("""
        <div class="result-card-red">
            <h4> Sistema Actual (M/M/1)</h4>
            <p><b>Básculas operativas (c):</b> 1</p>
            <hr>
            <p><b>• Utilización (ρ):</b> 90.91%</p>
            <p><b>• Camiones en cola (Lq):</b> 9.09 camiones</p>
            <p><b>• Camiones en estación (Ls):</b> 10.00 camiones</p>
            <p><b>• Tiempo en cola (Wq):</b> 0.1515 hrs (~ 9.09 min)</p>
            <p><b>• Tiempo total (Ws):</b> 0.1667 hrs (~ 10.00 min)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_ex2:
        st.markdown("""
        <div class="result-card-green">
            <h4> Propuesta (M/M/C)</h4>
            <p><b>Básculas operativas (c):</b> 2</p>
            <hr>
            <p><b>• Utilización (ρ):</b> 45.45%</p>
            <p><b>• Camiones en cola (Lq):</b> 0.2443 camiones</p>
            <p><b>• Camiones en estación (Ls):</b> 1.1533 camiones</p>
            <p><b>• Tiempo en cola (Wq):</b> 0.0041 hrs (~ 0.24 min / 14 seg)</p>
            <p><b>• Tiempo total (Ws):</b> 0.0192 hrs (~ 1.15 min)</p>
        </div>
        """, unsafe_allow_html=True)

    st.success(" **Conclusión del Caso OTC:** Al instalar la segunda báscula (c = 2), la fila de camiones en la rampa se reduce de más de 9 camiones a prácticamente 0, reduciendo el tiempo de espera de 9 minutos a solo 14 segundos y previniendo grandes filas en la autopista.")

# Pie de página con integrantes
st.markdown("""
    <div class="integrantes">
        <b>Desarrollado por:</b><br>
        Lady Dayana Cabezas | Felipe Jara Acosta | Xhakerz Jaimes Pinzon
    </div>
""", unsafe_allow_html=True)