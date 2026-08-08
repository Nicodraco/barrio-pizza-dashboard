"""Chat con los datos: el usuario pregunta en español y recibe respuesta.

Dos modos:
- "local":  motor de reglas que analiza las alertas calculadas (no requiere API).
- "llm":    usa un LLM gratuito (Groq) con los datos como contexto. Requiere una
            API key de Groq (console.groq.com, plan free).
"""
import re
import unicodedata

import pandas as pd


def norm(s):
    """Minúsculas, sin acentos y sin puntuación para comparar texto en español."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


SINONIMOS = {
    "harina": ["Harina 00", "Harina gluten free"],
    "queso": ["Mozzarella", "Queso vegano", "Parmesano"],
    "salsa": ["Salsa pelatti"],
    "tomate": ["Salsa pelatti"],
    "champinon": ["Hongos"],
    "hongo": ["Hongos"],
    "cebolla": ["Cebolla blanca"],
    "pimiento": ["Pimentón"],
    "peperoni": ["Pepperoni"],
    "jamon": ["Jamón"],
    "aceite": ["Aceite de oliva"],
    "oliva": ["Aceite de oliva"],
    "aceituna": ["Aceitunas"],
    "albahaca": ["Albahaca fresca"],
    "arugula": ["Arugula"],
    "rucula": ["Arugula"],
    "caja": ["Cajas de pizza"],
    "pina": ["Piña"],
    "prosciutto": ["Prosciutto"],
}


# --------------------------------------------------------------------------
# Motor local (sin API)
# --------------------------------------------------------------------------

def _filtrar_sucursal(df, suc):
    return df[df["sucursal"] == suc] if suc else df


def _mencionadas(pregunta, detalle):
    """Nombres de ingredientes mencionados en la pregunta (exactos, parciales o sinónimos)."""
    nombres = sorted(detalle["nombre"].dropna().unique(), key=len, reverse=True)
    tokens = [w for w in norm(pregunta).split() if len(w) >= 4]
    encontrados = []
    for n in nombres:
        nl = n.lower()
        if nl in norm(pregunta) or any(t in nl for t in tokens):
            encontrados.append(n)
    for t in tokens:
        for ing in SINONIMOS.get(t, []):
            if ing in nombres and ing not in encontrados:
                encontrados.append(ing)
    # mantener el orden original del catálogo para priorizar el nombre más específico
    orden = {n: i for i, n in enumerate(detalle["nombre"].dropna().unique())}
    return sorted(encontrados, key=lambda n: orden.get(n, 0))


def _lineas_tipo(df, tipo):
    filas = df[df["tipo"] == tipo]
    if filas.empty:
        return "Ninguna."
    return "\n".join(f"- {r['sucursal']} · {r['nombre']}: {r['mensaje']}" for _, r in filas.iterrows())


def _por_tipo(resultado, tipo, suc=None, menciones=None):
    """Subconjunto de alertas por tipo, con filtros de sucursal e insumo."""
    sub = resultado["alertas"][resultado["alertas"]["tipo"] == tipo]
    if suc:
        sub = sub[sub["sucursal"] == suc]
    if menciones:
        sub = sub[sub["nombre"].isin(menciones)]
    return sub


def _otras_alertas(resultado, tipo, suc=None, menciones=None):
    """Texto de las alertas que NO son de un tipo, para contexto en respuestas."""
    sub = resultado["alertas"][resultado["alertas"]["tipo"] != tipo]
    if suc:
        sub = sub[sub["sucursal"] == suc]
    if menciones:
        sub = sub[sub["nombre"].isin(menciones)]
    if sub.empty:
        return ""
    lineas = []
    for _, r in sub.iterrows():
        lineas.append(f"- {r['sucursal']} · {r['nombre']} ({_estado_corto(r['tipo'])}): {r['mensaje']}")
    return "\n" + "\n".join(lineas)


def _estado_corto(tipo):
    return {
        "RIESGO QUIEBRE": "de menos",
        "SOBRE-PEDIDO": "de más",
        "SE OLVIDO": "olvidado",
        "INGREDIENTE DESCONOCIDO": "desconocido",
    }.get(tipo, tipo)


def responder_local(pregunta, resultado, detalle_all=None):
    """Responde la pregunta usando las alertas ya calculadas."""
    q = norm(pregunta)
    alertas = resultado["alertas"]
    detalle = resultado["detalle"]
    sucursales = resultado["sucursales"]
    menciones = _mencionadas(pregunta, detalle)

    suc_ment = next(
        (s for s in sucursales if norm(s) in q), None
    )

    # 1) Ingrediente desconocido
    if any(k in q for k in ("desconocid", "catalogo", "aji", "chombo", "no existe")):
        des = alertas[alertas["tipo"] == "INGREDIENTE DESCONOCIDO"]
        if des.empty:
            return "No hay ingredientes desconocidos: todo lo pedido está en el catálogo."
        return "Ingredientes pedidos que NO están en el catálogo:\n" + _lineas_tipo(des, "INGREDIENTE DESCONOCIDO")

    # 2) Conteo de alertas
    if any(k in q for k in ("cuantas", "cuántas", "cuantos", "cuántos", "numero de alerta", "cantidad de alerta")):
        base = alertas if not suc_ment else alertas[alertas["sucursal"] == suc_ment]
        if menciones:
            base = base[base["nombre"].isin(menciones)]
        n = len(base)
        quien = f" en {suc_ment}" if suc_ment else " en total"
        if n == 0:
            return f"No hay alertas{quien}."
        conteos = base["tipo"].value_counts().to_dict()
        detalle_txt = ", ".join(f"{c} «{resultado['tipos'][t]}»" for t, c in conteos.items())
        return f"Hay {n} alertas{quien}: {detalle_txt}."

    # 3) Insumo + tipo de alerta (ej. "pide demasiado queso", "se olvidó mozzarella")
    tipo_preguntado = None
    if any(k in q for k in ("de mas", "de más", "demasiado", "sobre-pedido", "sobre pedido", "exceso", "mucho", "inmovilizado")):
        tipo_preguntado = "SOBRE-PEDIDO"
    elif any(k in q for k in ("quiebre", "de menos", "menos de lo", "falta", "faltante", "sin stock", "se queda sin")):
        tipo_preguntado = "RIESGO QUIEBRE"
    elif any(k in q for k in ("olvido", "olvidó", "olvidaron", "no pidio", "no pidió", "no incluyo", "no incluyó", "omitió", "omiti")):
        tipo_preguntado = "SE OLVIDO"

    if tipo_preguntado and menciones:
        ing = menciones[0]
        sub = _por_tipo(resultado, tipo_preguntado, suc_ment, menciones)
        if not sub.empty:
            texto = f"{_estado_corto(tipo_preguntado).title()} de {ing}"
            texto += f" en {suc_ment}" if suc_ment else ""
            texto += ":\n"
            for _, r in sub.iterrows():
                texto += f"\n- {r['sucursal']}: {r['mensaje']}"
            return texto
        # ninguna alerta de ese tipo para ese insumo: dar contexto de las otras
        verbo = {
            "SOBRE-PEDIDO": "pidiendo de más",
            "RIESGO QUIEBRE": "en riesgo de quiebre",
            "SE OLVIDO": "olvidando de pedir",
        }[tipo_preguntado]
        ing_desc = ", ".join(menciones)
        texto = f"Ninguna sucursal está {verbo} {ing_desc}."
        otras = _otras_alertas(resultado, tipo_preguntado, suc_ment)
        if otras:
            texto += f"\nLas alertas de la semana son:{otras}"
        return texto

    # 4) Insumo mencionado: detalles generales de ese insumo
    if menciones:
        ing = menciones[0]
        sub = alertas[alertas["nombre"] == ing]
        if suc_ment:
            sub = sub[sub["sucursal"] == suc_ment]
        if sub.empty:
            ok_row = detalle[(detalle["nombre"] == ing) & (detalle["tipo"] == "OK")]
            if suc_ment:
                ok_row = ok_row[ok_row["sucursal"] == suc_ment]
            if ok_row.empty:
                return f"No tengo datos de {ing} para {'la sucursal ' + suc_ment if suc_ment else 'esas sucursales'}."
            r = ok_row.iloc[0]
            return (
                f"Para {ing}: pedido OK. Proyección ≈{r['proyeccion_base']:g} {r['unidad_base']}, "
                f"stock {r['stock_base']:g} {r['unidad_base']}, pedido {r['pedido_formatos']:g} "
                f"{r['formato_compra']}. No hay alerta."
            )
        texto = f"Alertas sobre {ing}"
        texto += f" en {suc_ment}" if suc_ment else ""
        texto += ":\n"
        for _, r in sub.iterrows():
            texto += f"\n- {r['sucursal']}: {r['mensaje']}"
        return texto

    # 5) Resumen general
    if any(k in q for k in ("resumen", "general", "que hay", "qué hay", "reporte", "hola", "hello", "como estas")) or len(q.split()) <= 2:
        n = len(alertas)
        por_tipo = resultado["resumen_tipo"]
        texto = (
            f"Se detectaron {n} alertas en {len(sucursales)} sucursales "
            f"(proyección: {resultado['metodo']}).\n"
        )
        for t in ("RIESGO QUIEBRE", "SOBRE-PEDIDO", "SE OLVIDO", "INGREDIENTE DESCONOCIDO"):
            c = int(por_tipo.get(t, 0))
            if c:
                texto += f"\n- {c} de tipo «{resultado['tipos'][t]}»."
        if n == 0:
            texto += " No hay problemas pendientes."
        return texto

    # 6) Comparación / ranking entre sucursales
    if any(k in q for k in ("que sucursal", "qué sucursal", "cual sucursal", "cuál sucursal", "cuales sucursales", "cuáles sucursales", "ranking", "top", "pide mas", "pide más", "mayor", "menor", "compar", "quien pide más", "quién pide más")):
        pedidos = detalle.groupby("sucursal")["pedido_base"].sum()
        alertas_por_suc = alertas.groupby("sucursal")["tipo"].count().reindex(sucursales, fill_value=0)
        ranking = pedidos.sort_values(ascending=False)
        texto = "Órdenes totales por sucursal (en unidad base) y alertas:\n"
        for s, v in ranking.items():
            texto += f"\n- {s}: {v:,.0f} unidades base · {int(alertas_por_suc[s])} alertas"
        texto += f"\n\nLa sucursal que más pide es {ranking.index[0]}."
        return texto

    # 7) Sobre-pedido (de más) en general
    if any(k in q for k in ("de mas", "de más", "demasiado", "sobre-pedido", "sobre pedido", "exceso", "mucho", "inmovilizado")):
        over = _por_tipo(resultado, "SOBRE-PEDIDO", suc_ment)
        if over.empty:
            return "No se detectan sobre-pedidos." + (f" en {suc_ment}" if suc_ment else "")
        return "Sobre-pedidos detectados:\n" + _lineas_tipo(over, "SOBRE-PEDIDO")

    # 8) Riesgo de quiebre (de menos) en general
    if any(k in q for k in ("quiebre", "de menos", "menos de lo", "falta", "faltante", "sin stock", "se queda sin")):
        queb = _por_tipo(resultado, "RIESGO QUIEBRE", suc_ment)
        if queb.empty:
            return "No se detectan riesgos de quiebre." + (f" en {suc_ment}" if suc_ment else "")
        return "Riesgos de quiebre detectados:\n" + _lineas_tipo(queb, "RIESGO QUIEBRE")

    # 9) Se olvidó en general
    if any(k in q for k in ("olvido", "olvidó", "olvidaron", "no pidio", "no pidió", "no incluyo", "no incluyó", "omitió", "omiti")):
        olv = _por_tipo(resultado, "SE OLVIDO", suc_ment)
        if olv.empty:
            return "Nadie se olvidó de pedir nada." + (f" en {suc_ment}" if suc_ment else "")
        return "Insumos que se olvidaron de pedir:\n" + _lineas_tipo(olv, "SE OLVIDO")

    # 10) Por sucursal
    if any(k in q for k in ("por sucursal", "cada sucursal", "por tienda", "detalle por")):
        texto = "Resumen por sucursal:\n"
        for s in sucursales:
            sub = alertas[alertas["sucursal"] == s]
            n = len(sub)
            conteos = ", ".join(
                f"{c} {t.lower().replace(' ', '-')}" for t, c in sub["tipo"].value_counts().items()
            ) or "sin alertas"
            texto += f"\n- {s}: {n} alertas ({conteos})."
        return texto

    # Fallback
    return (
        "Puedo responder sobre las alertas de la semana. Prueba por ejemplo:\n"
        "- ¿Qué sucursal pide demasiado queso?\n"
        "- ¿Cuántas alertas hay?\n"
        "- ¿Quién se olvidó de pedir mozzarella?\n"
        "- ¿Qué sucursal pide más?\n"
        "- Resumen de las alertas"
    )


# --------------------------------------------------------------------------
# Motor con LLM (Groq, plan gratuito)
# --------------------------------------------------------------------------

def _construir_contexto(resultado, ingredientes=None):
    alertas = resultado["alertas"]
    detalle = resultado["detalle"]
    lineas = [
        f"Datos de órdenes de compra de Barrio Pizza (4 sucursales).",
        f"Método de proyección usado: {resultado['metodo']}.",
        "",
        "ALERTAS DETECTADAS:",
    ]
    if alertas.empty:
        lineas.append("- Ninguna.")
    else:
        for _, r in alertas.iterrows():
            lineas.append(f"- {r['sucursal']} | {r['nombre']} | {r['tipo']} | {r['mensaje']}")

    lineas.append("")
    lineas.append("PEDIDOS Y NECESIDAD (todas las líneas, unidad base salvo que se diga):")
    for _, r in detalle.iterrows():
        lineas.append(
            f"- {r['sucursal']} | {r['nombre']} | proy={r['proyeccion_base']:g} "
            f"{r['unidad_base']} | stock={r['stock_base']:g} | pedido={r['pedido_formatos']:g} "
            f"{r['formato_compra']} | recomendado={r['recomendado_formatos']:g}"
        )
    return "\n".join(lineas)


def responder_llm(pregunta, resultado, api_key, model="llama-3.3-70b-versatile"):
    """Responde con un LLM usando el contexto calculado. Requiere requests."""
    import requests

    contexto = _construir_contexto(resultado)
    system = (
        "Eres un asistente de compras de Barrio Pizza en Panamá. "
        "Responde en español, claro y breve, usando SOLO los datos del contexto. "
        "Si no sabes, dilo. No inventes cifras."
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Contexto:\n{contexto}\n\nPregunta: {pregunta}"},
        ],
        "temperature": 0.2,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=40)
    if resp.status_code == 401:
        return "Error de autenticación: revisá tu API key de Groq."
    if resp.status_code != 200:
        return f"El proveedor devolvió error {resp.status_code}: {resp.text[:200]}"
    return resp.json()["choices"][0]["message"]["content"]
