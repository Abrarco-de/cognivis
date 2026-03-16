import streamlit as st
import pandas as pd
import numpy as np
from mistralai import Mistral # Optimized for v1.1.0+

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cognivis OS", layout="wide", page_icon="🧠")

# --- 2. DATA CLEANING ENGINE (Universal POS Ingestion) ---
class DataCleaner:
    def __init__(self, df):
        self.raw_df = df
        self.clean_df = pd.DataFrame()

    def standardize(self):
        df = self.raw_df.copy()
        df.columns = df.columns.str.lower().str.strip()
        
        # Fuzzy Logic for Column Mapping
        mapping = {
            'Invoice_ID': ['invoice number', 'receipt no', 'id', 'invoice', 'receipt'],
            'Amount': ['price', 'total', 'amount', 'grand total', 'net total'],
            'Buyer_VAT': ['vat number', 'customer vat', 'tax id', 'buyer_vat', 'customer_tax'],
            'Product': ['product name', 'item', 'description', 'product']
        }

        for target, keywords in mapping.items():
            found_col = next((col for col in keywords if col in df.columns), None)
            if found_col:
                if target == 'Amount':
                    # Strip 'SAR' or symbols and convert to float
                    self.clean_df[target] = df[found_col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                    self.clean_df[target] = pd.to_numeric(self.clean_df[target], errors='coerce').fillna(0)
                else:
                    self.clean_df[target] = df[found_col]
            else:
                self.clean_df[target] = "" if target != 'Amount' else 0.0

        return self.clean_df

# --- 3. ZATCA SHIELD (Hardcoded Logic) ---
def run_zatca_audit(df):
    violations = []
    total_rev = df['Amount'].sum()
    
    for _, row in df.iterrows():
        # The 1000 SAR Threshold Rule
        if row['Amount'] >= 1000:
            vat_val = str(row['Buyer_VAT']).strip()
            if vat_val == "" or vat_val.lower() == "nan" or len(vat_val) < 5:
                violations.append({
                    "id": row['Invoice_ID'],
                    "amt": row['Amount'],
                    "msg": "Missing or Invalid Buyer VAT for sale >1000 SAR"
                })
    
    fact_sheet = {
        "revenue": total_rev,
        "violation_count": len(violations),
        "total_tx": len(df),
        "top_item": df['Product'].mode()[0] if not df.empty else "N/A"
    }
    return fact_sheet, violations

# --- 4. MISTRAL INTELLIGENCE LAYER ---
def get_mistral_insights(fact_sheet, api_key):
    # Instead of: api_key = st.sidebar.text_input(...)
# Use this:
try:
    api_key = st.secrets["MISTRAL_API_KEY"]
except:
    api_key = st.sidebar.text_input("Enter Mistral Key (Secret not found)", type="password")

# Then pass it to the Brain
insight = get_mistral_insights(facts, api_key)
    
    try:
        client = Mistral(api_key=api_key)
        
        prompt = f"""
        You are Cognivis AI, a Saudi retail expert. 
        Analyze these facts: {fact_sheet}.
        Provide a 3-part insight:
        1. Insight (Business trend)
        2. Possible Reason (Why)
        3. Recommendation (Action)
        Keep it human-like and short. No bold text.
        """

        # New Mistral v1.1.0 Call Format
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Brain Error: {str(e)}"

# --- 5. UI DASHBOARD ---
st.title("🧠 Cognivis OS")
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Mistral API Key", type="password")

uploaded_file = st.file_uploader("Upload POS Data (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    # Load and Clean
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    clean_df = DataCleaner(raw_df).standardize()
    facts, alerts = run_zatca_audit(clean_df)

    # UI Columns
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("🛡️ Compliance & Data")
        st.dataframe(clean_df, use_container_width=True)
        
        if alerts:
            st.error(f"ZATCA Risks Detected: {len(alerts)}")
            for a in alerts:
                # WhatsApp UI Simulation
                st.markdown(f"""
                <div style="background-color:#e1ffc7; padding:10px; border-radius:10px; margin-bottom:5px; color:#000; border-left:4px solid #25d366">
                <b>🚨 ZATCA Alert</b><br>Invoice {a['id']} ({a['amt']} SAR) is non-compliant.<br><i>{a['msg']}</i>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ System Compliant")

    with col_right:
        st.subheader("💡 AI Brain")
        if st.button("Run Analysis"):
            with st.spinner("Thinking..."):
                insight = get_mistral_insights(facts, api_key)
                st.info(insight)
        
        st.divider()
        st.metric("Total Revenue", f"{facts['revenue']} SAR")
        st.metric("Clean Transactions", facts['total_tx'])

else:
    st.write("Awaiting data upload...")
