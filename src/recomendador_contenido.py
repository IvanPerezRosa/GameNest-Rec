from motor_prolog import MotorProlog


def convertir_cadena_a_lista(texto):
    """
    Convierte una cadena separada por ';' en una lista limpia.
    """
    if not isinstance(texto, str):
        return []

    return [elemento.strip() for elemento in texto.split(";") if elemento.strip()]


def obtener_juegos_valorados_por_usuario(valoraciones, id_usuario):
    """
    Devuelve una lista con los IDs de los juegos que el usuario ya ha valorado.
    """
    valoraciones_usuario = valoraciones[valoraciones["id_usuario"] == id_usuario]
    return valoraciones_usuario["id_juego"].tolist()


def calcular_coincidencias_generos(generos_juego, generos_usuario):
    """
    Devuelve los géneros comunes entre el juego y el usuario.
    """
    lista_generos_juego = convertir_cadena_a_lista(generos_juego)
    lista_generos_usuario = convertir_cadena_a_lista(generos_usuario)

    return sorted(set(lista_generos_juego).intersection(set(lista_generos_usuario)))


def calcular_puntuacion_juego(juego, usuario):
    """
    Calcula la puntuación interna de un videojuego según el perfil del usuario.
    También devuelve un desglose explicativo de la puntuación.
    """
    puntuacion = 0
    desglose = []

    generos_comunes = calcular_coincidencias_generos(
        juego["generos"],
        usuario["generos_preferidos"]
    )

    if generos_comunes:
        puntos_generos = len(generos_comunes) * 4
        puntuacion += puntos_generos
        desglose.append(
            f"+{puntos_generos} por coincidencia de géneros: {', '.join(generos_comunes)}"
        )

    plataformas_usuario = convertir_cadena_a_lista(usuario["plataformas_preferidas"])
    if juego["plataforma"] in plataformas_usuario:
        puntuacion += 3
        desglose.append(f"+3 por plataforma compatible: {juego['plataforma']}")

    tipos_usuario = convertir_cadena_a_lista(usuario["tipos_preferidos"])
    if juego["tipo"] in tipos_usuario:
        puntuacion += 3
        desglose.append(f"+3 por tipo de juego compatible: {juego['tipo']}")

    if float(juego["precio"]) <= float(usuario["presupuesto_max"]):
        puntuacion += 2
        desglose.append("+2 por estar dentro del presupuesto")

    if int(juego["pegi"]) <= int(usuario["edad"]):
        puntuacion += 2
        desglose.append("+2 por ser adecuado para la edad según PEGI")

    if float(juego["precio"]) == 0:
        puntuacion += 1
        desglose.append("+1 por ser gratuito")
    elif float(juego["precio"]) <= float(usuario["presupuesto_max"]) * 0.5:
        puntuacion += 1
        desglose.append("+1 por costar menos de la mitad del presupuesto")

    return puntuacion, desglose


def recomendar_por_contenido(juegos, usuarios, valoraciones, id_usuario, limite=12):
    """
    Recomienda videojuegos según las preferencias del usuario.

    Primero prioriza juegos que coincidan en género.
    Si no hay suficientes, añade recomendaciones alternativas compatibles.
    """

    usuario = usuarios[usuarios["id_usuario"] == id_usuario]

    if usuario.empty:
        return []

    usuario = usuario.iloc[0]

    plataformas_usuario = convertir_cadena_a_lista(usuario["plataformas_preferidas"])
    juegos_valorados = obtener_juegos_valorados_por_usuario(valoraciones, id_usuario)

    candidatos = juegos[
        (~juegos["id_juego"].isin(juegos_valorados))
        & (juegos["plataforma"].isin(plataformas_usuario))
        & (juegos["pegi"] <= int(usuario["edad"]))
        & (juegos["precio"] <= float(usuario["presupuesto_max"]))
    ].copy()

    if candidatos.empty:
        return []

    resultados = candidatos.apply(
        lambda juego: calcular_puntuacion_juego(juego, usuario),
        axis=1
    )

    candidatos["puntuacion"] = resultados.apply(lambda resultado: resultado[0])
    candidatos["desglose_puntuacion"] = resultados.apply(lambda resultado: resultado[1])

    candidatos["coincidencias_generos"] = candidatos["generos"].apply(
        lambda generos_juego: len(
            calcular_coincidencias_generos(
                generos_juego,
                usuario["generos_preferidos"]
            )
        )
    )

    # Separar recomendaciones principales y alternativas
    principales = candidatos[candidatos["coincidencias_generos"] > 0].copy()
    alternativas = candidatos[candidatos["coincidencias_generos"] == 0].copy()

    principales["tipo_recomendacion"] = "Principal"
    alternativas["tipo_recomendacion"] = "Alternativa"

    # Las principales pueden entrar con puntuación normal
    principales = principales[principales["puntuacion"] >= 7]

    # Las alternativas deben ser más estrictas para evitar recomendar cualquier cosa
    alternativas = alternativas[alternativas["puntuacion"] >= 10]

    principales = principales.sort_values(
        by=["coincidencias_generos", "puntuacion", "precio"],
        ascending=[False, False, True]
    )

    alternativas = alternativas.sort_values(
        by=["puntuacion", "precio"],
        ascending=[False, True]
    )

    motor_prolog = MotorProlog()
    recomendaciones_validas = []

    # Primero añadimos recomendaciones principales
    for _, juego in principales.iterrows():
        if motor_prolog.recomendacion_valida(usuario, juego):
            recomendaciones_validas.append(juego.to_dict())

        if len(recomendaciones_validas) >= limite:
            return recomendaciones_validas

    # Si no hay suficientes, rellenamos con alternativas
    for _, juego in alternativas.iterrows():
        if motor_prolog.recomendacion_valida(usuario, juego):
            recomendaciones_validas.append(juego.to_dict())

        if len(recomendaciones_validas) >= limite:
            break

    return recomendaciones_validas

def generar_motivo_recomendacion(juego, usuario):
    """
    Genera una explicación textual de por qué se recomienda un videojuego.
    """
    motivos = []

    generos_comunes = calcular_coincidencias_generos(
        juego["generos"],
        usuario["generos_preferidos"]
    )

    if generos_comunes:
        motivos.append("coincide en los géneros: " + ", ".join(generos_comunes))

    plataformas_usuario = convertir_cadena_a_lista(usuario["plataformas_preferidas"])
    if juego["plataforma"] in plataformas_usuario:
        motivos.append("está disponible en una de tus plataformas")

    tipos_usuario = convertir_cadena_a_lista(usuario["tipos_preferidos"])
    if juego["tipo"] in tipos_usuario:
        motivos.append("coincide con tus tipos de juego preferidos")

    if float(juego["precio"]) <= float(usuario["presupuesto_max"]):
        motivos.append("entra dentro de tu presupuesto")

    if int(juego["pegi"]) <= int(usuario["edad"]):
        motivos.append("es adecuado para tu edad según PEGI")

    if float(juego["precio"]) == 0:
        motivos.append("es gratuito")

    motivos.append("ha sido validado por reglas Prolog")

    return "Recomendado porque " + ", ".join(motivos) + "."