import streamlit as st
import json
import os
import pandas as pd
import altair as alt
from datetime import datetime
import google.generativeai as genai

# --- SECURE CLOUD API KEY ---
genai.configure(api_key=st.secrets["AIzaSyDkx3XgUO-uePfoblHpefqv2_tZHRlgUOA"])
# ----------------------------

st.set_page_config(page_title="Surgical Ledger V1.6", layout="wide")

DB_FILE = "hospital_ledger.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

st.sidebar.title("🏥 Hospital Navigation")
page = st.sidebar.radio("Select Module:", ["1. HR Data Entry", "2. CEO Dashboard"])
st.sidebar.divider()
st.sidebar.info("Base Product Architecture V1.6 - Ready for Soft Demo")

# ==========================================
# PAGE 1: HR DATA ENTRY
# ==========================================
if page == "1. HR Data Entry":
    st.title("Surgical Reputation Ledger")
    st.subheader("HR Data Entry Portal (Level 3 Gold Standard)")
    st.divider()

    doctor_id = st.text_input("Enter NMC Registration Number", placeholder="e.g., NMC-UP-1234").strip()
    surgery_type = st.text_input("Surgery Type / Procedure Name", placeholder="e.g., Laparoscopic Appendectomy")

    col1, col2 = st.columns(2)
    with col1:
        outcome = st.radio("Surgical Outcome", ["Success", "Failure / Mortality"])
    with col2:
        variance = st.checkbox("⚠️ Patient faced complications NOT in pre-op consent")

    insurance_id = st.text_input("Insurance Claim / TPA Reference ID", placeholder="e.g., INS-888999")
    st.divider()

    if st.button("Log Surgery & Save to Ledger", type="primary"):
        if doctor_id and surgery_type:
            with st.spinner("Gemini AI analyzing medical complexity..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"""
                    Act as a Senior Medical Auditor. Analyze this surgery: {surgery_type}.
                    Provide a rarity/complexity score from 1 (Common/Simple) to 5 (Ultra-Rare/Highly Complex).
                    Consider standard hospital capabilities in Uttar Pradesh vs India vs Globally.
                    Return ONLY a valid JSON object with these exact three keys and integer values:
                    {{"state_tier": 0, "country_tier": 0, "global_tier": 0}}
                    """
                    
                    response = model.generate_content(prompt)
                    ai_text = response.text.strip().replace('```json', '').replace('```', '')
                    ai_scores = json.loads(ai_text)
                    
                    state_score = ai_scores.get("state_tier", 1)
                    country_score = ai_scores.get("country_tier", 1)
                    global_score = ai_scores.get("global_tier", 1)
                    blended_score = (state_score * 0.5) + (country_score * 0.3) + (global_score * 0.2)

                    ledger_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "surgery_type": surgery_type,
                        "outcome": {"status": outcome, "matches_consent": not variance},
                        "verification": {"insurance_claim_id": insurance_id, "gold_verified": bool(insurance_id)},
                        "ai_scores": {"blended": round(blended_score, 2)}
                    }

                    if doctor_id not in db:
                        db[doctor_id] = []
                    
                    db[doctor_id].append(ledger_entry)
                    save_db(db)
                    
                    st.success(f"Surgery logged! {doctor_id} now has {len(db[doctor_id])} procedure(s) on record.")

                except Exception as e:
                    st.error(f"AI Connection Error. Error details: {e}")
        else:
            st.error("Please enter both Doctor ID and Surgery Type.")

# ==========================================
# PAGE 2: CEO Dashboard
# ==========================================
elif page == "2. CEO Dashboard":
    st.title("Surgical Talent Acquisition Dashboard")
    st.divider()

    search_id = st.text_input("🔍 Search Surgeon by NMC ID", placeholder="e.g., NMC-UP-1234").strip()

    if st.button("Analyze Surgeon Profile", type="primary"):
        if search_id in db:
            surgeries = db[search_id]
            total_surgeries = len(surgeries)
            
            # THE NEW HEADER UPGRADE
            latest_surgery = surgeries[-1]['surgery_type']
            st.success("✅ Active Ledger Found")
            st.markdown(f"## Profile: {search_id}")
            st.markdown(f"**Latest Focus Area:** {latest_surgery}")
            st.divider()
            
            total_score = sum(s['ai_scores']['blended'] for s in surgeries)
            avg_score = round(total_score / total_surgeries, 2)
            total_verified = sum(1 for s in surgeries if s['verification']['gold_verified'])
            total_incidents = sum(1 for s in surgeries if not s['outcome']['matches_consent'])
            
            st.markdown("### 🏆 Career Performance Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Career Avg Complexity", f"{avg_score} / 5.0", f"Across {total_surgeries} Surgeries")
            with col2:
                st.metric("Gold Verified", f"{total_verified} / {total_surgeries}", f"{int((total_verified/total_surgeries)*100)}% Audit Rate")
            with col3:
                color = "normal" if total_incidents == 0 else "inverse"
                st.metric("Total Safety Variances", f"{total_incidents} Incidents", "Career Legal Risk", delta_color=color)
            
            st.divider()

            # --- THE LOCKED AXIS GRAPH UPGRADE ---
            st.markdown("### 📈 Surgical Complexity Trend")
            if total_surgeries > 1:
                trend_data = [s['ai_scores']['blended'] for s in surgeries]
                chart_data = pd.DataFrame({
                    "Procedure": range(1, total_surgeries + 1),
                    "Complexity Score": trend_data
                })
                
                # Altair chart forces the Y-Axis to stay between 0 and 5.5
                chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X('Procedure:O', title="Surgery Number"),
                    y=alt.Y('Complexity Score:Q', scale=alt.Scale(domain=[0, 5.5]), title="AI Rarity Score (0-5)")
                ).properties(height=300)
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("💡 Log at least one more surgery for this doctor to generate a trend graph.")

            st.divider()
            
            st.markdown("### 📜 Surgical History Log")
            for idx, s in enumerate(reversed(surgeries)):
                variance_icon = "✅ Safe" if s['outcome']['matches_consent'] else "⚠️ Complication"
                st.markdown(f"**{total_surgeries - idx}. {s['surgery_type']}** | Score: {s['ai_scores']['blended']} | {variance_icon} | Date: {s['timestamp']}")

        elif search_id:
            st.error("Surgeon not found. Please log a surgery for them first!")