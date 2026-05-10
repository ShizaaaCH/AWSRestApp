import os
from flask import Flask, jsonify, request, make_response
from models.Alumno import Alumno
from models.Profesor import Profesor
from database import db
from s3_handler import upload_file_to_s3
from sns_handler import publish_message_to_sns
from dotenv import load_dotenv
from dynamodb_handler import create_session, get_session, deactivate_session

load_dotenv()

def create_app():
    app = Flask(__name__)

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    def responder_json(data, status):
        return make_response(jsonify(data), status)

    def get_json_body():
        data = request.get_json(silent=True)
        if not data:
            return None, responder_json({"error": "Body vacío"}, 400)
        return data, None

    #---- ALUMNOS ------------------------------

    @app.route("/alumnos", methods=["GET"])
    def get_alumnos():
        alumnos = Alumno.query.all()
        return responder_json([a.to_dict() for a in alumnos], 200)

    @app.route("/alumnos/<int:id>", methods=["GET"])
    def get_alumno(id):
        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)
        return responder_json(alumno.to_dict(), 200)

    @app.route("/alumnos", methods=["POST"])
    def post_alumno():
        data, error_response = get_json_body()
        if error_response:
            return error_response

        es_valido, error = Alumno.validar(data)
        if not es_valido:
            return responder_json({"error": error}, 400)

        nuevo = Alumno(
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            matricula=data["matricula"],
            promedio=data["promedio"],
            password=data["password"],
        )

        try:
            db.session.add(nuevo)
            db.session.commit()
            return responder_json(nuevo.to_dict(), 201)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al guardar en la base de datos"}, 500)

    @app.route("/alumnos/<int:id>", methods=["PUT"])
    def put_alumno(id):
        data, error_response = get_json_body()
        if error_response:
            return error_response

        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)

        es_valido, error = Alumno.validar(data)
        if not es_valido:
            return responder_json({"error": error}, 400)

        try:
            alumno.nombres = data["nombres"]
            alumno.apellidos = data["apellidos"]
            alumno.matricula = data["matricula"]
            alumno.promedio = data["promedio"]
            alumno.password = data["password"]
            alumno.fotoPerfilUrl = data.get("fotoPerfilUrl")

            db.session.commit()
            return responder_json(alumno.to_dict(), 200)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al actualizar el alumno"}, 500)

    @app.route("/alumnos/<int:id>", methods=["DELETE"])
    def delete_alumno(id):
        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)

        try:
            db.session.delete(alumno)
            db.session.commit()
            return responder_json({"mensaje": "Eliminado"}, 200)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al eliminar el alumno"}, 500)

    @app.route("/alumnos/<int:id>/fotoPerfil", methods=["POST"])
    def post_alumno_foto(id):
        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)

        file = request.files.get("foto")
        if not file:
            return responder_json({"error": "No se proporcionó ningún archivo"}, 400)

        url = upload_file_to_s3(file, id)
        if not url:
            return responder_json({"error": "Error al subir archivo"}, 500)

        try:
            alumno.fotoPerfilUrl = url
            db.session.commit()
            return responder_json(alumno.to_dict(), 200)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al guardar la URL de la foto"}, 500)

    @app.route("/alumnos/<int:id>/email", methods=["POST"])
    def post_alumno_mail(id):
        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)
        
        mensaje = f"Registro de alumno:\nNombre: {alumno.nombres} {alumno.apellidos}\nMatrícula: {alumno.matricula}\nPromedio: {alumno.promedio}"
        topic = "Registro de alumno"

        exito = publish_message_to_sns(mensaje, topic)
        if not exito:
            return responder_json({"error": "Error al enviar mensaje"}, 500)
        
        return responder_json({"mensaje": "Mensaje enviado"}, 200)

    @app.route("/alumnos/<int:id>/session/login", methods=["POST"])
    def login_alumno(id):
        alumno = db.session.get(Alumno, id)
        if not alumno:
            return responder_json({"error": "No encontrado"}, 404)

        data, error_response = get_json_body()
        if error_response:
            return error_response

        password = data.get("password")
        if not password:
            return responder_json({"error": "Falta el campo 'password'"}, 400)

        #debería regresar 401 si la contraseña es incorrecta, pero para no revelar que el alumno existe o no, se regresa 401 tanto para alumno no encontrado como para contraseña incorrecta
        if password != alumno.password:
            return responder_json({"error": "Contraseña incorrecta"}, 400)

        session_string = create_session(id)
        return responder_json({"sessionString": session_string}, 200)
    
    @app.route("/alumnos/<int:id>/session/verify", methods=["POST"])
    def verify_session(id):
        data, error_response = get_json_body()
        if error_response:
            return error_response

        session_string = data.get("sessionString")
        if not session_string:
            return responder_json({"error": "Falta el campo 'sessionString'"}, 400)

        session = get_session(session_string)
        if not session or not session.get("active") or session.get("alumnoID") != id:
            return responder_json({"error": "Sesión inválida"}, 400)

        return responder_json({"mensaje": "Sesión válida"}, 200)
    
    @app.route("/alumnos/<int:id>/session/logout", methods=["POST"])
    def logout_alumno(id):
        data, error_response = get_json_body()
        if error_response:
            return error_response

        session_string = data.get("sessionString")
        if not session_string:
            return responder_json({"error": "Falta el campo 'sessionString'"}, 400)

        session = get_session(session_string)
        if not session or session.get("alumnoID") != id:
            return responder_json({"error": "Sesión inválida"}, 401)

        deactivate_session(session_string)
        return responder_json({"mensaje": "Sesión cerrada"}, 200)


    # ---- PROFESORES ------------------------------

    @app.route("/profesores", methods=["GET"])
    def get_profesores():
        profesores = Profesor.query.all()
        return responder_json([p.to_dict() for p in profesores], 200)

    @app.route("/profesores/<int:id>", methods=["GET"])
    def get_profesor(id):
        profesor = db.session.get(Profesor, id)
        if not profesor:
            return responder_json({"error": "No encontrado"}, 404)
        return responder_json(profesor.to_dict(), 200)

    @app.route("/profesores", methods=["POST"])
    def post_profesor():
        data, error_response = get_json_body()
        if error_response:
            return error_response

        es_valido, error = Profesor.validar(data)
        if not es_valido:
            return responder_json({"error": error}, 400)

        nuevo = Profesor(
            numeroEmpleado=data["numeroEmpleado"],
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            horasClase=data["horasClase"]
        )

        try:
            db.session.add(nuevo)
            db.session.commit()
            return responder_json(nuevo.to_dict(), 201)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al guardar en la base de datos"}, 500)

    @app.route("/profesores/<int:id>", methods=["PUT"])
    def put_profesor(id):
        data, error_response = get_json_body()
        if error_response:
            return error_response

        profesor = db.session.get(Profesor, id)
        if not profesor:
            return responder_json({"error": "No encontrado"}, 404)

        es_valido, error = Profesor.validar(data)
        if not es_valido:
            return responder_json({"error": error}, 400)

        try:
            profesor.numeroEmpleado = data["numeroEmpleado"]
            profesor.nombres = data["nombres"]
            profesor.apellidos = data["apellidos"]
            profesor.horasClase = data["horasClase"]

            db.session.commit()
            return responder_json(profesor.to_dict(), 200)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al actualizar el profesor"}, 500)

    @app.route("/profesores/<int:id>", methods=["DELETE"])
    def delete_profesor(id):
        profesor = db.session.get(Profesor, id)
        if not profesor:
            return responder_json({"error": "No encontrado"}, 404)

        try:
            db.session.delete(profesor)
            db.session.commit()
            return responder_json({"mensaje": "Eliminado"}, 200)
        except Exception:
            db.session.rollback()
            return responder_json({"error": "Error al eliminar el profesor"}, 500)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)