import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Asistente Financiero Familiar IA", page_icon="AF", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f7f8fa; color: #111827; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5e7eb; }
    div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; }
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { letter-spacing: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path: str):
    response = requests.get(f"{API_URL}{path}", headers=api_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json=None, files=None, data=None):
    response = requests.post(f"{API_URL}{path}", headers=api_headers(), json=json, files=files, data=data, timeout=120)
    response.raise_for_status()
    return response.json()


def money(value) -> str:
    return f"$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def login_screen():
    st.title("Asistente Financiero Familiar IA")
    st.caption("MVP para entender gastos familiares con resúmenes bancarios argentinos.")
    tab_login, tab_register = st.tabs(["Ingresar", "Crear cuenta"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")
        if st.button("Ingresar", type="primary", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    data={"username": email, "password": password},
                    timeout=30,
                )
                response.raise_for_status()
                st.session_state.token = response.json()["access_token"]
                st.rerun()
            except requests.HTTPError as exc:
                st.error(exc.response.json().get("detail", "No se pudo iniciar sesión"))

    with tab_register:
        full_name = st.text_input("Nombre", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Contraseña", type="password", key="register_password")
        if st.button("Crear cuenta", use_container_width=True):
            try:
                requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": email, "password": password, "full_name": full_name},
                    timeout=30,
                ).raise_for_status()
                st.success("Cuenta creada. Ya podés ingresar.")
            except requests.HTTPError as exc:
                st.error(exc.response.json().get("detail", "No se pudo registrar"))


def dashboard():
    st.title("Dashboard financiero")
    data = api_get("/dashboard/summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", money(data["income"]))
    c2.metric("Gastos", money(data["expenses"]))
    c3.metric("Ahorro", money(data["savings"]))
    c4.metric("% ahorro", f'{data["savings_rate"]:.1f}%')

    left, right = st.columns(2)
    with left:
        df = pd.DataFrame(data["expenses_by_category"])
        st.subheader("Gastos por categoría")
        if not df.empty:
            st.plotly_chart(px.bar(df, x="category", y="amount", color="category"), use_container_width=True)
        else:
            st.info("Todavía no hay gastos cargados.")
    with right:
        df = pd.DataFrame(data["fixed_vs_variable"])
        st.subheader("Fijos vs variables")
        if not df.empty:
            st.plotly_chart(px.pie(df, names="type", values="amount", hole=0.55), use_container_width=True)

    st.subheader("Evolución mensual")
    monthly = pd.DataFrame(data["monthly_evolution"])
    if not monthly.empty:
        st.plotly_chart(px.line(monthly, x="month", y=["income", "expenses"], markers=True), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.dataframe(pd.DataFrame(data["top_expenses"]), hide_index=True, use_container_width=True)
    c2.dataframe(pd.DataFrame(data["frequent_merchants"]), hide_index=True, use_container_width=True)
    c3.dataframe(pd.DataFrame(data["small_expenses"]), hide_index=True, use_container_width=True)


def upload_pdf():
    st.title("Subir resumen bancario")
    st.caption("Soporta detección BBVA Visa Platinum, Banco Nación Visa Signature y parser Visa genérico.")
    file = st.file_uploader("PDF del resumen", type=["pdf"])
    if file and st.button("Procesar PDF", type="primary"):
        try:
            result = api_post("/files/upload", files={"file": (file.name, file.getvalue(), "application/pdf")})
            st.success(f"PDF procesado. Movimientos importados: {len(result)}")
            st.dataframe(pd.DataFrame(result), hide_index=True, use_container_width=True)
        except requests.HTTPError as exc:
            st.error(exc.response.json().get("detail", "No se pudo procesar el PDF"))


def movements():
    st.title("Movimientos")
    categories = api_get("/categories")
    category_by_name = {c["name"]: c["id"] for c in categories}
    query = st.text_input("Buscar por comercio o descripción")
    rows = api_get(f"/transactions?q={query}" if query else "/transactions")
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No hay movimientos para mostrar.")
        return
    df["categoria"] = df["category"].apply(lambda c: c["name"] if isinstance(c, dict) and c else "Sin categoría")
    st.dataframe(
        df[["transaction_date", "categoria", "normalized_description", "amount", "bank_name", "card_type", "expense_type"]],
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Reclasificar movimiento"):
        tx_id = st.number_input("ID de movimiento", min_value=1, step=1)
        category_name = st.selectbox("Categoría", list(category_by_name.keys()))
        expense_type = st.selectbox("Tipo", ["fixed", "variable", "exceptional"])
        description = st.text_input("Descripción normalizada opcional")
        if st.button("Guardar cambios"):
            payload = {"category_id": category_by_name[category_name], "expense_type": expense_type}
            if description:
                payload["normalized_description"] = description.upper()
            response = requests.patch(f"{API_URL}/transactions/{tx_id}", json=payload, headers=api_headers(), timeout=30)
            if response.ok:
                st.success("Movimiento actualizado.")
            else:
                st.error(response.json().get("detail", "No se pudo actualizar"))


def manual_entries():
    st.title("Registro manual")
    categories = api_get("/categories")
    category_by_name = {c["name"]: c["id"] for c in categories}
    expense_tab, income_tab = st.tabs(["Gasto", "Ingreso"])

    with expense_tab:
        date = st.date_input("Fecha del gasto")
        description = st.text_input("Descripción", key="expense_desc")
        amount = st.number_input("Importe", min_value=0.0, step=100.0, key="expense_amount")
        category_name = st.selectbox("Categoría", list(category_by_name.keys()))
        expense_type = st.selectbox("Tipo de gasto", ["fixed", "variable", "exceptional"])
        notes = st.text_area("Observaciones", key="expense_notes")
        if st.button("Agregar gasto", type="primary"):
            api_post(
                "/manual/expenses",
                json={
                    "expense_date": datetime.combine(date, datetime.min.time()).isoformat(),
                    "category_id": category_by_name[category_name],
                    "description": description,
                    "amount": amount,
                    "expense_type": expense_type,
                    "notes": notes,
                },
            )
            st.success("Gasto agregado.")

    with income_tab:
        date = st.date_input("Fecha del ingreso")
        description = st.text_input("Descripción", key="income_desc")
        amount = st.number_input("Importe", min_value=0.0, step=1000.0, key="income_amount")
        notes = st.text_area("Observaciones", key="income_notes")
        if st.button("Agregar ingreso", type="primary"):
            api_post(
                "/manual/income",
                json={
                    "income_date": datetime.combine(date, datetime.min.time()).isoformat(),
                    "description": description,
                    "amount": amount,
                    "notes": notes,
                },
            )
            st.success("Ingreso agregado.")


def settings_screen():
    st.title("Configuración")
    st.write("API conectada:", API_URL)
    st.write("Categorías disponibles")
    st.dataframe(pd.DataFrame(api_get("/categories")), hide_index=True, use_container_width=True)


def app():
    if "token" not in st.session_state:
        login_screen()
        return

    with st.sidebar:
        st.title("Finanzas Familiares")
        page = st.radio("Secciones", ["Dashboard", "Subir PDFs", "Movimientos", "Ingresos y gastos", "Configuración"])
        if st.button("Cerrar sesión"):
            st.session_state.pop("token", None)
            st.rerun()

    try:
        if page == "Dashboard":
            dashboard()
        elif page == "Subir PDFs":
            upload_pdf()
        elif page == "Movimientos":
            movements()
        elif page == "Ingresos y gastos":
            manual_entries()
        else:
            settings_screen()
    except requests.ConnectionError:
        st.error("No se pudo conectar con la API. Verificá que el backend esté ejecutándose.")
    except requests.HTTPError as exc:
        st.error(exc.response.json().get("detail", "Ocurrió un error"))


app()
