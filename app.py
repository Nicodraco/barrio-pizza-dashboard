"""Dashboard de órdenes de compra de Barrio Pizza.

Correr con:  streamlit run app.py
"""
import os
import sys

import pandas as pd
import streamlit as st
import altair as alt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.carga import cargar_datos
from core.alertas import analizar
from core.proyeccion import proyectar
from core import chat as chat_mod
from core import tema

st.set_page_config(
    page_title="Barrio Pizza · Dashboard de Compras",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Carga y análisis (cacheado por método)
# --------------------------------------------------------------------------

@st.cache_data(show_spinner="Analizando las órdenes de la semana…")
def obtener_datos():
    return cargar_datos()


@st.cache_data(show_spinner="Calculando proyecciones y alertas…")
def obtener_analisis(metodo):
    return analizar(obtener_datos(), metodo=metodo)


METODOS = {
    "Robusto (sin outliers)": "robusto",
    "Promedio simple": "simple",
    "Con tendencia": "tendencia",
}

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.image(tema.LOGO_NEGRO, width=120)
    st.caption("Barrio Pizza · Control de órdenes de compra")
    metodo_label = st.radio(
        "Método de proyección",
        list(METODOS),
        index=0,
        help="Robusto ignora semanas atípicas. Tendencia capta crecimiento.",
    )
    metodo = METODOS[metodo_label]
    st.divider()
    sucursal_filter = st.multiselect(
        "Filtrar sucursales",
        obtener_analisis("robusto")["sucursales"],
        default=[],
        help="Vacío = todas.",
    )
    st.divider()
    st.markdown("**Sobre el chat con IA**")
    st.caption(
        "El 'motor local' responde sin API (reglas sobre los datos). "
        "Con 'Groq (LLM)' puedes conectarlo a un modelo gratuito."
    )
    st.divider()
    cursor_pizza_on = st.toggle(
        "Cursor de pizza",
        value=True,
        help="El puntero es una rebanada de la marca. Al presionar el clic, te llevarás una mordida.",
    )

# --------------------------------------------------------------------------
# Cálculo principal
# --------------------------------------------------------------------------

if cursor_pizza_on:
    st.html(tema.cursor_pizza())

res = obtener_analisis(metodo)
datos = obtener_datos()
detalle = res["detalle"]
alertas = res["alertas"]

sucursales = res["sucursales"]
if sucursal_filter:
    sucursales = [s for s in sucursales if s in sucursal_filter]
    detalle = detalle[detalle["sucursal"].isin(sucursales)]
    alertas = alertas[alertas["sucursal"].isin(sucursales)]

# --------------------------------------------------------------------------
# Encabezado y KPIs
# --------------------------------------------------------------------------

st.html(tema.cabecera_html(metodo_label))

st.title("Dashboard de órdenes de compra")
st.caption(
    "Compara lo que cada sucursal pidió esta semana contra el consumo proyectado "
    "y el inventario actual. Método: **" + metodo_label + "**."
)

kpi_total = len(alertas)
kpi_quiebre = int((alertas["tipo"] == "RIESGO QUIEBRE").sum())
kpi_sobre = int((alertas["tipo"] == "SOBRE-PEDIDO").sum())
kpi_olvido = int((alertas["tipo"] == "SE OLVIDO").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Alertas totales", kpi_total)
c2.metric("Riesgo de quiebre", kpi_quiebre)
c3.metric("Sobre-pedidos", kpi_sobre)
c4.metric("Se olvidaron de pedir", kpi_olvido)

tab_alertas, tab_matriz, tab_historico, tab_chat, tab_proveedor = st.tabs(
    ["Alertas", "Matriz sucursal × insumo", "Histórico y proyección", "Chat con IA", "Pedido sugerido por proveedor"]
)

def _estado_corto(tipo):
    return {
        "RIESGO QUIEBRE": "QUIEBRE",
        "SOBRE-PEDIDO": "DE MÁS",
        "SE OLVIDO": "OLVIDÓ",
        "INGREDIENTE DESCONOCIDO": "¿?",
        "OK": "OK",
    }.get(tipo, tipo)


# --------------------------------------------------------------------------
# Pestaña: Alertas
# --------------------------------------------------------------------------

with tab_alertas:
    if alertas.empty:
        st.success("No se detectaron alertas. Las órdenes están alineadas con la proyección.")
    else:
        st.subheader(f"{len(alertas)} alerta(s) detectadas esta semana")
        st.html(tema.comandas_html(alertas))

    with st.expander("Ver tabla de alertas (con todos los campos)"):
        if alertas.empty:
            st.info("Sin alertas.")
        else:
            st.dataframe(
                alertas[
                    ["sucursal", "nombre", "tipo", "proveedor", "pedido_formatos",
                     "formato_compra", "pedido_base", "proyeccion_base", "stock_base",
                     "necesidad_base", "recomendado_formatos", "es_perecedero", "mensaje"]
                ],
                width="stretch",
                hide_index=True,
            )
        st.download_button(
            "Descargar alertas (CSV)",
            detalle.to_csv(index=False).encode("utf-8-sig"),
            file_name="alertas_barrio_pizza.csv",
            mime="text/csv",
        )

# --------------------------------------------------------------------------
# Pestaña: Matriz
# --------------------------------------------------------------------------

with tab_matriz:
    st.markdown(
        "Semáforo por sucursal e insumo: qué tan alineado está el pedido con la "
        "necesidad proyectada."
    )
    pivot = detalle.pivot_table(
        index="sucursal", columns="nombre", values="tipo", aggfunc="first"
    ).reindex(index=sucursales)
    pivot_corto = pivot.map(_estado_corto)

    def _color_celda(val):
        return {
            "QUIEBRE": "background-color:#f5b7b1; color:#7b241c; font-weight:bold",
            "DE MÁS": "background-color:#f9e79f; color:#7e5109; font-weight:bold",
            "OLVIDÓ": "background-color:#aed6f1; color:#1b4f72; font-weight:bold",
            "¿?": "background-color:#d5dbdb; color:#566573; font-weight:bold",
            "OK": "background-color:#d5f5e3; color:#145a32",
        }.get(val, "")

    st.dataframe(
        pivot_corto.style.map(_color_celda),
        width="stretch",
        height=400,
    )
    st.caption("Verde = correcto · Rojo = riesgo de quiebre · Naranja = pide de más · Azul = se olvidó · Gris = desconocido")

# --------------------------------------------------------------------------
# Pestaña: Histórico y proyección
# --------------------------------------------------------------------------

with tab_historico:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        suc_sel = st.selectbox("Sucursal", sucursales)
        ids_ok = sorted(
            detalle[detalle["sucursal"] == suc_sel]["ingrediente_id"].unique()
        )
        iid_sel = st.selectbox("Insumo", ids_ok)
    with col_b:
        fila = detalle[
            (detalle["sucursal"] == suc_sel) & (detalle["ingrediente_id"] == iid_sel)
        ]
        if fila.empty:
            st.info("Sin datos para esta combinación.")
        else:
            r = fila.iloc[0]
            cons = datos["consumo"]
            serie = (
                cons[(cons["sucursal"] == suc_sel) & (cons["ingrediente_id"] == iid_sel)]
                .sort_values("semana")
            )
            proy = proyectar(serie["consumo_unidad_base"].tolist(), metodo)
            df_line = pd.DataFrame(
                {
                    "semana": serie["semana"].tolist(),
                    "Consumo real": serie["consumo_unidad_base"].tolist(),
                }
            )
            df_proy = pd.DataFrame(
                [{"semana": "S7 (proyección)", "Consumo real": proy["proyeccion"]}]
            )
            chart = (
                alt.Chart(df_line, title=f"{r['nombre']} · {suc_sel}")
                .mark_line(point=True)
                .encode(
                    x=alt.X("semana:N", title="Semana"),
                    y=alt.Y("Consumo real:Q", title=f"Unidad base ({r['unidad_base']})"),
                )
            )
            chart_proy = (
                alt.Chart(df_proy)
                .mark_point(size=160, filled=True, color="#c0392b", shape="diamond")
                .encode(x="semana:N", y="Consumo real:Q")
            )
            st.altair_chart(chart + chart_proy, width="stretch")

            if proy["outliers"]:
                atipicas = [s for s, o in zip(serie["semana"], proy["outliers"]) if o]
                st.warning(f"Semanas atípicas ignoradas en la proyección: {', '.join(atipicas)}.")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Proyección próxima semana", f"{proy['proyeccion']:,.2f}")
            m2.metric("Inventario actual", f"{r['stock_base']:g}")
            m3.metric("Pedido de la semana", f"{r['pedido_formatos']:g} {r['formato_compra']}")
            m4.metric("Recomendado", f"{r['recomendado_formatos']:g} {r['formato_compra']}")

# --------------------------------------------------------------------------
# Pestaña: Chat con IA
# --------------------------------------------------------------------------

with tab_chat:
    st.subheader("Chat con los datos")
    st.caption(
        "Pregunta en español, por ejemplo: “¿qué sucursal está pidiendo demasiado "
        "queso?” o “¿quién se olvidó de pedir mozzarella?”."
    )

    with st.expander("Opciones del chat", expanded=False):
        motor = st.radio("Motor", ["Motor local (sin API)", "Groq (LLM gratuito)"])
        groq_key = None
        groq_model = "llama-3.3-70b-versatile"
        if motor.startswith("Groq"):
            groq_key = st.text_input(
                "API key de Groq", type="password",
                help="Creala gratis en console.groq.com (no requiere tarjeta).",
            )
            groq_model = st.text_input("Modelo", groq_model)

    if "chat" not in st.session_state:
        st.session_state["chat"] = [
            ("assistant", "¡Hola! Soy el asistente de compras de Barrio Pizza. "
                          "Pregúntame sobre las alertas de esta semana.")
        ]

    for rol, texto in st.session_state["chat"]:
        with st.chat_message(rol):
            st.markdown(texto)

    pregunta = st.chat_input("Escribe tu pregunta sobre las órdenes de la semana…")
    if pregunta:
        st.session_state["chat"].append(("user", pregunta))
        with st.chat_message("user"):
            st.markdown(pregunta)

        if motor.startswith("Groq"):
            if not groq_key:
                respuesta = (
                    "Necesitas una API key de Groq para usar este motor, o cambia a "
                    "«Motor local» en las opciones del chat."
                )
            else:
                try:
                    respuesta = chat_mod.responder_llm(pregunta, res, groq_key, groq_model)
                except Exception as e:  # noqa: BLE001
                    respuesta = f"Error llamando al LLM: {e}"
        else:
            respuesta = chat_mod.responder_local(pregunta, res)

        st.session_state["chat"].append(("assistant", respuesta))
        with st.chat_message("assistant"):
            st.markdown(respuesta)

# --------------------------------------------------------------------------
# Pestaña: Pedido sugerido por proveedor
# --------------------------------------------------------------------------

with tab_proveedor:
    st.markdown(
        "Lista del **pedido corregido** (recomendado) agrupada por proveedor, "
        "para reenviarle a cada uno su parte directamente."
    )
    sugerido = detalle[detalle["recomendado_formatos"] > 0].copy()
    if sugerido.empty:
        st.info("Ningún insumo necesita pedirse con el método actual.")
    else:
        sugerido = sugerido[
            ["proveedor", "sucursal", "nombre", "recomendado_formatos",
             "formato_compra", "unidad_base", "es_perecedero"]
        ].rename(
            columns={
                "recomendado_formatos": "cantidad_formatos",
                "formato_compra": "formato",
            }
        )
        st.dataframe(sugerido.sort_values(["proveedor", "sucursal", "nombre"]),
                     width="stretch", hide_index=True)
        st.download_button(
            "Descargar pedido por proveedor (CSV)",
            sugerido.sort_values(["proveedor", "sucursal", "nombre"]).to_csv(index=False).encode("utf-8-sig"),
            file_name="pedido_sugerido_por_proveedor.csv",
            mime="text/csv",
        )

st.html(tema.pie_html())
st.caption(
    "Herramienta construida para la práctica de IA de Barrio Pizza. Los datos "
    "provienen de los 4 CSV del reto (proyección, inventario y órdenes de la semana)."
)
