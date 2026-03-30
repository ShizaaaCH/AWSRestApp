class Profesor:
    def __init__(self, id, numeroEmpleado, nombres, apellidos, horasClase):
        self.id = id
        self.numeroEmpleado = numeroEmpleado
        self.nombres = nombres
        self.apellidos = apellidos
        self.horasClase = horasClase

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
        required = ['id', 'numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
        
        for field in required:
            # 1. Validar nulos (null en Java -> None en Python)
            if field not in data or data[field] is None:
                return False, f"El campo {field} no puede ser nulo"
            
            # 2. Validar vacíos para strings
            if isinstance(data[field], str) and not data[field].strip():
                return False, f"El campo {field} no puede estar vacío"

        # 3. Validaciones de tipo y valores negativos (lo que hace fallar el test)
        if not isinstance(data['id'], int):
            return False, "ID debe ser entero"
            
        if not isinstance(data['numeroEmpleado'], int) or data['numeroEmpleado'] < 0:
            return False, "Número de empleado debe ser un entero positivo"
            
        if not isinstance(data['horasClase'], (int, float)) or data['horasClase'] < 0:
            return False, "Horas de clase debe ser un número positivo"
            
        return True, None