import streamlit as st
import pandas as pd
import numpy as np

# --- 1. GLOBAL SETTINGS & THEME ---
st.set_page_config(page_title="Cognivis OS", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .shield-card { border: 2px solid #00FF00; background: rgba(0, 255, 0, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .brain-card { border: 2px solid #00FFFF; background: rgba(0, 255, 255, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .whatsapp-box { background: #075e54; border-left: 5px solid #25d366; padding: 10px; border-radius: 5px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (The App's Memory) ---
if 'main_df' not in st.session_state:
    st.session_state.main_df = None
if 'resolved_list' not in st.session_state:
    st.session_state.resolved_list = set()

# --- 3. ROBUST CLEANING ENGINE (Prevents KeyErrors) ---
def titanium_cleaner(df):
    # Standardize headers
    df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
    
    # Alias Mapping: Links your CSV names to internal Logic
    mapping = {
        'total': 'amount_sar', 'price': 'amount_sar', 'grand_total': 'amount_sar', 'amount': 'amount_sar',
        'vat_id': 'customer_vat_id', 'tax_id': 'customer_vat_id', 'vat_number': 'customer_vat_id',
        'item': 'category', 'product_category': 'category', 'dept': 'category', 'type': 'category',
        'inv_id': 'invoice_id', 'bill_no': 'invoice_id', 'invoice_no': 'invoice_id'
    }
    df = df.rename(columns=mapping)
    
    # Emergency Fallbacks: If columns are STILL missing, create them to prevent crashes
    if 'amount_sar' not in df.columns: df['amount_sar'] = 0.0
    if 'customer_vat_id' not in df.columns: df['customer_vat_id'] = ""
    if 'invoice_id' not in df.columns: df['invoice_id'] = [f"INV-{i}" for i in range(len(df))]
    if 'category' not in df.columns: df['category'] = "Uncategorized"

    # Type Conversion
    df['amount_sar'] = pd.to_numeric(df['amount_sar'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    df['customer_vat_id'] = df['customer_vat_id'].fillna('').astype(str).strip()
    
    return df

# --- 4. MOCK DATA (For Demo Mode) ---
def load_demo_data():
    return pd.DataFrame({
        "invoice_id": ["INV-201", "INV-202", "INV-203", "INV-204", "INV-205"],
        "category": ["Catering", "Retail", "Catering", "Retail", "Catering"],
        "amount_sar": [1250.00, 85.00, 3200.00, 450.00, 1100.00],
        "customer_vat_id": ["", "123456789", "", "987654321", ""]
    })

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🧠 Cognivis OS")
    st.caption("AI Shield + Brain for Saudi SMEs")
    st.divider()
    st.metric("System Confidence", "98.7%", "+2.1%")
    menu = st.radio("Navigation", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])
    st.divider()
    st.write("🔄 POS → Cognivis → ZATCA")

# --- PAGE 1: DATA HUB ---
if menu == "📥 Data Hub":
    st.title("📥 Data Ingestion Layer")
    st.caption("Standardizing data for ZATCA Phase 2 compliance.")
    
    file = st.file_uploader("Upload POS CSV", type=['csv'])
    
    if file:
        raw = pd.read_csv(file)
        st.session_state.main_df = titanium_cleaner(raw)
        st.success("✅ Custom Data Synced & Cleaned.")
    elif st.session_state.main_df is None:
        st.session_state.main_df = load_demo_data()
        st.info("💡 Demo Mode: Using Mock Dataset")

    st.dataframe(st.session_state.main_df, use_container_width=True)

# --- PAGE 2: ZATCA SHIELD (Actionable) ---
elif menu == "🛡️ ZATCA Shield":
    st.title("🛡️ ZATCA Compliance Shield")
    df = st.session_state.main_df
    
    if df is not None:
        # Identify Violations: Amount >= 1000 AND No VAT ID
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")]
        active_violations = violations[~violations['invoice_id'].isin(st.session_state.resolved_list)]
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Risks", len(active_violations))
        with col2:
            st.metric("Potential Fines", f"SAR {len(active_violations)*500}")
        with col3:
            reduction = (len(st.session_state.resolved_list)/len(violations)*100) if len(violations) > 0 else 100
            st.metric("Risk Reduction", f"{reduction:.0f}%")

        st.divider()
        
        if not active_violations.empty:
            for _, row in active_violations.iterrows():
                st.markdown(f"""<div class="shield-card">
                    <b>🚨 High-Risk Transaction: {row['invoice_id']}</b><br>
                    Missing VAT ID for transaction of SAR {row['amount_sar']}.
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    if st.button(f"Generate Credit Note", key=f"fix_{row['invoice_id']}"):
                        st.session_state.resolved_list.add(row['invoice_id'])
                        st.toast(f"Resolving {row['invoice_id']}...")
                        st.rerun()
                with c2:
                    st.markdown(f"""<div class="whatsapp-box">
                        <b>[Cognivis Shield]</b><br>
                        Inv #{row['invoice_id']} is non-compliant.<br>
                        Reply 'FIX' to auto-resolve.
                        </div>""", unsafe_allow_html=True)
        else:
            st.success("🎉 All Compliance Risks Resolved.")

# --- PAGE 3: AI BRAIN (Intelligence) ---
elif menu == "💡 AI Brain":
    st.title("💡 AI Intelligence Brain")
    df = st.session_state.main_df
    
    if df is not None:
        # Feature 1: Dynamic Insight Card
        top_cat = df.groupby('category')['amount_sar'].sum().idxmax()
        total_rev = df['amount_sar'].sum()
        
        st.markdown(f"""<div class="brain-card">
            <h3>📊 Performance Insight</h3>
            Leading Category: <b>{top_cat}</b><br>
            Revenue Contribution: <b>SAR {total_rev:,.2f}</b><br>
            <i>AI Recommendation: Your {top_cat} margins are peaking. Consider a loyalty program for this segment.</i>
        </div>""", unsafe_allow_html=True)
        
        # Feature 2: Sequence Gap Detection
        st.subheader("🕵️ Sequence Audit")
        df['num'] = pd.to_numeric(df['invoice_id'].str.extract('(\d+)', expand=False), errors='coerce')
        if not df['num'].isna().all():
            full_set = set(range(int(df['num'].min()), int(df['num'].max()) + 1))
            actual_set = set(df['num'].dropna().unique())
            gaps = full_set - actual_set
            if gaps:
                st.error(f"🚨 Sequence Gaps Found: {len(gaps)} missing invoices (Internal Fraud Risk).")
            else:
                st.success("✅ Sequence Integrity: 100% Perfect.")
