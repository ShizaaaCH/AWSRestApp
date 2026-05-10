from database import db

class Alumno(db.Model):
    __tablename__ = 'alumnos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), nullable=False, unique=True)
    promedio = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fotoPerfilUrl = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio,
            "fotoPerfilUrl": self.fotoPerfilUrl
        }

    @staticmethod
    def validar(data):
        required = ['nombres', 'apellidos', 'matricula', 'promedio', 'password']
        for field in required:
            # Validar que el campo exista y no sea None (null en Java)
            if field not in data or data[field] is None:
                return False, f"Campo {field} es nulo o falta"
            # Validar que no sea un string vacío
            if isinstance(data[field], str) and not data[field].strip():
                return False, f"Campo {field} está vacío"
        
        # Validaciones de tipo y valores lógicos
        if not isinstance(data['promedio'], (int, float)) or data['promedio'] < 0:
            return False, "Promedio debe ser un número positivo"
        if not isinstance(data['matricula'], str):
            return False, "Matrícula debe ser un texto"
            
        return True, None