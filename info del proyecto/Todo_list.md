# Lista de trabajo completado — Dashboard de órdenes de compra · Barrio Pizza

**Fecha:** 8 de agosto de 2026
**Versión:** 1.0
**Relacionado:** `PRD.md`, `Plan.md`, `Diseño.md`, `Agentes_y_skills.md`

---

## 1. Estado general

| Área | Estado |
| --- | --- |
| Pipeline de datos | ✅ Completado |
| Dashboard Streamlit | ✅ Completado |
| Funcionalidades extra | ✅ Completado |
| Pruebas end-to-end | ✅ Completado (32 PASS / 0 FAIL) |
| Empaquetado Docker | ✅ Completado |
| Documentación | ✅ Completado (PRD, Plan, Diseño, Agentes, este Todo) |
| Publicación en la nube | 🔄 Pendiente (ver sección 9) |
| Video 3-5 min | 🔄 Pendiente |

---

## 2. Análisis y preparación (pre)

- [x] Leer el enunciado del reto (`reto-practicante-ia/README.md`).
- [x] Entender las reglas de entrega y la fecha límite (domingo 9/8, 11:59 p.m.).
- [x] Entender los 4 CSV y sus unidades (consumo/inventario en unidad base, órdenes en formatos).
- [x] Detectar casos emblemáticos: pepperoni atípico en Marbella (150 kg en S3
  vs ~28 en el resto), mozzarella olvidada en Brisas del Golf, `aji_chombo`
  desconocido en Costa del Este.
- [x] Decidir el stack: Streamlit + Docker + Playwright.

## 3. Pipeline de datos (`core/`)

- [x] `core/carga.py` — lectura de los 4 CSV.
- [x] `core/unidades.py` — conversión formatos ↔ unidad base (`unidad_base_por_formato`).
- [x] `core/proyeccion.py` — proyección de consumo de la semana 7:
  - [x] Método robusto (sin outliers, regla de Tukey 1.5×IQR). **Recomendado.**
  - [x] Promedio simple (media de las 6 semanas).
  - [x] Con tendencia (regresión lineal proyectada a semana 7).
- [x] `core/alertas.py` — necesidad real = proyección − inventario; generación de alertas:
  - [x] Riesgo de quiebre.
  - [x] Sobre-pedido.
  - [x] Se olvidó.
  - [x] Ingrediente desconocido.
  - [x] Regla de redondeo (excedente < 1 formato no genera alerta; recomendado con ceil).

## 4. Dashboard Streamlit

- [x] `app.py` — estructura principal con sidebar, KPIs y pestañas.
- [x] Barra lateral: método de proyección, filtro de sucursal, toggle cursor de pizza.
- [x] Pestaña de alertas como **comandas**.
- [x] Pestaña matriz.
- [x] Pestaña histórico.
- [x] Pestaña chat.
- [x] Pestaña por proveedor (pedido corregido agrupado para reenviar).
- [x] Descarga de CSV.
- [x] Filtro por sucursal.

## 5. Identidad visual (`core/tema.py`)

- [x] Paleta "mostrador a mediodía" (harina #FBF8F1, tomate #B5331F, albahaca #5F7A3A,
  oro #BF8A2C, azulejo #3E6B8A, tinta #241F1B).
- [x] Tipografía Fraunces / Inter / JetBrains Mono.
- [x] Logos reales incrustados en base64.
- [x] Cabecera de marca + cinta animada "SI HAY PIZZA" (respeta `prefers-reduced-motion`).
- [x] Comandas/alertas con sellos inclinados por tipo (QUIEBRE / DE MÁS / OLVIDÓ / ¿?).
- [x] Cursor de pizza (SVG, "muerde" al hacer clic, apagable).
- [x] Tema base en `.streamlit/config.toml`.
- [x] Adaptación al comportamiento actual de Streamlit (`st.html` con shadow DOM → bloques
  autocontenidos con su `<style>`).

## 6. Chat con los datos (`core/chat.py`)

- [x] Motor local (sin API): reglas en español que responden con las alertas calculadas.
- [x] Motor LLM opcional (Groq gratuito, requiere API key).

## 7. Pruebas

- [x] Suite end-to-end en `tests/e2e_test.py` (Playwright).
- [x] Cobertura: KPIs, cambio de método de proyección, todas las pestañas,
  descargas de CSV, filtro por sucursal y chat.
- [x] Resultado esperado/verificado: **32 PASS / 0 FAIL**.

## 8. Empaquetado y ejecución

- [x] `Dockerfile`.
- [x] `docker-compose.yml` (puerto 8501).
- [x] `requirements.txt`.
- [x] `.gitignore` / `.dockerignore`.
- [x] Instructivo en README para correr local y con Docker.

## 9. Pendiente para la entrega

- [ ] Publicar la app en un servicio gratuito (Streamlit Community Cloud /
  Hugging Face Spaces) y **probar el link en modo incógnito**.
- [ ] Grabar video de 3-5 min (recorrido del dashboard + razonamiento) y compartir link.
- [ ] Subir el repo a GitHub.
- [ ] Revisar fecha límite: domingo 9/8, 11:59 p.m.