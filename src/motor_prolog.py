from pathlib import Path
from pyswip import Prolog


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_REGLAS = BASE_DIR / "prolog" / "reglas.pl"


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
        plataforma_usuario = str(usuario["plataforma_preferida"])
        presupuesto_usuario = float(usuario["presupuesto_max"])
        tipo_usuario = str(usuario["tipo_preferido"])

        pegi_juego = int(juego["pegi"])
        plataforma_juego = str(juego["plataforma"])
        precio_juego = float(juego["precio"])
        tipo_juego = str(juego["tipo"])

        consulta = (
            f"recomendacion_valida("
            f"{edad_usuario}, "
            f"'{plataforma_usuario}', "
            f"{presupuesto_usuario}, "
            f"'{tipo_usuario}', "
            f"{pegi_juego}, "
            f"'{plataforma_juego}', "
            f"{precio_juego}, "
            f"'{tipo_juego}'"
            f")"
        )

        resultado = list(self.prolog.query(consulta))

        return len(resultado) > 0