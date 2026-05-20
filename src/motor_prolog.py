from pathlib import Path
from pyswip import Prolog


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_REGLAS = BASE_DIR / "prolog" / "reglas.pl"


def convertir_cadena_a_lista(texto):
    """
    Convierte una cadena separada por ';' en lista.
    """
    if not isinstance(texto, str):
        return []

    return [elemento.strip() for elemento in texto.split(";") if elemento.strip()]


def convertir_lista_a_prolog(lista):
    """
    Convierte una lista de Python en una lista válida para Prolog.

    Ejemplo:
    ["PC", "PS5"] -> ['PC','PS5']
    """
    elementos = []

    for item in lista:
        item_limpio = str(item).replace("'", "\\'")
        elementos.append(f"'{item_limpio}'")

    return "[" + ",".join(elementos) + "]"


class MotorProlog:
    """
    Clase encargada de conectar Python con Prolog.
    Valida si una recomendación cumple las reglas definidas en reglas.pl.
    """

    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(str(RUTA_REGLAS))

    def recomendacion_valida(self, usuario, juego):
        """
        Comprueba si un juego es válido para un usuario según las reglas Prolog.
        """

        edad_usuario = int(usuario["edad"])
        presupuesto_usuario = float(usuario["presupuesto_max"])

        plataformas_usuario = convertir_cadena_a_lista(usuario["plataformas_preferidas"])
        tipos_usuario = convertir_cadena_a_lista(usuario["tipos_preferidos"])

        plataformas_prolog = convertir_lista_a_prolog(plataformas_usuario)
        tipos_prolog = convertir_lista_a_prolog(tipos_usuario)

        pegi_juego = int(juego["pegi"])
        plataforma_juego = str(juego["plataforma"])
        precio_juego = float(juego["precio"])
        tipo_juego = str(juego["tipo"])

        consulta = (
            f"recomendacion_valida("
            f"{edad_usuario}, "
            f"{plataformas_prolog}, "
            f"{presupuesto_usuario}, "
            f"{tipos_prolog}, "
            f"{pegi_juego}, "
            f"'{plataforma_juego}', "
            f"{precio_juego}, "
            f"'{tipo_juego}'"
            f")"
        )

        resultado = list(self.prolog.query(consulta))

        return len(resultado) > 0