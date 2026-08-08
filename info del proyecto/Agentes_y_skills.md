# Agentes y habilidades (skills) utilizados en el proyecto

**Fecha:** 8 de agosto de 2026
**Versión:** 1.0
**Relacionado:** `PRD.md`, `Plan.md`, `Diseño.md`

---

## 1. Contexto

Este proyecto se desarrolló con ayuda de un asistente de IA (opencode) que
trabaja sobre el repositorio local. opencode usa un **agente principal** que
orquesta el trabajo y puede delegar en **subagentes** especializados y cargar
**skills** (habilidades reutilizables) para tareas concretas. Este documento
describe cómo se usaron.

## 2. Agentes

| Agente | Tipo | Qué hace en el proyecto |
| --- | --- | --- |
| **Agente principal** | opencode (asistente de IA) | Orquesta todo: lee el reto y los datos, diseña la arquitectura, escribe el código de `core/`, `app.py`, define el tema visual, corrige, testea y documenta. |
| **explore** | Subagente de búsqueda | Explora el codebase: ubica los CSV, los módulos `core/`, la estructura de pruebas y las partes donde tocar. Útil para entender el proyecto sin llenar la conversación principal de contexto. |
| **general / task** | Subagente de tareas | Ejecuta unidades de trabajo en paralelo o investiga temas puntuales (p. ej. confirmar el formato de los datos, revisar que no queden archivos sueltos). |

**Cómo se delegó:** el agente principal hizo el trabajo pesado; los subagentes
se usaron para búsquedas rápidas (localizar módulos, detectar convenciones,
mapear estructura) y para validar partes del entregable.

## 3. Agents vs. Skills en opencode

- **Agents**: "quiénes" trabajan (el agente rol).
- **Skills**: "qué saben hacer" (instrucciones + recursos recargados bajo demanda
  para una tarea, inyectadas solo cuando tocan).

## 4. Skills disponibles y su uso en el proyecto

| Skill | Cuándo se usa | Cómo aplica a este proyecto |
| --- | --- | --- |
| **frontend-design** | Crea/rediseña UI con intención visual. | Guía de la estética del dashboard (tickets/comandas, paleta de marca, tipografía, jerarquía visual). |
| **theme-factory** | Aplica/crea temas de color y tipografía a artefactos. | Paleta y fuentes de Barrio Pizza (Fraunces/Inter/JetBrains Mono) para dar consistencia. |
| **webapp-testing** | Prueba apps web locales con Playwright. | Correr y verificar el dashboard, capturas, y depurar la suite E2E. |
| **doc-coauthoring** | Escribe documentación de forma estructurada e iterativa. | Guía para crear PRD, Plan y Documento de diseño. |
| **claude-api** | Referencia de modelos LLM, parámetros y uso de API. | Útil para conectar el chat con los datos a un LLM (Groq) de forma correcta. |
| **brand-guidelines** | Aplica guías de marca a artefactos. | Lineamiento general para aplicar la marca del cliente (adaptado a Barrio, no a Anthropic). |

**No aplicaron** (pero están disponibles si se necesitan): `docx`, `pdf`, `pptx`,
`xlsx`, `canvas-design`, `internal-comms`, `mcp-builder`, `skill-creator`,
`slack-gif-creator`, `customize-opencode`, `algorithmic-art`, `web-artifacts-builder`.

## 5. Cómo se usó la IA en cada fase (resumen para el reto)

1. **Entendimiento del problema** → el agente principal leyó el reto y los CSV,
   y razonó el modelo de datos (unidades base vs. formatos).
2. **Pipeline / lógica** → escribió los módulos con el agente asistente;
   eligió heurística explicable (mediana/IQR) en vez de "promedio ciego".
3. **Dashboard** → diseñó la experiencia visual con la skill de frontend-design
   y la paleta de la marca.
4. **Chat + optimización** → chat local de reglas + opción LLM (Groq);
   búsqueda de componentes correctos con subagentes.
5. **Pruebas** → generó la suite E2E y la corrió con webapp-testing.
6. **Documentación** → escribió README, PRD, Plan y este documento con
   doc-coauthoring.

## 6. Limitaciones y decisiones

- La IA se usó **como asistente**; las decisiones de producto (qué alertas, qué
  redondeo, qué público) las definió el humano / el reto.
- El motor LLM del chat es opcional y gratuito; el motor local **no depende de
  API** para que el dashboard funcione siempre.
- Las skills solo se cargan cuando la tarea lo necesita (no inflaman el contexto
  por las dudas).