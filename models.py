"""
models.py
---------
Modelos y acceso a datos de la version segura del laboratorio.

Toda la interaccion con la base de datos pasa por Flask-SQLAlchemy, lo que
elimina la construccion manual de consultas SQL y, con ello, la inyeccion SQL.
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey("estudiantes.id", ondelete="SET NULL"),
        nullable=True,
    )

    estudiante = db.relationship("Estudiante", backref="usuarios")

    def set_password(self, password):
        """Genera y almacena el hash de la contrasena."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """Verifica una contrasena contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.username}>"


class Estudiante(db.Model):
    __tablename__ = "estudiantes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    carrera = db.Column(db.String(120), nullable=False)
    biografia = db.Column(db.Text, default="")

    calificaciones = db.relationship(
        "Calificacion",
        backref="estudiante",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Estudiante {self.nombre}>"


class Calificacion(db.Model):
    __tablename__ = "calificaciones"

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey("estudiantes.id"),
        nullable=False,
    )
    materia = db.Column(db.String(120), nullable=False)
    nota = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Calificacion {self.materia}: {self.nota}>"


class Archivo(db.Model):
    __tablename__ = "archivos"

    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(512), nullable=False)
    subido_por = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    usuario = db.relationship("Usuario", backref="archivos")

    def __repr__(self):
        return f"<Archivo {self.nombre_archivo}>"


def init_db(app):
    """Inicializa SQLAlchemy, crea las tablas y carga datos de ejemplo."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not Usuario.query.first():
            seed_data()


def seed_data():
    """Carga datos de ejemplo equivalentes al laboratorio original."""
    estudiantes = [
        Estudiante(
            id=1,
            nombre="Ana Torres",
            carrera="Ingenieria de Sistemas",
            biografia="Estudiante de septimo semestre.",
        ),
        Estudiante(
            id=2,
            nombre="Luis Gomez",
            carrera="Ciberseguridad",
            biografia="Interesado en pentesting.",
        ),
        Estudiante(
            id=3,
            nombre="Maria Ruiz",
            carrera="Ciencia de Datos",
            biografia="Le gusta el machine learning.",
        ),
    ]
    db.session.add_all(estudiantes)
    db.session.flush()

    admin = Usuario(id=1, username="admin", rol="admin")
    admin.set_password("admin123")

    profesor = Usuario(id=2, username="profesor", rol="docente")
    profesor.set_password("clave456")

    estudiante = Usuario(
        id=3,
        username="estudiante",
        rol="estudiante",
        estudiante_id=1,
    )
    estudiante.set_password("1234")

    db.session.add_all([admin, profesor, estudiante])

    calificaciones = [
        Calificacion(estudiante_id=1, materia="Redes", nota=4.2),
        Calificacion(estudiante_id=1, materia="Bases de Datos", nota=3.8),
        Calificacion(estudiante_id=2, materia="Criptografia", nota=4.7),
        Calificacion(estudiante_id=3, materia="Estadistica", nota=3.5),
    ]
    db.session.add_all(calificaciones)
    db.session.commit()
