import streamlit as st
import pandas as pd
# import google.generativeai as genai # We will activate this when we write the OCR function

# --- PAGE CONFIG ---
st.set_page_config(page_title="Surgical Intelligence Platform", layout="wide")

# --- MOCK DATABASE (To test the UI before we connect a real database) ---
if "procedures" not in st.session_state:
    st.session_state.procedures = []

# --- NAVIGATION ---
st.sidebar.title("Platform Navigation")
view = st.sidebar.radio("Select Portal:", ["Surgeon Portal", "Admin Console"])

# ==========================================
# PORTAL 1: SURGEON VIEW (The "Verified Resume")
# ==========================================
if view == "Surgeon Portal":
    st.title("Surgeon Portal: Verified Log")
    st.markdown("Upload hospital invoices to securely log verified procedures.")

    with st.form("log_procedure_form"):
        st.subheader("1. Upload Proof")
        # THE HARD MOAT: Replaced the manual text box with a File Uploader
        uploaded_file = st.file_uploader("Upload TPA Claim / Hospital Invoice (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])
        
        st.subheader("2. Procedure Details")
        col1, col2 = st.columns(2)
        with col1:
            surgeon_name = st.text_input("Primary Surgeon Name")
            procedure_name = st.text_input("Procedure Performed")
        with col2:
            date_performed = st.date_input("Date of Procedure")
            clinical_notes = st.text_area("Brief Clinical Context (Optional)")

        submit_button = st.form_submit_button(label="Extract & Verify Procedure")

    if submit_button:
        if uploaded_file is not None and surgeon_name and procedure_name:
            # Placeholder for our future Gemini Vision AI extraction logic
            st.info("Scanning document and extracting Invoice ID...")
            
            # Mocking a successful AI extraction and verification
            new_entry = {
                "Surgeon": surgeon_name,
                "Procedure": procedure_name,
                "Date": date_performed,
                "Complexity_Score": 4, # Mock score that AI will generate later
                "Verification_Status": "VERIFIED (ID: HOS-88921)",
                "Notes": clinical_notes
            }
            st.session_state.procedures.append(new_entry)
            st.success("Procedure Verified & Logged! Patient data scrubbed.")
        else:
            st.error("Please upload a billing document and fill out the mandatory fields.")

    # Show the Surgeon's current verified stats
    if st.session_state.procedures:
        st.divider()
        st.subheader("Your Verified Portfolio")
        df_surgeon = pd.DataFrame(st.session_state.procedures)
        st.dataframe(df_surgeon, use_container_width=True)

# ==========================================
# PORTAL 2: ADMIN CONSOLE (The "Truth Engine")
# ==========================================
elif view == "Admin Console":
    st.title("Admin Console: Talent Intelligence")
    st.markdown("Objective, mathematically ranked operator performance based on verified billing data.")

    if st.session_state.procedures:
        df_admin = pd.DataFrame(st.session_state.procedures)
        
        # Calculate Mock Stack Rank
        st.subheader("Operator Stack Rank (By Verified Complexity)")
        rankings = df_admin.groupby("Surgeon")["Complexity_Score"].sum().reset_index()
        rankings = rankings.sort_values(by="Complexity_Score", ascending=False)
        rankings.columns = ["Surgeon", "Total Verified Complexity Output"]
        
        st.dataframe(rankings, use_container_width=True)
        
        st.divider()
        st.subheader("Raw Verified Ledger")
        st.dataframe(df_admin, use_container_width=True)
    else:
        st.info("No verified procedures logged in the system yet. Waiting for surgeon inputs.")
