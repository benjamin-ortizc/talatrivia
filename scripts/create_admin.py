from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def create_admin(name: str, email: str, password: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("create_admin: el usuario ya existe")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN.value,
        )
        db.add(admin)
        db.commit()
        print("create_admin: usuario creado correctamente")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin(
        name="admin",
        email="admin@test.cl",
        password="admin",
    )