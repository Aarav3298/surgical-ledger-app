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
        uploaded_file = st.file_uploader("Attach Hospital Invoice / Claim PDF (Required for Verification)", type=["pdf", "png", "jpg", "jpeg"])
        
        st.divider()
        
        st.subheader("2. Clinical Details")
        # Reverting to the exact original clean layout
        surgeon_name = st.text_input("Surgeon Name", placeholder="Dr. First Last")
        procedure_name = st.text_input("Procedure Name", placeholder="e.g., Laparoscopic Cholecystectomy")
        
        # Original metrics required for the AI calculation
        actual_ot_time = st.number_input("Actual OT Time (minutes)", min_value=0, step=15)
        
        clinical_context = st.text_area("Clinical Context / Patient State", placeholder="Describe patient comorbidities, BMI, previous surgeries, etc.")
        complications = st.text_area("Complications (If any)", placeholder="Describe any intra-op or post-op complications, blood loss, etc.")
        
        st.divider()
        
        st.subheader("3. Audit Trail")
        audit_reference = st.text_input("Audit Reference (Invoice / Claim ID)", placeholder="Enter the exact ID from the uploaded document")

        submit_button = st.form_submit_button(label="Log & Verify Procedure", use_container_width=True)

    if submit_button:
        # The system forces them to upload a file AND enter the manual ID
        if uploaded_file is not None and surgeon_name and procedure_name and audit_reference:
            
            # Placeholder for the Gemini 2.5 Flash ASI calculation we built earlier
            mock_complexity_score = 4.5 
            
            new_entry = {
                "Surgeon": surgeon_name,
                "Procedure": procedure_name,
                "OT Time": actual_ot_time,
                "Clinical Context": clinical_context,
                "Complications": complications if complications else "None",
                "Complexity_Score": mock_complexity_score,
                "Audit_ID": audit_reference,
                "Status": "VERIFIED ✅"
            }
            st.session_state.procedures.append(new_entry)
            st.success(f"Procedure Logged! Linked to Audit ID: {audit_reference}")
        else:
            st.error("Submission Failed: You must attach the PDF proof and fill out the Surgeon, Procedure, and Audit ID fields.")

    # Show the Surgeon's current verified stats
    if st.session_state.procedures:
        st.divider()
        st.subheader("Your Verified Portfolio")
        df_surgeon = pd.DataFrame(st.session_state.procedures)
        # Reordering columns to match the old clean view
        st.dataframe(df_surgeon[["Status", "Audit_ID", "Surgeon", "Procedure", "Complexity_Score", "OT Time", "Clinical Context", "Complications"]], use_container_width=True)

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
            st.dataframe(df_admin[["Status", "Audit_ID", "Surgeon", "Procedure", "Complexity_Score"]], use_container_width=True)
    else:
        st.info("No verified procedures logged in the system yet.")
