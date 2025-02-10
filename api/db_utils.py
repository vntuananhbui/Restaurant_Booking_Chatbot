import sqlite3
from datetime import datetime

DB_NAME = "/Users/macintosh/TA-DOCUMENT/StudyZone/FPT_WORK/IVY Training/FSoft_LLMEngineer_Phase1_FAQBookingChatbot/Phase 1/RAG_FastAPI/api/rag_app1.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_query TEXT,
                     gpt_response TEXT,
                     model TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def create_document_store():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     filename TEXT,
                     upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages


def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def delete_document_record(file_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return True

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC')
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]



# Initialize the database tables
create_application_logs()
create_document_store()

#==========BOOKING INFORMATION===========
def create_booking_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     time TEXT,
                     date TEXT,
                     nums_of_customers INTEGER,
                     restaurant_position TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_booking(name, time, date, nums_of_customers, restaurant_position):
    conn = get_db_connection()
    conn.execute('INSERT INTO bookings (name, time, date, nums_of_customers, restaurant_position) VALUES (?, ?, ?, ?, ?)',
                 (name, time, date, nums_of_customers, restaurant_position))
    conn.commit()
    print("Add Booking complete!")

    conn.close()

def get_all_bookings():
    """
    Retrieve all bookings from the database.
    """
    conn = get_db_connection()
    cursor = conn.execute('''SELECT name, time, date, nums_of_customers, restaurant_position FROM bookings ORDER BY created_at DESC''')
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    return [dict(row) for row in rows]



# Initialize the booking table
create_booking_table()


def delete_table(table_name: str):
    """
    Delete an entire table from the database.
    """
    conn = sqlite3.connect("rag_app1.db")  # Replace with your database name
    try:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        print("Delte complete!")
        conn.commit()
    finally:
        conn.close()

def delete_booking_row(row_id: int):
    """
    Delete a specific row from the bookings table based on its ID.
    """
    conn = sqlite3.connect(DB_NAME)  # Replace with your database name
    try:
        conn.execute("DELETE FROM bookings WHERE id = ?", (row_id,))
        conn.commit()
    finally:
        conn.close()




