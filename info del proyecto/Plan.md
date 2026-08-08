# Plan del Proyecto — Dashboard de órdenes de compra · Barrio Pizza

**Fecha:** 8 de agosto de 2026
**Versión:** 1.0
**Relacionado:** `PRD.md`, `Diseño.md`, `Agentes_y_skills.md`, `Todo_list.md`

---

## 1. Objetivo

Entregar un dashboard que revise automáticamente las órdenes de compra de la
semana de las sucursales y marque alertas (quiebre / sobre-pedido / olvidó),
dentro de la fecha límite del reto (domingo 9 de agosto, 11:59 p.m.), con una
app publicada y todo lo que se pide en la entrega.

## 2. Alcance

**En alcance**
- Dashboard Streamlit con alertas visuales (comandas).
- Proyección de consumo (robusto, promedio, tendencia).
- Chat con los datos (motor local + LLM opcional vía Groq).
- Vista por proveedor, filtro por sucursal, descarga CSV.
- Identidad visual Barrio Pizza.
- Pruebas end-to-end con Playwright.
- Empaquetado con Docker + publicación en la nube.

**Fuera de alcance**
- Integración real con Odoo (se documenta, no se codea).
- Módulo de autenticación / multiusuario.
- Escritura de órdenes de vuelta al sistema.

## 3. Fases del plan

| Fase | Entregable | Estado |
| --- | --- | --- |
| 1. Entendimiento y datos | Leer reto, entender los 4 CSV y unidades. | ✅ Hecho |
| 2. Pipeline de datos | `core/`: carga, unidades, proyección, alertas. | ✅ Hecho |
| 3. Dashboard UI | `app.py` + tema visual (identidad de marca). | ✅ Hecho |
| 4. Extra (chat, proveedor, filtros) | Chat local/LLM, pestañas extras. | ✅ Hecho |
| 5. Pruebas | Playwright 32 checks PASS. | ✅ Hecho |
| 6. Empaquetado | Dockerfile + docker-compose. | ✅ Hecho |
| 7. Documentación y entrega | README, PRD, Plan, Diseño, Agentes, video, publicación. | 🔄 En curso |

## 4. Cronograma

| Día | Actividad | Meta |
| --- | --- | --- |
| 1 | Leer reto, analizar datos y unidades. | Comprensión clara del problema. |
| 2 | Pipeline de proyección y alertas. | Resultados correctos a nivel datos. |
| 3 | Dashboard visual con marca. | Primer vistazo usable. |
| 4 | Chat, extras y pruebas E2E. | 32 PASS / 0 FAIL. |
| 5 | Docker y despliegue en la nube. | Link público funcionando. |
| 6 | Video 3-5 min, README final, PRD, Plan y Diseño. | Entrega completa el domingo 9/8. |

## 5. Entregables

1. **Código completo** en GitHub.
2. **README** en la raíz (cómo correrlo, supuestos).
3. **App publicada** (contenido/espacio en la nube), probada en incógnito.
4. **Video de 3-5 min** (Loom o similar): recorrido + razonamiento.
5. **Docs de proyecto**: carpeta `info del proyecto/` (PRD, Plan, Diseño,
   Agentes y skills, Todo).

## 6. Plan de pruebas

- **Unitarias/lógica:** validar cálculo de proyección, necesidad y alertas.
- **End-to-end (Playwright):** KPIs, cambio de método, pestañas, descargas,
  filtro y chat.
- **Resultado esperado:** `32 PASS / 0 FAIL`.

## 7. Cómo se usará IA

1. Asistente de código (opencode/Claude) para estructura y lógica.
2. Heurística propia (mediana/IQR) para proyección explicable.
3. Chat local con los datos + opción de LLM gratuito vía Groq.

## 8. Riesgos y plan de mitigación

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Plazo de entrega ajustado (9/8) | Entrega fuera de tiempo | Fases completas primero; foco en lo esencial. |
| Conflicto de puerto 8501 (local/Docker) | App no carga | Usar solo un método para abrir la app. |
| Streamlit `st.dataframe` en canvas | Pruebas de DOM fallizan | Validar por datos/CSV, no por DOM. |
| Costo de LLM | Dependencia | Motor local por defecto; Groq gratuito opcional. |

## 9. Criterios de éxito

- El dashboard detecta correctamente los casos del reto (por lo menos: quiebre de harina/pepperoni, mozzarella olvidada, `aji_chombo` desconocido).
- Alguien sin contexto lo abre y entiende las alertas de un vistazo.
- Pasa las 32 pruebas E2E.
- Todo el repositorio + publicación funcionando antes del 9/8 11:59 p.m.