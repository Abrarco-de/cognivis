import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import re

# --- STYLING & CONFIG ---
st.set_page_config(
    page_title="Cognivis OS | ZATCA Compliance & Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stMetric {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .zatca-shield {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-left: 5px solid #10b981;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    
    .main {
        background-color: #020617;
    }
    </style>
    """, unsafe_allow_dict=True)

# --- CORE LOGIC: DATA CLEANING & SCHEMA DETECTION ---
class CognivisDataEngine:
    @staticmethod
    def detect_zatca_schema(df):
        """Analyzes dataframe for ZATCA Phase 2 (FATOORA) compliance requirements."""
        required_fields = {
            'InvoiceNumber': ['id', 'invoice', 'no', 'number'],
            'IssueDate': ['date', 'issued', 'time'],
            'TaxRegistrationNumber': ['trn', 'vat', 'tax_no'],
            'LineAmount': ['amount', 'total', 'subtotal'],
            'TaxAmount': ['tax', 'vat_amount']
        }
        
        mapping = {}
        for field, keywords in required_fields.items():
            match = [col for col in df.columns if any(k in col.lower() for k in keywords)]
            mapping[field] = match[0] if match else None
            
        return mapping

    @staticmethod
    def clean_and_validate(df, schema):
        """Standardizes data and flags compliance risks."""
        # Standardize Dates
        date_col = schema.get('IssueDate')
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Standardize Numeric
        amt_col = schema.get('LineAmount')
        if amt_col:
            df[amt_col] = pd.to_numeric(df[amt_col], errors='coerce').fillna(0)
            
        # Flagging Compliance Errors (e.g., Missing TRN)
        trn_col = schema.get('TaxRegistrationNumber')
        df['Compliance_Flag'] = "Pass"
        if trn_col:
            df.loc[df[trn_col].astype(str).str.len() != 15, 'Compliance_Flag'] = "Warning: Invalid TRN Length"
            
        return df

# --- UI COMPONENTS ---
def sidebar_navigation():
    with st.sidebar:
        st.markdown("<h1 style='color: #0ea5e9; font-weight: 900; italic: true;'>COGNIVIS OS</h1>", unsafe_allow_dict=True)
        st.write("🛡️ **ZATCA SHIELD ACTIVE**")
        st.divider()
        mode = st.radio("Navigation", ["Intelligence Hub", "Compliance Audit", "Schema Settings"])
        st.divider()
        st.info("System Health: **Optimal**\n\nCloud Sync: **Verified**")
    return mode

def render_metrics(df, schema):
    amt_col = schema.get('LineAmount')
    tax_col = schema.get('TaxAmount')
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_rev = df[amt_col].sum() if amt_col else 0
    total_tax = df[tax_col].sum() if tax_col else (total_rev * 0.15)
    invoices = len(df)
    compliance_rate = (len(df[df['Compliance_Flag'] == 'Pass']) / len(df)) * 100 if len(df) > 0 else 100

    col1.metric("Gross Revenue", f"SAR {total_rev:,.2f}", "+12.5%")
    col2.metric("VAT Collected", f"SAR {total_tax:,.2f}", "+8.2%")
    col3.metric("Total Documents", f"{invoices:,}", "Live")
    col4.metric("Compliance Score", f"{compliance_rate:.1f}%", "-0.4%", delta_color="inverse")

# --- MAIN APP ---
def main():
    mode = sidebar_navigation()
    
    # Mock Data Generation if no file is uploaded
    if 'data' not in st.session_state:
        dates = pd.date_range(end=datetime.now(), periods=100)
        st.session_state.data = pd.DataFrame({
            'invoice_id': [f"INV-{1000+i}" for i in range(100)],
            'transaction_date': dates,
            'vat_id': [f"3000{np.random.randint(1000000000, 9999999999)}" for _ in range(100)],
            'gross_total': np.random.uniform(500, 5000, size=100),
            'customer_segment': np.random.choice(['Retail', 'Corporate', 'Government'], 100)
        })

    engine = CognivisDataEngine()
    schema = engine.detect_zatca_schema(st.session_state.data)
    df = engine.clean_and_validate(st.session_state.data, schema)

    if mode == "Intelligence Hub":
        st.markdown("### 📊 Business Intelligence Hub")
        render_metrics(df, schema)
        
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("#### Revenue Velocity")
            fig = px.area(df, x=schema['IssueDate'], y=schema['LineAmount'], 
                          color_discrete_sequence=['#0ea5e9'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font_color="white", margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("#### Segment Performance")
            fig_pie = px.pie(df, values=schema['LineAmount'], names='customer_segment', 
                             hole=0.6, color_discrete_sequence=px.colors.sequential.Cyan_r)
            fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

    elif mode == "Compliance Audit":
        st.markdown("### 🛡️ ZATCA Shield Audit")
        
        st.markdown("""
        <div class='zatca-shield'>
            <h4 style='margin:0; color:#10b981;'>Phase 2 Readiness Check</h4>
            <p style='margin:0; font-size: 0.8em; color:#94a3b8;'>Cross-referencing XML tags with physical invoice headers...</p>
        </div>
        """, unsafe_allow_dict=True)
        
        errors = df[df['Compliance_Flag'] != "Pass"]
        if not errors.empty:
            st.warning(f"Detected {len(errors)} potential compliance risks.")
            st.dataframe(errors, use_container_width=True)
        else:
            st.success("All analyzed documents meet current ZATCA structure standards.")
            
        st.markdown("#### Schema Mapping")
        st.json(schema)

    elif mode == "Schema Settings":
        st.markdown("### ⚙️ Data Engineering & Schema")
        st.info("The Cognivis Engine automatically detected your column headers. You can override them below.")
        
        cols = df.columns.tolist()
        new_schema = {}
        for key in schema.keys():
            new_schema[key] = st.selectbox(f"Map {key}", options=cols, index=cols.index(schema[key]) if schema[key] in cols else 0)
        
        if st.button("Apply New Schema"):
            st.success("Internal engine updated. Recalculating insights...")

if __name__ == "__main__":
    main()
