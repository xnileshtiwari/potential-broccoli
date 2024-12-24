import streamlit as st
import sys
from pathlib import Path

# Get the absolute path of the project root directory
ROOT_DIR = Path(__file__).parent

# Add the project root directory to the Python path
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from main_chat import start_chatting 
from pinecone_vector_database.query import pincone_vector_database_query

# Initialize session state
if "vector_db_name" not in st.session_state:
    st.session_state.vector_db_name = None
    st.session_state.messages = []
    st.session_state.setup_complete = False

# Custom styling
st.markdown("""
    <style>
    /* Container styling */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Form styling */
    .stForm {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 16px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Chat container styling */
    .chat-container {
        background-color: white;
        border-radius: 15px;
        padding: 1rem;
        margin-top: 2rem;
    }
    
    /* Message styling */
    .stChatMessage {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    
    # Show initial setup form if vector_db_name is not set
    if not st.session_state.setup_complete:
        with st.container():
            st.markdown("### Welcome! Let's get started")
            st.markdown("Please enter the vector database name to begin analyzing legal documents.")
            
            with st.form(key='setup_form'):
                vector_db_input = st.text_input(
                    "Vector Database Name",
                    placeholder="Enter the database identifier",
                    help="This is usually an 8-character alphanumeric ID"
                )
                
                setup_submitted = st.form_submit_button("Start Analysis")
                
                if setup_submitted and vector_db_input:
                    st.session_state.vector_db_name = vector_db_input
                    st.session_state.setup_complete = True
                    st.rerun()
                
    # Show chat interface after setup
    else:
        # Add a sidebar with current session info
        with st.sidebar:
            st.markdown(f"**Active Database**: {st.session_state.vector_db_name}")
            if st.button("Reset Session"):
                st.session_state.clear()
                st.rerun()
        
        # Main chat interface
        st.markdown("### Legal Document Analysis Chat")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        user_input = st.chat_input("Ask a question about the legal document...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                # Get context from vector database
                with st.spinner("Searching document..."):
                    context = pincone_vector_database_query(
                        user_input, 
                        st.session_state.vector_db_name
                    )
                
                # Generate response
                with st.spinner("Generating response..."):
                    response = start_chatting(st.session_state.vector_db_name, user_input)
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                
            except Exception as e:
                st.error("An error occurred. Please try again or reset the session.")
                st.exception(e)

if __name__ == "__main__":
    main()