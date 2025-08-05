import psycopg2
import getpass

def get_db_connection():
    user = input("Enter DB username: ")
    password = getpass.getpass("Enter DB password: ")
    host = input("Enter DB host (e.g., localhost): ")
    port = input("Enter DB port (default 5432): ") or "5432"
    dbname = input("Enter DB name: ")

    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

def process_images_table(conn):
    cursor = conn.cursor()

    # Fetch all rows
    cursor.execute("SELECT id, name FROM images;")
    rows = cursor.fetchall()

    cat_rows = [row for row in rows if row[1].lower() == 'cat']
    dog_rows = [row for row in rows if row[1].lower() == 'dog']

    print(f"Found {len(cat_rows)} cat(s) and {len(dog_rows)} dog(s).")

    # Insert into cat table
    if cat_rows:
        cursor.executemany("INSERT INTO cat (id, name) VALUES (%s, %s);", cat_rows)

    # Insert into dog table
    if dog_rows:
        cursor.executemany("INSERT INTO dog (id, name) VALUES (%s, %s);", dog_rows)

    # Delete all rows from images table
    cursor.execute("DELETE FROM images;")
    conn.commit()
    cursor.close()
    print("Images table processed and cleared.")

def main():
    try:
        conn = get_db_connection()
        process_images_table(conn)
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
