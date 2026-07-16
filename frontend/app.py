import time
import streamlit as st
from api import LoanAPI

# ===============================================
# Page Configuration
# ===============================================
st.set_page_config(
    page_title="AI Loan Advisory Chatbot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================================
# Session State Initialization
# ===============================================
if "messages" not in st.session_state:
    # Adding a default welcome message for a better empty-state UI
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Loan Advisor. Upload your policy documents in the sidebar, and ask me anything.", "sources": []}
    ]

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []
    
# Initialize total_chunks so the new sidebar logic works
if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0

# ===============================================
# Main Header
# ===============================================
st.title("🏦 AI Loan Advisory Chatbot")
st.markdown("Query loan policies instantly and calculate your monthly EMIs.")

# ===============================================
# Sidebar (Management & Status)
# ===============================================
with st.sidebar:
    st.header("📂 Document Management")
    
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Upload Loan Policy PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if st.button("📤 Upload & Index", use_container_width=True, type="primary"):
            if uploaded_files:
                with st.status("Processing Documents...", expanded=True) as status:
                    st.write("Uploading to backend...")
                    start_time = time.time()
                    
                    response = LoanAPI.upload_documents(uploaded_files)
                    
                    # Process Uploaded
                    if response.get("uploaded_files"):
                        for file in response["uploaded_files"]:
                            if file not in st.session_state.uploaded_documents:
                                st.session_state.uploaded_documents.append(file)
                        st.write(f"✅ Indexed {len(response['uploaded_files'])} new files.")

                    # Update Chunks count
                    chunks = response.get('indexed_chunks', 0)
                    st.session_state.total_chunks += chunks
                    
                    status.update(label=f"Complete! Added {chunks} chunks.", state="complete", expanded=False)
                    st.rerun()
            else:
                st.warning("Please select at least one PDF file.")

    st.divider()

    # Uploaded Documents List (Clean UI)
    st.subheader("📚 Uploaded Documents")
    if st.session_state.uploaded_documents:
        for doc in st.session_state.uploaded_documents:
            st.markdown(f"🟢 **{doc}**")
    else:
        st.info("No documents uploaded yet.")

    st.divider()

    # Backend Status
    st.subheader("⚙️ System Status")
    with st.container(border=True):
        try:
            health = LoanAPI.health()
            if health.get("status") == "Healthy":
                st.markdown("🟢 **Backend API:** Online")
            else:
                st.markdown("🔴 **Backend API:** Offline")
        except:
            st.markdown("🔴 **Backend API:** Offline")


# ===============================================
# Main Content Area (Tabs)
# ===============================================
tab_chat, tab_calc = st.tabs(["💬 AI Loan Assistant", "🧮 EMI Calculator"])

# -----------------------------------------------
# TAB 1: AI Chat Section
# -----------------------------------------------
with tab_chat:
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available and not empty
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📄 View Sources"):
                    for source in message["sources"]:
                        st.write(f"- **{source['source']}** (Page {source['page']})")

    # Chat Input
    if question := st.chat_input("Ask any loan-related question here..."):
        
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Display Assistant Message
        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents..."):
                response = LoanAPI.chat(question)
                
            answer = response.get("answer", "I couldn't find an answer.")
            sources = response.get("sources", [])

            st.markdown(answer)

            if sources:
                with st.expander("📄 Sources Used"):
                    for source in sources:
                        st.write(f"- **{source['source']}** (Page {source['page']})")
            else:
                st.info("No specific source documents were used for this answer.")

        # Save Assistant Message to State
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

# -----------------------------------------------
# TAB 2: EMI Calculator
# -----------------------------------------------
with tab_calc:
    st.subheader("Calculate Your Monthly EMI")
    st.markdown("Adjust the parameters below to see yo" \
    "ur estimated monthly payments and total interest.")
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            principal = st.number_input("💰 Loan Amount (₹)", min_value=1000.0, value=1000000.0, step=50000.0, format="%.2f")
        with col2:
            interest_rate = st.number_input("📈 Annual Interest Rate (%)", min_value=0.0, value=8.5, step=0.1, format="%.2f")
        with col3:
            tenure = st.number_input("📅 Loan Tenure (Years)", min_value=1, value=20, step=1)

        if st.button("🧮 Calculate EMI", type="primary"):
            with st.spinner("Calculating..."):
                result = LoanAPI.calculate_emi(principal, interest_rate, tenure)
            
            st.divider()
            
            # Results Metrics
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Monthly EMI", f"₹ {result['monthly_emi']:,.2f}")
            with c2:
                st.metric("Total Interest", f"₹ {result['total_interest']:,.2f}")
            with c3:
                st.metric("Total Payment", f"₹ {result['total_payment']:,.2f}")

# Footer
st.divider()
st.caption("© 2026 AI Loan Advisory Agent | Powered by FastAPI, Gemini, ChromaDB & Streamlit")