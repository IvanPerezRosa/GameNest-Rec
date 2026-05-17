from cargar_datos import cargar_todos_los_datos
from recomendador_contenido import recomendar_por_contenido, generar_motivo_recomendacion


def mostrar_usuarios(usuarios):
    """
    Muestra los usuarios disponibles en el sistema.
    """
    print("\nUsuarios disponibles:")
    print("--------------------------------")

    for _, usuario in usuarios.iterrows():
        print(
            f"{usuario['id_usuario']}. {usuario['nombre']} "
            f"- Plataforma: {usuario['plataforma_preferida']} "
            f"- Género favorito: {usuario['genero_preferido']}"
        )


def mostrar_perfil_usuario(usuarios, id_usuario):
    """
    Muestra la información de un usuario concreto.
    """
    usuario = usuarios[usuarios["id_usuario"] == id_usuario]

    if usuario.empty:
        print("\nNo existe ningún usuario con ese ID.")
        return None

    usuario = usuario.iloc[0]

    print("\nPerfil del usuario seleccionado:")
    print("--------------------------------")
    print(f"Nombre: {usuario['nombre']}")
    print(f"Edad: {usuario['edad']}")
    print(f"Plataforma preferida: {usuario['plataforma_preferida']}")
    print(f"Presupuesto máximo: {usuario['presupuesto_max']}€")
    print(f"Género favorito: {usuario['genero_preferido']}")
    print(f"Tipo preferido: {usuario['tipo_preferido']}")

    return usuario


def mostrar_recomendaciones(recomendaciones, usuario):
    """
    Muestra las recomendaciones por consola.
    """
    print("\nRecomendaciones personalizadas:")
    print("--------------------------------")

    if not recomendaciones:
        print("No se han encontrado recomendaciones para este usuario.")
        return

    for i, juego in enumerate(recomendaciones, start=1):
        motivo = generar_motivo_recomendacion(juego, usuario)

        print(f"\n{i}. {juego['titulo']}")
        print(f"   Género: {juego['genero']}")
        print(f"   Plataforma: {juego['plataforma']}")
        print(f"   PEGI: {juego['pegi']}")
        print(f"   Precio: {juego['precio']}€")
        print(f"   Desarrolladora: {juego['desarrolladora']}")
        print(f"   Tipo: {juego['tipo']}")
        print(f"   Puntuación interna: {juego['puntuacion']}")
        print(f"   Motivo: {motivo}")


def main():
    juegos, usuarios, valoraciones = cargar_todos_los_datos()

    print("GameNest - Motor de Recomendación de Videojuegos")
    print("================================================")

    mostrar_usuarios(usuarios)

    try:
        id_usuario = int(input("\nIntroduce el ID del usuario: "))
    except ValueError:
        print("Debes introducir un número válido.")
        return

    usuario = mostrar_perfil_usuario(usuarios, id_usuario)

    if usuario is None:
        return

    recomendaciones = recomendar_por_contenido(
        juegos,
        usuarios,
        valoraciones,
        id_usuario,
        limite=5
    )

    mostrar_recomendaciones(recomendaciones, usuario)


if __name__ == "__main__":
    main()