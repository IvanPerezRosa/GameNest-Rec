from motor_prolog import MotorProlog


def obtener_juegos_valorados_por_usuario(valoraciones, id_usuario):
    """
    Devuelve una lista con los IDs de los juegos que el usuario ya ha valorado.
    """
    valoraciones_usuario = valoraciones[valoraciones["id_usuario"] == id_usuario]
    return valoraciones_usuario["id_juego"].tolist()


def calcular_puntuacion_juego(juego, usuario):
    """
    Calcula una puntuación interna para saber cuánto encaja un videojuego
    con el perfil del usuario.
    """
    puntuacion = 0

    if juego["genero"] == usuario["genero_preferido"]:
        puntuacion += 5

    if juego["tipo"] == usuario["tipo_preferido"]:
        puntuacion += 3

    if juego["plataforma"] == usuario["plataforma_preferida"]:
        puntuacion += 3

    if juego["precio"] <= usuario["presupuesto_max"]:
        puntuacion += 2

    if juego["pegi"] <= usuario["edad"]:
        puntuacion += 2

    if juego["precio"] == 0:
        puntuacion += 1
    elif juego["precio"] <= usuario["presupuesto_max"] * 0.5:
        puntuacion += 1

    return puntuacion


def recomendar_por_contenido(juegos, usuarios, valoraciones, id_usuario, limite=5):
    """
    Recomienda videojuegos según las características del usuario y de los juegos.
    Después valida cada recomendación con reglas Prolog.
    """

    usuario = usuarios[usuarios["id_usuario"] == id_usuario]

    if usuario.empty:
        return []

    usuario = usuario.iloc[0]

    juegos_valorados = obtener_juegos_valorados_por_usuario(valoraciones, id_usuario)

    candidatos = juegos[
        (~juegos["id_juego"].isin(juegos_valorados))
        & (juegos["plataforma"] == usuario["plataforma_preferida"])
        & (juegos["pegi"] <= usuario["edad"])
        & (juegos["precio"] <= usuario["presupuesto_max"])
    ].copy()

    if candidatos.empty:
        return []

    candidatos["puntuacion"] = candidatos.apply(
        lambda juego: calcular_puntuacion_juego(juego, usuario),
        axis=1
    )

    candidatos = candidatos[candidatos["puntuacion"] >= 7]

    if candidatos.empty:
        return []

    candidatos = candidatos.sort_values(
        by=["puntuacion", "precio"],
        ascending=[False, True]
    )

    motor_prolog = MotorProlog()
    recomendaciones_validas = []

    for _, juego in candidatos.iterrows():
        if motor_prolog.recomendacion_valida(usuario, juego):
            recomendaciones_validas.append(juego.to_dict())

        if len(recomendaciones_validas) >= limite:
            break

    return recomendaciones_validas


def generar_motivo_recomendacion(juego, usuario):
    """
    Genera una explicación sencilla de por qué se recomienda un videojuego.
    """
    motivos = []

    if juego["genero"] == usuario["genero_preferido"]:
        motivos.append("coincide con tu género favorito")

    if juego["plataforma"] == usuario["plataforma_preferida"]:
        motivos.append("está disponible en tu plataforma preferida")

    if juego["tipo"] == usuario["tipo_preferido"]:
        motivos.append("coincide con tu tipo de juego preferido")

    if juego["precio"] <= usuario["presupuesto_max"]:
        motivos.append("entra dentro de tu presupuesto")

    if juego["pegi"] <= usuario["edad"]:
        motivos.append("es adecuado para tu edad según PEGI")

    if juego["precio"] == 0:
        motivos.append("es gratuito")

    motivos.append("ha sido validado por reglas Prolog")

    return "Recomendado porque " + ", ".join(motivos) + "."