from sqlalchemy import inspect
from database import engine

def check_schema():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nExisting tables:")
    for table in tables:
        print(f"\n{table} table columns:")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")

if __name__ == "__main__":
    check_schema() 