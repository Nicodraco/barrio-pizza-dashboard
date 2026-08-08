"""Cálculo de la necesidad real y generación de alertas por sucursal/insumo.

Lógica por (sucursal, ingrediente):
  1. proyección del consumo de la próxima semana (módulo proyeccion).
  2. necesidad_real = proyección - inventario_actual (en unidad base).
  3. recomendado_formatos = ceil(necesidad / base_por_formato)  # formatos enteros
  4. Se compara con la cantidad de formatos pedida y se clasifica:
       - SE OLVIDO          : no pidió nada pero la necesidad real es > 0.
       - RIESGO QUIEBRE     : pidió menos de lo recomendado (>= 1 formato menos).
       - SOBRE-PEDIDO       : pidió más de lo recomendado (>= 1 formato más).
       - INGREDIENTE DESCONOCIDO: aparece en la orden pero no está en el catálogo.
"""
import pandas as pd

from core.proyeccion import proyectar
from core.unidades import base_a_formatos

TIPOS = {
    "RIESGO QUIEBRE": "Pide de menos / riesgo de quiebre",
    "SOBRE-PEDIDO": "Pide de más",
    "SE OLVIDO": "Se olvidó de pedir",
    "INGREDIENTE DESCONOCIDO": "No está en el catálogo",
    "OK": "Correcto",
}


def _fmt(n):
    if n is None:
        return "?"
    return f"{n:g}"


def analizar(datos, metodo="robusto"):
    """Genera el detalle completo y las alertas. Devuelve un dict con DataFrames."""
    ingredientes = datos["ingredientes"]
    consumo = datos["consumo"]
    inventario = datos["inventario"]
    orden = datos["orden"]

    ing_map = ingredientes.set_index("ingrediente_id").to_dict("index")
    sucursales = sorted(
        set(consumo["sucursal"])
        | set(inventario["sucursal"])
        | set(orden["sucursal"])
    )

    filas = []
    for suc in sucursales:
        cons_suc = consumo[consumo["sucursal"] == suc]
        inv_suc = inventario[inventario["sucursal"] == suc]
        ord_suc = orden[orden["sucursal"] == suc]

        ids = sorted(
            set(cons_suc["ingrediente_id"])
            | set(inv_suc["ingrediente_id"])
            | set(ord_suc["ingrediente_id"])
        )

        for iid in ids:
            base = {
                "sucursal": suc,
                "ingrediente_id": iid,
                "nombre": iid,
                "proveedor": "Desconocido",
                "unidad_base": "?",
                "formato_compra": "?",
                "base_por_formato": None,
                "es_perecedero": None,
                "pedido_formatos": 0.0,
                "pedido_base": None,
                "proyeccion_base": None,
                "stock_base": None,
                "necesidad_base": None,
                "recomendado_formatos": 0,
                "tipo": "OK",
                "mensaje": "",
                "semanas_atipicas": 0,
            }

            ord_vals = ord_suc.loc[ord_suc["ingrediente_id"] == iid, "cantidad_formatos"]
            if len(ord_vals):
                base["pedido_formatos"] = float(ord_vals.iloc[0])

            if iid not in ing_map:
                base["nombre"] = iid
                base["tipo"] = "INGREDIENTE DESCONOCIDO"
                base["mensaje"] = (
                    f"'{iid}' aparece en la orden de {suc} pero no existe en el "
                    "catálogo de ingredientes: revisar qué es y de dónde salió."
                )
                filas.append(base)
                continue

            ing = ing_map[iid]
            fs = float(ing["unidad_base_por_formato"])
            base.update(
                {
                    "nombre": ing["nombre"],
                    "proveedor": ing["proveedor"],
                    "unidad_base": ing["unidad_base"],
                    "formato_compra": ing["formato_compra"],
                    "base_por_formato": fs,
                    "es_perecedero": ing["es_perecedero"],
                    "pedido_base": base["pedido_formatos"] * fs,
                }
            )

            cons_vals = cons_suc.loc[
                cons_suc["ingrediente_id"] == iid, "consumo_unidad_base"
            ].tolist()
            inv_vals = inv_suc.loc[
                inv_suc["ingrediente_id"] == iid, "stock_actual_unidad_base"
            ].tolist()

            stock = float(inv_vals[0]) if inv_vals else 0.0
            base["stock_base"] = stock

            proy = proyectar(cons_vals, metodo) if cons_vals else {
                "proyeccion": 0.0, "outliers": []
            }
            base["proyeccion_base"] = proy["proyeccion"]
            base["semanas_atipicas"] = int(sum(proy["outliers"]))

            necesidad = proy["proyeccion"] - stock
            base["necesidad_base"] = necesidad
            recomendado = base_a_formatos(necesidad, fs)
            base["recomendado_formatos"] = recomendado

            pedido = base["pedido_formatos"]

            if pedido == 0 and necesidad > 0:
                base["tipo"] = "SE OLVIDO"
                base["mensaje"] = (
                    f"ALERTA: {suc} NO incluyó {base['nombre']} en su orden de la "
                    f"semana, pero necesitaría ≈{_fmt(necesidad)} {base['unidad_base']} "
                    f"(~{_fmt(recomendado)} {base['formato_compra']}) → riesgo de quiebre."
                )
            elif pedido > 0 and recomendado == 0:
                base["tipo"] = "SOBRE-PEDIDO"
                base["mensaje"] = (
                    f"ALERTA: {suc} pide {_fmt(pedido)} {base['formato_compra']} de "
                    f"{base['nombre']} pero el inventario ya cubre la proyección → "
                    f"excedente de {_fmt(pedido * fs)} {base['unidad_base']}."
                )
            elif pedido < recomendado:
                base["tipo"] = "RIESGO QUIEBRE"
                falta_fmt = recomendado - pedido
                base["mensaje"] = (
                    f"ALERTA: {suc} está pidiendo {_fmt(falta_fmt * fs)} {base['unidad_base']} "
                    f"({_fmt(falta_fmt)} {base['formato_compra']}) de {base['nombre']} "
                    "menos que lo proyectado → riesgo de quiebre."
                )
            elif pedido > recomendado:
                base["tipo"] = "SOBRE-PEDIDO"
                exceso_fmt = pedido - recomendado
                base["mensaje"] = (
                    f"ALERTA: {suc} está pidiendo {_fmt(exceso_fmt * fs)} {base['unidad_base']} "
                    f"({_fmt(exceso_fmt)} {base['formato_compra']}) de {base['nombre']} "
                    "de más → dinero inmovilizado y riesgo de vencimiento."
                )

            filas.append(base)

    detalle = pd.DataFrame(filas)
    alertas = detalle[detalle["tipo"] != "OK"].copy()

    resumen_tipo = (
        alertas["tipo"]
        .value_counts()
        .reindex([t for t in TIPOS if t != "OK"], fill_value=0)
    )
    resumen_sucursal = (
        alertas.groupby(["sucursal", "tipo"]).size().unstack(fill_value=0)
    )

    return {
        "detalle": detalle,
        "alertas": alertas,
        "sucursales": sucursales,
        "tipos": TIPOS,
        "resumen_tipo": resumen_tipo,
        "resumen_sucursal": resumen_sucursal,
        "metodo": metodo,
    }
