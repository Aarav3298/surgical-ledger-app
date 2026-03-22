import streamlit as st
import pandas as pd
import google.generativeai as genai
import altair as alt

# --- SECURE CLOUD API KEY ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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
st.sidebar.caption("Surgical Intelligence Platform v2.0")

# ==========================================
# MODULE 1: SURGEON PORTFOLIO
# ==========================================
if module == "👨‍⚕️ Module 1: Surgeon Portfolio":
    st.title("👨‍⚕️ Surgeon Portfolio")
    st.markdown("### Your Clinical Capability. Mathematically Verified.")
    st.info("Log your cases here to build a portable, AI-verified record of your surgical complexity.")

    # Initialize a temporary session state ledger if it doesn't exist
    if 'surgery_log' not in st.session_state:
        st.session_state['surgery_log'] = []

    # --- THE DATA ENTRY FORM ---
    with st.form("surgeon_log_form"):
        st.subheader("Log a New Procedure")
        
        surgeon_name = st.text_input("Surgeon Name / ID")
        procedure_name = st.text_input("Primary Procedure Name", placeholder="e.g., Laparoscopic Cholecystectomy")
        
        # This is the "Clinical Defensibility" fix Claude asked for
        clinical_context = st.text_area("Clinical Context & Co-morbidities", placeholder="e.g., 72-year-old diabetic, severe scarring, frozen Calot's triangle...")
        
        # This is the anti-fraud verification fix
        audit_ref = st.text_input("Audit Reference (Hospital Invoice No. or TPA Claim ID)", placeholder="Leave blank if pending...")
        
        submit_button = st.form_submit_button("Generate AI Complexity Score & Log")

    # --- THE AI ENGINE ---
    if submit_button:
        if not procedure_name or not surgeon_name:
            st.error("Please enter both your Name and the Procedure Name.")
        else:
            with st.spinner("AI evaluating clinical complexity..."):
                try:
                    # 1. The Prompt
                    prompt = f"""
                    You are an expert surgical auditor. Evaluate the complexity of the following surgical procedure on a scale of 1 to 5.
                    (1 = Routine/Minor, 3 = Standard/Moderate, 5 = Ultra-Rare/Highly Complex).
                    
                    Procedure: {procedure_name}
                    Clinical Context/Co-morbidities: {clinical_context}
                    
                    Respond ONLY with a valid JSON object in this exact format, nothing else:
                    {{"score": <number 1-5>, "reasoning": "<1 concise sentence explaining the score>"}}
                    """
                    
                    # 2. Call the Model (USING THE VALID 2.5 FLASH MODEL!)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(prompt)
                    
                    # 3. Parse the JSON Output
                    import json
                    result_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
                    ai_result = json.loads(result_text)
                    
                    # 4. Check Verification Status
                    verification_status = "🟢 VERIFIED" if audit_ref else "🟡 PENDING AUDIT"
                    
                    # 5. Save to our temporary ledger
                    log_entry = {
                        "surgeon": surgeon_name,
                        "procedure": procedure_name,
                        "context": clinical_context,
                        "score": ai_result["score"],
                        "reasoning": ai_result["reasoning"],
                        "status": verification_status,
                        "audit_ref": audit_ref
                    }
                    st.session_state['surgery_log'].insert(0, log_entry)
                    st.success("Procedure successfully scored and logged!")
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")

    # --- THE SURGEON'S DIGITAL LEDGER ---
    st.markdown("---")
    st.subheader("Your Case Ledger")
    
    if st.session_state['surgery_log']:
        for case in st.session_state['surgery_log']:
            with st.expander(f"{case['status']} | {case['procedure']} | Score: {case['score']}/5"):
                st.write(f"**Surgeon:** {case['surgeon']}")
                st.write(f"**Context Added:** {case['context'] if case['context'] else 'None'}")
                st.write(f"**AI Reasoning:** {case['reasoning']}")
                st.write(f"**Audit/Billing Ref:** {case['audit_ref'] if case['audit_ref'] else 'Not Provided'}")
    else:
        st.caption("No cases logged yet. Enter a procedure above to see your AI score.")

