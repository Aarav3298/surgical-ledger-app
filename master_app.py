import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Surgical Intelligence Platform", layout="wide")

# --- MOCK DATABASE ---
if "procedures" not in st.session_state:
    st.session_state.procedures = []

# --- NAVIGATION ---
st.sidebar.title("Platform Navigation")
view = st.sidebar.radio("Select Portal:", ["Surgeon Portal", "Admin Console"])

# ==========================================
# PORTAL 1: SURGEON VIEW (The "Verified Resume")
# ==========================================
if view == "Surgeon Portal":
    st.title("Surgeon Portal: Log Procedure")
    st.markdown("Enter procedure details and upload the billing invoice for verification.")

    with st.form("log_procedure_form"):
        st.subheader("1. Mandatory Proof")
        # The file uploader is just for attachment/audit purposes now
        uploaded_file = st.file_uploader("Attach Hospital Invoice / Claim PDF (Required for Verification)", type=["pdf", "png", "jpg"])
        
        st.subheader("2. Clinical Details")
        col1, col2 = st.columns(2)
        with col1:
            surgeon_name = st.text_input("Primary Surgeon Name")
            procedure_name = st.text_input("Procedure Performed")
            audit_id = st.text_input("Invoice / Claim ID (Type manually)")
        with col2:
            date_performed = st.date_input("Date of Procedure")
            comorbidities = st.multiselect("Patient Comorbidities (Select all that apply)", 
                                           ["None", "Diabetes", "Hypertension", "Obesity", "Cardiac Disease", "Renal Issue"])
            complications = st.text_area("Intra-op Complications / Blood Loss (If any)")

        submit_button = st.form_submit_button(label="Log & Verify Procedure")

    if submit_button:
        # The system forces them to upload a file AND enter the manual ID
        if uploaded_file is not None and surgeon_name and procedure_name and audit_id:
            
            # Placeholder for the Gemini API that will read these text fields and return a score
            mock_complexity_score = 4 
            
            new_entry = {
                "Surgeon": surgeon_name,
                "Procedure": procedure_name,
                "Date": date_performed,
                "Comorbidities": ", ".join(comorbidities) if comorbidities else "None",
                "Complexity_Score": mock_complexity_score,
                "Audit_ID": audit_id,
                "Proof_Attached": "Yes"
            }
            st.session_state.procedures.append(new_entry)
            st.success(f"Procedure Logged! Linked to Audit ID: {audit_id}")
        else:
            st.error("Submission Failed: You must attach the PDF proof and fill out all mandatory fields.")

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
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Calculate Stack Rank
            st.subheader("Operator Stack Rank")
            rankings = df_admin.groupby("Surgeon")["Complexity_Score"].sum().reset_index()
            rankings = rankings.sort_values(by="Complexity_Score", ascending=False)
            rankings.columns = ["Surgeon", "Total Verified Complexity"]
            st.dataframe(rankings, use_container_width=True)
            
        with col2:
            st.subheader("Raw Verified Ledger (Ready for Audit)")
            # Admins can see the exact Audit IDs to pull the physical files if they suspect cheating
            st.dataframe(df_admin, use_container_width=True)
    else:
        st.info("No verified procedures logged in the system yet.")
