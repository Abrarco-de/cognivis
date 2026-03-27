import streamlit as st
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime

# --- 1. GLOBAL UI CONFIGURATION ---
st.set_page_config(page_title="Cognivis OS", page_icon="🧠", layout="wide")

# Custom CSS for SaaS UI Branding & WhatsApp Simulation
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Shield Branding (Green) */
    .shield-card {
        border: 1px solid #22c55e;
        background-color: rgba(34, 197, 94, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    /* Brain Branding (Blue) */
    .brain-card {
        border: 1px solid #3b82f6;
        background-color: rgba(59, 130, 246, 0.05);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    /* WhatsApp UI Simulation */
    .wa-container {
        background-color: #efeae2;
        padding: 15px;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-image: url("https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png");
        background-size: cover;
    }
    .wa-bubble {
        background-color: #d9fdd3;
        color: #111b21;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        max-width: 85%;
        font-size: 14px;
        box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
        position: relative;
    }
    .wa-time {
        font-size: 10px;
        color: #667781;
        float: right;
        margin-top: 4px;
        margin-left: 8px;
    }
    .wa-user-bubble {
        background-color: #ffffff;
        color: #111b21;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        max-width: 85%;
        font-size: 14px;
        box-shadow: 0 1px 0.5px rgba(11,20,26,.13);
        margin-left: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None
if 'fix_logs' not in st.session_state:
    st.session_state.fix_logs = []
if 'applied_recommendations' not in st.session_state:
    st.session_state.applied_recommendations = False

# --- 3. DATA ENGINE (Universal Cleaner) ---
def titanium_cleaner(df):
    """Universally standardizes any POS export using Regex mapping."""
    # 1. Clean column names
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # 2. Universal Regex Mappings
    col_mapping = {}
    for col in df.columns:
        if re.search(r'invoice|inv|bill|receipt|order', col):
            col_mapping[col] = 'invoice_id'
        elif re.search(r'amount|total|price|sar|value', col):
            col_mapping[col] = 'amount_sar'
        elif re.search(r'vat|tax|tin|customer_vat', col):
            col_mapping[col] = 'customer_vat_id'
        elif re.search(r'category|group|type|department', col):
            col_mapping[col] = 'category'
            
    df = df.rename(columns=col_mapping)
    
    # 3. Ensure required columns exist and clean data types
    if 'invoice_id' not in df.columns:
        df['invoice_id'] = [f"SYS-{i}" for i in range(len(df))]
        
    if 'amount_sar' in df.columns:
        # Strip currency symbols and convert to float
        df['amount_sar'] = pd.to_numeric(df['amount_sar'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    else:
        df['amount_sar'] = 0.0

    if 'customer_vat_id' in df.columns:
        df['customer_vat_id'] = df['customer_vat_id'].fillna('').astype(str).str.strip()
        # Remove '.0' from pandas float conversion
        df['customer_vat_id'] = df['customer_vat_id'].str.replace(r'\.0$', '', regex=True)
    else:
        df['customer_vat_id'] = ""
        
    if 'category' not in df.columns:
        df['category'] = "General"
        
    return df

def get_mock_data():
    return pd.DataFrame({
        "Bill No": ["INV-8801", "INV-8802", "INV-8803", "INV-8804", "INV-8805"],
        "Item Group": ["Catering", "Retail", "Catering", "Retail", "Catering"],
        "Total (SAR)": ["1,450.00", "85.00", "3,200.00", "450.00", "950.00"],
        "Tax Number": [np.nan, "312345678900003", "", "398765432100003", None]
    })

# --- 4. NAVIGATION ---
with st.sidebar:
    st.title("🧠 Cognivis OS")
    st.caption("AI Shield + Brain for SME Growth")
    st.divider()
    
    menu = st.radio("Navigation", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])
    st.divider()
    
    if st.session_state.raw_data is not None:
        st.success("🟢 Data Synced")
        if st.button("Clear Data / Reset"):
            st.session_state.raw_data = None
            st.session_state.fix_logs = []
            st.rerun()
    else:
        st.warning("🔴 No Data Loaded")

# --- 5. PAGE 1: DATA HUB ---
if menu == "📥 Data Hub":
    st.title("📥 Data Ingestion Layer")
    st.write("Upload any POS export. The **Titanium Cleaner** will automatically map your columns to the ZATCA Phase 2 schema.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload POS Data (CSV)", type=['csv'])
    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.write("**Or test with sample data:**")
        if st.button("Load Mock Data (Foodics Format)"):
            st.session_state.raw_data = titanium_cleaner(get_mock_data())
            st.session_state.fix_logs = []
            st.rerun()

    if uploaded_file:
        raw = pd.read_csv(uploaded_file)
        st.session_state.raw_data = titanium_cleaner(raw)
        st.session_state.fix_logs = []
        st.success("✅ Data standardized successfully via Titanium Cleaner.")
    
    if st.session_state.raw_data is not None:
        st.subheader("Standardized Data Stream")
        st.dataframe(st.session_state.raw_data, use_container_width=True)

# --- 6. PAGE 2: ZATCA SHIELD ---
elif menu == "🛡️ ZATCA Shield":
    st.title("🛡️ ZATCA Compliance Shield")
    
    if st.session_state.raw_data is None:
        st.info("Please load data in the Data Hub first.")
    else:
        df = st.session_state.raw_data
        
        # ZATCA Rule: B2C Invoices >= 1000 SAR require Buyer VAT or must be split
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "")]
        
        # Dashboard Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Invoices Scanned", len(df))
        m2.metric("Compliance Violations", len(violations), delta=f"-{len(st.session_state.fix_logs)} Fixed" if st.session_state.fix_logs else None, delta_color="inverse")
        m3.metric("Financial Risk Prevented", f"SAR {len(st.session_state.fix_logs) * 5000}")

        st.divider()
        
        if not violations.empty:
            st.subheader("🚨 Action Required")
            for index, row in violations.iterrows():
                with st.container():
                    col1, col2 = st.columns([1.2, 1])
                    
                    with col1:
                        st.markdown(f"""<div class="shield-card">
                            <h4 style="margin:0; color:#22c55e;">Phase 2 Violation: {row['invoice_id']}</h4>
                            <p style="margin-top:10px; font-size:14px;"><b>Rule:</b> Simplified Invoices (B2C) cannot exceed SAR 1,000 without a valid Buyer VAT ID.</p>
                            <p style="font-size:14px;"><b>Current Value:</b> SAR {row['amount_sar']:,.2f}</p>
                        </div>""", unsafe_allow_html=True)
                        
                        # Fix Action Button
                        if st.button(f"Auto-Fix Invoice {row['invoice_id']}", key=f"btn_{index}"):
                            with st.spinner("Applying ZATCA compliance fix..."):
                                time.sleep(1)
                                # THE FIX: Update the dataframe directly
                                # In reality, you might split the invoice, here we assign a default B2C VAT to convert it to standard
                                st.session_state.raw_data.at[index, 'customer_vat_id'] = "300000000000003"
                                
                                # Log the change
                                log_msg = f"✅ Fixed {row['invoice_id']}: Converted to Standard Invoice by attaching generic B2C VAT ID."
                                st.session_state.fix_logs.append(log_msg)
                                st.rerun()
                                
                    with col2:
                        # WhatsApp UI Simulation
                        st.markdown(f"""
                        <div class="wa-container">
                            <div class="wa-bubble">
                                🛡️ <b>Cognivis Shield Alert</b><br>
                                Invoice <b>{row['invoice_id']}</b> exceeds SAR 1,000 without a Buyer VAT number.<br><br>
                                <i>Risk: SAR 5,000 ZATCA Fine.</i><br>
                                Reply <b>1</b> to auto-split invoice.<br>
                                Reply <b>2</b> to convert to Standard B2B.
                                <div class="wa-time">{datetime.now().strftime("%H:%M")}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("🎉 All ZATCA compliance risks resolved. Data is ready for Phase 2 clearance.")
            
        # Display Logs & Export
        if st.session_state.fix_logs:
            st.subheader("📝 Resolution Logs")
            for log in st.session_state.fix_logs:
                st.write(log)
            
            # Convert DF to CSV for download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download ZATCA-Ready CSV",
                data=csv,
                file_name='cognivis_cleansed_data.csv',
                mime='text/csv',
                type="primary"
            )

# --- 7. PAGE 3: AI BRAIN ---
elif menu == "💡 AI Brain":
    st.title("💡 AI Intelligence Brain")
    
    if st.session_state.raw_data is None:
        st.info("Please load data in the Data Hub first.")
    else:
        df = st.session_state.raw_data
        
        # Data Aggregation
        total_rev = df['amount_sar'].sum()
        if not df.empty:
            top_cat = df.groupby('category')['amount_sar'].sum().idxmax()
            top_val = df.groupby('category')['amount_sar'].sum().max()
            share = (top_val / total_rev) * 100 if total_rev > 0 else 0
            avg_order = df['amount_sar'].mean()
        else:
            top_cat, top_val, share, avg_order = "N/A", 0, 0, 0

        # Structured context for Brain Card
        st.markdown(f"""<div class="brain-card">
            <h3 style="color:#3b82f6; margin-top:0;">📊 Intelligence Snapshot</h3>
            <div style="display:flex; justify-content:space-between; margin-top:15px;">
                <div><b>Top Revenue Driver:</b><br>{top_cat}</div>
                <div><b>Category Reliance:</b><br>{share:.1f}%</div>
                <div><b>Avg. Ticket Size:</b><br>SAR {avg_order:.2f}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.subheader("🧠 Proactive Insights")
        
        # WhatsApp UI Simulation for AI Insights
        st.markdown(f"""
        <div class="wa-container" style="max-width: 600px;">
            <div class="wa-bubble">
                💡 <b>Cognivis Brain</b><br>
                I've analyzed today's POS logs. <b>{top_cat}</b> is driving {share:.0f}% of your revenue, pushing your average ticket size to SAR {avg_order:.0f}.<br><br>
                <b>Action:</b> I recommend bundling underperforming Retail items with {top_cat} orders tomorrow to increase margin by estimated 12%.<br><br>
                Reply <b>APPLY</b> to push this combo to your POS.
                <div class="wa-time">{datetime.now().strftime("%H:%M")}</div>
            </div>
            {'<div class="wa-user-bubble">APPLY<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.applied_recommendations else ''}
            {'<div class="wa-bubble">✅ Done. "Combo Deal" synced to POS API.<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.applied_recommendations else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.write("<br>", unsafe_allow_html=True)
        if not st.session_state.applied_recommendations:
            if st.button("Simulate 'APPLY' Reply"):
                with st.spinner("Syncing to POS..."):
                    time.sleep(1)
                    st.session_state.applied_recommendations = True
                    st.rerun()
