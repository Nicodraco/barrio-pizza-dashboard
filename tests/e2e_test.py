"""Pruebas end-to-end de todas las funcionalidades del dashboard con Playwright.

Requisitos:
  1. La app corriendo en http://localhost:8501  (streamlit run app.py)
  2. pip install playwright  &&  python -m playwright install chromium

Correr:
  python tests/e2e_test.py
"""
import sys

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
RESULTADOS = []


def registrar(nombre, ok, detalle=""):
    RESULTADOS.append((nombre, ok, detalle))
    print(("PASS" if ok else "FAIL") + f"  {nombre}" + (f"  -> {detalle}" if detalle and not ok else ""))


def sin_excepciones(page, nombre):
    n = page.locator('[data-testid="stException"]').count()
    if n:
        registrar(nombre, False, f"stException x{n}")
        return False
    return True


def valor_kpi_total(page):
    return page.locator('[data-testid="stMetric"]').first.locator('[data-testid="stMetricValue"]').inner_text().strip()


def set_radio(page, label):
    page.locator(f'[data-testid="stSidebar"] label:has-text("{label}")').click()


def set_selectbox(page, idx, value):
    page.locator('[data-testid="stSelectbox"]').nth(idx).click()
    page.wait_for_timeout(600)
    page.locator('[data-baseweb="popover"] li[role="option"]', has_text=value).first.click()
    page.wait_for_timeout(800)


def elegir_multiselect(page, value):
    page.locator('[data-testid="stMultiSelect"] [data-baseweb="select"]').first.click()
    page.wait_for_timeout(600)
    page.locator('[data-baseweb="popover"] li[role="option"]', has_text=value).first.click()
    page.keyboard.press("Escape")
    page.wait_for_timeout(600)


