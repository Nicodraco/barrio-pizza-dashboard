# Dashboard de órdenes de compra · Barrio Pizza

Herramienta construida para la **práctica de IA en Barrio Pizza**: revisa las
órdenes de compra de la semana de cada sucursal y detecta automáticamente si
están **pidiendo de más, de menos o se olvidaron de algo**, comparando contra el
consumo proyectado y el inventario actual.

## Cómo correrlo con Docker (recomendado)

El proyecto incluye `Dockerfile` y `docker-compose.yml`. Desde la carpeta del
proyecto:

```bash
docker compose up --build
```

Abrir `http://localhost:8501`.

Para controlar el contenedor:

```bash
docker compose stop     # detiene; la página deja de responder
docker compose start    # vuelve a levantar
```

> ⚠️ No levantes a la vez `streamlit run app.py` local y Docker: ambos usan el
> puerto 8501 y se pelean. Usa solo uno. Para el contenedor sólo debe haber un
> proceso en `8501` (el de Docker).

## Cómo correrlo en local (sin Docker)

1. Clonar o descargar este repo.
2. Crear un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Correr la app:

   ```bash
   streamlit run app.py
   ```

5. Abrir la URL que muestra (por defecto `http://localhost:8501`).

> Los 4 CSV de datos ya están en `datos/`. No hace falta nada más.

## Diseño (identidad visual Barrio Pizza)