# ==========================================
# MODULE 2: REVENUE PROTECTION
# ==========================================
elif module == "💰 Module 2: Revenue Protection":
    st.title("💰 Pre-Submission Intelligence")
    st.markdown("### Stop Insurance Rejections Before They Happen.")
    st.warning("AI generates mandatory billing checklists to prevent revenue leakage from undercoded or poorly documented complex surgeries.")

    with st.form("revenue_form"):
        st.subheader("Generate Operative Note Checklist")
        procedure_to_check = st.text_input("Planned Procedure", placeholder="e.g., Total Knee Arthroplasty (Bilateral) or Radical Mastectomy")
        
        generate_checklist = st.form_submit_button("Generate TPA Compliance Checklist")

    if generate_checklist:
        if not procedure_to_check:
            st.error("Please enter a procedure name.")
        else:
            with st.spinner("Analyzing TPA documentation requirements..."):
                try:
                    # 1. The Prompt (Acting as an Indian Insurance Auditor)
                    prompt = f"""
                    You are a veteran Medical Biller and Insurance Auditor specializing in the Indian private hospital and TPA (Third Party Administrator) landscape. 
                    
                    A surgeon is about to write the operative notes for: {procedure_to_check}.
                    
                    To prevent claim rejection or undercoding, what are the top 3 to 5 specific, critical anatomical or procedural details that MUST be explicitly documented in the operative notes? 
                    
                    Provide the response as a clear, concise, bulleted checklist. Do not include introductory fluff. Just the actionable checklist.
                    """
                    
                    # 2. Call the Model
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    response = model.generate_content(prompt)
                    
                    # 3. Display the Output
                    st.success("TPA Audit Rules Applied")
                    st.markdown("### 📋 Required Op-Note Documentation:")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")
# ==========================================
# MODULE 3: TALENT INTELLIGENCE
# ==========================================
elif module == "📊 Module 3: Talent Intelligence":
    st.title("📊 Clinical Governance & OT Allocation")
    st.markdown("### Strategic Resource Management for Administrators.")
    st.success("Identify your highest-complexity surgeons for priority OT allocation and retention tracking.")

    # Check if there is data to display
    if 'surgery_log' not in st.session_state or len(st.session_state['surgery_log']) == 0:
        st.info("No surgical data available yet. Have your surgeons log cases in Module 1 to populate this dashboard.")
    else:
        # Convert the ledger into a Pandas DataFrame for analysis
        df = pd.DataFrame(st.session_state['surgery_log'])
        
        # --- TOP LEVEL METRICS ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases Logged", len(df))
        with col2:
            st.metric("Avg Hospital Complexity", round(df['score'].mean(), 1))
        with col3:
            verified_cases = len(df[df['status'] == "🟢 VERIFIED"])
            st.metric("Verified Audit Rate", f"{int((verified_cases/len(df))*100)}%")

        st.markdown("---")
        
        # --- THE ALTAIR VISUALIZATION ---
        st.subheader("Surgeon Complexity Matrix")
        
        # Group the data by surgeon to get their average score and total volume
        surgeon_stats = df.groupby('surgeon').agg(
            Avg_Complexity=('score', 'mean'),
            Total_Cases=('procedure', 'count')
        ).reset_index()

        # Build a scatter plot showing Volume vs. Complexity
        chart = alt.Chart(surgeon_stats).mark_circle(size=600).encode(
            x=alt.X('Total_Cases', title='Total Cases Performed', axis=alt.Axis(tickMinStep=1)),
            y=alt.Y('Avg_Complexity', title='Average Complexity Score (1-5)', scale=alt.Scale(domain=[0, 5.5])),
            color=alt.Color('surgeon', legend=alt.Legend(title="Surgeon")),
            tooltip=['surgeon', 'Total_Cases', 'Avg_Complexity']
        ).properties(height=400, title="Volume vs. Surgical Complexity")
        
        st.altair_chart(chart, use_container_width=True)

        # --- AI STRATEGIC ALERTS ---
        st.subheader("Strategic OT Allocation Alerts")
        
        # Find the surgeon with the highest average complexity
        top_surgeon = surgeon_stats.loc[surgeon_stats['Avg_Complexity'].idxmax()]
        
        if top_surgeon['Avg_Complexity'] >= 3.5:
            st.warning(f"🏆 **High-Value Talent Detected:** Dr. {top_surgeon['surgeon']} is operating at an elite complexity level ({round(top_surgeon['Avg_Complexity'], 1)}/5). \n\n**Recommendation:** Prioritize main OT scheduling for this unit to maximize tertiary care revenue and retain top talent.")
        else:
            st.info("Log more Level 4 and 5 cases to generate AI-driven OT allocation recommendations.")
