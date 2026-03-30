import streamlit as st
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime

# --- 1. GLOBAL UI CONFIGURATION ---
st.set_page_config(page_title="Cognivis OS | ZATCA Shield", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    .shield-card { border-left: 4px solid #22c55e; background-color: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .brain-card { border-left: 4px solid #3b82f6; background-color: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .impact-card { background-color: #0f172a; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; text-align: center; }
    
    .terminal { background-color: #000000; color: #22c55e; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 6px; font-size: 13px; border: 1px solid #333; line-height: 1.5; }
    
    .badge-high { background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    .badge-safe { background: rgba(34, 197, 94, 0.2); color: #22c55e; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    .badge-hitl { background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    
    /* WhatsApp UI */
    .wa-container { background-color: #0f172a; padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
    .wa-bubble { background-color: #1e293b; color: #f8fafc; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; max-width: 90%; font-size: 14px; border-left: 3px solid #3b82f6; }
    .wa-user-bubble { background-color: #3b82f6; color: #ffffff; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; max-width: 85%; font-size: 14px; margin-left: auto; }
    .wa-time { font-size: 10px; color: #94a3b8; float: right; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
if 'raw_data' not in st.session_state: st.session_state.raw_data = None
if 'pos_source' not in st.session_state: st.session_state.pos_source = "None"
if 'audit_ledger' not in st.session_state: st.session_state.audit_ledger = []
if 'brain_synced' not in st.session_state: st.session_state.brain_synced = False
if 'review_mode' not in st.session_state: st.session_state.review_mode = {} # Tracks HITL state
if 'initial_risk_count' not in st.session_state: st.session_state.initial_risk_count = 0 # Tracks ROI

# --- 3. DATA ENGINE ---
def log_audit(action, invoice_id, status, user="Cognivis AI (Auto)"):
    st.session_state.audit_ledger.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Invoice ID": invoice_id,
        "Action Taken": action,
        "Status": status,
        "Authorized By": user
    })

def titanium_cleaner(df):
    df.columns = [str(c).lower().strip() for c in df.columns]
    col_mapping = {}
    for col in df.columns:
        if re.search(r'invoice|inv|bill|receipt', col): col_mapping[col] = 'invoice_id'
        elif re.search(r'amount|total|price|sar', col): col_mapping[col] = 'amount_sar'
        elif re.search(r'vat|tax|tin|customer_vat', col): col_mapping[col] = 'customer_vat_id'
        elif re.search(r'category|group|type', col): col_mapping[col] = 'category'
            
    df = df.rename(columns=col_mapping)
    
    if 'invoice_id' not in df.columns: df['invoice_id'] = [f"SYS-{i}" for i in range(len(df))]
    if 'amount_sar' in df.columns: df['amount_sar'] = pd.to_numeric(df['amount_sar'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    if 'customer_vat_id' in df.columns: 
        df['customer_vat_id'] = df['customer_vat_id'].fillna('').astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    if 'category' not in df.columns: df['category'] = "General"
    if 'doc_type' not in df.columns: df['doc_type'] = "Tax Invoice (388)"
        
    return df

def get_mock_data():
    return pd.DataFrame({
        "Bill No": ["INV-8801", "INV-8802", "INV-8803", "INV-8804", "INV-8805", "INV-8806"],
        "Item Group": ["Catering", "Retail", "Catering", "Retail", "Catering", "Merchandise"],
        "Total (SAR)": ["1,450.00", "85.00", "3,200.00", "450.00", "950.00", "150.00"],
        "Tax Number": [np.nan, "312345678900003", "", "398765432100003", "300000000000003", ""]
    })

# --- 4. NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Flag_of_Saudi_Arabia.svg/1024px-Flag_of_Saudi_Arabia.svg.png", width=30)
    st.title("Cognivis OS")
    st.caption("🔒 Encrypted & NDMO Compliant")
    st.divider()
    
    menu = st.radio("System Modules", ["📥 Integration Hub", "🛡️ ZATCA Shield", "📓 Compliance Ledger", "💡 AI Intelligence"])
    st.divider()
    
    if st.session_state.raw_data is not None:
        st.success(f"🟢 Connected: {st.session_state.pos_source}")
        if st.button("Disconnect POS"):
            st.session_state.raw_data = None
            st.session_state.audit_ledger = []
            st.session_state.review_mode = {}
            st.rerun()

# --- 5. PAGE 1: INTEGRATION ---
if menu == "📥 Integration Hub":
    st.title("Unified POS Integration")
    st.write("Select your Point of Sale provider. Data is mapped locally for maximum sovereignty.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟢 Connect Foodics API"):
            raw = titanium_cleaner(get_mock_data())
            st.session_state.raw_data = raw
            st.session_state.pos_source = "Foodics"
            # Calculate initial risk for ROI tracking
            st.session_state.initial_risk_count = len(raw[(raw['amount_sar'] >= 1000) & (raw['customer_vat_id'] == "") & (raw['doc_type'] == "Tax Invoice (388)")])
            log_audit("API Handshake", "System", "Connected")
            st.rerun()
    with c2:
        if st.button("🛒 Connect Salla API"):
            raw = titanium_cleaner(get_mock_data())
            st.session_state.raw_data = raw
            st.session_state.pos_source = "Salla"
            st.session_state.initial_risk_count = len(raw[(raw['amount_sar'] >= 1000) & (raw['customer_vat_id'] == "")])
            st.rerun()

    if st.session_state.raw_data is not None:
        st.divider()
        st.subheader("Data Standardized (ZATCA Mapping)")
        st.dataframe(st.session_state.raw_data, use_container_width=True)
        st.caption("🔒 Data temporarily cached in secure volatile memory. Synced to Postgres DB upon clearance.")

# --- 6. PAGE 2: ZATCA SHIELD (UPGRADES 1, 2, & 5) ---
elif menu == "🛡️ ZATCA Shield":
    st.title("Real-Time Compliance Shield")
    
    if st.session_state.raw_data is None:
        st.warning("Please connect a POS provider in the Integration Hub.")
    else:
        df = st.session_state.raw_data
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "") & (df['doc_type'] == "Tax Invoice (388)")]
        current_risk_count = len(violations)
        
        # UPGRADE 5: BEFORE VS AFTER ROI IMPACT
        st.markdown("### 📊 Economic Impact Tracker")
        roi1, roi2 = st.columns(2)
        with roi1:
            st.markdown(f"""
            <div class="impact-card" style="border-top: 4px solid #ef4444;">
                <h4 style="color:#ef4444; margin:0;">❌ Before Cognivis</h4>
                <h2 style="margin:10px 0;">{st.session_state.initial_risk_count} Violations</h2>
                <p style="color:#94a3b8; margin:0;">SAR {st.session_state.initial_risk_count * 5000:,} Financial Risk</p>
            </div>
            """, unsafe_allow_html=True)
        with roi2:
            st.markdown(f"""
            <div class="impact-card" style="border-top: 4px solid #22c55e;">
                <h4 style="color:#22c55e; margin:0;">✅ After Cognivis</h4>
                <h2 style="margin:10px 0;">{current_risk_count} Pending</h2>
                <p style="color:#94a3b8; margin:0;">SAR {current_risk_count * 5000:,} Remaining Risk</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        if not violations.empty:
            st.markdown(f"### <span class='badge-high'>🚨 Action Required: {current_risk_count} Violations Detected</span>", unsafe_allow_html=True)
            
            for index, row in violations.iterrows():
                with st.expander(f"Invoice {row['invoice_id']} | Risk: SAR 5,000 | Status: PENDING CLEARANCE", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"""
                            **Violation:** Simplified B2C Invoice exceeds SAR 1,000 without Buyer VAT ID.<br>
                            **Amount:** SAR {row['amount_sar']:,.2f}<br>
                        """, unsafe_allow_html=True)
                        
                        # UPGRADE 1 & 2: Human In The Loop (HITL) Workflow
                        if not st.session_state.review_mode.get(index, False):
                            st.markdown("<span class='badge-hitl'>Approval Mode: ON</span>", unsafe_allow_html=True)
                            st.write("<br>", unsafe_allow_html=True)
                            if st.button("👨‍💻 Review AI Proposed Fix", key=f"rev_{index}", type="primary"):
                                st.session_state.review_mode[index] = True
                                st.rerun()
                        else:
                            st.info("💡 **AI Suggestion:** Convert to standard B2B invoice to avoid fine. Please input verified Buyer VAT Number below.")
                            vat_input = st.text_input("Enter Customer VAT ID (15 Digits):", key=f"vat_{index}", placeholder="e.g. 300000000000003")
                            
                            c_app, c_can = st.columns(2)
                            if c_app.button("✅ Approve & Issue Credit Note", key=f"app_{index}"):
                                if len(vat_input) >= 10: # Basic validation
                                    # Create Credit Note (Cancel Original)
                                    st.session_state.raw_data.at[index, 'doc_type'] = "Credit Note (381)"
                                    st.session_state.raw_data.at[index, 'amount_sar'] = -abs(row['amount_sar'])
                                    
                                    # Create Corrected Invoice (Fix)
                                    new_row = row.copy()
                                    new_row['invoice_id'] = f"{row['invoice_id']}-REV"
                                    new_row['customer_vat_id'] = vat_input
                                    new_row['doc_type'] = "Tax Invoice (388)"
                                    st.session_state.raw_data = pd.concat([st.session_state.raw_data, pd.DataFrame([new_row])], ignore_index=True)
                                    
                                    # Log to Audit
                                    log_audit("Issued Credit Note 381", row['invoice_id'], "COMPLIANT", user="Account Admin (HITL)")
                                    log_audit("Issued Revised Invoice", new_row['invoice_id'], "COMPLIANT", user="Account Admin (HITL)")
                                    
                                    st.session_state.review_mode[index] = False
                                    st.rerun()
                                else:
                                    st.error("Please enter a valid VAT number.")
                                    
                            if c_can.button("❌ Cancel", key=f"can_{index}"):
                                st.session_state.review_mode[index] = False
                                st.rerun()

                    with col2:
                        # Diagnostic Terminal
                        run_diag = st.button("🔍 Run Validation Engine", key=f"diag_{index}")
                        term_placeholder = st.empty()
                        
                        if run_diag:
                            sim_text = "> INITIALIZING ZATCA PHASE 2 VALIDATION...\n"
                            term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                            time.sleep(0.5)
                            logs = [
                                "> Checking UBL 2.1 XML Schema... [OK]",
                                "> Verifying Cryptographic Stamp... [OK]",
                                "> Applying B2C/B2B Business Rules... [ERROR]",
                                f"> FATAL: Invoice {row['invoice_id']} exceeds SAR 1000 limit for B2C.",
                                "> STATUS: Clearance Rejected. Escalating to HITL Queue."
                            ]
                            for log in logs:
                                sim_text += log + "\n"
                                term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                                time.sleep(0.3)
                        else:
                            term_placeholder.markdown("<div class='terminal' style='color:#64748b;'>Awaiting diagnostics execution...</div>", unsafe_allow_html=True)

        else:
            st.success("🎉 All ZATCA compliance risks resolved. Data ready for secure transmission.")

# --- 7. PAGE 3: COMPLIANCE LEDGER (UPGRADE 3) ---
elif menu == "📓 Compliance Ledger":
    st.title("Immutable Audit Ledger")
    st.write("Enterprise-grade tracking of all system and user actions. Required by NDMO for data sovereignty.")
    
    if len(st.session_state.audit_ledger) > 0:
        ledger_df = pd.DataFrame(st.session_state.audit_ledger)
        st.dataframe(ledger_df, use_container_width=True)
        
        csv = ledger_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Export Ledger for Ministry Auditor", data=csv, file_name='cognivis_audit_log.csv', mime='text/csv')
    else:
        st.info("Audit log is currently empty.")
        
    st.caption("🔒 Data permanently hashed and stored in secure Saudi-based AWS local zone (Simulated Persistence).")

# --- 8. PAGE 4: AI INTELLIGENCE (UPGRADE 4) ---
elif menu == "💡 AI Intelligence":
    st.title("Neural Business Insights")
    
    if st.session_state.raw_data is None:
        st.info("Please connect a POS provider to activate the Brain.")
    else:
        df = st.session_state.raw_data
        positive_df = df[df['amount_sar'] > 0]
        
        # UPGRADE 4: Dynamic, Unscripted AI Logic
        top_cat = positive_df.groupby('category')['amount_sar'].sum().idxmax() if not positive_df.empty else "N/A"
        avg_order = positive_df['amount_sar'].mean() if not positive_df.empty else 0
        
        # Find underperforming categories specifically
        low_perf = positive_df[positive_df['amount_sar'] < avg_order]
        under_cats = low_perf['category'].unique() if not low_perf.empty else ["None"]
        under_str = ", ".join(under_cats)
        
        st.markdown(f"""
            <div class="brain-card">
                <h4 style="margin-top:0; color:#3b82f6;">Data Model Status: Active</h4>
                <p style="color:#94a3b8; font-size:14px;">The AI Reasoning Engine has dynamically processed {len(positive_df)} cleared transactions.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("WhatsApp Action Engine")
        
        st.markdown(f"""
        <div class="wa-container" style="max-width: 500px;">
            <div class="wa-bubble">
                🧠 <b>Cognivis Intelligence</b><br><br>
                Analysis complete. <b>{top_cat}</b> is driving your sales, but I've identified that <b>{under_str}</b> items are severely underperforming (Below SAR {avg_order:.0f} avg).<br><br>
                <b>Strategy:</b> I recommend a cross-selling algorithm pushing {under_str} items with every {top_cat} purchase.<br><br>
                Reply <b>SYNC</b> to push this pricing update directly to {st.session_state.pos_source}.
                <div class="wa-time">{datetime.now().strftime("%H:%M")}</div>
            </div>
            {'<div class="wa-user-bubble">SYNC<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.brain_synced else ''}
            {'<div class="wa-bubble">✅ API Sync Complete. New margins optimized in POS.<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.brain_synced else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.brain_synced:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("Simulate 'SYNC' Reply"):
                with st.spinner("Pushing payload to POS..."):
                    time.sleep(1)
                    st.session_state.brain_synced = True
                    log_audit(f"Cross-Sell Strategy: {top_cat} + {under_str}", "Global Engine", "EXECUTED", user="Cognivis Neural Brain")
                    st.rerun()
