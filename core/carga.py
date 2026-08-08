"""Carga y limpieza de los 4 CSV del reto."""
from pathlib import Path

import pandas as pd

DATOS_DIR = Path(__file__).resolve().parent.parent / "datos"


def cargar_datos(datos_dir=None):
    """Carga los 4 CSV y devuelve un dict con cada DataFrame."""
    datos_dir = Path(datos_dir) if datos_dir else DATOS_DIR
    return {
        "ingredientes": pd.read_csv(datos_dir / "ingredientes.csv"),
        "consumo": pd.read_csv(datos_dir / "consumo_historico.csv"),
        "inventario": pd.read_csv(datos_dir / "inventario_actual.csv"),
        "orden": pd.read_csv(datos_dir / "orden_compra_semana.csv"),
    }
