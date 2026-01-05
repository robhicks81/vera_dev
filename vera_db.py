import psycopg2

def log_interaction(speaker, message):
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname="vera_db",
            user="vera",
            password="vera_secure",
            host="localhost"
        )
        cur = conn.cursor()
        
        # Insert Log
        cur.execute(
            "INSERT INTO interaction_logs (speaker, message) VALUES (%s, %s)",
            (speaker, message)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"   [DB] Saved: {speaker} -> {message[:20]}...")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")