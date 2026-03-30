from flask import Flask, jsonify, request, make_response
from models.Alumno import Alumno
from models.Profesor import Profesor

app = Flask(__name__)

db_alumnos = []
db_profesores = []

# Helper para forzar JSON y códigos de estado limpios
def responder_json(data, status):
    return make_response(jsonify(data), status)

# ==========================================
# ENDPOINTS ALUMNOS
# ==========================================

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    # El test espera Content-Type: application/json (jsonify lo hace)
    return responder_json([a.to_dict() for a in db_alumnos], 200)

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = next((a for a in db_alumnos if a.id == id), None)
    if alumno:
        return responder_json(alumno.to_dict(), 200)
    return responder_json({"error": "No encontrado"}, 404)

@app.route('/alumnos', methods=['POST'])
def post_alumno():
    data = request.get_json()
    if not data:
        return responder_json({"error": "Body vacío"}, 400)
    
    es_valido, error = Alumno.validar(data)
    if not es_valido:
        return responder_json({"error": error}, 400)
    
    # EL TEST MANDA SU PROPIO ID
    nuevo = Alumno(data['id'], data['nombres'], data['apellidos'], 
                   data['matricula'], data['promedio'])
    db_alumnos.append(nuevo)
    return responder_json(nuevo.to_dict(), 201)

@app.route('/alumnos/<int:id>', methods=['PUT'])
def put_alumno(id):
    data = request.get_json()
    alumno = next((a for a in db_alumnos if a.id == id), None)
    if not alumno:
        return responder_json({"error": "No encontrado"}, 404)
    
    es_valido, error = Alumno.validar(data)
    if not es_valido:
        return responder_json({"error": error}, 400)

    alumno.nombres = data['nombres']
    alumno.apellidos = data['apellidos']
    alumno.matricula = data['matricula']
    alumno.promedio = data['promedio']
    return responder_json(alumno.to_dict(), 200)

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    global db_alumnos
    alumno = next((a for a in db_alumnos if a.id == id), None)
    if not alumno:
        return responder_json({"error": "No encontrado"}, 404)
    
    db_alumnos = [a for a in db_alumnos if a.id != id]
    return responder_json({"mensaje": "Eliminado"}, 200)

# ==========================================
# ENDPOINTS PROFESORES
# ==========================================

@app.route('/profesores', methods=['GET'])
def get_profesores():
    return responder_json([p.__dict__ for p in db_profesores], 200)

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = next((p for p in db_profesores if p.id == id), None)
    if profesor:
        return responder_json(profesor.to_dict(), 200)
    return responder_json({"error": "No encontrado"}, 404)

@app.route('/profesores', methods=['POST'])
def post_profesor():
    data = request.get_json()
    if not data:
        return responder_json({"error": "Body vacío"}, 400)
    
    es_valido, error = Profesor.validar(data)
    if not es_valido:
        return responder_json({"error": error}, 400)
    
    nuevo = Profesor(data['id'], data['numeroEmpleado'], data['nombres'], 
                     data['apellidos'], data['horasClase'])
    db_profesores.append(nuevo)
    return responder_json(nuevo.to_dict(), 201)

@app.route('/profesores/<int:id>', methods=['PUT'])
def put_profesor(id):
    data = request.get_json()
    profesor = next((p for p in db_profesores if p.id == id), None)
    if not profesor:
        return responder_json({"error": "No encontrado"}, 404)
    
    es_valido, error = Profesor.validar(data)
    if not es_valido:
        return responder_json({"error": error}, 400)

    profesor.numeroEmpleado = data['numeroEmpleado']
    profesor.nombres = data['nombres']
    profesor.apellidos = data['apellidos']
    profesor.horasClase = data['horasClase']
    return responder_json(profesor.to_dict(), 200)

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    global db_profesores
    profesor = next((p for p in db_profesores if p.id == id), None)
    if not profesor:
        return responder_json({"error": "No encontrado"}, 404)
    
    db_profesores = [p for p in db_profesores if p.id != id]
    return responder_json({"mensaje": "Eliminado"}, 200)

# ==========================================
# RUN
# ==========================================    

if __name__ == '__main__':
    # Importante: host 0.0.0.0 para AWS
    app.run(host='0.0.0.0', port=5000)