def limpiar_multiselect(page):
    """Borra todos los chips (como un usuario real, con la X de cada chip)."""
    for _ in range(10):
        del_btn = page.locator('[data-testid="stMultiSelect"] [data-baseweb="tag"] [title="Delete"]').first
        if del_btn.count() == 0:
            break
        del_btn.click()
        page.wait_for_timeout(500)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(30000)
        page.goto(URL)
        page.wait_for_selector('h1:has-text("Dashboard de órdenes de compra")')
        page.wait_for_timeout(1500)

        # ===== A. Página principal =====
        registrar("Carga y titulo", True)
        labels = [m.locator('[data-testid="stMetricLabel"]').inner_text() for m in page.locator('[data-testid="stMetric"]').all()]
        ok = all(e in labels for e in ["Alertas totales", "Riesgo de quiebre", "Sobre-pedidos", "Se olvidaron de pedir", "Proyección próxima semana"])
        registrar("KPIs globales presentes", ok, f"{labels[:5]}")
        sin_excepciones(page, "Sin excepciones en carga")
        registrar("Alertas totales = 5 (robusto)", valor_kpi_total(page) == "5", valor_kpi_total(page))

        # ===== B. Método de proyección =====
        set_radio(page, "Con tendencia"); page.wait_for_timeout(2500)
        registrar("Tendencia -> 20 alertas", valor_kpi_total(page) == "20", valor_kpi_total(page))
        sin_excepciones(page, "Sin excepciones tendencia")
        set_radio(page, "Promedio simple"); page.wait_for_timeout(2500)
        registrar("Promedio simple -> 6 alertas", valor_kpi_total(page) == "6", valor_kpi_total(page))
        set_radio(page, "Robusto (sin outliers)"); page.wait_for_timeout(2500)
        registrar("Robusto -> 5 alertas", valor_kpi_total(page) == "5", valor_kpi_total(page))

        # ===== C. Pestaña Alertas (estado por defecto) =====
        page.get_by_role("tab", name="Alertas").click(); page.wait_for_timeout(1500)
        cuerpo = page.locator("body").inner_text()
        registrar("Subheader 'alerta(s) detectadas'", "detectadas esta semana" in cuerpo)
        for s in ["Mozzarella", "aji_chombo", "Harina 00", "Cebolla blanca", "Albahaca fresca"]:
            registrar(f"Alerta menciona '{s}'", s in cuerpo, "ausente")
        for bz in ["QUIEBRE", "DE MÁS", "OLVIDÓ"]:
            registrar(f"Badge '{bz}' presente", bz in cuerpo, "ausente")
        sin_excepciones(page, "Sin excepciones en Alertas")
        page.get_by_text("Ver tabla de alertas (con todos los campos)").click()
        page.wait_for_timeout(800)
        registrar("Tabla expandible de alertas", page.locator('[data-testid="stDataFrame"]').count() > 0)
        with page.expect_download() as dl:
            page.get_by_role("button", name="Descargar alertas (CSV)").click()
        registrar("Descarga CSV alertas", dl.value.suggested_filename.endswith(".csv"), dl.value.suggested_filename)

        # ===== D. Pestaña Matriz =====
        page.get_by_role("tab", name="Matriz").click(); page.wait_for_timeout(1500)
        # Streamlit dibuja los dataframes en canvas (sin texto en el DOM);
        # verificamos que el componente Styler se renderiza sin excepciones.
        n_df = page.locator('[data-testid="stDataFrame"]').count()
        registrar("Matriz: componente dataframe renderizado", n_df > 0, f"dataframes: {n_df}")
        registrar("Matriz: leyenda del semaforo", "Verde = correcto" in page.locator("body").inner_text())
        sin_excepciones(page, "Sin excepciones en Matriz")

        # ===== E. Pestaña Histórico =====
        page.get_by_role("tab", name="Histórico").click(); page.wait_for_timeout(1500)
        registrar("Historico: 2 selectboxes", page.locator('[data-testid="stSelectbox"]').count() >= 2)
        set_selectbox(page, 0, "Costa del Este"); page.wait_for_timeout(1200)
        set_selectbox(page, 1, "harina"); page.wait_for_timeout(2500)
        chart = page.locator('[data-testid="stArrowVegaLiteChart"]').count() + page.locator(".vega-embed").count()
        registrar("Historico: grafico visible", chart > 0, f"chart elements: {chart}")
        registrar("Historico: metricas detalle", page.locator('[data-testid="stMetric"]').count() >= 4)
        sin_excepciones(page, "Sin excepciones en Historico")

        # ===== F. Pestaña Chat (motor local) =====
        page.get_by_role("tab", name="Chat con IA").click(); page.wait_for_timeout(1000)
        ta = page.locator('[data-testid="stChatInputTextArea"]')
        registrar("Chat: textarea presente", ta.count() == 1)
        ta.fill("¿cuántas alertas hay?"); ta.press("Enter"); page.wait_for_timeout(2500)
        chat = " ".join(page.locator('[data-testid="stChatMessage"]').all_inner_texts())
        registrar("Chat: '¿cuántas alertas hay?'", "5 alertas" in chat, chat[:200])
        ta.fill("¿quién se olvidó de pedir mozzarella?"); ta.press("Enter"); page.wait_for_timeout(2500)
        chat = " ".join(page.locator('[data-testid="stChatMessage"]').all_inner_texts())
        registrar("Chat: '¿quién se olvidó mozzarella?'", "Mozzarella" in chat)
        ta.fill("resumen de las alertas"); ta.press("Enter"); page.wait_for_timeout(2500)
        chat = " ".join(page.locator('[data-testid="stChatMessage"]').all_inner_texts())
        registrar("Chat: 'resumen'", "5 alertas" in chat and "sucursales" in chat, chat[-200:])
        sin_excepciones(page, "Sin excepciones en Chat")

        # ===== G. Pestaña Proveedor =====
        page.get_by_role("tab", name="Pedido sugerido por proveedor").click(); page.wait_for_timeout(1500)
        df = page.locator('[data-testid="stDataFrame"]')
        registrar("Proveedor: tabla renderizada", df.count() > 0, f"dataframes: {df.count()}")
        registrar("Proveedor: titulo/descripcion", "pedido corregido" in page.locator("body").inner_text())
        with page.expect_download() as dl:
            page.get_by_role("button", name="Descargar pedido por proveedor (CSV)").click()
        registrar("Descarga CSV por proveedor", dl.value.suggested_filename.endswith(".csv"), dl.value.suggested_filename)
        sin_excepciones(page, "Sin excepciones en Proveedor")

        # ===== H. Recarga =====
        page.goto(URL); page.wait_for_timeout(3000)
        registrar("Recarga estado por defecto", valor_kpi_total(page) == "5", valor_kpi_total(page))
        sin_excepciones(page, "Sin excepciones al recargar")

        # ===== I. Filtro de sucursales + limpiar =====
        elegir_multiselect(page, "Marbella"); page.wait_for_timeout(2500)
        registrar("Filtrar 'Marbella' -> 0 alertas", valor_kpi_total(page) == "0", valor_kpi_total(page))
        sin_excepciones(page, "Sin excepciones con filtro")
        limpiar_multiselect(page); page.wait_for_timeout(2500)
        registrar("Limpiar filtro (X de chips) -> 5 alertas", valor_kpi_total(page) == "5", valor_kpi_total(page))

        browser.close()

    n_ok = sum(1 for _, ok, _ in RESULTADOS if ok)
    n_fail = len(RESULTADOS) - n_ok
    print("\n" + "=" * 64)
    print(f"RESULTADO: {n_ok} PASS / {n_fail} FAIL de {len(RESULTADOS)} checks")
    for nombre, ok, detalle in RESULTADOS:
        if not ok:
            print(f"  [FAIL] {nombre} {detalle}")
    print("=" * 64)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
