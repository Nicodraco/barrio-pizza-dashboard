"""Proyección del consumo de la próxima semana.

Soporta tres métodos:
- "robusto": media de las semanas normales (detecta y excluye outliers).
- "simple":   promedio simple de las 6 semanas.
- "tendencia": regresión lineal sobre semanas normales proyectada a la semana 7.
"""
import numpy as np


def _flag_outliers(valores):
    """Máscara booleana de outliers con la regla de Tukey (1.5 x IQR).

    Con menos de 4 puntos, o desviación cero, usa un criterio de desvío
    relativo a la mediana (>=30%) para no marcar todo por variación normal.
    """
    y = np.asarray(valores, dtype=float)
    n = len(y)
    mask = np.zeros(n, dtype=bool)
    if n < 4:
        return mask
    q1, q3 = np.percentile(y, [25, 75])
    iqr = q3 - q1
    if iqr == 0:
        med = float(np.median(y))
        if med != 0:
            mask = np.abs(y - med) > 0.3 * abs(med)
        return mask
    return (y < q1 - 1.5 * iqr) | (y > q3 + 1.5 * iqr)


def proyectar(consumo, metodo="robusto"):
    """Proyecta el consumo semanal a partir de la lista de valores S1..S6.

    Devuelve un dict con la proyección, estadísticas y qué semanas se
    consideraron atípicas.
    """
    y = np.asarray(consumo, dtype=float)
    n = len(y)
    if n == 0:
        return {"proyeccion": 0.0, "metodo": metodo, "outliers": [], "valores": []}

    out = _flag_outliers(y)
    media_todas = float(np.nanmean(y))
    media_robusta = float(np.nanmean(y[~out])) if (~out).any() else media_todas
    pendiente = 0.0

    if metodo == "simple":
        proyeccion = media_todas
    elif metodo == "tendencia":
        idx = np.arange(1, n + 1, dtype=float)
        ok = ~out
        if ok.sum() >= 3 and float(np.std(idx[ok])) > 0:
            pendiente, intercepto = np.polyfit(idx[ok], y[ok], 1)
            proyeccion = pendiente * (n + 1) + intercepto
        else:
            proyeccion = media_robusta
        proyeccion = max(float(proyeccion), 0.0)
    else:  # robusto
        proyeccion = media_robusta

    return {
        "proyeccion": float(proyeccion),
        "metodo": metodo,
        "media": media_todas,
        "mediana": float(np.median(y)),
        "media_robusta": media_robusta,
        "desviacion": float(np.std(y)) if n > 1 else 0.0,
        "pendiente": float(pendiente),
        "outliers": out.tolist(),
        "valores": y.tolist(),
    }
