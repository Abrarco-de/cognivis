import streamlit as st
import pandas as pd
import numpy as np
from mistralai import Mistral

# --- PAGE SETUP ---
st.set_page_config(page_title="Cognivis OS | Mistral Brain", layout="wide", page_icon="🧠")

# --- LAYER 1: DATA INGESTION & SCHEMA DETECTION ---
class DataCleaner:
    def __init__(self, df):
        self.raw_df = df
        self.clean_df = pd.DataFrame()

    def detect_and_clean_schema(self):
        """Fuzzy Schema Matching: Finds the right columns no matter what the POS calls them."""
        df = self.raw_df.copy()
        df.columns = df.columns.str.lower().str.strip() # Normalize headers
        
        # 1. Map Invoice Number
        inv_cols = ['invoice number', 'invoice_id', 'receipt no', 'id', 'invoice']
        inv_col = next((col for col in inv_cols if col in df.columns), None)
        self.clean_df['Invoice_ID'] = df[inv_col] if inv_col else [f"AUTO-{i}" for i in range(len(df))]

        # 2. Map Amount / Price
        amt_cols = ['price', 'total', 'amount', 'net total', 'grand total']
        amt_col = next((col for col in amt_cols if col in df.columns), None)
        if amt_col:
            # Clean currency symbols and convert to float
            self.clean_df['Amount'] = df[amt_col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            self.clean_df['Amount'] = pd.to_numeric(self.clean_df['Amount'], errors='coerce').fillna(0)
        else:
            self.clean_df['Amount'] = 0.0

        # 3. Map Customer VAT Number
        vat_cols = ['vat number', 'customer vat', 'tax id', 'buyer_vat']
        vat_col = next((col for col in vat_cols if col in df.columns), None)
        self.clean_df['Buyer_VAT'] = df[vat_col].astype(str).replace('nan', '') if vat_col else ""

        # 4. Map Product Name
        prod_cols = ['product name', 'item', 'product', 'description']
        prod_col = next((col for col in prod_cols if col in df.columns), None)
        self.clean_df['Product'] = df[prod_col] if prod_col else "Unknown Item"

        return self.clean_df

# --- LAYER 2: THE ZATCA SHIELD (Rigid Math) ---
def run_zatca_audit(df):
    violations = []
    total_revenue = df['Amount'].sum()
    
    for _, row in df.iterrows():
        # Rule: >1000 SAR MUST have a Buyer VAT ID
        if row['Amount'] >= 1000 and (row['Buyer_VAT'] == "" or len(row['Buyer_VAT']) < 5):
            violations.append({
                "invoice": row['Invoice_ID'],
                "amount": row['Amount'],
                "issue": "Missing Customer VAT number on Standard Invoice (>1000 SAR)."
            })
            
    # Create the Fact Sheet
    fact_sheet = {
        "revenue": round(total_revenue, 2),
        "transaction_count": len(df),
        "violation_count": len(violations),
        "top_product": df['Product'].mode()[0] if not df.empty else "None"
    }
    return fact_sheet, violations

# --- LAYER 3: THE INTELLIGENCE LAYER (MISTRAL AI) ---
def get_mistral_insights(fact_sheet, api_key):
    try:
        client = Mistral(api_key=api_key)
        
        prompt = f"""
        You are Cognivis, a highly intelligent Business Assistant for a Saudi retail shop.
        Read this Fact Sheet:
        - Total Revenue: {fact_sheet['revenue']} SAR
        - Total Transactions: {fact_sheet['transaction_count']}
        - ZATCA Violations Found: {fact_sheet['violation_count']}
        - Most Sold Item: {fact_sheet['top_product']}

        Write a short, human-like insight message (no graphs). 
        Format it simply: 
        1. "Insight:" (What happened)
        2. "Possible reason:" (Why it happened)
        3. "Recommendation:" (What the owner should do next).
        Do not use bold markdown formatting, keep it plain and conversational.
        """
        
        response = client.chat.complete(
            model="mistral-large-latest", # Or mistral-small-latest for faster/cheaper responses
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Mistral API Error: Please check your API key. ({str(e)})"

# --- LAYER 4: UI & WHATSAPP SIMULATION ---
st.title("🧠 Cognivis AI Operating System")
st.markdown("Upload any messy POS data. We clean it, audit it, and explain it.")

# API Key Input
st.sidebar.header("Configuration")
mistral_key = st.sidebar.text_input("Enter Mistral API Key", type="password")

# File Upload
uploaded_file = st.file_uploader("Upload POS CSV/Excel (Simulates Foodics/Square export)", type=['csv', 'xlsx'])

if uploaded_file:
    # 1. Read Data
    if uploaded_file.name.endswith('.csv'):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)
        
    st.subheader("1. Schema Detection & Cleaning")
    st.write("Raw Messy Data:", raw_df.head(3))
    
    cleaner = DataCleaner(raw_df)
    clean_df = cleaner.detect_and_clean_schema()
    st.success("✅ Data cleaned and standardized automatically.")
    st.write("Cleaned Data:", clean_df.head(3))
    
    st.divider()
    
    # 2. Run Audit
    facts, alerts = run_zatca_audit(clean_df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("2. ZATCA Compliance Shield")
        if facts['violation_count'] == 0:
            st.success("✅ 100% Compliant. No ZATCA risks detected.")
        else:
            st.error(f"🚨 {facts['violation_count']} Critical Risks Found!")
            
            # 3. WhatsApp Alert Simulation
            st.write("**Simulated WhatsApp Alerts:**")
            for alert in alerts:
                st.markdown(f"""
                <div style="background-color:#dcf8c6; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid #25D366; color:#000;">
                <strong>💬 Cognivis Alert</strong><br>
                ⚠️ <b>Invoice {alert['invoice']}</b> may violate VAT rules.<br>
                Amount: {alert['amount']} SAR<br>
                <i>Issue: {alert['issue']}</i><br>
                <a href="#" style="color:#075E54; text-decoration:none; font-size:12px;">Tap here to issue Credit Note</a>
                </div>
                """, unsafe_allow_html=True)
                
    with col2:
        st.subheader("3. Human-Style Business Insights")
        if mistral_key:
            with st.spinner("Mistral is analyzing the facts..."):
                insight = get_mistral_insights(facts, mistral_key)
                # Displaying it in a clean, assistant-like card
                st.markdown(f"""
                <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #4F8BFF;">
                💡 <b>Cognivis Brain:</b><br><br>
                {insight}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("👈 Please enter your Mistral API Key in the sidebar to generate AI insights.")

else:
    st.info("Please upload a CSV or Excel file to see the magic.")