import streamlit as st
from api_utils import get_api_response
import sys
import os


import requests
import streamlit as st

API_URL = "http://localhost:8000/getbooking"  # Adjust URL based on your FastAPI server

def display_booking_schedule():
    """
    Fetch and display booking data from the /getbooking API endpoint.
    """
    st.subheader("Booking Schedule")
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success" and data["data"]:
                bookings = data["data"]
                # Display bookings in a table
                st.table(bookings)
            else:
                st.write("No bookings available.")
        else:
            st.error(f"Failed to fetch bookings. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred while fetching bookings: {str(e)}")


import streamlit as st

def display_chat_interface():
    """
    Chat interface for the user to interact with the assistant.
    Handles both normal responses and booking confirmations.
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if the message contains booking information
            if "<booking>" in message["content"] and "</booking>" in message["content"]:
                booking_content = message["content"].split("<booking>")[1].split("</booking>")[0].strip()

                # Handle confirmed bookings
                if "<confirm>" in booking_content and "</confirm>" in booking_content:
                    booking_data = booking_content.split("<confirm>")[1].split("</confirm>")[0].strip()
                    try:
                        booking = eval(booking_data)  # Safely parse JSON-like string
                        # Display booking in a styled box
                        st.success("Booking Confirmed!")
                        st.markdown("### Booking Details")
                        st.markdown(f"**Name:** {booking['name']}")
                        st.markdown(f"**Time:** {booking['time']}")
                        st.markdown(f"**Date:** {booking['date']}")
                        st.markdown(f"**Number of Customers:** {booking['nums_of_customers']}")
                        st.markdown(f"**Seating Preference:** {booking['restaurant_position']}")
                    except Exception as e:
                        st.error("Failed to parse confirmed booking.")
                        st.error(str(e))
            else:
                # Display regular chat message
                st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

            if response:
                st.session_state.session_id = response.get("session_id")
                st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

                # Display assistant's response (non-nested)
                with st.chat_message("assistant"):
                    # Display normal content or booking logic
                    if "<booking>" in response["answer"] and "</booking>" in response["answer"]:
                        booking_content = response["answer"].split("<booking>")[1].split("</booking>")[0].strip()

                        if "<confirm>" in booking_content and "</confirm>" in booking_content:
                            booking_data = booking_content.split("<confirm>")[1].split("</confirm>")[0].strip()
                            try:
                                booking = eval(booking_data)
                                st.success("Booking Confirmed!")
                                st.markdown("### Booking Details")
                                st.markdown(f"**Name:** {booking['name']}")
                                st.markdown(f"**Time:** {booking['time']}")
                                st.markdown(f"**Date:** {booking['date']}")
                                st.markdown(f"**Number of Customers:** {booking['nums_of_customers']}")
                                st.markdown(f"**Seating Preference:** {booking['restaurant_position']}")
                            except Exception as e:
                                st.error("Failed to parse confirmed booking.")
                                st.error(str(e))

                        elif "<notconfirm>" in booking_content and "</notconfirm>" in booking_content:
                            booking_data = booking_content.split("<notconfirm>")[1].split("</notconfirm>")[0].strip()
                            try:
                                booking = eval(booking_data)
                                missing_info = []
                                if not booking["name"]:
                                    missing_info.append("your name")
                                if not booking["time"]:
                                    missing_info.append("the time you'd like to book")
                                if not booking["date"]:
                                    missing_info.append("the date you'd like to book")
                                if not booking["nums_of_customers"]:
                                    missing_info.append("the number of customers")
                                if not booking["restaurant_position"]:
                                    missing_info.append("your seating preference (indoor or outdoor)")

                                if missing_info:
                                    missing_info_str = ", ".join(missing_info[:-1]) + (
                                        f", and {missing_info[-1]}" if len(missing_info) > 1 else missing_info[-1]
                                    )
                                    st.warning(
                                        f"I'm happy to help you with your booking! However, I need more information from you. "
                                        f"Could you please provide {missing_info_str}?"
                                    )
                                else:
                                    st.error("Unexpected error: All details appear missing.")
                            except Exception as e:
                                st.error("Failed to parse incomplete booking.")
                                st.error(str(e))

                    else:
                        # Display normal response
                        st.markdown(response["answer"])
            else:
                st.error("Failed to get a response from the API. Please try again.")
