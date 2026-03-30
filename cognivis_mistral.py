import streamlit as st
import pandas as pd
import numpy as np
import time
import re
import random
import uuid
from datetime import datetime

# --- 1. GLOBAL UI CONFIGURATION ---
st.set_page_config(page_title="Cognivis OS | Enterprise", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .shield-card { border-left: 4px solid #22c55e; background-color: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .brain-card { border-left: 4px solid #3b82f6; background-color: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .impact-card { background-color: #0f172a; border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; text-align: center; }
    .terminal { background-color: #000000; color: #22c55e; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 6px; font-size: 13px; border: 1px solid #333; line-height: 1.5; }
    .saas-header { background: #0f172a; padding: 10px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px; font-size: 13px; color: #cbd5e1; }
    .badge-high { background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    .badge-hitl { background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
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
if 'review_mode' not in st.session_state: st.session_state.review_mode = {}
if 'initial_risk_count' not in st.session_state: st.session_state.initial_risk_count = 0

# --- 3. DATA ENGINE ---
def log_audit(action, invoice_id, status, user="System Engine"):
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
    if 'customer_vat_id' in df.columns: df['customer_vat_id'] = df['customer_vat_id'].fillna('').astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    if 'category' not in df.columns: df['category'] = "General"
    if 'doc_type' not in df.columns: df['doc_type'] = "Tax Invoice (388)"
    return df

def get_mock_data():
    return pd.DataFrame({
        "Bill No": ["INV-8801", "INV-8802", "INV-8803"],
        "Item Group": ["Catering", "Retail", "Catering"],
        "Total (SAR)": ["1,450.00", "85.00", "3,200.00"],
        "Tax Number": [np.nan, "312345678900003", ""]
    })

# --- 4. SAAS SIDEBAR ---
with st.sidebar:
    # UPGRADE 5: Multi-Tenant SaaS Feel
    st.markdown("""
        <div class="saas-header">
            <strong>🏢 Org:</strong> Al Baik Restaurant Group<br>
            <strong>🟢 Status:</strong> 12 Active POS Terminals<br>
            <strong>👤 User:</strong> Admin (Abrar Ahmed)<br>
            <strong>⏱️ Last Sync:</strong> Live
        </div>
    """, unsafe_allow_html=True)
    
    st.title("Cognivis OS")
    st.divider()
    menu = st.radio("System Modules", ["📥 Integration Hub", "🛡️ ZATCA Shield", "📓 Compliance Ledger", "💡 Pattern Engine (Phase 1)"])
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
            st.session_state.initial_risk_count = len(raw[(raw['amount_sar'] >= 1000) & (raw['customer_vat_id'] == "") & (raw['doc_type'] == "Tax Invoice (388)")])
            log_audit("API Handshake", "System", "Connected")
            st.rerun()

    if st.session_state.raw_data is not None:
        st.divider()
        st.subheader("Data Standardized (ZATCA Mapping)")
        st.dataframe(st.session_state.raw_data, use_container_width=True)

# --- 6. PAGE 2: ZATCA SHIELD (UPGRADES 1, 2 & 3) ---
elif menu == "🛡️ ZATCA Shield":
    st.title("Real-Time Compliance Shield")
    
    if st.session_state.raw_data is None:
        st.warning("Please connect a POS provider in the Integration Hub.")
    else:
        # UPGRADE 1: Real-Time Live Interception Button
        st.markdown("### ⚡ Live Transaction Monitoring")
        if st.button("🛒 Simulate Live POS Transaction (Incoming)"):
            new_inv_id = f"INV-880{random.randint(4, 99)}"
            new_amount = random.uniform(1100.0, 4500.0) # Guaranteed to trigger fine risk
            new_transaction = pd.DataFrame([{
                "invoice_id": new_inv_id,
                "amount_sar": new_amount,
                "customer_vat_id": "",
                "category": "Retail",
                "doc_type": "Tax Invoice (388)"
            }])
            st.session_state.raw_data = pd.concat([new_transaction, st.session_state.raw_data], ignore_index=True)
            st.session_state.initial_risk_count += 1
            log_audit("Live POS Payload Intercepted", new_inv_id, "PENDING CLEARANCE")
            st.rerun()

        st.divider()
        
        df = st.session_state.raw_data
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "") & (df['doc_type'] == "Tax Invoice (388)")]
        current_risk_count = len(violations)
        
        st.markdown("### 📊 Economic Impact Tracker")
        roi1, roi2 = st.columns(2)
        with roi1:
            st.markdown(f"""
            <div class="impact-card" style="border-top: 4px solid #ef4444;">
                <h4 style="color:#ef4444; margin:0;">❌ Incoming Risk</h4>
                <h2 style="margin:10px 0;">{st.session_state.initial_risk_count} Violations</h2>
                <p style="color:#94a3b8; margin:0;">SAR {st.session_state.initial_risk_count * 5000:,} Financial Risk</p>
            </div>
            """, unsafe_allow_html=True)
        with roi2:
            st.markdown(f"""
            <div class="impact-card" style="border-top: 4px solid #22c55e;">
                <h4 style="color:#22c55e; margin:0;">✅ Shield Status</h4>
                <h2 style="margin:10px 0;">{current_risk_count} Pending</h2>
                <p style="color:#94a3b8; margin:0;">Intercepted before ZATCA submission</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        if not violations.empty:
            st.markdown(f"### <span class='badge-high'>🚨 Action Required: {current_risk_count} Intercepted Transactions</span>", unsafe_allow_html=True)
            
            for index, row in violations.iterrows():
                with st.expander(f"Invoice {row['invoice_id']} | Risk: SAR 5,000 | Intercepted", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"""
                            **Rule Violation:** Simplified B2C Invoice exceeds SAR 1,000 without Buyer VAT ID.<br>
                            **Amount:** SAR {row['amount_sar']:,.2f}<br>
                        """, unsafe_allow_html=True)
                        
                        if not st.session_state.review_mode.get(index, False):
                            st.markdown("<span class='badge-hitl'>Approval Mode: ON (HITL Required)</span>", unsafe_allow_html=True)
                            st.write("<br>", unsafe_allow_html=True)
                            if st.button("👨‍💻 Resolve Violation", key=f"rev_{index}", type="primary"):
                                st.session_state.review_mode[index] = True
                                st.rerun()
                        else:
                            st.info("💡 **Pattern Engine Suggestion:** Convert to standard B2B invoice. Please input verified 15-digit Buyer VAT Number.")
                            vat_input = st.text_input("Enter Customer VAT ID (15 Digits):", key=f"vat_{index}")
                            
                            c_app, c_can = st.columns(2)
                            if c_app.button("✅ Approve & Issue Correction", key=f"app_{index}"):
                                # UPGRADE 3: Strict VAT Validation
                                if len(vat_input) == 15 and vat_input.isdigit():
                                    st.session_state.raw_data.at[index, 'doc_type'] = "Credit Note (381)"
                                    st.session_state.raw_data.at[index, 'amount_sar'] = -abs(row['amount_sar'])
                                    
                                    new_row = row.copy()
                                    new_row['invoice_id'] = f"{row['invoice_id']}-REV"
                                    new_row['customer_vat_id'] = vat_input
                                    new_row['doc_type'] = "Tax Invoice (388)"
                                    st.session_state.raw_data = pd.concat([st.session_state.raw_data, pd.DataFrame([new_row])], ignore_index=True)
                                    
                                    log_audit("Issued Credit Note 381", row['invoice_id'], "COMPLIANT", user="Account Admin (HITL)")
                                    log_audit("Issued Revised B2B Invoice", new_row['invoice_id'], "ZATCA CLEARED", user="Account Admin (HITL)")
                                    
                                    st.session_state.review_mode[index] = False
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid VAT: Must be exactly 15 numeric digits.")
                                    
                            if c_can.button("❌ Cancel", key=f"can_{index}"):
                                st.session_state.review_mode[index] = False
                                st.rerun()

                    with col2:
                        run_diag = st.button("🔍 Simulate ZATCA API Handshake", key=f"diag_{index}")
                        term_placeholder = st.empty()
                        
                        # UPGRADE 2: Real ZATCA API Simulation
                        if run_diag:
                            sim_text = "> INITIATING POST /e-invoicing/developer-portal/invoices/clearance\n"
                            term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                            time.sleep(0.4)
                            logs = [
                                "> Compiling UBL 2.1 XML Payload... [OK]",
                                "> Generating Cryptographic Stamp (ECDSA)... [OK]",
                                f"> Generating Invoice Hash (SHA-256)... {uuid.uuid4().hex[:12]}",
                                "> Transmitting to ZATCA Core Gateway... [PENDING]",
                                "> RECEIVING RESPONSE...",
                                f"> STATUS 400: BAD REQUEST. Clearance Rejected.",
                                f"> ERROR_CODE: BR-KSA-14 (B2C limit exceeded without VAT).",
                                "> ACTION: Connection Terminated. Shield successfully intercepted fine."
                            ]
                            for log in logs:
                                sim_text += log + "\n"
                                term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                                time.sleep(0.3)
                        else:
                            term_placeholder.markdown("<div class='terminal' style='color:#64748b;'>Awaiting ZATCA Handshake...</div>", unsafe_allow_html=True)

        else:
            st.success("🎉 All pending transactions cleared by ZATCA API. Zero Fine Liability.")

# --- 7. PAGE 3: COMPLIANCE LEDGER ---
elif menu == "📓 Compliance Ledger":
    st.title("Immutable Audit Ledger")
    st.write("Enterprise-grade tracking. Data permanently hashed and stored in secure Saudi-based AWS local zone.")
    
    if len(st.session_state.audit_ledger) > 0:
        ledger_df = pd.DataFrame(st.session_state.audit_ledger)
        st.dataframe(ledger_df, use_container_width=True)
    else:
        st.info("Audit log is currently empty.")

# --- 8. PAGE 4: PATTERN ENGINE (UPGRADE 4) ---
elif menu == "💡 Pattern Engine (Phase 1)":
    st.title("Operational Analytics & Pattern Recognition")
    
    if st.session_state.raw_data is None:
        st.info("Please connect a POS provider to activate the Engine.")
    else:
        df = st.session_state.raw_data
        positive_df = df[df['amount_sar'] > 0]
        
        top_cat = positive_df.groupby('category')['amount_sar'].sum().idxmax() if not positive_df.empty else "N/A"
        avg_order = positive_df['amount_sar'].mean() if not positive_df.empty else 0
        low_perf = positive_df[positive_df['amount_sar'] < avg_order]
        under_cats = low_perf['category'].unique() if not low_perf.empty else ["None"]
        under_str = ", ".join(under_cats)
        
        st.markdown(f"""
            <div class="brain-card">
                <h4 style="margin-top:0; color:#3b82f6;">Data Model Status: Active</h4>
                <p style="color:#94a3b8; font-size:14px;">The Pattern Detection Engine has dynamically processed {len(positive_df)} cleared transactions to identify margin leakage.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("WhatsApp Action Engine")
        
        st.markdown(f"""
        <div class="wa-container" style="max-width: 500px;">
            <div class="wa-bubble">
                🧠 <b>Cognivis Intelligence</b><br><br>
                Pattern detected. <b>{top_cat}</b> is driving your sales, but <b>{under_str}</b> items are severely underperforming (Below SAR {avg_order:.0f} avg).<br><br>
                <b>Strategy:</b> I recommend a cross-selling algorithm pushing {under_str} items with every {top_cat} purchase.<br><br>
                Reply <b>SYNC</b> to push this logic to the POS.
                <div class="wa-time">{datetime.now().strftime("%H:%M")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
