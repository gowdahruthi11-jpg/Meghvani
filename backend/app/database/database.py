from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings, BACKEND_DIR
from app.database.migrations import run_migrations

# Normalize SQLite database URL so it consistently points to BACKEND_DIR / 'meghvani.db'
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
elif database_url.startswith("sqlite:///") and (database_url.endswith("/meghvani.db") or database_url.endswith("./meghvani.db") or database_url == "sqlite:///meghvani.db"):
    db_path = (BACKEND_DIR / "meghvani.db").resolve()
    database_url = f"sqlite:///{db_path.as_posix()}"

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False
)

# Run lightweight schema migrations for newly added columns
run_migrations(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
