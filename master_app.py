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
                    
                    # 2. Call the Model
                    model = genai.GenerativeModel('gemini-1.5-flash')
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
    st.warning("AI will analyze operative notes to generate a mandatory billing checklist, preventing revenue leakage from undercoded complex surgeries.")
    
    # We will build the Gemini API prompt for insurance here!
    st.write("*(Insurance checklist generator coming soon...)*")

# ==========================================
# MODULE 3: TALENT INTELLIGENCE
# ==========================================
elif module == "📊 Module 3: Talent Intelligence":
    st.title("📊 Clinical Governance & OT Allocation")
    st.markdown("### Strategic Resource Management for Administrators.")
    st.success("Identify your highest-complexity surgeons for priority OT allocation and retention tracking.")
    
    # We will move your Altair graphs here!
    st.write("*(Complexity trend graphs coming soon...)*")
