import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader # We use this to read uploaded PDFs

# --- CONFIGURATION ---
st.set_page_config(page_title="DeepSeeker (My RAG App)", page_icon="🧠", layout="wide")

# --- 1. SIDEBAR & SECRETS CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Check if the key exists in Streamlit Secrets (Cloud)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"] # Use the hidden key
        st.success("✅ API Key loaded from Secrets")
    else:
        # Fallback: If running locally without secrets, ask for it
        api_key = st.text_input("Enter Google API Key:", type="password")
    
    # THE FILE UPLOADER
    st.header("📂 Knowledge Base")
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

# 2. LOGIC: PROCESS THE FILE
user_knowledge = ""

if uploaded_file and api_key:
    try:
        # Check file type
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            # Loop through every page and extract text
            for page in reader.pages:
                user_knowledge += page.extract_text()
        else:
            # It's a text file
            user_knowledge = uploaded_file.read().decode("utf-8")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")

# 3. AI SETUP
if api_key:
    genai.configure(api_key=api_key)
    try:
        # We use a slightly smarter model for analyzing documents if available
        # But stick to Gemma or Flash Lite for free tier
        model = genai.GenerativeModel('gemma-3-4b-it') 
    except:
        st.error("API Key invalid or model not found.")

# --- MAIN CHAT INTERFACE ---
st.title("🧠 DeepSeeker: Chat with Your Data")
st.markdown("Upload a document in the sidebar to create your own Custom AI.")

# Initialize Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture Input
if user_input := st.chat_input("Ask about your document..."):
    
    if not api_key:
        st.warning("Please enter your API Key in the sidebar first!")
        st.stop()

    # Show User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- RAG LOGIC ---
    # We only add the context if a file was uploaded
    context_block = ""
    if user_knowledge:
        context_block = f"CONTEXT FROM UPLOADED DOCUMENT:\n{user_knowledge}\n\n"
    
    prompt = f"""
    Act as a skeptical, grumpy Senior Hiring Manager. Look for gaps in the resume. Only recommend hiring if they are exceptional.
    
    {context_block}
    
    HISTORY:
    {st.session_state.messages}
    
    QUESTION:
    {user_input}
    
    INSTRUCTIONS:
    - If context is provided, answer BASED ON THAT CONTEXT.
    - If the answer is not in the document, say "I couldn't find that in the document."
    """

    with st.chat_message("assistant"):
        with st.spinner("Analyzing document..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:

                st.error(f"Error: {e}")
