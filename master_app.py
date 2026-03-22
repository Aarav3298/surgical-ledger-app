import streamlit as st
import pandas as pd
import google.generativeai as genai
import altair as alt
import json
import re

# --- SECURE CLOUD API KEY ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Using the stable frontier model to prevent quota errors
MODEL_NAME = 'gemini-2.5-flash' 

# --- ZERO-PHI MIDDLEWARE (DPDP COMPLIANCE) ---
def scrub_phi(text):
    if not text:
        return text
    # Redact 10-digit Indian mobile numbers
    text = re.sub(r'\b\d{10}\b', '[REDACTED_PHONE]', text)
    # Redact Emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[REDACTED_EMAIL]', text)
    # Redact Dates (DD/MM/YYYY)
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[REDACTED_DATE]', text)
    # Redact obvious names following titles
    text = re.sub(r'\b(?:Patient|Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\b', '[REDACTED_NAME]', text)
    return text

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Surgical Intelligence Platform", page_icon="⚕️", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("App Navigation")
st.sidebar.markdown("---")
module = st.sidebar.radio(
    "Select Module:",
    [
        "👨‍⚕️ Module 1: Surgeon Portfolio", 
        "💰 Module 2: Revenue Protection", 
        "📊 Module 3: Talent Intelligence"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Surgical Intelligence Platform v4.0 (Enterprise)")

# Initialize session state for the ledger
if 'surgery_log' not in st.session_state:
    st.session_state['surgery_log'] = []


# ==========================================
# MODULE 1: SURGEON PORTFOLIO
# ==========================================
if module == "👨‍⚕️ Module 1: Surgeon Portfolio":
    st.title("👨‍⚕️ Surgeon Portfolio")
    st.markdown("### The Advanced Surgical Index (ASI). Mathematically Verified.")
    st.info("Log your cases to build an AI-verified record of your clinical capability, time efficiency, and risk-adjusted outcomes.")

    with st.form("surgeon_log_form"):
        st.caption("🔒 **DPDP Compliance Notice:** Do not enter Protected Health Information (PHI) such as patient names, phone numbers, or exact birth dates. Enter strictly de-identified clinical context.")
        col1, col2 = st.columns(2)
        with col1:
            surgeon_name = st.text_input("Surgeon Name / ID")
            procedure_name = st.text_input("Primary Procedure Name", placeholder="e.g., Whipple Procedure")
            actual_ot_time = st.number_input("Actual OT Time (Hours)", min_value=0.5, max_value=24.0, step=0.5, value=2.0)
        with col2:
            clinical_context = st.text_area("Clinical Context & Co-morbidities", placeholder="Patient demographics, abnormal anatomy, adhesions...", height=115)
            complications = st.text_input("Complications Noted", placeholder="Type 'None' or describe (e.g., minor hemorrhage)")
        
        audit_ref = st.text_input("Audit Reference (Hospital Invoice No. or TPA Claim ID)", placeholder="Leave blank if pending...")
        submit_button = st.form_submit_button("Generate ASI Score & Log Case")

    if submit_button:
        if not procedure_name or not surgeon_name:
            st.error("Please enter both your Name and the Procedure Name.")
        else:
            with st.spinner("AI evaluating Advanced Surgical Index & Benchmarks..."):
                try:
                    # Run the context through the PII Scrubber before sending to AI
                    safe_context = scrub_phi(clinical_context)
                    
                    prompt = f"""
                    You are an elite Chief Medical Officer and Surgical Auditor. Evaluate this procedure and calculate the Advanced Surgical Index (ASI) and global benchmarks.
                    
                    Procedure: {procedure_name}
                    Clinical Context & Co-morbidities: {safe_context}
                    
                    Calculate the following strict components:
                    1. baseline: Procedural Difficulty (0.00 to 10.00 scale) for a healthy patient.
                    2. context_modifier: Add +0.00 to +3.00 based on the provided clinical context.
                    3. rarity_modifier: Add +0.00 to +2.00 if the procedure/findings are highly unusual.
                    4. benchmark_time: The global standard average OT time in hours for this procedure (float).
                    5. expected_complication_rate: The baseline statistical percentage risk of complications for this procedure (float, e.g., 5.5).
                    
                    Respond ONLY with a valid JSON object in this exact format:
                    {{
                        "baseline": <float>,
                        "context_modifier": <float>,
                        "rarity_modifier": <float>,
                        "final_asi_score": <float, max 15.00>,
                        "benchmark_time": <float>,
                        "expected_complication_rate": <float>,
                        "clinical_justification": "<1 concise sentence explaining the modifiers>"
                    }}
                    """
                    
                    model = genai.GenerativeModel(MODEL_NAME)
                    response = model.generate_content(prompt)
                    
                    result_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    ai_result = json.loads(result_text)
                    
                    verification_status = "🟢 VERIFIED" if audit_ref else "🟡 PENDING AUDIT"
                    ot_efficiency = round((ai_result["benchmark_time"] / actual_ot_time) * 100, 1)
                    
                    log_entry = {
                        "surgeon": surgeon_name,
                        "procedure": procedure_name,
                        "context": safe_context,
                        "actual_time": actual_ot_time,
                        "complications": complications,
                        "baseline": ai_result["baseline"],
                        "context_mod": ai_result["context_modifier"],
                        "rarity_mod": ai_result["rarity_modifier"],
                        "final_asi": ai_result["final_asi_score"],
                        "benchmark_time": ai_result["benchmark_time"],
                        "expected_risk": ai_result["expected_complication_rate"],
                        "ot_efficiency": ot_efficiency,
                        "reasoning": ai_result["clinical_justification"],
                        "status": verification_status
                    }
                    st.session_state['surgery_log'].insert(0, log_entry)
                    st.success(f"Case Logged! Final ASI: {ai_result['final_asi_score']}/15.00 | OT Efficiency: {ot_efficiency}%")
                    
                except Exception as e:
                    st.error(f"AI Calculation Error: {e}. Please try again.")

    # THE SURGEON'S GRANULAR LEDGER
    st.markdown("---")
    st.subheader("Your Verified Case Ledger")
    if st.session_state['surgery_log']:
        for case in st.session_state['surgery_log']:
            with st.expander(f"{case['status']} | {case['procedure']} | ASI Score: {case['final_asi']}/15.00"):
                st.markdown(f"**Surgeon:** {case['surgeon']}")
                st.markdown(f"**Clinical Context:** {case['context'] if case['context'] else 'None provided'}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Baseline ASI", case['baseline'])
                col2.metric("Context Mod", f"+{case['context_mod']}")
                col3.metric("Rarity Mod", f"+{case['rarity_mod']}")
                col4.metric("OT Efficiency", f"{case['ot_efficiency']}%")
                st.markdown(f"**AI Justification:** {case['reasoning']}")
                st.markdown(f"*(Global Benchmark Time: {case['benchmark_time']} hrs | Your Time: {case['actual_time']} hrs)*")
    else:
        st.caption("No cases logged yet.")

# ==========================================
# MODULE 2: REVENUE PROTECTION 
# ==========================================
elif module == "💰 Module 2: Revenue Protection":
    st.title("💰 Pre-Submission Intelligence")
    st.markdown("### Stop Insurance Rejections Before They Happen.")
    st.warning("AI generates mandatory billing checklists to prevent revenue leakage from undercoded complex surgeries.")

    with st.form("revenue_form"):
        procedure_to_check = st.text_input("Planned Procedure", placeholder="e.g., Total Knee Arthroplasty (Bilateral)")
        generate_checklist = st.form_submit_button("Generate TPA Compliance Checklist")

    if generate_checklist and procedure_to_check:
        with st.spinner("Analyzing TPA documentation requirements..."):
            try:
                prompt = f"""
                You are a veteran Medical Biller specializing in the Indian private hospital and TPA landscape. 
                A surgeon is about to write the operative notes for: {procedure_to_check}.
                What are the top 3-5 specific anatomical or procedural details that MUST be explicitly documented to prevent claim rejection or downcoding? 
                Provide a clear, bulleted checklist only.
                """
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)
                
                st.success("TPA Audit Rules Applied")
                st.info("### 📋 Copy-Paste Operative Note Addendum:")
                st.code(response.text, language="markdown")
                
            except Exception as e:
                st.error(f"AI Error: {e}")

# ==========================================
# MODULE 3: TALENT INTELLIGENCE
# ==========================================
elif module == "📊 Module 3: Talent Intelligence":
    st.title("📊 Clinical Governance Executive Dashboard")
    st.markdown("### Risk-Adjusted Surgical Optimization")

    if 'surgery_log' not in st.session_state or len(st.session_state['surgery_log']) == 0:
        st.info("No surgical data available. Log cases in Module 1 to populate the dashboard.")
    else:
        df = pd.DataFrame(st.session_state['surgery_log'])
        
        # Create an enterprise-clean copy for the Excel export (stripping emojis)
        export_df = df.copy()
        export_df['status'] = export_df['status'].str.replace('🟢', '').str.replace('🟡', '').str.strip()
        
        # Generate CSV using the clean dataframe
        csv = export_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Export Department Data to Excel (CSV)",
            data=csv,
            file_name="hospital_surgical_audit.csv",
            mime="text/csv",
        )
        
        # AGGREGATE SURGEON DATA
        df['success_rate'] = df.apply(lambda row: 100 if str(row['complications']).strip().lower() in ['none', ''] else max(0, 100 - row['expected_risk'] - 15), axis=1)
        
        surgeon_stats = df.groupby('surgeon').agg(
            Total_Cases=('procedure', 'count'),
            Avg_ASI=('final_asi', 'mean'),
            Avg_Efficiency=('ot_efficiency', 'mean'),
            Avg_Success=('success_rate', 'mean')
        ).reset_index()
        
        max_cases = surgeon_stats['Total_Cases'].max() if surgeon_stats['Total_Cases'].max() > 0 else 1
        surgeon_stats['CIS'] = (
            (surgeon_stats['Avg_Success'] * 0.40) + 
            ((surgeon_stats['Avg_ASI'] / 15.0) * 100 * 0.25) + 
            (surgeon_stats['Avg_Efficiency'].clip(upper=150) * 0.20) + 
            ((surgeon_stats['Total_Cases'] / max_cases) * 100 * 0.15)
        ).round(1)

        st.markdown("---")
        selected_surgeon = st.selectbox("Select Surgeon to Review:", surgeon_stats['surgeon'].tolist())
        s_data = surgeon_stats[surgeon_stats['surgeon'] == selected_surgeon].iloc[0]

        st.subheader(f"Performance Scorecard: Dr. {selected_surgeon}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Clinical Impact Score (CIS)", f"{s_data['CIS']}/100")
        col2.metric("Avg ASI (Complexity)", f"{round(s_data['Avg_ASI'], 2)}/15")
        col3.metric("OT Efficiency", f"{round(s_data['Avg_Efficiency'], 1)}%")
        col4.metric("Risk-Adjusted Success", f"{round(s_data['Avg_Success'], 1)}%")

        st.markdown("---")
        st.subheader("Departmental Benchmark Matrix")
        chart = alt.Chart(surgeon_stats).mark_circle().encode(
            x=alt.X('Avg_Efficiency', title='OT Efficiency % (Time vs Benchmark)', scale=alt.Scale(zero=False)),
            y=alt.Y('Avg_ASI', title='Average ASI Score (Complexity)', scale=alt.Scale(domain=[0, 15])),
            size=alt.Size('Total_Cases', title='Case Volume', scale=alt.Scale(range=[200, 1000])),
            color=alt.Color('surgeon', legend=alt.Legend(title="Surgeon")),
            tooltip=['surgeon', 'CIS', 'Avg_ASI', 'Avg_Efficiency', 'Total_Cases']
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

        st.markdown("---")
        st.subheader("AI CMO Summary & Recommendation")
        
        if s_data['Avg_Success'] < 80:
            st.error("🚨 **URGENT REVIEW (Liability Risk):** Risk-adjusted outcomes are below acceptable clinical thresholds regardless of surgical volume. Immediate case audit recommended.")
        elif s_data['Avg_ASI'] > 9.0 and s_data['Avg_Success'] >= 90:
            st.success("🏆 **ELITE ANCHOR:** This surgeon is a cornerstone of the department, handling the highest complexity (Level 4/5 equivalent) cases with excellent outcomes. Prioritize retention and prime OT scheduling.")
        elif s_data['Avg_Efficiency'] > 110 and s_data['Avg_ASI'] < 7.0:
            st.info("⚡ **HIGH-YIELD WORKHORSE:** Exceptional operational efficiency on standard-complexity cases. Highly profitable for the hospital due to rapid OT turnover. Maximize daily case loads.")
        elif s_data['CIS'] >= 85:
            st.success("⭐ **TOP TIER PERFORMER:** Outstanding balance of complexity, speed, and safety. A highly valuable asset to the surgical department.")
        else:
            st.warning("📊 **STEADY PERFORMER:** Solid clinical metrics across standard departmental volume. Monitor for opportunities to increase complex case exposure or improve OT turnaround times.")
