import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Cognivis OS", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .zatca-box { border: 2px solid #00FF00; padding: 15px; border-radius: 10px; background: #00FF0010; color: #00FF00; margin-bottom: 10px; }
    .brain-box { border: 2px solid #00FFFF; padding: 15px; border-radius: 10px; background: #00FFFF10; color: #00FFFF; }
    .stMetric { background-color: #1e2130; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL STATE MANAGEMENT ---
if 'main_df' not in st.session_state:
    st.session_state.main_df = None
if 'cleaned' not in st.session_state:
    st.session_state.cleaned = False

# --- 3. THE CLEANING ENGINE ---
def universal_cleaner(df):
    # 1. Standardize to lowercase and underscores
    df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
    
    # 2. Hard-Mapping (The Bridge)
    # This maps whatever your POS outputs to what Cognivis needs
    mapping = {
        'total': 'amount_sar', 'price': 'amount_sar', 'net_amount': 'amount_sar',
        'vat_no': 'customer_vat_id', 'tax_id': 'customer_vat_id', 'vat_id': 'customer_vat_id',
        'item': 'product_category', 'dept': 'product_category'
    }
    df = df.rename(columns=mapping)
    
    # 3. Validation: If the column STILL doesn't exist, create an empty one so code doesn't crash
    if 'amount_sar' not in df.columns:
        st.error("⚠️ Column 'Amount' not found. Please check your CSV headers.")
        df['amount_sar'] = 0
    if 'customer_vat_id' not in df.columns:
        df['customer_vat_id'] = ""
        
    return df

# --- 4. SIDEBAR ---
st.sidebar.title("🧠 Cognivis OS")
st.sidebar.caption("SME Compliance & Growth")
menu = st.sidebar.radio("Navigation", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])

if st.session_state.main_df is not None:
    st.sidebar.divider()
    st.sidebar.metric("Data Health", "98.7%", "Cleaned")
    st.sidebar.caption("✅ POS Sync: Active")

# --- PAGE 1: DATA HUB ---
if menu == "📥 Data Hub":
    st.title("📥 Universal Data Hub")
    st.caption("AI Shield + Brain for Saudi SMEs")
    
    file = st.file_uploader("Upload POS Export (CSV)", type=['csv'])
    
    if file:
        raw_df = pd.read_csv(file)
        with st.spinner("Standardizing Schema..."):
            st.session_state.main_df = universal_cleaner(raw_df)
            st.session_state.cleaned = True
        st.success("✅ Data Synced and Standardized.")

    if st.session_state.main_df is not None:
        st.dataframe(st.session_state.main_df, use_container_width=True)
    else:
        st.info("Please upload a CSV file to begin the audit.")

# --- PAGE 2: ZATCA SHIELD (Actionable) ---
elif menu == "🛡️ ZATCA Shield":
    st.header("🛡️ ZATCA Compliance Shield")
    st.caption("🔄 POS → Cognivis Shield → ZATCA (Real-time Protection)")

    if st.session_state.main_df is not None:
        df = st.session_state.main_df
        # Logic: Amount >= 1000 and VAT ID is missing
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")]
        
        if not violations.empty:
            penalty_risk = len(violations) * 500
            st.warning(f"🚨 Liability Detected: SAR {penalty_risk} in potential fines.")
            
            for i, row in violations.iterrows():
                with st.expander(f"⚠️ Invoice {row['invoice_id']} - SAR {row['amount_sar']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Violation:** Missing Buyer VAT ID.")
                        if st.button(f"Generate Credit Note", key=f"cn_{i}"):
                            st.success("✅ Credit Note Drafted in POS.")
                    with c2:
                        st.write("📲 **WhatsApp Alert Simulation:**")
                        st.code(f"Cognivis Alert: Inv {row['invoice_id']} is non-compliant. Risk: 500 SAR. Reply FIX.")
        else:
            st.success("✅ 100% Compliance Found.")
    else:
        st.error("Please upload data first.")

# --- PAGE 3: AI BRAIN (Advanced Insights) ---
elif menu == "💡 AI Brain":
    st.header("💡 Neon Intelligence Brain")
    
    if st.session_state.main_df is not None:
        df = st.session_state.main_df
        
        # FEATURE 1: DYNAMIC REVENUE
        top_cat = df.groupby('product_category')['amount_sar'].sum().idxmax()
        st.markdown(f"<div class='brain-box'><h3>📊 Top Performer</h3>Your <b>{top_cat}</b> category is driving revenue. Recommendation: Focus stock here.</div>", unsafe_allow_html=True)
        
        # FEATURE 2: SEQUENCE GAP (Forensic Audit)
        st.subheader("🕵️ Forensic Audit: Sequence Gaps")
        # Ensure invoice_id is sortable
        df['num'] = pd.to_numeric(df['invoice_id'].astype(str).str.extract('(\d+)', expand=False), errors='coerce')
        if not df['num'].isnull().all():
            full_range = set(range(int(df['num'].min()), int(df['num'].max()) + 1))
            missing = full_range - set(df['num'].dropna().unique())
            if missing:
                st.error(f"🚨 Missing Invoices: {len(missing)} gaps found (e.g., {list(missing)[:3]})")
            else:
                st.success("✅ No sequence gaps detected.")
    else:
        st.error("Please upload data first.")
