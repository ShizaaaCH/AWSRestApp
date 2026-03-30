class Alumno:
    def __init__(self, _id, _nombres, _apellidos, _matricula, _promedio):
        self.id = _id
        self.nombres = _nombres
        self.apellidos = _apellidos
        self.matricula = _matricula
        self.promedio = _promedio

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio
        }

    @staticmethod
    def validar(data):
        required = ['id', 'nombres', 'apellidos', 'matricula', 'promedio']
        for field in required:
            # Validar que el campo exista y no sea None (null en Java)
            if field not in data or data[field] is None:
                return False, f"Campo {field} es nulo o falta"
            # Validar que no sea un string vacío
            if isinstance(data[field], str) and not data[field].strip():
                return False, f"Campo {field} está vacío"
        
        # Validaciones de tipo y valores lógicos
        if not isinstance(data['id'], int):
            return False, "ID debe ser entero"
        if not isinstance(data['promedio'], (int, float)) or data['promedio'] < 0:
            return False, "Promedio debe ser un número positivo"
        if not isinstance(data['matricula'], str):
            return False, "Matrícula debe ser un texto"
            
        return True, None