import streamlit as st
import pandas as pd
from mistralai import Mistral

# --- MISTRAL CONFIG ---
MISTRAL_API_KEY = "YOUR_MISTRAL_KEY"

# --- UI STYLING ---
st.set_page_config(page_title="Cognivis OS", layout="wide")
st.markdown("""
    <style>
    .zatca-card { background-color: #00FF0015; border: 1px solid #00FF00; padding: 20px; border-radius: 10px; }
    .ai-card { background-color: #00FFFF15; border: 1px solid #00FFFF; padding: 20px; border-radius: 10px; }
    .stMetric { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LAYER 1: UNIVERSAL CLEANER ---
class DataCleaner:
    def __init__(self, df):
        self.df = df
        self.clean_df = pd.DataFrame()

    def auto_process(self):
        cols = {c.lower().replace(' ', '_'): c for c in self.df.columns}
        # Fuzzy mapping
        self.clean_df['ID'] = self.df[cols.get('invoice_number', self.df.columns[0])]
        
        amt_key = next((k for k in ['total', 'amount', 'price', 'grand_total'] if k in cols), self.df.columns[1])
        self.clean_df['Amount'] = pd.to_numeric(self.df[cols[amt_key]].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        
        vat_key = next((k for k in ['vat_number', 'tax_id', 'customer_vat'] if k in cols), None)
        self.clean_df['VAT_ID'] = self.df[cols[vat_key]].astype(str) if vat_key else ""
        
        return self.clean_df

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🧠 Cognivis Brain")
page = st.sidebar.radio("Go to:", ["📥 Data Upload", "🛡️ ZATCA Compliance", "💡 AI Human Insights"])
st.sidebar.divider()

if 'df' not in st.session_state:
    st.session_state.df = None

# --- PAGE 1: UPLOAD ---
if page == "📥 Data Upload":
    st.header("Step 1: Universal Data Ingestion")
    file = st.file_uploader("Upload POS CSV", type=['csv'])
    if file:
        raw = pd.read_csv(file)
        cleaner = DataCleaner(raw)
        st.session_state.df = cleaner.auto_process()
        st.success("Data Cleaned & Standardized.")
        st.dataframe(st.session_state.df)

# --- PAGE 2: ZATCA COMPLIANCE ---
elif page == "🛡️ ZATCA Compliance":
    st.header("Step 2: The ZATCA Shield")
    if st.session_state.df is not None:
        df = st.session_state.df
        violations = df[ (df['Amount'] >= 1000) & (df['VAT_ID'].str.len() < 5) ]
        
        # Safety Score Logic
        score = 100 - (len(violations) * 10)
        st.metric("Compliance Safety Score", f"{max(score, 0)}%", delta="-8%" if len(violations) > 0 else "Optimal")
        
        if not violations.empty:
            for _, row in violations.iterrows():
                st.markdown(f"""<div class='zatca-card'>🚨 <b>Violation:</b> Invoice {row['ID']} exceeds 1,000 SAR but lacks a Buyer VAT ID.</div>""", unsafe_allow_html=True)
        else:
            st.success("No ZATCA risks found.")

# --- PAGE 3: AI INSIGHTS ---
elif page == "💡 AI Human Insights":
    st.header("Step 3: Neon Intelligence")
    if st.session_state.df is not None:
        st.markdown("<div class='ai-card'>Scanning for business patterns...</div>", unsafe_allow_html=True)
        if st.button("Generate Human-Style Insights"):
            # Mocking the Mistral call for flow
            st.info("Insight: Your top selling item is performing well, but your margin on high-value orders is at risk due to compliance gaps.")
