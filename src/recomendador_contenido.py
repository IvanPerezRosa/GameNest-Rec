from motor_prolog import MotorProlog


def convertir_generos_a_lista(generos):
    """
    Convierte una cadena separada por ';' en una lista de géneros.
    """
    if not isinstance(generos, str):
        return []

    return [genero.strip() for genero in generos.split(";") if genero.strip()]


def obtener_juegos_valorados_por_usuario(valoraciones, id_usuario):
    """
    Devuelve una lista con los IDs de los juegos que el usuario ya ha valorado.
    """
    valoraciones_usuario = valoraciones[valoraciones["id_usuario"] == id_usuario]
    return valoraciones_usuario["id_juego"].tolist()


def calcular_coincidencias_generos(generos_juego, generos_usuario):
    """
    Calcula cuántos géneros coinciden entre un juego y un usuario.
    """
    lista_generos_juego = convertir_generos_a_lista(generos_juego)
    lista_generos_usuario = convertir_generos_a_lista(generos_usuario)

    coincidencias = set(lista_generos_juego).intersection(set(lista_generos_usuario))

    return len(coincidencias)


def calcular_puntuacion_juego(juego, usuario):
    """
    Calcula una puntuación interna según cuánto encaja el juego con el usuario.
    """
    puntuacion = 0

    coincidencias_generos = calcular_coincidencias_generos(
        juego["generos"],
        usuario["generos_preferidos"]
    )

    puntuacion += coincidencias_generos * 4

    if juego["tipo"] == usuario["tipo_preferido"]:
        puntuacion += 3

    if juego["plataforma"] == usuario["plataforma_preferida"]:
        puntuacion += 3

    if float(juego["precio"]) <= float(usuario["presupuesto_max"]):
        puntuacion += 2

    if int(juego["pegi"]) <= int(usuario["edad"]):
        puntuacion += 2

    if float(juego["precio"]) == 0:
        puntuacion += 1
    elif float(juego["precio"]) <= float(usuario["presupuesto_max"]) * 0.5:
        puntuacion += 1

    return puntuacion


def recomendar_por_contenido(juegos, usuarios, valoraciones, id_usuario, limite=5):
    """
    Recomienda videojuegos permitiendo varios géneros por juego y por usuario.
    """

    usuario = usuarios[usuarios["id_usuario"] == id_usuario]

    if usuario.empty:
        return []

    usuario = usuario.iloc[0]

    juegos_valorados = obtener_juegos_valorados_por_usuario(valoraciones, id_usuario)

    candidatos = juegos[
        (~juegos["id_juego"].isin(juegos_valorados))
        & (juegos["plataforma"] == usuario["plataforma_preferida"])
        & (juegos["pegi"] <= int(usuario["edad"]))
        & (juegos["precio"] <= float(usuario["presupuesto_max"]))
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
    Genera una explicación de por qué se recomienda un videojuego.
    """
    motivos = []

    generos_juego = convertir_generos_a_lista(juego["generos"])
    generos_usuario = convertir_generos_a_lista(usuario["generos_preferidos"])

    generos_comunes = sorted(set(generos_juego).intersection(set(generos_usuario)))

    if generos_comunes:
        motivos.append("coincide en los géneros: " + ", ".join(generos_comunes))

    if juego["plataforma"] == usuario["plataforma_preferida"]:
        motivos.append("está disponible en tu plataforma preferida")

    if juego["tipo"] == usuario["tipo_preferido"]:
        motivos.append("coincide con tu tipo de juego preferido")

    if float(juego["precio"]) <= float(usuario["presupuesto_max"]):
        motivos.append("entra dentro de tu presupuesto")

    if int(juego["pegi"]) <= int(usuario["edad"]):
        motivos.append("es adecuado para tu edad según PEGI")

    if float(juego["precio"]) == 0:
        motivos.append("es gratuito")

    motivos.append("ha sido validado por reglas Prolog")

    return "Recomendado porque " + ", ".join(motivos) + "."