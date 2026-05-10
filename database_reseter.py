from app import create_app
from database import db

app = create_app()

with app.app_context():
    # Destruye todas las tablas y sus datos
    db.drop_all()

    # Las vuelve a crear limpias y vacías
    db.create_all()

    print("¡Base de datos formateada y lista para pruebas!")