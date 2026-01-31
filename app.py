import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
import calendar

st.set_page_config(page_title="Shubh Medical e-Khata", layout="centered")

# ---------------- SECURITY ----------------
APP_PASSWORD = st.secrets["app_password"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Shubh Medical e-Khata")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Unlock"):
        if pwd == APP_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# ---------------- DATA ----------------
SHEET_URL = st.secrets["sheet_url"]

@st.cache_data
def load_data():
    return pd.read_csv(SHEET_URL)

df = load_data()

st.title("🧾 Shubh Medical e-Khata")
st.caption("Professional Udhar Management System")

# ---------------- ADD ENTRY ----------------
st.subheader("➕ New Entry")

with st.form("entry"):
    customer = st.text_input("Customer Name")
    mobile = st.text_input("Mobile Number")
    medicine = st.text_input("Medicine")
    amount = st.number_input("Amount ₹", min_value=0)
    status = st.selectbox("Status", ["UNPAID", "PAID"])
    notes = st.text_input("Notes")
    submit = st.form_submit_button("Save Entry")

    if submit and customer:
        st.success("Entry saved (Sheet sync coming next)")

# ---------------- MONTHLY SUMMARY ----------------
st.divider()
st.subheader("📊 Monthly Summary")

df["Month"] = pd.to_datetime(df["Date"]).dt.month
df["Year"] = pd.to_datetime(df["Date"]).dt.year

month = st.selectbox("Month", list(calendar.month_name)[1:])
year = st.selectbox("Year", sorted(df["Year"].dropna().unique(), reverse=True))

m_num = list(calendar.month_name).index(month)
mdata = df[(df["Month"] == m_num) & (df["Year"] == year)]

paid = mdata[mdata["Status"] == "PAID"]["Amount"].sum()
unpaid = mdata[mdata["Status"] == "UNPAID"]["Amount"].sum()

st.metric("Paid ₹", paid)
st.metric("Unpaid ₹", unpaid)
st.metric("Total ₹", paid + unpaid)

# ---------------- PDF EXPORT ----------------
if st.button("📄 Export Monthly PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Shubh Medical Report – {month} {year}", ln=True)

    for _, r in mdata.iterrows():
        pdf.multi_cell(0, 8, f"{r['Customer Name']} | ₹{r['Amount']} | {r['Status']}")

    file = f"Shubh_Medical_{month}_{year}.pdf"
    pdf.output(file)
    st.download_button("Download PDF", open(file, "rb"), file_name=file)

# ---------------- WHATSAPP MARATHI ----------------
st.divider()
st.subheader("📞 WhatsApp Reminders (Marathi)")

for _, r in df[df["Status"] == "UNPAID"].iterrows():
    msg = f"नमस्कार {r['Customer Name']}, आपले ₹{r['Amount']} रुपये Shubh Medical येथे बाकी आहेत. कृपया लवकर भरणा करा."
    link = f"https://wa.me/91{r['Mobile']}?text={msg}"
    st.markdown(f"[📩 {r['Customer Name']} ला संदेश पाठवा]({link})")
