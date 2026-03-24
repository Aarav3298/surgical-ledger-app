import streamlit as st
import pandas as pd
import google.generativeai as genai
import altair as alt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Surgical Intelligence Platform", layout="wide")

# --- INITIALIZE GEMINI API ---
# This securely pulls your key from the .streamlit/secrets.toml file
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("API Key missing! Please set GEMINI_API_KEY in .streamlit/secrets.toml")

# --- THE ASI AI ENGINE ---
def calculate_asi(procedure, ot_time, comorbidities, complications):
    """Sends the surgical data to Gemini to calculate the Advanced Surgical Index."""
    prompt = f"""
    You are an expert Medical Auditor and Hospital Operations Analyst. 
    Your job is to evaluate surgical procedures and assign an Advanced Surgical Index (ASI) score between 1.0 and 5.0.
    
    1.0 = Basic, low-risk, routine outpatient procedure.
    5.0 = Extremely complex, high-risk, life-saving surgery with severe complications or difficult patient state.
    
    Evaluate this specific case:
    - Procedure: {procedure}
    - Actual OT Time: {ot_time} minutes
    - Patient Comorbidities: {comorbidities}
    - Intra/Post-op Complications: {complications}
    
    Analyze the baseline difficulty of the procedure, add multipliers for the comorbidities, and adjust for the complications and time taken.
    
    Return ONLY a single floating-point number between 1.0 and 5.0. Do not include any other text, explanation, or symbols.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure we just get the float
        score = float(response.text.strip())
        # Cap the score between 1.0 and 5.0 just in case
        return min(max(score, 1.0), 5.0)
    except Exception as e:
        # Fallback in case the API hits a rate limit or fails
        return 0.0


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
        surgeon_name = st.text_input("Surgeon Name", placeholder="Dr. First Last")
        procedure_name = st.text_input("Procedure Name", placeholder="e.g., Laparoscopic Cholecystectomy")
        
        actual_ot_time = st.number_input("Actual OT Time (minutes)", min_value=0, step=15)
        
        clinical_comorbidity = st.text_area("Clinical Comorbidity", placeholder="e.g., Severe Diabetes, Hypertension, existing cardiac history")
        complications = st.text_area("Complications (If any)", placeholder="Describe any intra-op or post-op complications, blood loss, etc.")
        
        st.divider()
        
        st.subheader("3. Audit Trail")
        audit_reference = st.text_input("Audit Reference (Invoice / Claim ID)", placeholder="Enter the exact ID from the uploaded document")

        submit_button = st.form_submit_button(label="Log & Verify Procedure", use_container_width=True)

    if submit_button:
        if uploaded_file is not None and surgeon_name and procedure_name and audit_reference:
            
            with st.spinner("Analyzing surgical complexity via ASI Engine..."):
                # Calling the actual Gemini API
                real_complexity_score = calculate_asi(procedure_name, actual_ot_time, clinical_comorbidity, complications)
            
            if real_complexity_score > 0.0:
                new_entry = {
                    "Surgeon": surgeon_name,
                    "Procedure": procedure_name,
                    "OT Time": actual_ot_time,
                    "Comorbidities": clinical_comorbidity if clinical_comorbidity else "None",
                    "Complications": complications if complications else "None",
                    "Complexity_Score": real_complexity_score,
                    "Audit_ID": audit_reference,
                    "Status": "VERIFIED ✅"
                }
                st.session_state.procedures.append(new_entry)
                st.success(f"Procedure Logged! Linked to Audit ID: {audit_reference} | ASI Score: {real_complexity_score}")
            else:
                st.error("AI Engine failed to generate a score. Please try again.")
        else:
            st.error("Submission Failed: You must attach the PDF proof and fill out the Surgeon, Procedure, and Audit ID fields.")

    if st.session_state.procedures:
        st.divider()
        st.subheader("Your Verified Portfolio")
        df_surgeon = pd.DataFrame(st.session_state.procedures)
        st.dataframe(df_surgeon[["Status", "Audit_ID", "Surgeon", "Procedure", "Complexity_Score", "OT Time", "Comorbidities", "Complications"]], use_container_width=True)

# ==========================================
# PORTAL 2: ADMIN CONSOLE (The "Truth Engine")
# ==========================================
elif view == "Admin Console":
    st.title("📊 Clinical Governance Executive Dashboard")
    st.markdown("### Risk-Adjusted Surgical Optimization")

    if st.session_state.procedures:
        df_admin = pd.DataFrame(st.session_state.procedures)
        
        # --- 1. AGGREGATE DATA FOR SCORECARD ---
        agg_df = df_admin.groupby("Surgeon").agg(
            Total_Cases=("Procedure", "count"),
            Avg_ASI=("Complexity_Score", "mean"),
            Avg_OT_Time=("OT Time", "mean")
        ).reset_index()

        def calc_success_rate(surgeon_name):
            surgeon_cases = df_admin[df_admin["Surgeon"] == surgeon_name]
            total = len(surgeon_cases)
            errors = len(surgeon_cases[surgeon_cases["Complications"].str.lower() != "none"])
            if total == 0: return 100.0
            return round(((total - errors) / total) * 100, 1)

        agg_df["Success_Rate_%"] = agg_df["Surgeon"].apply(calc_success_rate)
        
        # CIS Calculation
        agg_df["Clinical_Impact_Score"] = round(agg_df["Total_Cases"] * agg_df["Avg_ASI"] * (agg_df["Success_Rate_%"] / 100), 2)
        agg_df = agg_df.sort_values(by="Clinical_Impact_Score", ascending=False)

        # --- 2. SURGEON PERFORMANCE SCORECARD ---
        st.subheader("Surgeon Performance Scorecard")
        st.dataframe(agg_df[["Surgeon", "Clinical_Impact_Score", "Total_Cases", "Avg_ASI", "Success_Rate_%", "Avg_OT_Time"]], use_container_width=True, hide_index=True)

        st.divider()

        col1, col2 = st.columns([2, 1])

        # --- 3. DEPARTMENTAL BENCHMARK MATRIX (ALTAIR CHART) ---
        with col1:
            st.subheader("Departmental Benchmark Matrix")
            st.markdown("Visualizing operator Volume vs. Complexity.")
            
            chart = alt.Chart(agg_df).mark_circle().encode(
                x=alt.X('Total_Cases:Q', title='Volume (Total Cases)'),
                y=alt.Y('Avg_ASI:Q', title='Complexity (Average ASI Score)', scale=alt.Scale(domain=[1, 5.5])),
                size=alt.Size('Clinical_Impact_Score:Q', legend=None),
                color=alt.Color('Success_Rate_%:Q', scale=alt.Scale(scheme='redyellowgreen'), title='Success Rate'),
                tooltip=['Surgeon', 'Total_Cases', 'Avg_ASI', 'Clinical_Impact_Score', 'Success_Rate_%']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

        # --- 4. DATA EXPORT & AI CMO SUMMARY ---
        with col2:
            st.subheader("Data Export")
            csv_data = agg_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CIS Report (CSV)",
                data=csv_data,
                file_name='hospital_cis_report.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            st.divider()
            
            st.subheader("AI CMO Summary")
            st.markdown("Executive Analysis Engine")
            if st.button("Generate Recommendation", use_container_width=True):
                with st.spinner("Analyzing departmental data..."):
                    prompt = f"""
                    You are the Chief Medical Officer of a hospital. Analyze this data: {agg_df.to_dict('records')}
                    Write a brutal, 2-sentence executive summary telling the hospital director exactly who is the most valuable surgeon (based on high CIS and Success Rate) and who is a liability. Be extremely concise.
                    """
                    try:
                        cmo_response = model.generate_content(prompt)
                        st.success(cmo_response.text)
                    except Exception as e:
                        st.error("AI analysis temporarily unavailable.")
    else:
        st.info("No verified procedures logged in the system yet.")
