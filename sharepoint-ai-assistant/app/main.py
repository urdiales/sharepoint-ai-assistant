"""
Streamlit UI for Local AI SharePoint Assistant.
Connects user chat to LLM agent and SharePoint.
This is the main entry point for the application that creates the web interface.
"""

import streamlit as st
from app.chat_agent import create_llm_agent
from app.sharepoint_client import SharePointClient
from app.utils import preview_pdf, preview_docx, preview_xlsx
import pandas as pd

# Configure the Streamlit page with a title and wide layout
st.set_page_config(page_title="Local AI SharePoint Assistant", layout="wide")

# Initialize session state variables on first run
# These variables persist across reruns of the Streamlit app
if "connected" not in st.session_state:
    st.session_state.connected = False  # Track SharePoint connection status
if "agent" not in st.session_state:
    st.session_state.agent = None  # Store the LLM agent instance
if "sp_client" not in st.session_state:
    st.session_state.sp_client = None  # Store the SharePoint client instance

# Create a sidebar for SharePoint connection settings
st.sidebar.header("Connect to SharePoint")

# If not connected, show connection form
if not st.session_state.connected:
    site_url = st.sidebar.text_input("Site URL")
    client_id = st.sidebar.text_input("API Key")
    client_secret = st.sidebar.text_input("API Secret", type="password")
    
    # When Connect button is clicked, initialize clients and update connection status
    if st.sidebar.button("Connect"):
        st.session_state.sp_client = SharePointClient()
        st.session_state.agent = create_llm_agent()
        st.session_state.connected = True
        st.sidebar.success("Connected!")
else:
    # If already connected, show disconnect button
    if st.sidebar.button("Disconnect"):
        st.session_state.connected = False
        st.session_state.agent = None
        st.session_state.sp_client = None
        st.experimental_rerun()  # Rerun the app to refresh the UI
    st.sidebar.info("Connected to SharePoint")

# Main page title
st.title("🧠 Local AI SharePoint Assistant")

# Create tabs for different functionality
tab1, tab2 = st.tabs(["Chat", "Search/Preview"])

# --- Tab 1: Chat ---
with tab1:
    if st.session_state.connected:
        # Initialize or retrieve chat history from session state
        chat_history = st.session_state.get("chat_history", [])
        
        # Display existing chat history
        for entry in chat_history:
            st.markdown(entry)
            
        # Create input field for user questions
        user_input = st.text_input("Ask a question about SharePoint")
        
        # When Send button is clicked, process the user input with the LLM agent
        if st.button("Send"):
            agent = st.session_state.agent
            response = agent.run(user_input)  # Run the agent with user input
            
            # Add the Q&A to chat history and update session state
            chat_history.append(f"**You:** {user_input}")
            chat_history.append(f"**Assistant:** {response}")
            st.session_state.chat_history = chat_history
    else:
        st.warning("Connect to SharePoint first.")

# --- Tab 2: Search/Preview ---
with tab2:
    if st.session_state.connected:
        sp_client = st.session_state.sp_client
        
        # Hardcoded list of libraries for demo purposes
        libraries = ["Documents", "HR Library", "Onboarding Checklist"]
        selected_lib = st.selectbox("Select library", libraries)
        
        # Search functionality
        search_query = st.text_input("Search documents by name")
        if st.button("Search Library"):
            df = sp_client.search_documents(selected_lib, search_query)
            st.dataframe(df)  # Display search results as a table
        
        # File preview functionality
        files = ["HR_Policy_v3.docx", "Employee_Handbook.pdf", "Onboarding_Checklist.xlsx"]
        selected_file = st.selectbox("Preview a document", files)
        
        if st.button("Preview File"):
            # Download the selected file from SharePoint
            file_bytes = sp_client.download_file(selected_lib, selected_file)
            
            # Preview the file based on its extension
            if selected_file.endswith(".pdf"):
                st.write(preview_pdf(file_bytes))
            elif selected_file.endswith(".docx"):
                st.write(preview_docx(file_bytes))
            elif selected_file.endswith(".xlsx"):
                st.dataframe(preview_xlsx(file_bytes))
                
            # Add a download button for the file
            st.download_button("Download", data=file_bytes, file_name=selected_file)
    else:
        st.warning("Connect to SharePoint first.")