El dashboard sigue la marca real de Barrio Pizza Panamá ("SI HAY PIZZA · del
barrio y para el barrio", desde 2015, pizzas napolitanas).

- **Marca**: usa los logos reales (`assets/logo_negro.png`, `assets/logo_blanco.png`)
  incrustados como data URI, más la cinta animada "SI HAY PIZZA • DEL BARRIO •"
  (se pausa con `prefers-reduced-motion`).
- **Paleta "mostrador a mediodía"**: harina `#FBF8F1`, tomate san marzano
  `#B5331F`, albahaca `#5F7A3A`, oro de corteza `#BF8A2C`, azulejo panameño
  `#3E6B8A`, tinta `#241F1B`.
- **Tipografía**: Fraunces (display), Inter (UI), JetBrains Mono (números).
- **Alertas como "comandas"**: cada alerta se muestra como un ticket con cifras
  monoespaciadas y un sello inclinado por estado (QUIEBRE / DE MÁS / OLVIDÓ).
- **Cursor de pizza**: el puntero es una rebanada dibujada con la paleta de la
  marca (puede apagarse con el toggle "Cursor de pizza" en la sidebar); al
  presionar el clic la rebanada aparece mordida. Son SVGs incrustados como
  data-URI en un `<style>` global vía `st.html` (en esta versión de Streamlit,
  `st.html` ya no usa shadow DOM, así que el CSS aplica a toda la app).
- Cómo está hecho: el tema base vive en `.streamlit/config.toml` y los bloques de
  marca en `core/tema.py`. Nota técnica: esta versión de Streamlit elimina los
  `<style>` de `st.markdown` y aísla `st.html` en un shadow DOM, por eso cada
  bloque (encabezado + cinta, y comandas) se entrega como un `st.html`
  autocontenido con su propio `<style>`, y el logo se incrusta en base64.

## Qué hace

1. **Proyecta** el consumo de la próxima semana por (sucursal, insumo) usando las
   6 semanas de histórico.
2. Calcula la **necesidad real** = consumo proyectado − inventario actual.
3. Convierte la necesidad a **formatos completos de compra** (ceil) y la compara
   contra la orden de la semana.
4. Genera **alertas** en lenguaje claro, por tipo:
   - **Riesgo de quiebre**: pidió menos de lo proyectado (por al menos un formato).
   - **Sobre-pedido**: pidió de más (por al menos un formato).
   - **Se olvidó**: no incluyó un insumo que sí necesita.
   - **Ingrediente desconocido**: pidió algo que no está en el catálogo.

Incluye un **chat con los datos**: escribes una pregunta en español y la
herramienta responde sobre las órdenes de la semana (motor local sin API, o
conectable a un LLM gratuito vía Groq).

## Métodos de proyección

En la barra lateral puedes elegir:

| Método | Qué hace |
| --- | --- |
| **Robusto (sin outliers)** | Media de las semanas normales; detecta y excluye semanas atípicas (regla de Tukey, 1.5×IQR). Recomendado. |
| **Promedio simple** | Media de las 6 semanas. |
| **Con tendencia** | Regresión lineal sobre semanas normales proyectada a la semana 7 (capta crecimiento, ej. harina en Costa del Este). |

## Supuestos y decisiones

- **Unidades**: consumo e inventario vienen en unidad base (kg, L, und); las
  órdenes vienen en **formatos**. Se convierten con `unidad_base_por_formato`
  de `ingredientes.csv`.
- **Redondeo**: solo se compran formatos completos. Un excedente menor a un
  formato se considera redondeo normal y **no** genera alerta. La necesidad se
  redondea hacia arriba (ceil) para el "recomendado".
- **Semanas atípicas**: Marbella/pepperoni tiene un valor de 150 kg en S3 vs ~28
  en las demás; la proyección robusta lo excluye.
- **Se olvidó**: si una sucursal tiene consumo > 0 y stock insuficiente pero su
  orden no incluye el insumo (p. ej. mozzarella en Brisas del Golf), se marca.
- **Ingrediente desconocido**: `aji_chombo` aparece en la orden de Costa del Este
  pero no está en el catálogo → se alerta para revisión manual.
- **Inventario cubre todo**: si la necesidad real es ≤ 0 y aún así piden, se
  marca sobre-pedido.

## Cómo probarlo (Playwright)

El proyecto incluye una suite de pruebas end-to-end que recorre **todas** las
funcionalidades en un navegador real (KPIs, cambio de método de proyección,
pestañas de alertas/matriz/histórico/chat/proveedor, descargas de CSV, filtro de
sucursales y chat con IA).

```bash
# 1. Con la app corriendo (streamlit run app.py):
pip install -r requirements.txt
python -m playwright install chromium

# 2. Correr las pruebas:
python tests/e2e_test.py
```

Resultado esperado: `32 PASS / 0 FAIL`.

Nota: los `st.dataframe` de Streamlit se dibujan en canvas (Glide Data Grid), por
lo que su contenido no es accesible por el DOM; en esas pestañas la prueba
verifica que el componente se renderiza sin excepciones y la exactitud de los
datos se valida a nivel de datos (los CSV descargables contienen el contenido
completo).

## Documentación del proyecto

En la carpeta `info del proyecto/` se documentan los requisitos, el plan y el
detalle del proyecto:

| Documento | Qué contiene |
| --- | --- |
| `PRD.md` | Requisitos del producto (problema, usuarios, alcance, alertas, Odoo). |
| `Plan.md` | Plan del proyecto: fases, cronograma, entregables, riesgos y criterios de éxito. |
| `Diseño.md` | Identidad visual: paleta, tipografía, layout y decisiones de diseño. |
| `Agentes_y_skills.md` | Agentes y habilidades (skills) de IA usados en el desarrollo. |
| `Todo_list.md` | Lista de trabajo completado y pendiente para la entrega. |

## Cómo se usó IA en este proyecto

1. **Asistente de código**: la solución se desarrolló con ayuda de una IA
   (opencode/Claude) para estructura, lógica y el dashboard.
2. **Proyección**: heurística propia y explicable (mediana/IQR) en lugar de un
   promedio ciego — elegida porque es transparente para la gerente de compras.
3. **Chat con los datos**:
   - Motor **local** (sin API): reglas en español que responden usando las
     alertas ya calculadas.
   - Motor **LLM**: opcional, conecta un modelo gratuito (Groq) enviándole el
     contexto de datos calculado. Requiere una API key gratuita de
     `console.groq.com`.

## Cómo conectar esto a Odoo en producción

En la vida real las órdenes viven en Odoo (módulo Compras). La integración sería:

1. **Extraer datos** de Odoo vía su API XML-RPC o JSON-RPC (`odoo.models`):
   - Consumo: órdenes de entrega de los últimos 6 períodos por producto.
   - Inventario: stock actual por ubicación (módulo Inventario).
   - Órdenes pendientes de la semana (módulo Compras).
2. **Ejecutar este mismo pipeline** (proyección → necesidad → alertas) sobre los
   datos en vivo en vez de los CSV.
3. **Acciones en Odoo**:
   - Marcar las líneas de la orden como "requieren revisión" con un campo booleano.
   - Enviar notificaciones por correo a la gerente de compras con las alertas.
   - Con un *server action* o *scheduled action*, sugerir el pedido corregido y
     crearlo como borrador (`purchase.order`) listo para aprobar.

## Estructura

```
├── app.py                 # Dashboard Streamlit
├── Dockerfile             # Imagen para Docker
├── docker-compose.yml     # Orquesta del contenedor (puerto 8501)
├── .streamlit/config.toml # Tema base (colores de marca)
├── assets/                # Logos reales de Barrio Pizza
├── core/
│   ├── carga.py           # Lectura de los 4 CSV
│   ├── unidades.py        # Conversión formatos ↔ unidad base
│   ├── proyeccion.py      # Proyección robusta a outliers
│   ├── alertas.py         # Necesidad real y generación de alertas
│   ├── chat.py            # Chat con los datos (local + LLM)
│   └── tema.py            # Identidad visual: encabezado, cinta y comandas
├── tests/
│   └── e2e_test.py        # Pruebas end-to-end (Playwright, 32 checks)
├── datos/                 # 4 CSV del reto
├── info del proyecto/     # Documentación: PRD, Plan, Diseño, Agentes, Todo
└── requirements.txt
```
