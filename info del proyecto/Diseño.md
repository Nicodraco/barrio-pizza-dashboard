# Documento de Diseño — Dashboard de órdenes de compra · Barrio Pizza

**Fecha:** 8 de agosto de 2026
**Versión:** 1.0
**Relacionado:** `PRD.md`, `Plan.md`, `Agentes_y_skills.md`, `Todo_list.md`

---

## 1. Propósito del documento

Describir el diseño visual y de interacción del dashboard. No es un mockup: es
la fuente de verdad de cómo se ve y se comporta la herramienta, usando la
identidad real de **Barrio Pizza Panamá** ("SI HAY PIZZA · del barrio y para el
barrio", desde 2015, pizzas napolitanas).

## 2. Identidad de marca

- **Logos reales**: `assets/logo_negro.png` y `assets/logo_blanco.png`,
  incrustados como data URI (base64) para no depender de rutas externas.
- **Frase/insignia**: "SI HAY PIZZA · DEL BARRIO Y PARA EL BARRIO · SUPPORT
  YOUR LOCAL BARRIO · #TEAMBARRIO".
- **Sonido**: napolitano, mostrador de barrio, artesanal — no corporativo.

## 3. Paleta de color "Mostrador a mediodía"

| Rol | Color | Código | Uso |
| --- | --- | --- | --- |
| Harina (fondo) | Crema | `#FBF8F1` / `#FFFDF8` | Fondos de página y tarjetas |
| Tomate San Marzano | Rojo | `#B5331F` | Acentos, alertas de quiebre |
| Albahaca | Verde | `#5F7A3A` | Detalles frescos |
| Oro de corteza | Ámbar | `#BF8A2C` | Sobre-pedido, bordes |
| Azulejo panameño | Azul | `#3E6B8A` | Frescos, "se olvidó" |
| Tinta | Marrón oscuro | `#241F1B` | Texto principal |
| Piel/soporte | Tonos suaves | `#8B857A`, `#E7DFCF` | Textos secundarios, bordes |

## 4. Tipografía

| Fuente | Uso |
| --- | --- |
| **Fraunces** (serif, 400–900 + itálica) | Títulos display (encabezado, títulos de comanda) |
| **Inter** (sans) | UI, párrafos, mensajes de alerta |
| **JetBrains Mono** (mono) | Números, etiquetas, pies, badges (look de ticket) |

Se cargan vía Google Fonts (`@import`) en cada bloque `st.html`.

## 5. Layout y componentes

### 5.1 Encabezado
- Logotipo negro a la izquierda (altura 112 px).
- Eyebrow en JetBrains Mono mayúsculas: "CONTROL DE ÓRDENES DE COMPRA · PANAMÁ,
  DESDE 2015".
- Título display Fraunces 900: **SI HAY PIZZA —** con acento itálico en
  "del barrio y para el barrio".
- A la derecha: chip "SEMANA 7 · PROYECCIÓN `<método>`" con borde punteado.

### 5.2 Cinta "SI HAY PIZZA"
- Marquee animado (marquesina) entre dos bordes tinta, con la frase repetida y
  la palabra destacada en rojo.
- **Accesibilidad**: con `prefers-reduced-motion` la animación se detiene y el
  contenido se reacomoda en varias líneas centradas.

### 5.3 Comandas de alerta (el corazón visual)
Cada alerta se renderiza como un **ticket o comanda** con:

- **Encabezado**: sucursal en mono + **sello** inclinado (−4°) por tipo:
  | Tipo | Sello | Modificador |
  | --- | --- | --- |
  | RIESGO QUIEBRE | "QUIEBRE" | tomate (`tomato`) |
  | SOBRE-PEDIDO | "DE MÁS" | oro (`gold`) |
  | SE OLVIDO | "OLVIDÓ" | azulejo (`azulejo`) |
  | INGREDIENTE DESCONOCIDO | "¿?" | piedra (`stone`) |
- **Título**: nombre del ingrediente en Fraunces.
- **Cuerpo**: cuadrícula (`comanda-grid`) de 4 celdas monoespaciadas y numeradas:
  Pedido · Proyección · Stock hoy · Recomendado.
- **Mensaje**: frase clara y accionable en Inter.
- **Pie**: proveedor + badge de frescura ("perecible·frío" los frescos en
  azulejo).
- Sombra suave, bordes redondeados y secciones separadas por líneas punteadas
  (efecto de ticket).

### 5.4 Cursor de pizza
- El puntero del sistema se reemplaza por una **rebanada de pizza** (SVG
  embebido como data URI): masa, queso fundido, pepperoni y albahaca.
- Al hacer clic, la rebanada aparece **mordida** (variante con bocado).
- Apagable desde la sidebar (toggle "Cursor de pizza").

## 6. Interacción y estado

- **Barra lateral** (widgets nativos de Streamlit, tema base):
  - Método de proyección: Robusto (sin outliers) / Promedio simple / Con
    tendencia.
  - Filtro por sucursal.
  - Toggle del cursor de pizza.
- **Pestañas principales**: Alertas · Matriz · Histórico · Chat · Por proveedor.
- **Descarga de CSV** en cada vista.
- KPIs de resumen al inicio para ver el estado de un vistazo.

## 7. Accesibilidad

- `prefers-reduced-motion` detiene la marquesina.
- Alto contraste entre fondos crema y tinta.
- Textos secundarios y badges legibles en mono y tamaños controlados.
- El cursor de pizza es opt-in (toggle), preservando el cursor nativo por defecto
  cuando se desactiva.

## 8. Implementación técnica

- **Tema base**: `.streamlit/config.toml` (Theme) define colores para widgets
  nativos.
- **Bloques de marca**: `core/tema.py` genera HTML autocontenido por bloque
  (encabezado+cinta, comandas, pie), cada uno con su propio `<style>`.
  - **Nota de Streamlit**: en esta versión, `st.markdown` elimina las etiquetas
    `<style>` y `st.html` aísla el contenido en shadow DOM. Por esto cada bloque
    es una sola llamada `st.html` con su CSS dentro.
- **Logos**: incrustados en base64 (data URI) para no depender de rutas.

## 9. Decisiones de diseño

- Alertas como **comandas físicas**: conecta con el mundo de la pizzadería y
  hace las alertas legibles de un vistazo.
- **Sellos rotados** en colores de la paleta: estado visual inmediato sin leer.
- **Números en monoespaciado**: comparaciones de Pedido/Proyección/Stock
  alineadas como en una factura.
- Ningún dato crudo: la gerente ve tickets, no tablas.

## 10. Futuras mejoras de diseño (backlog)

- Modo oscuro con paleta "horno de noche".
- Versión responsive para tablet del local.
- Exportar recibo de pedido corregido (imprimible por proveedor).
- Iconografía de marca adicional (albahaca, horno, azulejo panameño).