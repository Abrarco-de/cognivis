import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. GLOBAL UI CONFIGURATION ---
st.set_page_config(page_title="Cognivis OS", page_icon="🧠", layout="wide")

# Custom CSS for SaaS UI Branding
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Shield Branding (Green) */
    .shield-card {
        border: 2px solid #00FF00;
        background-color: rgba(0, 255, 0, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    /* Brain Branding (Blue) */
    .brain-card {
        border: 2px solid #00FFFF;
        background-color: rgba(0, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    .whatsapp-box {
        background-color: #075e54;
        border-left: 5px solid #25d366;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Helvetica', sans-serif;
    }
    
    .metric-container {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Persistence Layer) ---
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None
if 'resolved_invoices' not in st.session_state:
    st.session_state.resolved_invoices = set()
if 'applied_recommendations' not in st.session_state:
    st.session_state.applied_recommendations = False

# --- 3. DATA ENGINE (Ingestion & Cleaning) ---
def titanium_cleaner(df):
    """Standardizes any POS export into the Cognivis Schema."""
    df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
    
    mapping = {
        'invoice': 'invoice_id', 'inv_id': 'invoice_id', 'bill_no': 'invoice_id',
        'amount': 'amount_sar', 'total': 'amount_sar', 'price': 'amount_sar',
        'vat': 'customer_vat_id', 'tax_id': 'customer_vat_id',
        'category': 'category', 'item_group': 'category'
    }
    df = df.rename(columns=mapping)
    
    # Critical Fixes
    if 'amount_sar' in df.columns:
        df['amount_sar'] = pd.to_numeric(df['amount_sar'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    if 'customer_vat_id' in df.columns:
        df['customer_vat_id'] = df['customer_vat_id'].fillna('').astype(str).str.strip()
    else:
        df['customer_vat_id'] = ""
    if 'category' not in df.columns:
        df['category'] = "General"
        
    return df

def get_mock_data():
    return pd.DataFrame({
        "invoice_id": ["INV-8801", "INV-8802", "INV-8803", "INV-8804", "INV-8805"],
        "category": ["Catering", "Retail", "Catering", "Retail", "Catering"],
        "amount_sar": [1450.00, 85.00, 3200.00, 450.00, 950.00],
        "customer_vat_id": ["", "123456789", "", "987654321", ""]
    })

# --- 4. NAVIGATION ---
with st.sidebar:
    st.title("🧠 Cognivis OS")
    st.caption("AI Shield + Brain for SME Growth")
    st.divider()
    
    st.metric("System Confidence", "98.7%", "+0.2%")
    st.write("🔄 **System Flow:**")
    st.caption("POS → Cognivis Shield → ZATCA")
    
    menu = st.radio("Menu", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])
    st.divider()
    st.info("Demo Mode Active")

# Load Data logic
if st.session_state.raw_data is None:
    st.session_state.raw_data = get_mock_data()

# --- 5. PAGE 1: DATA HUB ---
if menu == "📥 Data Hub":
    st.title("📥 Data Ingestion Layer")
    st.write("Universal schema detection for local POS exports.")
    
    uploaded_file = st.file_uploader("Upload POS CSV", type=['csv'])
    if uploaded_file:
        raw = pd.read_csv(uploaded_file)
        st.session_state.raw_data = titanium_cleaner(raw)
        st.success("✅ Data standardized successfully.")
    
    st.subheader("Data Stream Preview")
    st.dataframe(st.session_state.raw_data, use_container_width=True)
    if not uploaded_file:
        st.caption("⚠️ Displaying mock dataset for demonstration.")

# --- 6. PAGE 2: ZATCA SHIELD ---
elif menu == "🛡️ ZATCA Shield":
    st.title("🛡️ ZATCA Compliance Shield")
    df = st.session_state.raw_data
    
    # Compliance Logic
    violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")]
    active_violations = violations[~violations['invoice_id'].isin(st.session_state.resolved_invoices)]
    
    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Active Violations", len(active_violations))
    with m2:
        penalty = len(active_violations) * 500
        st.metric("Potential Liability", f"SAR {penalty}")
    with m3:
        reduction = (len(st.session_state.resolved_invoices) / len(violations)) * 100 if len(violations) > 0 else 100
        st.metric("Risk Reduction", f"{reduction:.0f}%")

    st.divider()
    
    if not active_violations.empty:
        for index, row in active_violations.iterrows():
            with st.container():
                st.markdown(f"""<div class="shield-card">
                    <b>🚨 Violation Detected: {row['invoice_id']}</b><br>
                    Issue: Amount (SAR {row['amount_sar']}) exceeds threshold for Simplified Invoices without Buyer VAT ID.
                </div>""", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button(f"Fix Invoice {row['invoice_id']}", key=f"btn_{index}"):
                        with st.spinner("Generating Credit Note..."):
                            time.sleep(1)
                            st.session_state.resolved_invoices.add(row['invoice_id'])
                            st.rerun()
                with col2:
                    st.markdown(f"""<div class="whatsapp-box">
                        <b>[Cognivis Shield]</b><br>
                        Invoice #{row['invoice_id']} is non-compliant.<br>
                        Risk: SAR 500 fine.<br>
                        Reply 'FIX' to auto-resolve.
                        </div>""", unsafe_allow_html=True)
    else:
        st.success("🎉 All compliance risks resolved. Data is ready for ZATCA submission.")

# --- 7. PAGE 3: AI BRAIN ---
elif menu == "💡 AI Brain":
    st.title("💡 AI Intelligence Brain")
    df = st.session_state.raw_data
    
    # Data Aggregation
    total_rev = df['amount_sar'].sum()
    top_cat = df.groupby('category')['amount_sar'].sum().idxmax()
    top_val = df.groupby('category')['amount_sar'].sum().max()
    share = (top_val / total_rev) * 100
    avg_order = df['amount_sar'].mean()
    risk_exp = (len(df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")])) * 500

    # Structured context for Brain Card
    st.markdown(f"""<div class="brain-card">
        <h3>📊 Intelligence Snapshot</h3>
        • Top Revenue Driver: <b>{top_cat}</b><br>
        • Category Share: <b>{share:.1f}%</b><br>
        • Avg. Ticket Size: <b>SAR {avg_order:.2f}</b><br>
        • Current Risk Exposure: <b>SAR {risk_exp}</b>
        </div>""", unsafe_allow_html=True)

    st.subheader("🧠 Human-Like Insights (Mistral Powered)")
    
    # Mock AI insights for production feel
    with st.expander("✨ View Latest Analysis", expanded=True):
        st.write(f"**📊 Performance:** Your {top_cat} category is currently carrying {share:.0f}% of your volume. This indicates a high concentration of corporate-style demand.")
        st.write(f"**⚠️ Risk:** You have SAR {risk_exp} in audit risk due to missing buyer details on high-value tickets.")
        st.write(f"**🚀 Recommendation:** Increase stock for {top_cat} supplies by 15% before the weekend peak.")
        
        if not st.session_state.applied_recommendations:
            if st.button("Apply Recommendation"):
                with st.spinner("Updating inventory & pricing..."):
                    time.sleep(1.5)
                    st.session_state.applied_recommendations = True
                    st.rerun()
        else:
            st.success("✅ Recommendation applied to POS system.")

    # Forensic Audit Feature
    st.divider()
    st.subheader("🕵️ Forensic Audit: Sequence Gaps")
    df['num'] = pd.to_numeric(df['invoice_id'].str.extract('(\d+)', expand=False), errors='coerce')
    if not df['num'].isna().all():
        full_range = set(range(int(df['num'].min()), int(df['num'].max()) + 1))
        missing = full_range - set(df['num'].dropna().unique())
        if missing:
            st.error(f"🚨 Sequence Gaps Found: {len(missing)} missing invoices detected.")
        else:
            st.success("✅ Sequential Integrity Verified (100%).")
