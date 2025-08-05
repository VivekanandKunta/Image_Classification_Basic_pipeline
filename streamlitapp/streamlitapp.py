import streamlit as st
import psycopg2
import pandas as pd
import random

def get_db_connection():
    return psycopg2.connect(
        dbname="image_classification_pipeline",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )

def fetch_table_data(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

def display_table(title, df):
    st.subheader(title)
    if df.empty:
        st.write("Table is empty")
    else:
        st.dataframe(df)

def process_images_table(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM images;")
    rows = cursor.fetchall()
    cat_rows = [row for row in rows if row[1].lower() == 'cat']
    dog_rows = [row for row in rows if row[1].lower() == 'dog']
    
    if cat_rows:
        cursor.executemany("INSERT INTO cat (id, name) VALUES (%s, %s);", cat_rows)
    if dog_rows:
        cursor.executemany("INSERT INTO dog (id, name) VALUES (%s, %s);", dog_rows)
    
    cursor.execute("DELETE FROM images;")
    conn.commit()
    cursor.close()
    return len(cat_rows), len(dog_rows)

def reset_to_original(conn, original_images):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cat;")
    cursor.execute("DELETE FROM dog;")
    if original_images:
        cursor.executemany("INSERT INTO images (id, name) VALUES (%s, %s);", original_images)
    conn.commit()
    cursor.close()

def insert_random_data(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM images;")
    animals = ['cat', 'dog']
    random_data = [(i, random.choice(animals)) for i in range(1, random.randint(5, 10))]
    cursor.executemany("INSERT INTO images (id, name) VALUES (%s, %s);", random_data)
    cursor.execute("DELETE FROM cat;")
    cursor.execute("DELETE FROM dog;")
    conn.commit()
    cursor.close()
    return random_data

def main():
    st.title("Image Classification Pipeline")
    
    try:
        conn = get_db_connection()
        
        # Store original state
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM images;")
        original_images = cursor.fetchall()
        cursor.close()
        
        # Display initial state
        st.header("Before Processing")
        for table in ['images', 'cat', 'dog']:
            df = fetch_table_data(conn, table)
            display_table(f"{table.capitalize()} Table", df)
        
        # Process button
        if st.button("Process Images Table"):
            cat_count, dog_count = process_images_table(conn)
            st.success(f"Processed: {cat_count} cat(s) and {dog_count} dog(s) moved to respective tables.")
            
            # Display state after processing
            st.header("After Processing")
            for table in ['images', 'cat', 'dog']:
                df = fetch_table_data(conn, table)
                display_table(f"{table.capitalize()} Table", df)
        
        # Reset and random insert buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset to Original"):
                reset_to_original(conn, original_images)
                st.success("Database reset to original state.")
                st.rerun()
        with col2:
            if st.button("Insert Random Data"):
                new_data = insert_random_data(conn)
                st.success(f"Inserted {len(new_data)} random records.")
                st.rerun()
                
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
