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
from recomendador_contenido import recomendar_por_contenido, generar_motivo_recomendacion


app = Flask(__name__)
app.secret_key = "gamenest_clave_secreta_desarrollo"


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
        plataforma_preferida = request.form["plataforma_preferida"]
        presupuesto_max = request.form["presupuesto_max"]
        genero_preferido = request.form["genero_preferido"]
        tipo_preferido = request.form["tipo_preferido"]

        try:
            nuevo_usuario = crear_usuario(
                nombre,
                username,
                password,
                edad,
                plataforma_preferida,
                presupuesto_max,
                genero_preferido,
                tipo_preferido
            )

            session["id_usuario"] = int(nuevo_usuario["id_usuario"])
            flash("Cuenta creada correctamente.", "success")
            return redirect(url_for("perfil"))

        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("registro"))

    return render_template("registro.html")


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
        usuario_actualizado = actualizar_perfil(
            usuario["id_usuario"],
            request.form["nombre"],
            request.form["edad"],
            request.form["plataforma_preferida"],
            request.form["presupuesto_max"],
            request.form["genero_preferido"],
            request.form["tipo_preferido"]
        )

        if usuario_actualizado is None:
            flash("No se pudo actualizar el perfil.", "error")
            return redirect(url_for("perfil"))

        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("perfil"))

    return render_template("editar_perfil.html", usuario=usuario)


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
        limite=5
    )

    for juego in recomendaciones_generadas:
        juego["motivo"] = generar_motivo_recomendacion(juego, usuario)

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