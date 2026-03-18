import streamlit as st
import pandas as pd

# --- INITIALIZE MEMORY (Session State) ---
if 'main_df' not in st.session_state:
    # This is the default data until a user uploads a file
    st.session_state.main_df = pd.DataFrame({
        "Invoice_ID": [1000],
        "Product_Category": ["Test"],
        "Amount_SAR": [0],
        "Customer_VAT_ID": [""]
    })

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🧠 Cognivis")
menu = st.sidebar.radio("Navigation", ["📥 Upload Data", "🛡️ ZATCA Shield", "💡 AI Brain"])

# --- PAGE 1: UPLOAD & SYNC ---
if menu == "📥 Upload Data":
    st.title("📥 Data Hub")
    uploaded_file = st.file_uploader("Upload your POS CSV", type=['csv'])
    
    if uploaded_file is not None:
        # Update the "Memory" with the new file
        new_df = pd.read_csv(uploaded_file)
        st.session_state.main_df = new_df
        st.success("✅ File Synced Successfully!")
    
    st.write("### Current Active Data:")
    st.dataframe(st.session_state.main_df)

# --- PAGE 2: THE SHIELD (Uses the Memory) ---
elif menu == "🛡️ ZATCA Shield":
    st.header("🛡️ Compliance Shield")
    df = st.session_state.main_df # This pulls the LATEST data uploaded
    
    # Financial Impact Logic
    violations = df[(df['Amount_SAR'] >= 1000) & (df['Customer_VAT_ID'].isna() | (df['Customer_VAT_ID'] == ""))]
    
    penalty = len(violations) * 500
    st.warning(f"⚠️ **Risk Detected:** SAR {penalty} in potential penalties.")
    
    for _, row in violations.iterrows():
        st.error(f"Invoice {row['Invoice_ID']} is missing VAT ID.")

# --- PAGE 3: THE BRAIN (Uses the Memory) ---
elif menu == "💡 AI Brain":
    st.header("💡 Business Intelligence")
    df = st.session_state.main_df # This pulls the LATEST data uploaded
    
    if not df.empty and 'Product_Category' in df.columns:
        top_cat = df.groupby("Product_Category")["Amount_SAR"].sum().idxmax()
        st.metric("Top Performer", top_cat)
    else:
        st.info("Upload a file with 'Product_Category' to see insights.")
