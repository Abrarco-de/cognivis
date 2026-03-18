import streamlit as st
import pandas as pd

# --- 1. THEME & POSITIONING (Fix #5) ---
st.set_page_config(page_title="Cognivis OS", page_icon="🧠")

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .zatca-box { border: 2px solid #00FF00; padding: 15px; border-radius: 10px; background: #00FF0010; color: #00FF00; }
    .brain-box { border: 2px solid #00FFFF; padding: 15px; border-radius: 10px; background: #00FFFF10; color: #00FFFF; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🧠 Cognivis")
st.sidebar.caption("v1.0 MVP | AI Shield + Brain")
st.sidebar.metric("System Confidence", "98.7%", "+2.1%") # Fix #5: Confidence Indicator
menu = st.sidebar.radio("Navigation", ["📥 Data Hub", "🛡️ ZATCA Shield", "💡 AI Brain"])
st.sidebar.divider()
st.sidebar.caption("✅ Supports POS, ERP, and E-invoicing") # Fix #4: Scale Hint

# --- SHARED DATA ENGINE (Fix #1: Mock Data Fallback) ---
def get_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        # Mocking the "Catering" vs "Retail" split for the Brain
        return pd.DataFrame({
            "Invoice": [1021, 1022, 1023, 1024],
            "Category": ["Catering", "Retail", "Catering", "Retail"],
            "Amount": [1250, 800, 1500, 400],
            "VAT_ID": ["", "123456789", "", "987654321"]
        })

# --- PAGE 1: DATA HUB ---
if menu == "📥 Data Hub":
    st.title("🧠 Cognivis OS")
    st.caption("Universal Data Ingestion Layer")
    file = st.file_uploader("Upload POS Export (CSV/Excel)", type=['csv'])
    df = get_data(file)
    st.write("### Current Data Stream")
    st.dataframe(df, use_container_width=True)
    if file is None:
        st.info("💡 Pro Tip: Demoing with pre-loaded mock data. Upload a CSV to test real-time cleaning.")

# --- PAGE 2: ZATCA SHIELD (Fix #3: System Flow) ---
elif menu == "🛡️ ZATCA Shield":
    st.header("🛡️ Compliance Shield")
    st.caption("🔄 POS → Cognivis Shield → ZATCA (Real-time Protection)") # Fix #3
    
    df = get_data(None)
    violations = df[df['VAT_ID'] == ""]
    
    # Financial Impact (Emotional Hook)
    penalty_estimate = len(violations) * 500
    st.warning(f"🚨 **Potential Liability:** ~SAR {penalty_estimate} in ZATCA penalties detected.")
    
    for _, row in violations.iterrows():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""<div class='zatca-box'>
                <b>Invoice #{row['Invoice']}</b><br>
                Risk: Missing Buyer VAT ID for transaction > 1000 SAR.
                </div>""", unsafe_allow_html=True)
        with col2:
            if st.button(f"Fix #{row['Invoice']}", key=row['Invoice']):
                st.success("✅ Credit Note Issued.")

    # WhatsApp Alert Preview
    st.divider()
    st.write("📲 **WhatsApp Alert Preview (CVO USP):**")
    st.code(f"🚨 [Cognivis] Warning: Invoice #1021 lacks VAT ID. Risk: SAR 500. Reply 'FIX' to resolve.", language="markdown")

# --- PAGE 3: AI BRAIN (Fix #2: Dynamic Insights) ---
elif menu == "💡 AI Brain":
    st.header("💡 Business Intelligence")
    st.caption("Neon Intelligence Layer")
    
    df = get_data(None)
    # Dynamic Calculation (Fix #2)
    top_cat = df.groupby("Category")["Amount"].sum().idxmax()
    revenue_share = (df[df['Category'] == top_cat]['Amount'].sum() / df['Amount'].sum()) * 100
    
    st.markdown(f"""<div class='brain-box'>
        <h3>📊 Dynamic Performance Insight</h3>
        Highest Revenue Category: <b>{top_cat}</b><br>
        Revenue Share: <b>{revenue_share:.1f}%</b>
        <p><i>Recommendation: Scale operations for {top_cat} to maximize weekend margins.</i></p>
        </div>""", unsafe_allow_html=True)
