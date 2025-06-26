from database import engine
import sqlalchemy as sa

def fix_migrations():
    with engine.connect() as conn:
        # Delete existing version
        conn.execute(sa.text('DELETE FROM alembic_version'))
        # Insert create_tables migration version
        conn.execute(sa.text("INSERT INTO alembic_version (version_num) VALUES ('create_tables')"))
        conn.commit()

if __name__ == '__main__':
    fix_migrations()
    print("Migration version reset successfully") 