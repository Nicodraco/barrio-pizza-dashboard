# PRD — Dashboard de órdenes de compra · Barrio Pizza

**Documento de Requisitos del Producto (PRD)**
**Fecha:** 8 de agosto de 2026
**Estado:** En desarrollo (para entrega de práctica de IA)

---

## 1. Resumen ejecutivo

Barrio Pizza es una cadena de pizzerías con 10 sucursales en Panamá. Cada
semana, cada sucursal arma su orden de compra de insumos. Hoy esas órdenes se
aprueban "al ojo" por la gerente de compras: es lento y propenso a errores. A
veces piden de más (dinero inmovilizado, comida que se vence) y a veces de menos
(se quedan sin producto en pleno servicio).

Se construirá una **herramienta visual (dashboard)** que revise automáticamente
las órdenes de compra de la semana y muestre alertas claras: ¿piden de más,
piden de menos, u olvidaron algo?

## 2. Problema

- Las órdenes de compra de 10 sucursales se evalúan manualmente, una por una.
- Revisar producto por producto consume mucho tiempo de la gerente de compras.
- Los errores humanos en la revisión provocan quiebres de stock o sobre-stock.

## 3. Motivación y visión

La visión final: la gerente carga todas las órdenes de la semana y la
herramienta arroja las alertas al instante, sin revisar producto por producto.

Este reto pide construir un dashboard para **4 sucursales** con datos dados,
pero reflejando esa visión final. En producción, las órdenes vivirían en **Odoo**
(módulo Compras) y el mismo pipeline correría sobre datos en vivo.

## 4. Usuarios

| Usuario | Necesidad |
| --- | --- |
| **Gerente de compras** | Aprobar/revisar órdenes de la semana de todas las sucursales en minutos, con alertas accionables. |
| **Evaluadores del reto** | Ver una solución que funciona, clara, razonada y con buen manejo de datos. |

## 5. Datos

4 archivos CSV, ya incluidos en `datos/`:

| Archivo | Qué contiene |
| --- | --- |
| `ingredientes.csv` | Catálogo: proveedor, unidad base, formato de compra (ej. "Saco 25 kg"), unidad base por formato y si es perecedero. |
| `consumo_historico.csv` | Consumo real de cada sucursal por ingrediente en las **últimas 6 semanas**. |
| `inventario_actual.csv` | Stock actual (unidad base) de cada ingrediente por sucursal. |
| `orden_compra_semana.csv` | Lo que cada sucursal pide esta semana, en **formatos** (ej. `3` = 3 sacos). |

**Ojo con las unidades:** consumo e inventario están en unidad base (kg, L,
unidades); las órdenes están en **formatos**. Hay que convertir con
`unidad_base_por_formato` de `ingredientes.csv`.

## 6. Requisitos funcionales

### 6.1 Mínimos (obligatorios)

1. **Proyección de consumo** de la próxima semana por (sucursal, insumo) usando
   las 6 semanas de histórico.
2. **Necesidad real** = consumo proyectado − inventario actual.
3. **Comparación con la orden** y generación de **alertas claras y accionables**,
   en el estilo:
   > *"ALERTA: <sucursal> está pidiendo <cantidad> <unidad> de <ingrediente>
   > menos que lo proyectado → riesgo de quiebre."*
4. **Dashboard visual**: las alertas visibles de un vistazo, sin leer tablas
   crudas. Pensado para la gerente de compras.

### 6.2 Tipos de alerta

| Alerta | Qué detecta |
| --- | --- |
| **Riesgo de quiebre** | Pidió menos de lo proyectado (al menos un formato). |
| **Sobre-pedido** | Pidió de más (al menos un formato). |
| **Se olvidó** | Consumo > 0 y stock insuficiente pero el insumo no está en la orden. |
| **Ingrediente desconocido** | Pidió algo que no está en el catálogo (ej. `aji_chombo` en Costa del Este). |

### 6.3 Funcionalidades extra implementadas

- **Chat con los datos:** preguntas en español; responde sobre las órdenes de la
  semana. Motor **local** (reglas, sin API) o **LLM gratuito** vía Groq (opcional).
- **Métodos de proyección selectables:** robusto (sin outliers), promedio simple,
  y con tendencia (regresión lineal).
- **Pestañas:** alertas, matriz, histórico, chat, vista por proveedor.
- **Descarga de CSV** y **filtro por sucursal**.
- **Identidad visual Barrio Pizza:** marca real (logos en data URI), paleta de
  marca, tipografías, alertas como "comandas" (tickets) con sellos, cursor de pizza.
- **Organizar pedido corregido por proveedor** (para reenviar a cada proveedor).
- **Pruebas end-to-end** con Playwright (32 checks).

## 7. Requisitos no funcionales

