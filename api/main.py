from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_sqlachemy_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
from langchain_core.prompts import ChatPromptTemplate

logging.basicConfig(filename='app.log', level=logging.INFO)
app = FastAPI()



# @app.post("/chat", response_model=QueryResponse)
# def chat(query_input: QueryInput):
#     session_id = query_input.session_id
#     logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")
#     if not session_id:
#         session_id = str(uuid.uuid4())

    
#     chat_history = get_chat_history(session_id)
#     rag_chain = get_rag_chain(query_input.model.value)
#     answer = rag_chain.invoke({
#         "input": query_input.question,
#         "chat_history": chat_history
#     })['answer']
    
#     insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
#     logging.info(f"Session ID: {session_id}, AI Response: {answer}")
#     return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)

from db_sqlachemy_utils import insert_booking



@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")
    if not session_id:
        session_id = str(uuid.uuid4())

    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']

    # Check if the response contains booking information
    if "<booking>" in answer and "</booking>" in answer:
        # Extract booking details from the response
        booking_content = answer.split("<booking>")[1].split("</booking>")[0].strip()

        if "<confirm>" in booking_content and "</confirm>" in booking_content:
            # Handle confirmed bookings
            booking_data = booking_content.split("<confirm>")[1].split("</confirm>")[0].strip()
            try:
                booking = eval(booking_data)  # Safely parse the JSON-like response
                insert_booking(
                    name=booking["name"],
                    time=booking["time"],
                    date=booking["date"],
                    nums_of_customers=booking["nums_of_customers"],
                    restaurant_position=booking["restaurant_position"]
                )
                logging.info(f"Booking confirmed and added to database: {booking}")
            except Exception as e:
                logging.error(f"Failed to parse and insert confirmed booking: {e}")

        elif "<notconfirm>" in booking_content and "</notconfirm>" in booking_content:
            # Handle incomplete bookings
            booking_data = booking_content.split("<notconfirm>")[1].split("</notconfirm>")[0].strip()
            try:
                booking = eval(booking_data)  # Safely parse the JSON-like response
                logging.warning(f"Incomplete booking received: {booking}")
                # Optionally log or notify that additional information is needed
            except Exception as e:
                logging.error(f"Failed to parse incomplete booking: {e}")
        else:
            logging.warning("Unexpected booking format received.")

    
    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


from fastapi import UploadFile, File, HTTPException
import os
import shutil

@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")
    
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)
        
        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    # Delete from Chroma
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    if chroma_delete_success:
        # If successfully deleted from Chroma, delete from our database
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}

from db_sqlachemy_utils import get_all_bookings

@app.get("/getbooking")
def get_booking_data():
    """
    Retrieve all bookings from the database and return as JSON.
    """
    try:
        bookings = get_all_bookings()  # Fetch bookings from the database
        return {"status": "success", "data": bookings}
    except Exception as e:
        return {"status": "error", "message": str(e)}

