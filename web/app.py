import sys
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.append(str(SRC_DIR))

from cargar_datos import cargar_todos_los_datos
from gestionar_usuarios import (
    crear_usuario,
    autenticar_usuario,
    obtener_usuario_por_id,
    actualizar_perfil
)
from recomendador_contenido import recomendar_por_contenido


app = Flask(__name__)
app.secret_key = "gamenest_clave_secreta_desarrollo"


PLATAFORMAS_DISPONIBLES = [
    "PC",
    "PS5",
    "Switch"
]


GENEROS_DISPONIBLES = [
    "RPG",
    "Accion",
    "Aventura",
    "Shooter",
    "Deportes",
    "Simulacion",
    "Conduccion",
    "Battle Royale",
    "Plataformas",
    "Lucha",
    "Metroidvania",
    "Roguelike",
    "Sandbox",
    "Mundo abierto",
    "Terror",
    "Competitivo",
    "Exploracion",
    "Estrategia",
    "MOBA",
    "Gestion",
    "Relax",
    "Narrativo",
    "Familiar",
    "Arcade",
    "Fantasia",
    "JRPG",
    "Cooperativo"
]


TIPOS_DISPONIBLES = [
    "Singleplayer",
    "Multiplayer"
]


def convertir_cadena_a_lista(texto):
    """
    Convierte una cadena separada por ';' en una lista.
    """
    if not texto:
        return []

    return [elemento.strip() for elemento in str(texto).split(";") if elemento.strip()]


def usuario_actual():
    """
    Devuelve el usuario actualmente autenticado.
    """
    id_usuario = session.get("id_usuario")

    if not id_usuario:
        return None

    return obtener_usuario_por_id(id_usuario)


@app.route("/")
def index():
    usuario = usuario_actual()
    return render_template("index.html", usuario=usuario)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        username = request.form["username"]
        password = request.form["password"]
        edad = request.form["edad"]
        presupuesto_max = request.form["presupuesto_max"]

        plataformas_preferidas = ";".join(request.form.getlist("plataformas_preferidas"))
        generos_preferidos = ";".join(request.form.getlist("generos_preferidos"))
        tipos_preferidos = ";".join(request.form.getlist("tipos_preferidos"))

        if not plataformas_preferidas:
            flash("Debes seleccionar al menos una plataforma.", "error")
            return redirect(url_for("registro"))

        if not generos_preferidos:
            flash("Debes seleccionar al menos un género.", "error")
            return redirect(url_for("registro"))

        if not tipos_preferidos:
            flash("Debes seleccionar al menos un tipo de juego.", "error")
            return redirect(url_for("registro"))

        try:
            nuevo_usuario = crear_usuario(
                nombre,
                username,
                password,
                edad,
                plataformas_preferidas,
                presupuesto_max,
                generos_preferidos,
                tipos_preferidos
            )

            session["id_usuario"] = int(nuevo_usuario["id_usuario"])
            flash("Cuenta creada correctamente.", "success")
            return redirect(url_for("perfil"))

        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("registro"))

    return render_template(
        "registro.html",
        plataformas_disponibles=PLATAFORMAS_DISPONIBLES,
        generos_disponibles=GENEROS_DISPONIBLES,
        tipos_disponibles=TIPOS_DISPONIBLES
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        usuario = autenticar_usuario(username, password)

        if usuario is None:
            flash("Usuario o contraseña incorrectos.", "error")
            return redirect(url_for("login"))

        session["id_usuario"] = int(usuario["id_usuario"])
        flash("Sesión iniciada correctamente.", "success")
        return redirect(url_for("perfil"))

    return render_template("login.html")


@app.route("/perfil")
def perfil():
    usuario = usuario_actual()

    if usuario is None:
        flash("Debes iniciar sesión para acceder a tu perfil.", "error")
        return redirect(url_for("login"))

    return render_template("perfil.html", usuario=usuario)


@app.route("/editar-perfil", methods=["GET", "POST"])
def editar_perfil():
    usuario = usuario_actual()

    if usuario is None:
        flash("Debes iniciar sesión para editar tu perfil.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        plataformas_preferidas = ";".join(request.form.getlist("plataformas_preferidas"))
        generos_preferidos = ";".join(request.form.getlist("generos_preferidos"))
        tipos_preferidos = ";".join(request.form.getlist("tipos_preferidos"))

        if not plataformas_preferidas:
            flash("Debes seleccionar al menos una plataforma.", "error")
            return redirect(url_for("editar_perfil"))

        if not generos_preferidos:
            flash("Debes seleccionar al menos un género.", "error")
            return redirect(url_for("editar_perfil"))

        if not tipos_preferidos:
            flash("Debes seleccionar al menos un tipo de juego.", "error")
            return redirect(url_for("editar_perfil"))

        usuario_actualizado = actualizar_perfil(
            usuario["id_usuario"],
            request.form["nombre"],
            request.form["edad"],
            plataformas_preferidas,
            request.form["presupuesto_max"],
            generos_preferidos,
            tipos_preferidos
        )

        if usuario_actualizado is None:
            flash("No se pudo actualizar el perfil.", "error")
            return redirect(url_for("perfil"))

        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("perfil"))

    plataformas_usuario = convertir_cadena_a_lista(usuario.get("plataformas_preferidas"))
    generos_usuario = convertir_cadena_a_lista(usuario.get("generos_preferidos"))
    tipos_usuario = convertir_cadena_a_lista(usuario.get("tipos_preferidos"))

    return render_template(
        "editar_perfil.html",
        usuario=usuario,
        plataformas_disponibles=PLATAFORMAS_DISPONIBLES,
        generos_disponibles=GENEROS_DISPONIBLES,
        tipos_disponibles=TIPOS_DISPONIBLES,
        plataformas_usuario=plataformas_usuario,
        generos_usuario=generos_usuario,
        tipos_usuario=tipos_usuario
    )


@app.route("/recomendaciones")
def recomendaciones():
    usuario = usuario_actual()

    if usuario is None:
        flash("Debes iniciar sesión para ver recomendaciones.", "error")
        return redirect(url_for("login"))

    juegos, usuarios, valoraciones = cargar_todos_los_datos()

    recomendaciones_generadas = recomendar_por_contenido(
        juegos,
        usuarios,
        valoraciones,
        int(usuario["id_usuario"]),
        limite=12
    )

    return render_template(
        "recomendaciones.html",
        usuario=usuario,
        recomendaciones=recomendaciones_generadas
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)