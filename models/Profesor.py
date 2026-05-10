from database import db
class Profesor(db.Model):
    __tablename__ = 'profesores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numeroEmpleado = db.Column(db.Integer, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "numeroEmpleado": self.numeroEmpleado,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "horasClase": self.horasClase
        }

    @staticmethod
    def validar(data):
        # Campos exactos que pide el test de Java
        required = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
        
        for field in required:
            # 1. Validar nulos (null en Java -> None en Python)
            if field not in data or data[field] is None:
                return False, f"El campo {field} no puede ser nulo"
            
            # 2. Validar vacíos para strings
            if isinstance(data[field], str) and not data[field].strip():
                return False, f"El campo {field} no puede estar vacío"

        # 3. Validaciones de tipo y valores negativos (lo que hace fallar el test)
        if not isinstance(data['numeroEmpleado'], int) or data['numeroEmpleado'] < 0:
            return False, "Número de empleado debe ser un entero positivo"
            
        if not isinstance(data['horasClase'], int) or data['horasClase'] < 0:
            return False, "Horas de clase debe ser un número positivo entero"
            
        return True, None