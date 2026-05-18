import pandas as pd
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_USUARIOS = BASE_DIR / "data" / "usuarios.csv"


COLUMNAS_USUARIOS = [
    "id_usuario",
    "nombre",
    "username",
    "password_hash",
    "edad",
    "plataforma_preferida",
    "presupuesto_max",
    "genero_preferido",
    "tipo_preferido"
]


def cargar_usuarios():
    """
    Carga el archivo usuarios.csv.
    Si está vacío o le falta alguna columna, lo normaliza.
    """
    if not RUTA_USUARIOS.exists():
        usuarios = pd.DataFrame(columns=COLUMNAS_USUARIOS)
        usuarios.to_csv(RUTA_USUARIOS, index=False)
        return usuarios

    usuarios = pd.read_csv(RUTA_USUARIOS)

    for columna in COLUMNAS_USUARIOS:
        if columna not in usuarios.columns:
            usuarios[columna] = ""

    usuarios = usuarios[COLUMNAS_USUARIOS]
    usuarios.to_csv(RUTA_USUARIOS, index=False)

    return usuarios


def guardar_usuarios(usuarios):
    """
    Guarda el DataFrame de usuarios en el CSV.
    """
    usuarios.to_csv(RUTA_USUARIOS, index=False)


def obtener_siguiente_id():
    """
    Obtiene el siguiente ID disponible.
    """
    usuarios = cargar_usuarios()

    if usuarios.empty:
        return 1

    return int(usuarios["id_usuario"].max()) + 1


def existe_username(username):
    """
    Comprueba si ya existe un nombre de usuario.
    """
    usuarios = cargar_usuarios()
    username = username.strip().lower()

    if usuarios.empty:
        return False

    return username in usuarios["username"].astype(str).str.lower().values


def crear_usuario(nombre, username, password, edad, plataforma_preferida,
                  presupuesto_max, genero_preferido, tipo_preferido):
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
        "plataforma_preferida": plataforma_preferida,
        "presupuesto_max": float(presupuesto_max),
        "genero_preferido": genero_preferido,
        "tipo_preferido": tipo_preferido
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


def actualizar_perfil(id_usuario, nombre, edad, plataforma_preferida,
                      presupuesto_max, genero_preferido, tipo_preferido):
    """
    Actualiza las preferencias del usuario.
    No modifica username ni contraseña.
    """
    usuarios = cargar_usuarios()

    indice = usuarios[usuarios["id_usuario"] == int(id_usuario)].index

    if len(indice) == 0:
        return None

    i = indice[0]

    usuarios.at[i, "nombre"] = nombre.strip()
    usuarios.at[i, "edad"] = int(edad)
    usuarios.at[i, "plataforma_preferida"] = plataforma_preferida
    usuarios.at[i, "presupuesto_max"] = float(presupuesto_max)
    usuarios.at[i, "genero_preferido"] = genero_preferido
    usuarios.at[i, "tipo_preferido"] = tipo_preferido

    guardar_usuarios(usuarios)

    return usuarios.loc[i].to_dict()