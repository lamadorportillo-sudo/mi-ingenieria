import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Archivo de base de datos
DB_FILE = "datos_proyectos.csv"

def cargar_db():
    columnas = ["Fecha", "Proyecto", "Contratista", "Presupuesto_L", "Pagado_L", "Saldo_L", "Modalidad"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in columnas:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=columnas)
    else:
        return pd.DataFrame(columns=columnas)

st.set_page_config(page_title="Ingeniería Pro - Nube", layout="wide")
st.title("🏗️ Sistema de Control de Obras y Pagos")

df = cargar_db()

tab1, tab2 = st.tabs(["📊 Gestión y Edición", "➕ Nuevo Registro"])

with tab2:
    st.header("Registrar Nuevo Proyecto o Pago")
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        f_fecha = col1.date_input("Fecha", datetime.now())
        f_proy = col1.text_input("Proyecto")
        f_cont = col2.text_input("Contratista / Cliente")
        f_pres = col2.number_input("Presupuesto (L)", min_value=0.0)
        f_pago = col1.number_input("Pago Inicial (L)", min_value=0.0)
        
        if st.form_submit_button("Guardar Datos"):
            if f_proy and f_cont:
                mod = "Licitación Pública" if f_pres > 1200000 else "Contratación Directa"
                nueva = pd.DataFrame([[f_fecha.strftime("%d/%m/%Y"), f_proy, f_cont, f_pres, f_pago, f_pres-f_pago, mod]], columns=df.columns)
                df = pd.concat([df, nueva], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Registrado!")
                st.rerun()

with tab1:
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Contratado", f"L {df['Presupuesto_L'].sum():,.2f}")
        m2.metric("Total Pagado", f"L {df['Pagado_L'].sum():,.2f}")
        m3.metric("Saldo Pendiente", f"L {df['Saldo_L'].sum():,.2f}", delta_color="inverse")
        
        st.subheader("Listado de Movimientos")
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("🛠️ Panel de Edición y Borrado")
        idx = st.selectbox("Seleccione para modificar:", df.index, format_func=lambda x: f"{df.at[x, 'Proyecto']} ({df.at[x, 'Contratista']})")
        
        with st.expander("Modificar datos seleccionados"):
            e_proy = st.text_input("Nombre", df.at[idx, 'Proyecto'])
            e_cont = st.text_input("Contratista", df.at[idx, 'Contratista'])
            e_pres = st.number_input("Presupuesto", value=float(df.at[idx, 'Presupuesto_L']))
            e_pago = st.number_input("Pagado", value=float(df.at[idx, 'Pagado_L']))
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("💾 Actualizar"):
                df.at[idx, 'Proyecto'] = e_proy
                df.at[idx, 'Contratista'] = e_cont
                df.at[idx, 'Presupuesto_L'] = e_pres
                df.at[idx, 'Pagado_L'] = e_pago
                df.at[idx, 'Saldo_L'] = e_pres - e_pago
                df.to_csv(DB_FILE, index=False)
                st.rerun()
            if c_btn2.button("🗑️ Eliminar"):
                df = df.drop(idx)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    else:
        st.info("No hay datos. Ve a la pestaña 'Nuevo Registro'.")
