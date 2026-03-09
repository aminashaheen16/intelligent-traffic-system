import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_counts (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT NOW(),
            vehicle_type VARCHAR(50),
            direction VARCHAR(20),
            video_source VARCHAR(255)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT NOW(),
            violation_type VARCHAR(50),
            vehicle_type VARCHAR(50),
            snapshot_path VARCHAR(255),
            video_source VARCHAR(255)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS parking_status (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT NOW(),
            slot_id INTEGER,
            status VARCHAR(20),
            vehicle_type VARCHAR(50)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_db()
