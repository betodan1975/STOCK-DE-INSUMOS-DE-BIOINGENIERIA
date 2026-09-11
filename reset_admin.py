"""Resetea (o crea) el usuario admin con la contrasena 'admin1234'.

Uso:
    cd api
    python reset_admin.py

Idempotente:
- Si el usuario admin no existe, lo crea con rol admin y activo=True.
- Si ya existe, le actualiza el password_hash a bcrypt('admin1234'),
  lo reactiva y se asegura de que tenga rol admin.

Reutiliza las funciones de hashing y la sesion de DB definidas
en auth.py / database.py / models.py.
"""
from __future__ import annotations

from auth import hash_password
from database import SessionLocal, engine
from models import Base, Usuario


PASSWORD_DEFECTO = "admin1234"
USERNAME_ADMIN = "admin"


def run() -> None:
    # Asegurar que las tablas existan (no rompe si ya estan).
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter_by(username=USERNAME_ADMIN).one_or_none()
        nuevo_hash = hash_password(PASSWORD_DEFECTO)

        if admin is None:
            admin = Usuario(
                username=USERNAME_ADMIN,
                password_hash=nuevo_hash,
                nombre="Administrador",
                rol="admin",
                activo=True,
            )
            db.add(admin)
            accion = "creado"
        else:
            admin.password_hash = nuevo_hash
            admin.activo = True
            admin.rol = "admin"
            accion = "actualizado"

        db.commit()
    finally:
        db.close()

    print("=" * 56)
    print(f"Usuario admin {accion} correctamente.")
    print(f"Usuario: {USERNAME_ADMIN} / Contrasena: {PASSWORD_DEFECTO}")
    print("Cambia la contrasena cuando puedas desde la app.")
    print("=" * 56)


if __name__ == "__main__":
    run()
