import streamlit as st
from api_utils import upload_document, list_documents, delete_document
from chat_interface import display_booking_schedule
from chat_interface import display_chat_interface


def display_sidebar():
    
    # Sidebar Tabs
    tabs = st.sidebar.radio("Role", options=["Customer Chat", "Owner"])

    if tabs == "Owner":
        # Sidebar: Model Selection
        model_options = ["gemini-1.5-pro"]
        st.sidebar.selectbox("Model", options=model_options, key="model")
        # Sidebar: Upload Document
        st.sidebar.header("Upload Document")
        uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf"])
        if uploaded_file is not None:
            if st.sidebar.button("Upload"):
                with st.spinner("Uploading..."):
                    upload_response = upload_document(uploaded_file)
                    if upload_response:
                        st.sidebar.success(f"File '{uploaded_file.name}' uploaded successfully with ID {upload_response['file_id']}.")
                        st.session_state.documents = list_documents()  # Refresh the list after upload

        # Sidebar: List Documents
        st.sidebar.header("Uploaded Documents")
        if st.sidebar.button("Refresh Document List"):
            with st.spinner("Refreshing..."):
                st.session_state.documents = list_documents()

        # Initialize document list if not present
        if "documents" not in st.session_state:
            st.session_state.documents = list_documents()

        documents = st.session_state.documents
        if documents:
            for doc in documents:
                st.sidebar.text(f"{doc['filename']} (ID: {doc['id']}, Uploaded: {doc['upload_timestamp']})")
            
            # Delete Document
            selected_file_id = st.sidebar.selectbox("Select a document to delete", options=[doc['id'] for doc in documents], format_func=lambda x: next(doc['filename'] for doc in documents if doc['id'] == x))
            if st.sidebar.button("Delete Selected Document"):
                with st.spinner("Deleting..."):
                    delete_response = delete_document(selected_file_id)
                    if delete_response:
                        st.sidebar.success(f"Document with ID {selected_file_id} deleted successfully.")
                        st.session_state.documents = list_documents()  # Refresh the list after deletion
                    else:
                        st.sidebar.error(f"Failed to delete document with ID {selected_file_id}.")
        display_booking_verification()

    elif tabs == "Customer Chat":
         model_options = ["gemini-1.5-pro"]
         st.sidebar.selectbox("Model", options=model_options, key="model")
         display_chat_interface()

    # elif tabs == "Admin":
    #     display_booking_schedule()
    # elif tabs == "Debug":
    #     display_booking_verification()
        



import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../api")))



from db_utils import get_all_bookings, delete_table, delete_booking_row

def display_booking_verification():
    """
    Display booking information in a table with better labels and numbered rows.
    """
    # Fetch bookings from the database
    bookings = get_all_bookings()

    if bookings:
        st.write("### Bookings in Database")

        # Convert booking data to a pandas DataFrame
        df = pd.DataFrame(bookings)

        # Rename columns for better readability
        df = df.rename(columns={
            "id": "ID",
            "name": "Name",
            "time": "Time",
            "date": "Date",
            "nums_of_customers": "Number of Customers",
            "restaurant_position": "Restaurant Position"
        })

        # Add a numbered index starting from 1
        df.index += 1
        df.index.name = "No."

        # Display the table using Streamlit's st.dataframe
        st.dataframe(df, use_container_width=True)

        # Add a button to delete the entire bookings table
        if st.button("Delete Entire Table"):
            delete_table("bookings")
            st.warning("The bookings table has been deleted.")
            st.rerun()

    else:
        st.write("No bookings found in the database.")
