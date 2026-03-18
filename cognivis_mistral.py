import streamlit as st
import pandas as pd
import time

# ==============================
# ⚙️ CONFIG
# ==============================
st.set_page_config(page_title="Cognivis OS", page_icon="🧠", layout="wide")

# 🔑 (Optional) Add your key
MISTRAL_API_KEY = "YOUR_MISTRAL_API_KEY"

# ==============================
# 🎨 UI STYLE
# ==============================
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #ffffff; }

.shield-card {
    border: 2px solid #00FF00;
    background-color: rgba(0,255,0,0.05);
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.brain-card {
    border: 2px solid #00FFFF;
    background-color: rgba(0,255,255,0.05);
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.whatsapp-box {
    background:#075e54;
    border-left:5px solid #25d366;
    padding:10px;
    border-radius:5px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🧠 SESSION STATE
# ==============================
if "data" not in st.session_state:
    st.session_state.data = None
if "resolved" not in st.session_state:
    st.session_state.resolved = set()
if "applied" not in st.session_state:
    st.session_state.applied = False

# ==============================
# 📊 MOCK DATA
# ==============================
def load_data():
    return pd.DataFrame({
        "invoice_id": ["INV-1","INV-2","INV-3","INV-4","INV-5"],
        "category": ["Catering","Retail","Catering","Retail","Catering"],
        "amount_sar": [1450,85,3200,450,950],
        "customer_vat_id": ["","123","","987",""]
    })

# ==============================
# 🧹 CLEANER
# ==============================
def clean(df):
    df.columns = [c.lower().replace(" ","_") for c in df.columns]

    if "amount_sar" not in df:
        df["amount_sar"] = 0

    df["amount_sar"] = pd.to_numeric(
        df["amount_sar"].astype(str).str.replace(r"[^\d.]", "", regex=True),
        errors="coerce"
    ).fillna(0)

    if "customer_vat_id" not in df:
        df["customer_vat_id"] = ""

    if "category" not in df:
        df["category"] = "General"

    if "invoice_id" not in df:
        df["invoice_id"] = [f"INV-{i}" for i in range(len(df))]

    return df

# ==============================
# 🧠 AI ENGINE (SAFE)
# ==============================
def generate_ai(df):
    try:
        total = df["amount_sar"].sum()
        avg = df["amount_sar"].mean()

        cat = df.groupby("category")["amount_sar"].sum()
        top_cat = cat.idxmax()
        top_val = cat.max()

        dep = (top_val / total) * 100 if total > 0 else 0

        risk_cases = df[(df["amount_sar"] >= 1000) & (df["customer_vat_id"]=="")]
        risk = len(risk_cases) * 500

        # ---------- RULE LOGIC ----------
        dep_msg = "high dependency" if dep > 70 else "moderate dependency" if dep > 50 else "healthy distribution"
        risk_msg = f"SAR {risk} compliance risk" if risk > 0 else "no compliance risk"

        # ---------- TRY AI ----------
        try:
            from mistralai import Mistral
            client = Mistral(api_key=MISTRAL_API_KEY)

            prompt = f"""
You are a business consultant.

Give:
1. Performance insight
2. Risk insight
3. Action

Data:
Revenue: {total}
Top category: {top_cat}
Dependency: {dep:.1f}%
Risk: {risk}
"""

            res = client.chat.complete(
                model="mistral-small",
                messages=[{"role":"user","content":prompt}]
            )

            return res.choices[0].message.content

        except:
            # ---------- FALLBACK ----------
            return f"""
📊 Performance:
{top_cat} drives {dep:.1f}% revenue → {dep_msg}.

⚠️ Risk:
{risk_msg} detected.

🚀 Action:
Ensure VAT IDs for invoices >1000 SAR.
Reduce dependency on {top_cat}.
"""

    except Exception as e:
        return f"Error: {e}"

# ==============================
# 📍 SIDEBAR
# ==============================
with st.sidebar:
    st.title("🧠 Cognivis OS")
    menu = st.radio("Menu", ["📥 Data","🛡️ Shield","💡 Brain"])

# Load default
if st.session_state.data is None:
    st.session_state.data = load_data()

# ==============================
# 📥 DATA
# ==============================
if menu == "📥 Data":
    st.title("📥 Data Hub")

    file = st.file_uploader("Upload CSV")

    if file:
        df = pd.read_csv(file)
        st.session_state.data = clean(df)
        st.success("Data Loaded")

    st.dataframe(st.session_state.data)

# ==============================
# 🛡️ SHIELD
# ==============================
elif menu == "🛡️ Shield":
    st.title("🛡️ Compliance Shield")

    df = st.session_state.data

    viol = df[(df["amount_sar"]>=1000) & (df["customer_vat_id"]=="")]
    active = viol[~viol["invoice_id"].isin(st.session_state.resolved)]

    st.metric("Violations", len(active))
    st.metric("Risk", f"SAR {len(active)*500}")

    for i,row in active.iterrows():
        st.markdown(f"""<div class="shield-card">
        Invoice {row['invoice_id']} missing VAT
        </div>""", unsafe_allow_html=True)

        if st.button(f"Fix {row['invoice_id']}", key=i):
            st.session_state.resolved.add(row["invoice_id"])
            st.rerun()

# ==============================
# 💡 BRAIN
# ==============================
elif menu == "💡 Brain":
    st.title("💡 AI Brain")

    df = st.session_state.data

    with st.spinner("Thinking..."):
        insight = generate_ai(df)

    st.markdown(f"""
    <div class="brain-card">
    <pre>{insight}</pre>
    </div>
    """, unsafe_allow_html=True)
