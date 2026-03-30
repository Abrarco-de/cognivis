import streamlit as st
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime

# --- 1. GLOBAL UI CONFIGURATION (National Infrastructure Theme) ---
st.set_page_config(page_title="Cognivis OS | ZATCA Shield", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Global Theme */
    .stApp { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Shield Branding (Neon Green) */
    .shield-card {
        border-left: 4px solid #22c55e;
        background-color: #0f172a;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Brain Branding (Neon Blue) */
    .brain-card {
        border-left: 4px solid #3b82f6;
        background-color: #0f172a;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Multi-POS Integration Buttons */
    .pos-btn-container { display: flex; gap: 10px; margin-bottom: 20px; }
    div[data-testid="column"] button { width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #0f172a; transition: 0.3s; }
    div[data-testid="column"] button:hover { border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
    
    /* Terminal UI for ZATCA Simulation */
    .terminal {
        background-color: #000000;
        color: #22c55e;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 6px;
        font-size: 13px;
        border: 1px solid #333;
        line-height: 1.5;
    }
    
    /* Status Badges */
    .badge-high { background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    .badge-safe { background: rgba(34, 197, 94, 0.2); color: #22c55e; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;}
    
    /* WhatsApp UI Simulation */
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

# --- 3. DATA ENGINE & MOCK DATA ---
def log_audit(action, invoice_id, status):
    """Immutable Audit Ledger appending"""
    st.session_state.audit_ledger.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Invoice ID": invoice_id,
        "Action Taken": action,
        "Status": status,
        "User/System": "Cognivis AI Auto-Resolve"
    })

def titanium_cleaner(df):
    """Standardizes incoming POS data to ZATCA Phase 2 schema requirements."""
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
    if 'doc_type' not in df.columns: df['doc_type'] = "Tax Invoice (388)" # ZATCA Code 388
        
    return df

def get_mock_data():
    return pd.DataFrame({
        "Bill No": ["INV-8801", "INV-8802", "INV-8803", "INV-8804", "INV-8805"],
        "Item Group": ["Catering", "Retail", "Catering", "Retail", "Catering"],
        "Total (SAR)": ["1,450.00", "85.00", "3,200.00", "450.00", "950.00"],
        "Tax Number": [np.nan, "312345678900003", "", "398765432100003", "300000000000003"]
    })

# --- 4. NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Flag_of_Saudi_Arabia.svg/1024px-Flag_of_Saudi_Arabia.svg.png", width=30)
    st.title("Cognivis OS")
    st.caption("SME Infrastructure Layer")
    st.divider()
    
    menu = st.radio("System Modules", ["📥 Integration Hub", "🛡️ ZATCA Shield", "📓 Compliance Ledger", "💡 AI Intelligence"])
    st.divider()
    
    if st.session_state.raw_data is not None:
        st.success(f"🟢 Connected: {st.session_state.pos_source}")
        if st.button("Disconnect POS"):
            st.session_state.raw_data = None
            st.session_state.audit_ledger = []
            st.session_state.pos_source = "None"
            st.rerun()

# --- 5. PAGE 1: INTEGRATION HUB (UPGRADE 4: Multi-POS) ---
if menu == "📥 Integration Hub":
    st.title("Unified POS Integration")
    st.write("Select your Point of Sale provider. The **Cognivis Data Core** will map the schema directly to ZATCA Phase 2 Fatoora standards.")
    
    st.subheader("1-Click Connectors")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟢 Connect Foodics API"):
            st.session_state.raw_data = titanium_cleaner(get_mock_data())
            st.session_state.pos_source = "Foodics"
            log_audit("API Handshake", "System", "Connected")
            st.rerun()
    with c2:
        if st.button("🛒 Connect Salla API"):
            st.session_state.raw_data = titanium_cleaner(get_mock_data())
            st.session_state.pos_source = "Salla"
            log_audit("API Handshake", "System", "Connected")
            st.rerun()
    with c3:
        if st.button("⬛ Connect Square POS"):
            st.session_state.raw_data = titanium_cleaner(get_mock_data())
            st.session_state.pos_source = "Square"
            log_audit("API Handshake", "System", "Connected")
            st.rerun()

    if st.session_state.raw_data is not None:
        st.divider()
        st.subheader("Data Standardized (ZATCA Mapping)")
        st.dataframe(st.session_state.raw_data, use_container_width=True)

# --- 6. PAGE 2: ZATCA SHIELD (UPGRADES 1, 2, & 3) ---
elif menu == "🛡️ ZATCA Shield":
    st.title("Real-Time Compliance Shield")
    
    if st.session_state.raw_data is None:
        st.warning("Please connect a POS provider in the Integration Hub.")
    else:
        df = st.session_state.raw_data
        
        # Risk Logic: B2C > 1000 SAR without VAT
        violations = df[(df['amount_sar'] >= 1000) & (df['customer_vat_id'] == "") & (df['doc_type'] == "Tax Invoice (388)")]
        
        # UPGRADE 3: Confidence & Risk Engine Metrics
        comp_score = int(((len(df) - len(violations)) / len(df)) * 100)
        risk_fine = len(violations) * 5000
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Compliance Score", f"{comp_score}%", delta=f"{100 - comp_score}% Risk" if comp_score < 100 else "Perfect", delta_color="inverse")
        m2.metric("Violations Blocked", len(violations))
        m3.metric("ZATCA Fine Risk Prevented", f"SAR {risk_fine:,}")
        m4.metric("AI Confidence Level", "98.5%")

        st.divider()
        
        if not violations.empty:
            st.markdown(f"### <span class='badge-high'>🚨 {len(violations)} Critical Violations Detected</span>", unsafe_allow_html=True)
            
            for index, row in violations.iterrows():
                with st.expander(f"Invoice {row['invoice_id']} | Risk: SAR 5,000 | Status: PENDING CLEARANCE", expanded=True):
                    col1, col2 = st.columns([1, 1.5])
                    
                    with col1:
                        st.markdown(f"""
                            **Violation:** Simplified B2C Invoice exceeds SAR 1,000 without Buyer VAT ID.<br>
                            **Amount:** SAR {row['amount_sar']:,.2f}<br>
                            **Required Action:** Must be issued as a Standard B2B Invoice or voided.
                        """, unsafe_allow_html=True)
                        
                        run_diag = st.button("🔍 Run ZATCA Diagnostics", key=f"diag_{index}")
                        fix_btn = st.button("🛠️ Generate Credit Note & Fix", type="primary", key=f"fix_{index}")

                    with col2:
                        term_placeholder = st.empty()
                        
                        # UPGRADE 1: Real ZATCA Simulation Layer
                        if run_diag:
                            sim_text = "> INITIALIZING ZATCA PHASE 2 VALIDATION...\n"
                            term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                            time.sleep(0.5)
                            
                            logs = [
                                "> Checking UBL 2.1 XML Schema... [OK]",
                                "> Verifying Cryptographic Stamp (ECDSA)... [OK]",
                                "> Checking Invoice Hash Chain... [OK]",
                                "> Validating Base64 QR Code Payload... [OK]",
                                "> Applying B2C/B2B Business Rules... [ERROR]",
                                f"> FATAL: Invoice {row['invoice_id']} exceeds SAR 1000 limit for B2C.",
                                "> STATUS: Clearance Rejected. Risk of SAR 5,000 penalty."
                            ]
                            
                            for log in logs:
                                sim_text += log + "\n"
                                term_placeholder.markdown(f"<div class='terminal'>{sim_text}</div>", unsafe_allow_html=True)
                                time.sleep(0.4)
                        else:
                            term_placeholder.markdown("<div class='terminal' style='color:#64748b;'>Awaiting diagnostics execution...</div>", unsafe_allow_html=True)

                        # UPGRADE 2: Credit Note / Correction Engine
                        if fix_btn:
                            with st.spinner("Executing legally compliant correction..."):
                                time.sleep(1)
                                
                                # 1. Create Credit Note (Cancel Original)
                                st.session_state.raw_data.at[index, 'doc_type'] = "Credit Note (381)"
                                st.session_state.raw_data.at[index, 'amount_sar'] = -abs(row['amount_sar'])
                                
                                # 2. Create Corrected Invoice (Fix)
                                new_row = row.copy()
                                new_row['invoice_id'] = f"{row['invoice_id']}-REV"
                                new_row['customer_vat_id'] = "300000000000003" # Inserted Default Corporate VAT
                                new_row['doc_type'] = "Tax Invoice (388)"
                                st.session_state.raw_data = pd.concat([st.session_state.raw_data, pd.DataFrame([new_row])], ignore_index=True)
                                
                                # 3. Log to Audit
                                log_audit("Issued Credit Note 381", row['invoice_id'], "COMPLIANT")
                                log_audit("Issued Revised Standard Invoice", new_row['invoice_id'], "COMPLIANT")
                                
                                st.rerun()
        else:
            st.success("🎉 All ZATCA compliance risks resolved. Zero Fine Liability.")
            st.balloons()

# --- 7. PAGE 3: COMPLIANCE LEDGER (UPGRADE 5) ---
elif menu == "📓 Compliance Ledger":
    st.title("Immutable Audit Ledger")
    st.write("Enterprise-grade tracking of all system-initiated compliance corrections for Ministry audits.")
    
    if len(st.session_state.audit_ledger) > 0:
        ledger_df = pd.DataFrame(st.session_state.audit_ledger)
        st.dataframe(ledger_df, use_container_width=True)
        
        csv = ledger_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Export Ledger for ZATCA Auditor", data=csv, file_name='cognivis_audit_log.csv', mime='text/csv')
    else:
        st.info("Audit log is currently empty. No modifications have been made.")

# --- 8. PAGE 4: AI INTELLIGENCE ---
elif menu == "💡 AI Intelligence":
    st.title("Neural Business Insights")
    
    if st.session_state.raw_data is None:
        st.info("Please connect a POS provider to activate the Brain.")
    else:
        df = st.session_state.raw_data
        positive_df = df[df['amount_sar'] > 0] # Exclude Credit Notes
        
        top_cat = positive_df.groupby('category')['amount_sar'].sum().idxmax() if not positive_df.empty else "N/A"
        avg_order = positive_df['amount_sar'].mean() if not positive_df.empty else 0
        
        st.markdown(f"""
            <div class="brain-card">
                <h4 style="margin-top:0; color:#3b82f6;">Data Model Status: Active</h4>
                <p style="color:#94a3b8; font-size:14px;">The AI Reasoning Engine has processed your Fatoora data and identified margin leakage.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("WhatsApp Action Engine")
        
        st.markdown(f"""
        <div class="wa-container" style="max-width: 500px;">
            <div class="wa-bubble">
                🧠 <b>Cognivis Intelligence</b><br><br>
                Analysis complete. <b>{top_cat}</b> is driving your sales, but average ticket size is stuck at SAR {avg_order:.0f}.<br><br>
                <b>Strategy:</b> I have generated a "Compliance Combo" adjusting margins on low-performing retail items.<br><br>
                Reply <b>SYNC</b> to push this pricing update directly to {st.session_state.pos_source}.
                <div class="wa-time">{datetime.now().strftime("%H:%M")}</div>
            </div>
            {'<div class="wa-user-bubble">SYNC<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.brain_synced else ''}
            {'<div class="wa-bubble">✅ API Sync Complete. Margins optimized.<div class="wa-time">' + datetime.now().strftime("%H:%M") + '</div></div>' if st.session_state.brain_synced else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.brain_synced:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("Simulate 'SYNC' Reply"):
                with st.spinner("Pushing payload to POS..."):
                    time.sleep(1)
                    st.session_state.brain_synced = True
                    log_audit("AI Margin Optimization Synced", "Global Price List", "EXECUTED")
                    st.rerun()
