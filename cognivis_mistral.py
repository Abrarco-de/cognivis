import streamlit as st
import pandas as pd
import numpy as np
from mistralai import Mistral

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cognivis OS", layout="wide", page_icon="🧠")

# --- 2. DATA CLEANING ENGINE ---
class DataCleaner:
    def __init__(self, df):
        self.raw_df = df
        self.clean_df = pd.DataFrame()

    def standardize(self):
        df = self.raw_df.copy()
        # Clean headers: lowercase and remove extra spaces
        df.columns = df.columns.str.lower().str.strip()
        
        mapping = {
            'Invoice_ID': ['invoice number', 'receipt no', 'id', 'invoice', 'receipt'],
            'Amount': ['price', 'total', 'amount', 'grand total', 'net total'],
            'Buyer_VAT': ['vat number', 'customer vat', 'tax id', 'buyer_vat', 'customer_tax'],
            'Product': ['product name', 'item', 'description', 'product', 'item description']
        }

        for target, keywords in mapping.items():
            # Match any of our keywords to the actual column names
            found_col = next((col for col in df.columns if col in keywords), None)
            
            if found_col:
                if target == 'Amount':
                    self.clean_df[target] = df[found_col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                    self.clean_df[target] = pd.to_numeric(self.clean_df[target], errors='coerce').fillna(0)
                else:
                    self.clean_df[target] = df[found_col]
            else:
                self.clean_df[target] = "Unknown" if target != 'Amount' else 0.0
        return self.clean_df

# --- 3. ZATCA SHIELD LOGIC ---
def run_zatca_audit(df):
    violations = []
    total_rev = df['Amount'].sum()
    
    for _, row in df.iterrows():
        if row['Amount'] >= 1000:
            vat_val = str(row['Buyer_VAT']).strip()
            if vat_val == "" or vat_val.lower() == "nan" or len(vat_val) < 5:
                violations.append({
                    "id": row['Invoice_ID'],
                    "amt": row['Amount'],
                    "msg": "Missing/Invalid Buyer VAT for sale >1000 SAR"
                })
    
    fact_sheet = {
        "revenue": total_rev,
        "violation_count": len(violations),
        "total_tx": len(df),
        "top_item": df['Product'].mode()[0] if not df.empty else "N/A"
    }
    return fact_sheet, violations

# --- 4. MISTRAL INTELLIGENCE ---
def get_mistral_insights(fact_sheet, api_key):
    if not api_key: 
        return "Please provide an API Key to enable the AI Brain."
    
    try:
        client = Mistral(api_key=api_key)
        prompt = f"Analyze these business facts: {fact_sheet}. Provide a 3-part insight: 1. Insight, 2. Reason, 3. Recommendation. Keep it short and conversational. No bold text."
        
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Brain Error: {str(e)}"

# --- 5. UI DASHBOARD ---
st.title("🧠 Cognivis OS")

# API Key Logic: Try Secrets first, then Sidebar
api_key = st.secrets.get("MISTRAL_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Mistral API Key (Not found in Secrets)", type="password")

uploaded_file = st.file_uploader("Upload POS Data (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    # Load
    if uploaded_file.name.endswith('.csv'):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)
    
    # Process
    cleaner = DataCleaner(raw_df)
    clean_df = cleaner.standardize()
    facts, alerts = run_zatca_audit(clean_df)

    # Layout
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("🛡️ Compliance & Data")
        st.dataframe(clean_df, use_container_width=True)
        
        if alerts:
            st.error(f"🚨 {len(alerts)} Critical Risks Detected")
            for a in alerts:
                st.markdown(f"""
                <div style="background-color:#e1ffc7; padding:10px; border-radius:10px; margin-bottom:5px; color:#000; border-left:4px solid #25d366">
                <b>🚨 ZATCA Alert</b><br>Invoice {a['id']} ({a['amt']} SAR) is non-compliant.<br><i>{a['msg']}</i>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ System Fully Compliant")

    with col_right:
        st.subheader("💡 AI Brain")
        if st.button("Generate AI Insights"):
            with st.spinner("Mistral is thinking..."):
                insight = get_mistral_insights(facts, api_key)
                st.info(insight)
        
        st.divider()
        st.metric("Total Revenue", f"{facts['revenue']} SAR")
        st.metric("Total Transactions", facts['total_tx'])
        st.metric("Top Selling Item", facts['top_item'])
else:
    st.info("Upload the test CSV to begin the audit.")
