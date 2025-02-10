from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///App_SQLAchemy.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# ========== MODELS ==========
class ApplicationLog(Base):
    __tablename__ = "application_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    user_query = Column(String, nullable=False)
    gpt_response = Column(String, nullable=False)
    model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentStore(Base):
    __tablename__ = "document_store"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    time = Column(String, nullable=False)
    date = Column(String, nullable=False)
    nums_of_customers = Column(Integer, nullable=False)
    restaurant_position = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(bind=engine)


# ========== DATABASE FUNCTIONS ==========

def insert_application_logs(session_id: str, user_query: str, gpt_response: str, model: str):
    session = SessionLocal()
    try:
        log = ApplicationLog(session_id=session_id, user_query=user_query, gpt_response=gpt_response, model=model)
        session.add(log)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting log: {e}")
    finally:
        session.close()


def get_chat_history(session_id: str):
    session = SessionLocal()
    try:
        logs = session.query(ApplicationLog).filter(ApplicationLog.session_id == session_id).order_by(ApplicationLog.created_at).all()
        return [{"role": "human", "content": log.user_query} for log in logs] + \
               [{"role": "ai", "content": log.gpt_response} for log in logs]
    finally:
        session.close()


def insert_document_record(filename: str):
    session = SessionLocal()
    try:
        doc = DocumentStore(filename=filename)
        session.add(doc)
        session.commit()
        return doc.id
    except Exception as e:
        session.rollback()
        print(f"Error inserting document record: {e}")
        return None
    finally:
        session.close()


def delete_document_record(file_id: int):
    session = SessionLocal()
    try:
        doc = session.query(DocumentStore).filter(DocumentStore.id == file_id).first()
        if doc:
            session.delete(doc)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting document record: {e}")
        return False
    finally:
        session.close()


def get_all_documents():
    session = SessionLocal()
    try:
        docs = session.query(DocumentStore).order_by(DocumentStore.upload_timestamp.desc()).all()
        return [{"id": doc.id, "filename": doc.filename, "upload_timestamp": doc.upload_timestamp} for doc in docs]
    finally:
        session.close()


def insert_booking(name: str, time: str, date: str, nums_of_customers: int, restaurant_position: str):
    session = SessionLocal()
    try:
        new_booking = Booking(
            name=name,
            time=time,
            date=date,
            nums_of_customers=nums_of_customers,
            restaurant_position=restaurant_position
        )
        session.add(new_booking)
        session.commit()
        print("Booking added successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error inserting booking: {e}")
    finally:
        session.close()


def get_all_bookings():
    session = SessionLocal()
    try:
        bookings = session.query(Booking).order_by(Booking.created_at.desc()).all()
        return [{"id": b.id, "name": b.name, "time": b.time, "date": b.date, "nums_of_customers": b.nums_of_customers,
                 "restaurant_position": b.restaurant_position, "created_at": b.created_at} for b in bookings]
    finally:
        session.close()


def delete_booking_row(booking_id: int):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            session.delete(booking)
            session.commit()
            print(f"Booking {booking_id} deleted successfully!")
        else:
            print(f"Booking {booking_id} not found.")
    except Exception as e:
        session.rollback()
        print(f"Error deleting booking: {e}")
    finally:
        session.close()


def delete_table(table_name: str):
    session = SessionLocal()
    try:
        session.execute(f"DROP TABLE IF EXISTS {table_name}")
        session.commit()
        print(f"Table {table_name} deleted successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error deleting table {table_name}: {e}")
    finally:
        session.close()
