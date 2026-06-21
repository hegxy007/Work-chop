import streamlit as st

st.set_page_config(
    page_title="Work Chop - Find Work, Chop Money",
    page_icon="🇳🇬",
    layout="centered"
)

# Naija style CSS
st.markdown("""
<style>
    .stApp { background: #f0fdf4; }
    h1 { color: #008751; text-align: center; font-weight: 900; }
    .slogan { text-align: center; font-size: 20px; color: #111; margin-bottom: 20px; }
    .stButton>button {
        background-color: #008751 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Logo + Header
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("workchop_logo_naija.png", width=200)

st.markdown('<h1>WORK CHOP</h1>', unsafe_allow_html=True)
st.markdown('<p class="slogan"><b>I tanda like rock no shaking</b> — Find Work, Chop Money.</p>', unsafe_allow_html=True)

st.markdown("---")

# Job Categories
st.subheader("🇳🇬 Wetin you wan do today?")
job_type = st.selectbox(
    "Pick category:",
    ["", "Driver / Delivery", "Cleaning / House Help", "Plumbing / Electrical", 
     "Tailoring / Fashion", "Tech / Phone Repair", "Event Usher / Waiter", "Other"]
)

if job_type:
    st.subheader("📍 Where you dey?")
    location = st.text_input("Type your area", placeholder="e.g. Wuse, Abuja or Ikeja, Lagos")
    
    st.subheader("💰 How much you wan charge?")
    col1, col2 = st.columns(2)
    with col1:
        min_pay = st.number_input("Minimum ₦", min_value=1000, step=500, value=5000)
    with col2:
        pay_type = st.selectbox("Per:", ["Day", "Job", "Hour"])
    
    if st.button("🔍 Find Work Now", type="primary"):
        if location:
            st.success(f"✅ We don see {job_type} jobs for {location}!")
            st.balloons()
            st.info("📱 **Next step:** WhatsApp bot + Real jobs coming soon. Drop your number make we alert you!")
            whatsapp = st.text_input("Your WhatsApp number", placeholder="0803 XXX XXXX")
            if whatsapp:
                st.write("🔥 **Sharp!** We go ping you once real jobs drop. No dulling!")
        else:
            st.error("Abeg put your location first 🙏")

st.markdown("---")
st.markdown("### 📲 Coming Soon to Mobile")
st.write("**Android + iPhone app dey load...** Follow us on Twitter @WorkChopNG")

st.markdown("---")
st.caption("© 2026 Work Chop. Built for Naija by Naija. 🇳🇬 | I tanda like rock no shaking")
