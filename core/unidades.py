"""Conversión entre formatos de compra y la unidad base (kg, L, und).

Regla del reto: los insumos solo se compran en formatos completos.
"""
import math


def formatos_a_base(cantidad_formatos, base_por_formato):
    """Cantidad de unidad base que representa una cantidad de formatos."""
    return cantidad_formatos * base_por_formato


def base_a_formatos(cantidad_base, base_por_formato):
    """Mínima cantidad de formatos completos que cubre una necesidad (ceil).

    Un excedente menor a un formato completo se considera redondeo normal.
    """
    if cantidad_base is None or base_por_formato is None or base_por_formato <= 0:
        return 0
    if cantidad_base <= 0:
        return 0
    return math.ceil(cantidad_base / base_por_formato)
