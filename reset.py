from sqlalchemy import text, inspect
from database import engine

def drop_specific_tables():
    tables = [
        "users",
        "chats",
        "messages",
        "medicines",
        "medications",
        "medication_schedules",
        "medication_logs",
        "insights",
        "bp_logs",
        "bp_schedules",
        "sugar_logs",
        "sugar_schedules",
        "connections",
        "doctor_profiles",
        "patient_profiles",
        "patient_notes",
        "reminders",
        "weight_logs",
        "user_roles"
    ]

    with engine.begin() as conn:
        for table in tables:
            print(f"Dropping table: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
    
    print("Specific tables dropped successfully.")

def drop_all_tables():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    with engine.begin() as conn:
        conn.execute(text("SET CONSTRAINTS ALL DEFERRED;"))
        
        for table in table_names:
            print(f"Dropping table: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
        
        conn.execute(text("SET CONSTRAINTS ALL IMMEDIATE;"))
    
    print(f"Successfully dropped {len(table_names)} tables:")
    for table in table_names:
        print(f"- {table}")

if __name__ == "__main__":
    # drop_specific_tables()  # Drops only the tables in the list
    drop_all_tables()    # Drops all tables in the database