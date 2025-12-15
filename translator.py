import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Internship Resume Checker",
    page_icon="🚀",
    layout="wide" # Changed to wide for a more pro feel
)

# --- SIDEBAR: SETTINGS & CREDIT ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. API Key Handling
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ System Online")
    else:
        api_key = st.text_input("Enter Google API Key:", type="password")
        if not api_key:
            st.warning("⚠️ Please enter a key to start.")

    # 2. File Uploader
    st.markdown("---")
    st.subheader("📂 Step 1: Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    st.markdown("---")
    st.caption("🔒 Privacy Note: Files are analyzed in memory and not saved.")
    
    # --- THE CREDIT (Bottom Corner) ---
    st.markdown("---")
    st.markdown("🛠️ **Made by Rafi Mumtaz**")

# --- MAIN UI ---
# Generic Professional Title
st.title("🚀 AI Internship Resume Checker")
st.markdown("""
**Will you get the interview?** This AI analyzes your resume against industry standards. Upload your PDF to see your "Hiring Probability" score.
""")
st.divider()

# --- FILE PROCESSING ---
user_knowledge = ""
if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            user_knowledge += page.extract_text()
        st.toast(f"✅ Analyzed {len(reader.pages)} pages successfully!", icon="📄")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- CHAT & AI LOGIC ---
if api_key:
    genai.configure(api_key=api_key)
    # Using Flash Lite for speed/free tier
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Upload your resume and I'll calculate your odds of getting that internship."}
        ]

    # Display Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- INTERACTIVE BUTTONS ---
    # Only show these if a file is uploaded
    if user_knowledge:
        col1, col2, col3 = st.columns(3)
        action_clicked = False
        
        with col1:
            if st.button("🔥 Roast My Resume", use_container_width=True):
                user_input = "Roast this resume ruthlessly. Tell me why I won't get hired."
                action_clicked = True
        with col2:
            if st.button("📊 Probability Score", use_container_width=True):
                user_input = "Rate this resume out of 100 based on internship standards and explain the score."
                action_clicked = True
        with col3:
            if st.button("🔑 Key Improvements", use_container_width=True):
                user_input = "What are the top 3 specific things I must change to get hired?"
                action_clicked = True
    else:
        action_clicked = False

    # --- INPUT HANDLING ---
    if chat_input := st.chat_input("Ask about your resume..."):
        user_input = chat_input
        action_clicked = True

    if action_clicked and user_input:
        
        if not user_knowledge:
            st.warning("⚠️ Please upload a PDF in the sidebar first!")
            st.stop()

        # Add User Message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # --- SYSTEM PROMPT ---
        prompt = f"""
        You are a Senior Hiring Manager at a top-tier company.
        
        RESUME CONTENT:
        {user_knowledge}
        
        CHAT HISTORY:
        {st.session_state.messages}
        
        USER QUESTION:
        {user_input}
        
        INSTRUCTIONS:
        1. Always be honest and direct.
        2. If asked for a score, provide a specific "Pass Probability" percentage (e.g., 85%).
        3. Keep answers structured and professional.
        """

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing profile..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
