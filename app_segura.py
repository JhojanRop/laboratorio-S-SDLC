"""
app_segura.py
-------------
Version segura del laboratorio de Gestion Academica.

Rutas equivalentes a app.py, pero con las vulnerabilidades corregidas:
  1. SQLi      -> consultas ORM parametrizadas (Flask-SQLAlchemy).
  2. XSS       -> salida escapada por defecto (sin ``| safe``).
  3. IDOR      -> control de acceso por rol y propietario.
  4. Uploads   -> nombre seguro, whitelist de extensiones y limite de tamano.
"""

import os
from functools import wraps
from uuid import uuid4

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from config import config
from models import Archivo, Calificacion, Estudiante, Usuario, db, init_db

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "txt"}

app = Flask(__name__, template_folder="templates_seguras")
env = os.getenv("APP_ENV", "development")
app.config.from_object(config.get(env, config["default"]))

print("Prueba")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY no configurada. Revisa tu archivo .env")

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

init_db(app)


def login_required(view):
    """Redirige al login cuando no hay una sesion activa."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def is_staff():
    """Indica si el usuario actual es administrador o docente."""
    return session.get("rol") in ("admin", "docente")


@app.after_request
def security_headers(response):
    """Cabeceras HTTP de endurecimiento."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; object-src 'none'; base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@app.route("/")
def inicio():
    """Pagina de inicio con el banner del laboratorio."""
    return render_template("index.html", usuario=session.get("username"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Inicio de sesion con consulta parametrizada (sin SQLi)."""
    error = None
    if request.method == "POST":
        usuario = request.form.get("username", "").strip()
        clave = request.form.get("password", "")

        user = Usuario.query.filter_by(username=usuario).first()

        if user and user.check_password(clave):
            session.clear()  # Evita fijacion de sesion.
            session["username"] = user.username
            session["rol"] = user.rol
            session["user_id"] = user.id
            session["estudiante_id"] = user.estudiante_id
            return redirect(url_for("inicio"))

        error = "Credenciales invalidas"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/buscar")
def buscar():
    """Buscador de estudiantes con consulta ORM parametrizada."""
    termino = request.args.get("q", "").strip()
    resultados = []
    if termino:
        resultados = Estudiante.query.filter(Estudiante.nombre.ilike(f"%{termino}%")).all()
    return render_template("buscar.html", resultados=resultados, termino=termino)


@app.route("/perfil/<int:id>")
def perfil(id):
    """Muestra el perfil de un estudiante con autoescape de Jinja2."""
    estudiante = db.get_or_404(Estudiante, id)
    notas = Calificacion.query.filter_by(estudiante_id=id).all()
    return render_template("perfil.html", estudiante=estudiante, notas=notas)


@app.route("/perfil/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_biografia(id):
    """Permite editar la biografia solo al propietario o al personal."""
    estudiante = db.get_or_404(Estudiante, id)

    if not is_staff() and session.get("estudiante_id") != id:
        abort(403)

    if request.method == "POST":
        bio = request.form.get("biografia", "").strip()
        if len(bio) > 2000:
            return (
                render_template(
                    "editar_biografia.html",
                    estudiante=estudiante,
                    error="La biografia no puede superar los 2000 caracteres.",
                ),
                400,
            )
        estudiante.biografia = bio
        db.session.commit()
        return redirect(url_for("perfil", id=id))

    return render_template("editar_biografia.html", estudiante=estudiante)


@app.route("/nota/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_nota(id):
    """Edita una nota solo si el usuario es personal o el propietario."""
    calificacion = db.get_or_404(Calificacion, id)

    if not is_staff() and session.get("estudiante_id") != calificacion.estudiante_id:
        abort(403)

    if request.method == "POST":
        try:
            nueva_nota = float(request.form.get("nota", ""))
        except ValueError:
            return (
                render_template(
                    "editar_nota.html",
                    calificacion=calificacion,
                    error="La nota debe ser un numero valido.",
                ),
                400,
            )

        if not 0 <= nueva_nota <= 5:
            return (
                render_template(
                    "editar_nota.html",
                    calificacion=calificacion,
                    error="La nota debe estar entre 0 y 5.",
                ),
                400,
            )

        calificacion.nota = nueva_nota
        db.session.commit()
        return redirect(url_for("buscar"))

    return render_template("editar_nota.html", calificacion=calificacion)


@app.route("/subir", methods=["GET", "POST"])
@login_required
def subir():
    """Sube archivos validando nombre, extension y tamano."""
    mensaje = None
    if request.method == "POST":
        archivo = request.files.get("archivo")
        if archivo and archivo.filename:
            nombre_original = secure_filename(archivo.filename)
            if not nombre_original:
                mensaje = "Nombre de archivo invalido."
            else:
                extension = (
                    nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""
                )
                if extension not in ALLOWED_EXTENSIONS:
                    mensaje = (
                        "Extension no permitida. Permitidas: "
                        f"{', '.join(sorted(ALLOWED_EXTENSIONS))}."
                    )
                else:
                    nombre_unico = f"{uuid4().hex}.{extension}"
                    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)
                    archivo.save(ruta)

                    registro = Archivo(
                        nombre_archivo=nombre_original,
                        ruta=ruta,
                        subido_por=session.get("user_id"),
                    )
                    db.session.add(registro)
                    db.session.commit()
                    mensaje = f"Archivo '{nombre_original}' subido correctamente."

    return render_template(
        "subir.html",
        mensaje=mensaje,
        extensiones=sorted(ALLOWED_EXTENSIONS),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3001, debug=app.config["DEBUG"])
