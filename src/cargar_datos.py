import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def cargar_juegos():
    ruta = DATA_DIR / "juegos.csv"
    return pd.read_csv(ruta)


def cargar_usuarios():
    ruta = DATA_DIR / "usuarios.csv"
    return pd.read_csv(ruta)


def cargar_valoraciones():
    ruta = DATA_DIR / "valoraciones.csv"
    return pd.read_csv(ruta)


def cargar_todos_los_datos():
    juegos = cargar_juegos()
    usuarios = cargar_usuarios()
    valoraciones = cargar_valoraciones()

    return juegos, usuarios, valoraciones


def mostrar_resumen_datos():
    juegos, usuarios, valoraciones = cargar_todos_los_datos()

    print("Datos cargados correctamente")
    print("--------------------------------")
    print(f"Número de juegos: {len(juegos)}")
    print(f"Número de usuarios: {len(usuarios)}")
    print(f"Número de valoraciones: {len(valoraciones)}")


if __name__ == "__main__":
    mostrar_resumen_datos()