| Categoría | Requisito |
| --- | --- |
| **Manejo de unidades** | Conversión correcta formatos ↔ unidad base. |
| **Redondeo** | Solo se compran formatos completos. Excedente menor a un formato = redondeo normal, **sin** alerta. Necesidad se redondea hacia arriba (ceil) para el recomendado. |
| **Datos incompletos** | Detección de ingredientes desconocidos, semanas atípicas (regla de Tukey, 1.5×IQR) y stocks insuficientes. |
| **Rendimiento** | Respuesta instantánea al revisar la semana completa. |
| **Usabilidad** | La gerente no debe leer código ni tablas crudas. |
| **Accesibilidad** | Reduce animaciones con `prefers-reduced-motion`. |
| **Seguridad** | API key de Groq opcional; el motor local no requiere API. |

## 8. Storyboard / flujo del usuario

1. Abre el dashboard (`http://localhost:8501`).
2. Ve el resumen de **KPIs** y las **alertas** como "comandas".
3. Cambia el **método de proyección** en la barra lateral y ve las alertas actualizarse.
4. Filtra por **sucursal**.
5. Hace **preguntas en el chat** en español y obtienes respuestas sobre las órdenes.
6. Descarga los **CSV** / ve el pedido **por proveedor**.

## 9. Método de proyección

| Método | Qué hace | Nota |
| --- | --- | --- |
| **Robusto (sin outliers)** | Media de las semanas normales; excluye semanas atípicas (Tukey, 1.5×IQR). | Recomendado. |
| **Promedio simple** | Media de las 6 semanas. | |
| **Con tendencia** | Regresión lineal sobre semanas normales proyectada a la semana 7. | Capta crecimiento (ej. harina en Costa del Este). |

## 10. Supuestos y decisiones clave

- **Unidades:** como las órdenes vienen en formato, se requiere conversión.
- **Redondeo:** excedente menor a un formato completo = redondeo, no alerta.
- **Semanas atípicas:** Marbella/pepperoni tiene 150 kg en S3 vs ~28 usuales → excluido en robusto.
- **"Se olvidó":** mozzarella en Brisas del Golf (hay consumo > 0, stock insuficiente, no pedido).
- **"Ingrediente desconocido":** `aji_chombo` en Costa del Este no está en catálogo → alerta para revisión manual.
- **Inventario cubre todo:** si la necesidad real ≤ 0 y aún así piden → sobre-pedido.

## 11. Stack técnico

- **Frontend/App:** Streamlit (Python), tema vía `.streamlit/config.toml` y `core/tema.py`.
- **Lógica:** `core/` con módulos de carga, unidades, proyección, alertas, chat y tema.
- **Despliegue:** Docker (`Dockerfile` + `docker-compose.yml`, puerto 8501) o Streamlit Community Cloud.
- **Pruebas:** Playwright (Python) — `tests/e2e_test.py`, 32 checks.
- **Datos:** 4 CSV de ejemplo en `datos/`.

## 12. Estructura del código

```
├── app.py                 # Dashboard Streamlit
├── Dockerfile
├── docker-compose.yml
├── .streamlit/config.toml  # Tema base
├── assets/                 # Logos reales de Barrio Pizza
├── core/
│   ├── carga.py            # Lectura de los 4 CSV
│   ├── unidades.py         # Conversión formatos ↔ unidad base
│   ├── proyeccion.py       # Proyección robusta
│   ├── alertas.py          # Necesidad real y alertas
│   ├── chat.py             # Chat (local + LLM)
│   └── tema.py             # Identidad visual
├── tests/e2e_test.py       # Playwright (32 checks)
├── datos/                  # 4 CSV del reto
└── requirements.txt
```

## 13. Integración con Odoo (producción)

1. **Extraer datos** de Odoo vía XML-RPC/JSON-RPC: consumo (órdenes de entrega de
   los últimos 6 períodos), inventario (stock actual) y órdenes pendientes (Compras).
2. **Ejecutar el mismo pipeline** (proyección → necesidad → alertas) sobre los
   datos en vivo.
3. **Acciones en Odoo:** marcar líneas de orden con "requieren revisión", enviar
   notificaciones por correo a la gerente, y con un *server/scheduled action*
   sugerir el pedido corregido como `purchase.order` borrador listo para aprobar.

## 14. Entregables del reto

1. **Repo de GitHub** con el código + README.
2. **Video de 3-5 min** mostrando su funcionamiento y razonamiento.
3. **App en vivo** publicada (Streamlit Community Cloud / Hugging Face Spaces).
   Probar en incógnito antes de enviar.
4. **Explicación del uso de IA** (asistente de código, proyección heurística,
   chat local + LLM).

## 15. Riesgos y consideraciones

- **Dataframes de Streamlit en canvas:** los `st.dataframe` se dibujan en un
  canvas (Glide Data Grid), cuyo contenido no es accesible desde el DOM; las
  pruebas se validan a nivel de datos (CSV), no del DOM.
- **Puerto 8501:** no levantar Streamlit local y Docker a la vez (compiten por el puerto).
- **Costo del LLM:** se usa un modelo gratuito (Groq); el motor local es el predeterminado.
- **Fecha límite:** domingo 9 de agosto, 11:59 p.m.