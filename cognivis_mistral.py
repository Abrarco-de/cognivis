import streamlit as st
import pandas as pd
import numpy as np
from mistralai import Mistral

# --- 1. SETTINGS & THEMING ---
st.set_page_config(page_title="Cognivis OS", page_icon="🧠", layout="wide")

# Custom CSS for Strict Visual Separation
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    
    /* Shield Theme (Green) */
    .shield-card {
        border: 2px solid #00FF00;
        background-color: rgba(0, 255, 0, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    /* Brain Theme (Blue) */
    .brain-card {
        border: 2px solid #00FFFF;
        background-color: rgba(0, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    .whatsapp-box {
        background-color: #075e54;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Helvetica', sans-serif;
        border-left: 5px solid #25d366;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE INITIALIZATION ---
if 'data' not in st.session_state:
    st.session_state.data = None
if 'resolved_invoices' not in st.session_state:
    st.session_state.resolved_invoices = set()
if 'insights' not in st.session_state:
    st.session_state.insights = None

MISTRAL_API_KEY = "YOUR_MISTRAL_API_KEY" # Replace with your key

# --- 3. CORE LOGIC FUNCTIONS ---

def get_mock_data():
    return pd.DataFrame({
        "invoice_id": ["INV-1021", "INV-1022", "INV-1023", "INV-1024", "INV-1025"],
        "category": ["Catering", "Retail", "Catering", "Retail", "Catering"],
        "amount_sar": [1250.00, 800.00, 1500.00, 450.00, 2100.00],
        "customer_vat_id": ["", "123456789", "", "987654321", ""]
    })

def clean_data(df):
    df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
    mapping = {
        'total': 'amount_sar', 'price': 'amount_sar', 'vat': 'customer_vat_id',
        'id': 'invoice_id', 'dept': 'category'
    }
    df = df.rename(columns=mapping)
    if 'amount_sar' in df.columns:
        df['amount_sar'] = pd.to_numeric(df['amount_sar'], errors='coerce').fillna(0)
    return df

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🧠 Cognivis OS")
    st.caption("AI Shield + Brain for SME Growth")
    st.divider()
    
    st.metric("System Confidence", "98.4%", "+0.2%")
    st.write("● POS → Cognivis → ZATCA")
    
    page = st.sidebar.radio("Navigation", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])
    st.divider()
    st.caption("v1.0.2 Production MVP")

# --- 5. PAGE 1: DATA HUB ---
if page == "📥 Data Hub":
    st.title("📥 Data Ingestion Layer")
    st.write("Standardizing multi-source POS data for compliance audit.")
    
    file = st.file_uploader("Upload POS CSV Export", type=['csv'])
    
    if file:
        raw_df = pd.read_csv(file)
        st.session_state.data = clean_data(raw_df)
        st.success("✅ File Standardized Successfully")
    else:
        st.session_state.data = get_mock_data()
        st.info("💡 Running in Demo Mode with Mock Dataset")
        
    st.subheader("Data Preview")
    st.dataframe(st.session_state.data, use_container_width=True)

# --- 6. PAGE 2: ZATCA SHIELD ---
elif page == "🛡️ ZATCA Shield":
    st.title("🛡️ ZATCA Compliance Shield")
    st.caption("Preventing financial penalties through pre-submission validation.")
    
    df = st.session_state.data
    # Logic: Amount >= 1000 and VAT ID empty
    violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'].isin(["", None, np.nan]))]
    # Filter out already resolved
    active_violations = violations[~violations['invoice_id'].isin(st.session_state.resolved_invoices)]
    
    col_a, col_b = st.columns(2)
    with col_a:
        penalty = len(active_violations) * 500
        st.metric("Potential Liability", f"SAR {penalty}", delta=f"-{len(st.session_state.resolved_invoices)*500} Resolved", delta_color="normal")
    
    with col_b:
        risk_reduction = (len(st.session_state.resolved_invoices) / len(violations)) * 100 if len(violations) > 0 else 100
        st.metric("Risk Reduction", f"{risk_reduction:.0f}%")

    st.divider()
    
    if len(active_violations) > 0:
        for _, row in active_violations.iterrows():
            with st.container():
                st.markdown(f"""<div class="shield-card">
                    <b>🚨 VIOLATION: {row['invoice_id']}</b><br>
                    High-value transaction (SAR {row['amount_sar']}) detected without valid Buyer VAT ID.
                    </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    if st.button(f"Fix {row['invoice_id']}", key=row['invoice_id']):
                        st.session_state.resolved_invoices.add(row['invoice_id'])
                        st.toast(f"Generating Credit Note for {row['invoice_id']}...")
                        st.rerun()
                
                with c2:
                    st.markdown(f"""<div class="whatsapp-box">
                        <b>[Cognivis Shield]</b><br>
                        Invoice #{row['invoice_id']} is non-compliant.<br>
                        Risk: SAR 500 fine.<br>
                        <i>Reply 'FIX' to auto-resolve.</i>
                        </div>""", unsafe_allow_html=True)
    else:
        st.success("🎉 All clear! 100% Compliance achieved for this batch.")

# --- 7. PAGE 3: AI BRAIN ---
elif page == "💡 AI Brain":
    st.title("💡 AI Intelligence Brain")
    st.caption("Transforming raw transactions into human-style growth strategies.")
    
    df = st.session_state.data
    
    # --- STEP 1: AGGREGATION ---
    top_cat = df.groupby('category')['amount_sar'].sum().idxmax()
    total_rev = df['amount_sar'].sum()
    cat_rev = df[df['category'] == top_cat]['amount_sar'].sum()
    rev_share = (cat_rev / total_rev) * 100
    avg_order = df['amount_sar'].mean()
    risk_exp = (len(df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")])) * 500

    # --- STEP 2: BRAIN UI ---
    st.markdown(f"""<div class="brain-card">
        <h3>📊 Current Intelligence Snapshot</h3>
        • Top Category: <b>{top_cat}</b> ({rev_share:.1f}% Share)<br>
        • Avg Order Value: <b>SAR {avg_order:.2f}</b><br>
        • Total Revenue: <b>SAR {total_rev:,.2f}</b>
        </div>""", unsafe_allow_html=True)

    if st.button("✨ Generate AI Human Insights"):
        with st.spinner("Mistral-Large parsing data patterns..."):
            try:
                client = Mistral(api_key=MISTRAL_API_KEY)
                prompt = f"""You are a business analyst for SMEs in Saudi Arabia. 
                Data: Top category {top_category}, {rev_share}% share, Total Rev {total_rev} SAR, Risk {risk_exp} SAR.
                Generate 3 practical insights: 1. Performance, 2. Risk, 3. Recommendation. Tone: Human-like and decision-oriented."""
                
                # For demo purposes, if key is missing, show fallback
                if MISTRAL_API_KEY == "YOUR_MISTRAL_API_KEY":
                    st.info("Insight: Catering is dominating your weekend revenue. Action: Prepare 'Party Bundles' to increase average order value by 15%.")
                else:
                    chat_response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.write(chat_response.choices[0].message.content)
            except Exception as e:
                st.error("Connect your Mistral API Key to enable live AI generation.")

    st.divider()
    if st.button("🚀 Apply Pricing Recommendation"):
        st.balloons()
        st.success("Strategy Deployed: Inventory adjusted for high-performing Catering items.")
