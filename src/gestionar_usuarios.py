import pandas as pd
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_USUARIOS = BASE_DIR / "data" / "usuarios.csv"
RUTA_VALORACIONES = BASE_DIR / "data" / "valoraciones.csv"


COLUMNAS_USUARIOS = [
    "id_usuario",
    "nombre",
    "username",
    "password_hash",
    "edad",
    "plataformas_preferidas",
    "presupuesto_max",
    "generos_preferidos",
    "tipos_preferidos"
]


def cargar_usuarios():
    """
    Carga usuarios.csv y normaliza las columnas.
    Se usa dtype=str para evitar errores de Pandas con columnas vacías.
    """
    if not RUTA_USUARIOS.exists():
        usuarios = pd.DataFrame(columns=COLUMNAS_USUARIOS)
        usuarios.to_csv(RUTA_USUARIOS, index=False)
        return usuarios

    try:
        usuarios = pd.read_csv(RUTA_USUARIOS, dtype=str)
    except pd.errors.EmptyDataError:
        usuarios = pd.DataFrame(columns=COLUMNAS_USUARIOS)

    for columna in COLUMNAS_USUARIOS:
        if columna not in usuarios.columns:
            usuarios[columna] = ""

    usuarios = usuarios[COLUMNAS_USUARIOS].fillna("")

    if not usuarios.empty:
        usuarios["id_usuario"] = usuarios["id_usuario"].replace("", "0").astype(int)
        usuarios["edad"] = usuarios["edad"].replace("", "0").astype(int)
        usuarios["presupuesto_max"] = usuarios["presupuesto_max"].replace("", "0").astype(float)

        usuarios["nombre"] = usuarios["nombre"].astype(str)
        usuarios["username"] = usuarios["username"].astype(str)
        usuarios["password_hash"] = usuarios["password_hash"].astype(str)
        usuarios["plataformas_preferidas"] = usuarios["plataformas_preferidas"].astype(str)
        usuarios["generos_preferidos"] = usuarios["generos_preferidos"].astype(str)
        usuarios["tipos_preferidos"] = usuarios["tipos_preferidos"].astype(str)

    usuarios.to_csv(RUTA_USUARIOS, index=False)

    return usuarios


def guardar_usuarios(usuarios):
    """
    Guarda los usuarios en usuarios.csv.
    """
    usuarios = usuarios[COLUMNAS_USUARIOS].copy()

    usuarios["plataformas_preferidas"] = usuarios["plataformas_preferidas"].astype(str)
    usuarios["generos_preferidos"] = usuarios["generos_preferidos"].astype(str)
    usuarios["tipos_preferidos"] = usuarios["tipos_preferidos"].astype(str)

    usuarios.to_csv(RUTA_USUARIOS, index=False)


def obtener_siguiente_id():
    """
    Obtiene el siguiente ID disponible.

    Se tienen en cuenta los IDs de usuarios.csv y valoraciones.csv para evitar
    conflictos con usuarios históricos del dataset de valoraciones.
    """
    usuarios = cargar_usuarios()
    ids = []

    if not usuarios.empty:
        ids.extend(usuarios["id_usuario"].dropna().astype(int).tolist())

    if RUTA_VALORACIONES.exists():
        valoraciones = pd.read_csv(RUTA_VALORACIONES)

        if "id_usuario" in valoraciones.columns and not valoraciones.empty:
            ids.extend(valoraciones["id_usuario"].dropna().astype(int).tolist())

    if not ids:
        return 1

    return max(ids) + 1


def existe_username(username):
    """
    Comprueba si ya existe un nombre de usuario.
    """
    usuarios = cargar_usuarios()
    username = username.strip().lower()

    if usuarios.empty:
        return False

    return username in usuarios["username"].astype(str).str.lower().values


def crear_usuario(nombre, username, password, edad, plataformas_preferidas,
                  presupuesto_max, generos_preferidos, tipos_preferidos):
    """
    Crea una cuenta nueva y guarda la contraseña cifrada.
    """
    usuarios = cargar_usuarios()
    username = username.strip().lower()

    if existe_username(username):
        raise ValueError("El nombre de usuario ya existe.")

    nuevo_usuario = {
        "id_usuario": obtener_siguiente_id(),
        "nombre": nombre.strip(),
        "username": username,
        "password_hash": generate_password_hash(password),
        "edad": int(edad),
        "plataformas_preferidas": str(plataformas_preferidas),
        "presupuesto_max": float(presupuesto_max),
        "generos_preferidos": str(generos_preferidos),
        "tipos_preferidos": str(tipos_preferidos)
    }

    usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    guardar_usuarios(usuarios)

    return nuevo_usuario


def autenticar_usuario(username, password):
    """
    Comprueba usuario y contraseña.
    Devuelve el usuario si es correcto, o None si falla.
    """
    usuarios = cargar_usuarios()
    username = username.strip().lower()

    usuario = usuarios[usuarios["username"].astype(str).str.lower() == username]

    if usuario.empty:
        return None

    usuario = usuario.iloc[0]

    if not check_password_hash(str(usuario["password_hash"]), password):
        return None

    return usuario.to_dict()


def obtener_usuario_por_id(id_usuario):
    """
    Obtiene un usuario por ID.
    """
    usuarios = cargar_usuarios()
    usuario = usuarios[usuarios["id_usuario"] == int(id_usuario)]

    if usuario.empty:
        return None

    return usuario.iloc[0].to_dict()


def actualizar_perfil(id_usuario, nombre, edad, plataformas_preferidas,
                      presupuesto_max, generos_preferidos, tipos_preferidos):
    """
    Actualiza el perfil del usuario.
    No modifica username ni contraseña.
    """
    usuarios = cargar_usuarios()

    indice = usuarios[usuarios["id_usuario"] == int(id_usuario)].index

    if len(indice) == 0:
        return None

    i = indice[0]

    usuarios.loc[i, "nombre"] = nombre.strip()
    usuarios.loc[i, "edad"] = int(edad)
    usuarios.loc[i, "plataformas_preferidas"] = str(plataformas_preferidas)
    usuarios.loc[i, "presupuesto_max"] = float(presupuesto_max)
    usuarios.loc[i, "generos_preferidos"] = str(generos_preferidos)
    usuarios.loc[i, "tipos_preferidos"] = str(tipos_preferidos)

    guardar_usuarios(usuarios)

    return usuarios.loc[i].to_dict()