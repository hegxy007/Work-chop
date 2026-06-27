import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random
import io
import sqlite3  # Use SQLite first, forget gspread for now
import requests # 1. ADD FOR PAYSTACK

st.write("hello")

# PAGE Config
st.set_page_config(
    page_title="Work Chop - For Humanity, By Humanity",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)  # FORCE SIDEBAR OPEN - no space before this line

# DATABASE - Use SQLite, no creds.json needed
conn = sqlite3.connect('workchop.db', check_same_thread=False) # FIX: check_same_thread=False
cursor = conn.cursor()

# Create table if no exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        user_type TEXT
    )
''')
conn.commit()

# COMMENT OUT GSPREAD UNTIL YOU GET creds.json
# import gspread
# gc = gspread.service_account(filename='creds.json')
# sheet = gc.open("WorkChop_DB").sheet1

# FORCE SIDEBAR OPEN - ADD THIS RIGHT AFTER set_page_config
st.markdown("""
<style>
/* FORCE SIDEBAR TO STAY OPEN */
section[data-testid="stSidebar"] {
    display: block !important;
    width: 21rem !important;
    min-width: 21rem !important;
    transform: translateX(0px) !important;
}
/* SHOW THE COLLAPSE BUTTON BUT MAKE IT GREEN */
button[data-testid="collapsedControl"] {
    display: block !important;
    background-color: #14532D !important;
    color: #FFD700 !important;
}
/* REMOVE THE AUTO-HIDE */
.stApp [data-testid="stSidebar"][aria-expanded="false"] {
    display: block !important;
    transform: translateX(0px) !important;
}
</style>
""", unsafe_allow_html=True)

# LANGUAGE DICTIONARY
LANGUAGES = {
    "English": {
        "welcome": "Welcome Back", "login": "Login", "join": "Join Free", "email": "Email",
        "password": "Password", "full_name": "Full Name", "phone": "Phone", "nin": "NIN (11 digits)",
        "send_otp": "Send OTP", "enter_otp": "Enter OTP", "register_sabiman": "Register as Sabiman",
        "register_client": "Register as Client", "i_be": "I be:", "logout": "Logout", "hello": "Hello",
        "role": "Role", "rating": "Rating", "home": "Home", "about": "About Us", "gallery": "Gallery",
        "contact": "Contact Us", "help": "Help Center", "language": "Choose Your Language", "fund_wallet": "Fund Wallet"
    },
    "Hausa": {
        "welcome": "Barka da Zuwa", "login": "Shiga", "join": "Yi Rajista Kyauta", "email": "Imel",
        "password": "Kalmar Sirri", "full_name": "Cikakken Suna", "phone": "Lambar Wayar",
        "nin": "NIN (Lambobi 11)", "send_otp": "Aika OTP", "enter_otp": "Shigar da OTP",
        "register_sabiman": "Yi Rajista a matsayin Sabiman", "register_client": "Yi Rajista a matsayin Client",
        "i_be": "Ni ne:", "logout": "Fita", "hello": "Sannu", "role": "Matsayi", "rating": "Kimantawa",
        "home": "Gida", "about": "Game da Mu", "gallery": "Hotuna", "contact": "Tuntube Mu",
        "help": "Cibiyar Taimako", "language": "Zaɓi Harshenka", "fund_wallet": "Cika Wallet"
    },
    "Igbo": {
        "welcome": "Nnọ", "login": "Banye", "join": "Debanye aha n'efu", "email": "Email",
        "password": "Okwuntughe", "full_name": "Aha zuru ezu", "phone": "Nọmba ekwentị",
        "nin": "NIN (Ọnụọgụ 11)", "send_otp": "Zipu OTP", "enter_otp": "Tinye OTP",
        "register_sabiman": "Debanye aha dịka Sabiman", "register_client": "Debanye aha dịka Client",
        "i_be": "Abụ m:", "logout": "Pụọ", "hello": "Ndewo", "role": "Ọrụ", "rating": "Ntụle",
        "home": "Ụlọ", "about": "Gbasara Anyị", "gallery": "Foto", "contact": "Kpọtụrụ Anyị",
        "help": "Ebe Enyemaka", "language": "Họrọ Asụsụ Gị", "fund_wallet": "Jupụta Wallet"
    },
    "Yoruba": {
        "welcome": "Kaabo", "login": "Wọle", "join": "Forukọsilẹ Ọfẹ", "email": "Imeeli",
        "password": "Ọrọigbaniwọle", "full_name": "Orukọ Kikun", "phone": "Nọmba Foonu",
        "nin": "NIN (Nọmba 11)", "send_otp": "Firanṣẹ OTP", "enter_otp": "Tẹ OTP sii",
        "register_sabiman": "Forukọsilẹ bi Sabiman", "register_client": "Forukọsilẹ bi Client",
        "i_be": "Mo jẹ:", "logout": "Jade", "hello": "Bawo", "role": "Ipa", "rating": "Iwọn",
        "home": "Ile", "about": "Nipa Wa", "gallery": "Awọn Aworan", "contact": "Kan si Wa",
        "help": "Ile-iṣẹ Iranlọwọ", "language": "Yan Ede Rẹ", "fund_wallet": "Fọ Wallet"
    }
}
# ========== 1. INIT STATE ==========
# SESSION STATE - FIXED: Removed duplicate at bottom
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'admin_page' not in st.session_state:
    st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'otp_store' not in st.session_state:
    st.session_state.otp_store = {}
if 'admin_messages' not in st.session_state:
    st.session_state.admin_messages = []
# WORK CHOP UPDATE: Auto-release check timer
if 'last_auto_release_check' not in st.session_state:
    st.session_state.last_auto_release_check = datetime.now()
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'nin': '12345678901', 'phone': '08000000', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'bio': 'Work Chop Founder & CEO', 'profile_pic': None, 'portfolio': [], 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'nin': '23456789012', 'phone': '08011111', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.8, 'jobs_posted': 5, 'bio': 'Business owner in Abuja. Love fast service!', 'profile_pic': None, 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 5000},
        'client2@test.com': {'password': 'client123', 'role': 'client', 'name': 'Fatima Client', 'nin': '56789012345', 'phone': '08044444', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_posted': 0, 'bio': 'New client ready to test', 'profile_pic': None, 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 0},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'nin': '34567890123', 'phone': '08022222', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_done': 47, 'bio': '10 years plumbing experience. I fix am well. No story!', 'skills': ['Plumbing', 'Electrical', 'AC Repair'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 3000, 'daily': 15000, 'weekly': 80000, 'monthly': 300000}, 'available': True, 'work_categories': ['Plumbing', 'Electrical'], 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 0,
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'nin': '45678901234', 'phone': '08033333', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 62, 'bio': 'Fashion designer. I sew cloth wey go make you shine!', 'skills': ['Tailoring', 'Fashion Design', 'Embroidery'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 5000, 'daily': 25000, 'weekly': 120000, 'monthly': 400000}, 'available': True, 'work_categories': ['Tailoring', 'Fashion'], 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 0,
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'nin': '67890123456', 'phone': '08055555', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.7, 'jobs_done': 0, 'bio': 'New Sabiman ready to work. Electrical specialist!', 'skills': ['Electrical', 'Solar Installation'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 4000, 'daily': 20000, 'weekly': 100000, 'monthly': 350000}, 'available': True, 'work_categories': ['Electrical', 'Solar'], 'region': 'Port Harcourt', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'wallet_balance': 0,
            'is_activated': False, 'activation_deposit': 0, 'jobs_completed_for_activation': 0, 'activation_bonus_paid': False},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix My Kitchen Sink', 'category': 'Plumbing', 'location': 'Wuse 2, Abuja', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'desc': 'My sink dey leak water. Need urgent repair today.', 'status': 'Work Done - Awaiting Confirmation', 'created': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), 'commission': 0, 'sabiman_payout': 0, 'client_satisfied': False, 'sabiman_satisfied': False, 'paid_at': None, 'job_type': 'client_request',
         'auto_release_at': (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"), 'reminder_sent': False, 'disputed': False},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'House Cleaning', 'category': 'Cleaning', 'location': 'Lekki, Lagos', 'region': 'Lagos', 'amount': 25000, 'duration': 'Daily', 'desc': 'Clean 3 bedroom flat', 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), 'commission': 5000, 'sabiman_payout': 20000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), 'job_type': 'client_request',
         'auto_release_at': None, 'reminder_sent': False, 'disputed': False},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman2@test.com', 'title': 'Sew Agbada', 'category': 'Tailoring', 'location': 'Ikeja, Lagos', 'region': 'Lagos', 'amount': 50000, 'duration': 'Weekly', 'desc': 'Wedding agbada', 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M"), 'commission': 10000, 'sabiman_payout': 40000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"), 'job_type': 'client_request',
         'auto_release_at': None, 'reminder_sent': False, 'disputed': False},
        {'id': 4, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'category': 'Electrical', 'location': 'Gwarinpa, Abuja', 'region': 'Abuja', 'amount': 35000, 'duration': 'Hourly', 'desc': 'Fix AC compressor', 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), 'commission': 7000, 'sabiman_payout': 28000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), 'job_type': 'client_request',
         'auto_release_at': None, 'reminder_sent': False, 'disputed': False},
        {'id': 5, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Toilet', 'category': 'Plumbing', 'location': 'Maitama, Abuja', 'region': 'Abuja', 'amount': 12000, 'duration': 'One-time', 'desc': 'Toilet no dey flush', 'status': 'Work Done - Awaiting Confirmation', 'created': datetime.now().strftime("%Y-%m-%d %H:%M"), 'commission': 0, 'sabiman_payout': 0, 'client_satisfied': False, 'sabiman_satisfied': False, 'paid_at': None, 'job_type': 'client_request',
         'auto_release_at': (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"), 'reminder_sent': False, 'disputed': False},
        {'id': 6, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Garden Work', 'category': 'Cleaning', 'location': 'Asokoro, Abuja', 'region': 'Abuja', 'amount': 8000, 'duration': 'Monthly', 'desc': 'Cut grass monthly', 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"), 'commission': 800, 'sabiman_payout': 7200, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"), 'job_type': 'client_request',
         'auto_release_at': None, 'reminder_sent': False, 'disputed': False},
    ]
if 'traffic_log' not in st.session_state:
    st.session_state.traffic_log = []

def t(key):
    return LANGUAGES[st.session_state.language].get(key, key)

def generate_otp():
    return str(random.randint(100000, 999))

def log_traffic(action):
    if st.session_state.logged_in:
        user = st.session_state.users[st.session_state.current_user]
        st.session_state.users[st.session_state.current_user]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.traffic_log.append({
            'user': st.session_state.current_user,
            'role': user['role'],
            'action': action,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        })

def calculate_commission(amount):
    if amount >= 10000:
        return amount * 0.20
    elif amount >= 5000:
        return amount * 0.10
    else:
        return amount * 0.05

# WORK CHOP HEADER - NAIJA WC LOGO LIVE
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image("logo.png", width=80)
    except:
        st.markdown("## 🇳🇬")  # Fallback if logo no load
with col2:
    st.markdown("# WORK CHOP")
    st.caption("Find Local Services in Nigeria")

st.markdown("---")
# WORK CHOP UPDATE: Zero Risk Activation Logic
def process_payment(job_id):
    job = next((j for j in st.session_state.jobs if j['id'] == job_id), None)
    if job and job.get('client_satisfied') and job.get('sabiman_satisfied'):
        sabiman = st.session_state.users[job['sabiman']]
        commission = calculate_commission(job['amount'])
        activation_deposit = 0

        if not sabiman.get('is_activated', False) and sabiman.get('activation_deposit', 0) == 0:
            activation_deposit = 500.00

        net_payout = job['amount'] - commission - activation_deposit

        job['commission'] = commission
        job['sabiman_payout'] = net_payout
        job['status'] = 'Completed - Paid'
        job['paid_at'] = datetime.now().strftime("%Y-%m-%d")

        sabiman['jobs_done'] += 1

        if activation_deposit > 0:
            sabiman['activation_deposit'] = activation_deposit
            sabiman['is_activated'] = True

        if sabiman.get('is_activated') and not sabiman.get('activation_bonus_paid', False):
            sabiman['jobs_completed_for_activation'] = sabiman.get('jobs_completed_for_activation', 0) + 1
            if sabiman['jobs_completed_for_activation'] >= 5:
                sabiman['activation_bonus_paid'] = True
                job['sabiman_payout'] += sabiman['activation_deposit']
        return True
    return False

# WORK CHOP UPDATE: 24hr Auto-Release
def process_auto_release():
    current_time = datetime.now()
    for job in st.session_state.jobs:
        if (job['status'] == 'Work Done - Awaiting Confirmation'
            and not job.get('disputed', False)
            and job.get('auto_release_at')):
            release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
            if current_time >= release_time:
                if not job.get('client_satisfied'):
                    job['client_satisfied'] = True 
                if not job.get('sabiman_satisfied'):
                    job['sabiman_satisfied'] = True
                process_payment(job['id'])
                log_traffic(f"Auto-released payment for job {job['id']}")

if (datetime.now() - st.session_state.last_auto_release_check).seconds > 300:
    process_auto_release()
    st.session_state.last_auto_release_check = datetime.now()

# 2. ADD PAYSTACK + BANK + USSD FUNDING - FOR NAIJA PEOPLE NO CARD
def fund_wallet_section():
    st.markdown(f"### 💰 {t('fund_wallet')}")
    user = st.session_state.users[st.session_state.current_user]
    st.metric("Current Balance", f"₦{user.get('wallet_balance', 0):,}")
    
    tab1, tab2, tab3 = st.tabs(["💳 Card/Paystack", "🏦 Bank Transfer", "📱 USSD"])
    
    with tab1:
        if "PAYSTACK_SECRET_KEY" not in st.secrets:
            st.warning("⚠️ Admin: Add PAYSTACK_SECRET_KEY to .streamlit/secrets.toml")
        else:
            amount = st.number_input("Amount ₦", min_value=100, value=1000, key="ps_amt")
            if st.button("Pay with Card", key="ps_btn"):
                headers = {"Authorization": f"Bearer {st.secrets['PAYSTACK_SECRET_KEY']}", "Content-Type": "application/json"}
                data = {"email": st.session_state.current_user, "amount": amount * 100, "reference": f"WC_{random.randint(10000,99999)}"}
                try:
                    r = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
                    if r.status_code == 200:
                        st.markdown(f"[**Click to Pay ₦{amount:,}**]({r.json()['data']['authorization_url']})")
                        st.caption("Test Card: 4081 4081 4081 4081 | 12/34 | 408 | 0000")
                    else: st.error(r.text)
                except Exception as e: st.error(e)
    
    with tab2:
        st.info("Transfer to: **Work Chop Ltd** \nAcc: 1234567890 \nBank: GTBank")
        ref = st.text_input("Your Transfer Reference")
        amount = st.number_input("Amount Sent ₦", min_value=100, key="bank_amt")
        if st.button("I Have Paid"): st.success(f"✅ We go confirm ₦{amount:,} in 5 mins. Ref: {ref}")
    
    with tab3:
        st.info("Dial: **`*737*1*1*1234567890#`** then enter ₦ amount")
        ref = st.text_input("USSD Ref Number")
        amount = st.number_input("Amount ₦", min_value=100, key="ussd_amt")
        if st.button("Confirm USSD Payment"): st.success(f"✅ We go confirm ₦{amount:,} in 5 mins. Ref: {ref}")

# 3. SIDEBAR + LOGIN - FIXED
with st.sidebar:
    st.selectbox(f"🌍 {t('language')}", ["English", "Hausa", "Igbo", "Yoruba"], key='language')
    st.markdown("---")
    if st.session_state.logged_in:
        user = st.session_state.users[st.session_state.current_user]
        st.success(f"{t('hello')}, {user['name']}")
        if st.button(t("logout"), type="primary", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.current_user = None; st.rerun()
    else:
        st.subheader(t("welcome"))
        email = st.text_input(t("email"))
        password = st.text_input(t("password"), type="password")
        if st.button(t("login"), type="primary", use_container_width=True):
            u = st.session_state.users.get(email)
            if u and u['password'] == password:
                st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
            else: st.error("Wrong credentials")
# 4. MAIN APP LOGIC - FIXED: This was missing. No more blank screen
if st.session_state.logged_in:
    user = st.session_state.users[st.session_state.current_user]
    if user['role'] == 'admin':
        st.title("Admin Dashboard")
        st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
    elif user['role'] == 'client':
        st.title("Client Dashboard")
        fund_wallet_section() # 3 FUNDING OPTIONS HERE
        st.write("Post your job here")
    elif user['role'] == 'sabiman':
        st.title("Sabiman Dashboard")
        if not user.get('is_activated'): st.warning("⚠️ Account Not Activated. First ₦500 job activates you FREE.")
else:
    st.info("👈 Login from the sidebar to continue")
    st.code("Admin: admin@workchop.ng / admin123\nClient: client@test.com / client123")
# ========== TOP NAVIGATION BAR - SHOW BASED ON LOGIN ==========
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}

if not st.session_state.logged_in:
    # MODE 1: VISITOR NAV - Only show when logged out
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Home", use_container_width=True, key="top_home"):
            st.session_state.page = 'Home'
            st.rerun()
    with col2:
        if st.button("About Us", use_container_width=True, key="top_about"):
            st.session_state.page = 'About'
            st.rerun()
    with col3:
        if st.button("Gallery", use_container_width=True, key="top_gallery"):
            st.session_state.page = 'Gallery'
            st.rerun()
    with col4:
        if st.button("Contact", use_container_width=True, key="top_contact"):
            st.session_state.page = 'Contact'
            st.rerun()
    with col5:
        if st.button("Login", use_container_width=True, key="top_login"):
            st.sidebar.expander("Click here to login 👈", expanded=True) # Point to sidebar
            st.session_state.page = 'Home'
            st.rerun()
    
    # SHOW PUBLIC PAGES
    if st.session_state.page == 'Home':
        st.title("🇳🇬 WORK CHOP"); st.write("**I tanda like rock no shaking**")
    elif st.session_state.page == 'About':
        st.title(t('about')); st.write("Zero Risk Activation for 26M Nigerians")
    elif st.session_state.page == 'Gallery':
        st.title(t('gallery')); st.info("📸 Gallery coming soon")
    elif st.session_state.page == 'Contact':
        st.title(t('contact')); st.write("📍 Lagos | 📧 support@workchop.ng")

else:
    # MODE 2: LOGGED IN NAV - Hide Home/About/Gallery
    role = user.get('role')
    
    if role == 'client':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="c_dash"):
                st.session_state.page = 'Dashboard'; st.rerun()
        with col2:
            if st.button("My Jobs", use_container_width=True, key="c_jobs"):
                st.session_state.page = 'My Jobs'; st.rerun()
        with col3:
            if st.button("Profile", use_container_width=True, key="c_profile"):
                st.session_state.page = 'Profile'; st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="c_logout"):
                st.session_state.logged_in = False; st.session_state.current_user = None
                st.session_state.page = 'Home'; st.rerun()
        
        # === PAYSTACK + BANK + USSD WALLET FUNDING - FOR NAIJA ===
        if st.session_state.page == 'Dashboard':
            st.markdown(f"### 💰 {t('fund_wallet')}")
            st.metric("Wallet Balance", f"₦{user.get('wallet_balance', 0):,}")
            
            tab1, tab2, tab3 = st.tabs(["💳 Card/Paystack", "🏦 Bank Transfer", "📱 USSD"])
            
            with tab1:
                if "PAYSTACK_SECRET_KEY" not in st.secrets:
                    st.warning("⚠️ Add PAYSTACK_SECRET_KEY to .streamlit/secrets.toml")
                else:
                    amount = st.number_input("Enter amount (₦)", min_value=100, value=1000, step=100, key="fund_amt")
                    if st.button("Pay with Paystack", type="primary", key="paystack_btn"):
                        import requests, random
                        try:
                            headers = {"Authorization": f"Bearer {st.secrets['PAYSTACK_SECRET_KEY']}", "Content-Type": "application/json"}
                            data = {"email": st.session_state.current_user, "amount": amount * 100, "reference": f"WC_{random.randint(10000,99999)}"}
                            response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
                            if response.status_code == 200:
                                url = response.json()['data']['authorization_url']
                                st.success("✅ Click below to pay with TEST CARD")
                                st.markdown(f"[**Pay ₦{amount:,} Now**]({url})")
                                st.caption("Test Card: 4081 4081 4081 4081 | Expiry: 12/34 | CVV: 408 | PIN: 0000")
                            else: st.error(f"Paystack error: {response.text}")
                        except Exception as e: st.error(f"Error: {e}")
            
            with tab2:
                st.info("Transfer to: **Work Chop Ltd** \nAcc: 1234567890 \nBank: GTBank")
                ref = st.text_input("Your Transfer Reference", key="bank_ref")
                amount = st.number_input("Amount Sent ₦", min_value=100, key="bank_amt")
                if st.button("I Have Paid"): st.success(f"✅ We go confirm ₦{amount:,} in 5 mins. Ref: {ref}")
            
            with tab3:
                st.info("Dial: **`*737*1*1*1234567890#`** then enter ₦ amount")
                ref = st.text_input("USSD Ref Number", key="ussd_ref")
                amount = st.number_input("Amount ₦", min_value=100, key="ussd_amt")
                if st.button("Confirm USSD Payment"): st.success(f"✅ We go confirm ₦{amount:,} in 5 mins. Ref: {ref}")
            # === END PAYSTACK CODE ===
        
        elif st.session_state.page == 'My Jobs':
            st.title("My Jobs"); st.dataframe(pd.DataFrame([j for j in st.session_state.jobs if j['client'] == st.session_state.current_user]))
        elif st.session_state.page == 'Profile':
            st.title("Profile"); st.json(user)
    
    elif role == 'admin':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="a_dash"):
                st.session_state.page = 'Dashboard'; st.rerun()
        with col2:
            if st.button("Manage Users", use_container_width=True, key="a_users"):
                st.session_state.page = 'Manage Users'; st.rerun()
        with col3:
            if st.button("Reports", use_container_width=True, key="a_reports"):
                st.session_state.page = 'Reports'; st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="a_logout"):
                st.session_state.logged_in = False; st.session_state.current_user = None
                st.session_state.page = 'Home'; st.rerun()
        
        if st.session_state.page == 'Dashboard':
            st.title("Admin Dashboard"); st.metric("Total Users", len(st.session_state.users))
        elif st.session_state.page == 'Manage Users':
            st.title("Manage Users"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
        elif st.session_state.page == 'Reports':
            st.title("Reports"); st.dataframe(pd.DataFrame(st.session_state.jobs))
    
    elif role == 'sabiman':
        st.title("Sabiman Dashboard")
        st.write(f"Hello {user['name']}")
        if not user.get('is_activated'): st.warning("⚠️ Account Not Activated. First ₦500 job activates you FREE.")
        st.dataframe(pd.DataFrame([j for j in st.session_state.jobs if j['sabiman'] == st.session_state.current_user]))
# ========== SABIMAN NAV + ALL PAGE CONTENT - FIXED ==========
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role') # FIX: Use role, not user_type

if role == 'sabiman':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Dashboard", use_container_width=True, key="s_dash"):
            st.session_state.page = 'Dashboard'; st.rerun()
    with col2:
        if st.button("Find Jobs", use_container_width=True, key="s_jobs"):
            st.session_state.page = 'Find Jobs'; st.rerun()
    with col3:
        if st.button("My Gigs", use_container_width=True, key="s_gigs"):
            st.session_state.page = 'My Gigs'; st.rerun()
    with col4:
        if st.button("Logout", use_container_width=True, key="s_logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None # FIX: Use current_user
            st.session_state.page = 'Home'
            st.rerun()

# ========== PAGE CONTENT WITH REDIRECT GUARDS ==========
if st.session_state.page == 'Home':
    if not st.session_state.logged_in:
        st.title("WORK CHOP - For Humanity, By Humanity")
        st.write("Public home page. **I tanda like rock no shaking**")
    else:
        st.session_state.page = 'Dashboard'
        st.rerun()

elif st.session_state.page == 'About':
    if not st.session_state.logged_in:
        st.title("About Us"); st.write("Our story... Zero Risk Activation for 26M Nigerians")
    else:
        st.session_state.page = 'Dashboard'  
        st.rerun()

elif st.session_state.page == 'Gallery':
    if not st.session_state.logged_in:
        st.title("Gallery"); st.write("Public portfolio"); st.info("📸 Coming soon")
    else:
        st.session_state.page = 'Dashboard'
        st.rerun()

elif st.session_state.page == 'Dashboard':
    if st.session_state.logged_in:
        st.title(f"{role.title()} Dashboard") # FIX: Use role
        st.success("Home/About/Gallery don hide ✅")
        
        if role == 'client':
            st.write("Client Dashboard Here")
            # PUT FUND WALLET CODE HERE IF YOU WANT
        elif role == 'sabiman':
            st.write(f"Welcome {user['name']}")
            if not user.get('is_activated'): st.warning("⚠️ Account Not Activated. First ₦500 job activates you FREE.")
            st.dataframe(pd.DataFrame([j for j in st.session_state.jobs if j['sabiman'] == st.session_state.current_user]))
        elif role == 'admin':
            st.write("Admin Dashboard Here")
            st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
    else:
        st.session_state.page = 'Home'
        st.rerun()

elif st.session_state.page == 'Find Jobs':
    if role == 'sabiman':
        st.title("Find Jobs")
        available_jobs = [j for j in st.session_state.jobs if j['status'] == 'Requested']
        st.dataframe(pd.DataFrame(available_jobs))
    else:
        st.session_state.page = 'Dashboard'; st.rerun()

elif st.session_state.page == 'My Gigs':
    if role == 'sabiman':
        st.title("My Gigs")
        my_jobs = [j for j in st.session_state.jobs if j['sabiman'] == st.session_state.current_user]
        st.dataframe(pd.DataFrame(my_jobs))
    else:
        st.session_state.page = 'Dashboard'; st.rerun()
# 1. PAGE CONFIG - MUST BE FIRST
st.set_page_config(page_title="Work Chop - For Humanity, By Humanity", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

# 2. CSS - MUST BE BEFORE ANYTHING ELSE # FIXED POSITION
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap');
.stApp { background: #0f0f0f; font-family: 'Outfit', sans-serif; }
header[data-testid="stHeader"] { display: none; }
.main.block-container { padding-top: 1rem; background: #0f0f0f; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #008751 0%, #059669 100%); padding-top: 1rem; min-width: 300px!important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: white!important; }
section[data-testid="stSidebar"].stButton>button { background: white!important; color: #008751!important; font-weight: 700!important; border: 2px solid white!important; }
h1, h2, h3, h4 { color: white!important; font-weight: 700; }
p, label,.stMarkdown { color: #d1d5db!important; }
div[data-testid="stDataFrame"] { background: #1a1a1a; }
.stButton>button { background: linear-gradient(135deg, #008751 0%, #059669 100%)!important; color: white!important; font-weight: 700!important; border-radius: 12px!important; padding: 0.75rem 2rem!important; border: none!important; }
</style>
""", unsafe_allow_html=True)

# 3. DB + SESSION + USERS - YOUR 274 LINES START HERE
conn = sqlite3.connect('workchop.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, user_type TEXT)')
conn.commit()

LANGUAGES = {"English": {"welcome": "Welcome Back", "login": "Login", "email": "Email", "password": "Password", "logout": "Logout", "hello": "Hello", "home": "Home", "about": "About Us", "gallery": "Gallery", "contact": "Contact Us", "help": "Help Center", "language": "Choose Your Language", "fund_wallet": "Fund Wallet"}}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)

if 'language' not in st.session_state: st.session_state.language = "English"
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'wallet_balance': 5000},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'wallet_balance': 0},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [{'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Sink', 'amount': 15000, 'status': 'Work Done - Awaiting Confirmation', 'auto_release_at': (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"), 'client_satisfied': False, 'sabiman_satisfied': False}]
# 4. HEADER
col1, col2 = st.columns([1, 5])
with col1: st.markdown("## 🇳🇬")
with col2: st.markdown("# WORK CHOP"); st.caption("Find Local Services in Nigeria")
st.markdown("---")

# 5. SIDEBAR LOGIN
with st.sidebar:
    st.selectbox(f"🌍 {t('language')}", ["English"], key='language')
    if st.session_state.logged_in:
        user = st.session_state.users[st.session_state.current_user]
        st.success(f"{t('hello')}, {user['name']}")
        if st.button(t("logout"), type="primary", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
    else:
        st.subheader(t("welcome"))
        email = st.text_input(t("email")); password = st.text_input(t("password"), type="password")
        if st.button(t("login"), type="primary", use_container_width=True):
            u = st.session_state.users.get(email)
            if u and u['password'] == password: st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
            else: st.error("Wrong credentials")

# 6. TOP NAV + PAGES - THIS IS YOUR BLOCK MERGED
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if not st.session_state.logged_in:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: 
        if st.button("Home", use_container_width=True, key="top_home"): st.session_state.page = 'Home'; st.rerun()
    with col2: 
        if st.button("About Us", use_container_width=True, key="top_about"): st.session_state.page = 'About'; st.rerun()
    with col3: 
        if st.button("Gallery", use_container_width=True, key="top_gallery"): st.session_state.page = 'Gallery'; st.rerun()
    with col4: 
        if st.button("Contact", use_container_width=True, key="top_contact"): st.session_state.page = 'Contact'; st.rerun()
    with col5: 
        if st.button("Login", use_container_width=True, key="top_login"): st.sidebar.expander("Login 👈", expanded=True); st.rerun()

    # 7. PAGE CONTENT - YOUR BEAUTIFUL HOME PAGE GOES HERE
    if st.session_state.page == 'Home':
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-family: Space Grotesk; font-size: 3.5rem; color: #14532D; margin-bottom: 0;'>WORK CHOP</h1>
            <h2 style='font-family: IBM Plex Mono; font-size: 1.2rem; color: #4A453E; letter-spacing: 2px; margin-top: 0.5rem;'>FOR HUMANITY, BY HUMANITY</h2>
            <p style='font-size: 1.1rem; color: #1C1A17; margin-top: 1.5rem;'><strong>I tanda like rock no shaking</strong> - Connecting 26M+ Nigerian skilled workers</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown("#### **33.3% Unemployment** \n23 million Nigerians dey jobless.")
        with col2: st.markdown("#### **Zero Risk Activation** \nSabimen join FREE with NIN.")
        with col3: st.markdown("#### **Escrow Protected** \nMoney dey safe. Paid in 24hrs.")
        st.markdown("---")
        st.markdown("### **How Work Chop Dey Work** \n**For Sabimen:** 1.Register FREE 2.Get Hired 3.Do the Work 4.Get Paid")

    elif st.session_state.page == 'About':
        st.markdown("# **About Work Chop**"); st.markdown("### *Nigeria's Labor Revolution*")
        st.markdown("#### **The Problem** \n26 million skilled workers dey informal sector. No connection.")
    
    elif st.session_state.page == 'Gallery':
        st.markdown("# **Work Chop Gallery**"); st.info("📸 Gallery coming soon")
    
    elif st.session_state.page == 'Contact':
        st.markdown("# **Contact Work Chop**"); st.write("📍 15 Awolowo Road, Ikoyi, Lagos")

else: # LOGGED IN
    if role == 'client':
        col1, col2, col3, col4 = st.columns(4)
        with col1: 
            if st.button("Dashboard", key="c_dash"): st.session_state.page = 'Dashboard'; st.rerun()
        with col4: 
            if st.button("Logout", key="c_logout"): st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
        if st.session_state.page == 'Dashboard': st.title("Client Dashboard"); st.metric("Wallet", f"₦{user.get('wallet_balance', 0):,}")

    elif role == 'sabiman':
        col1, col2, col3, col4 = st.columns(4)
        with col1: 
            if st.button("Dashboard", key="s_dash"): st.session_state.page = 'Dashboard'; st.rerun()
        with col4: 
            if st.button("Logout", key="s_logout"): st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
        if st.session_state.page == 'Dashboard':
            st.title("Sabiman Dashboard")
            if not user.get('is_activated'): st.warning("⚠️ Account Not Activated. First ₦500 job activates you FREE.")

    elif role == 'admin':
        st.title("Admin Dashboard"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
# END FILE#
############ SIDE BAR #######
# 1. PAGE CONFIG
st.set_page_config(page_title="Work Chop - For Humanity, By Humanity", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")
# 2. CSS - MUST BE FIRST
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap');
.stApp { background: #0f0f0f; font-family: 'Outfit', sans-serif; }
header[data-testid="stHeader"] { display: none; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #008751 0%, #059669 100%); padding-top: 1rem; min-width: 300px!important; }
section[data-testid="stSidebar"] * { color: white!important; }
.stButton>button { background: linear-gradient(135deg, #008751 0%, #059669 100%)!important; color: white!important; font-weight: 700!important; border-radius: 12px!important; }
</style>
""", unsafe_allow_html=True)

# 3. DB + SESSION + HELPERS
conn = sqlite3.connect('workchop.db', check_same_thread=False); cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, user_type TEXT)'); conn.commit()

LANGUAGES = {
    "English": {"welcome": "Welcome Back", "login": "Login", "join": "Join Free", "email": "Email", "password": "Password", "full_name": "Full Name", "phone": "Phone", "nin": "NIN (11 digits)", "send_otp": "Send OTP", "enter_otp": "Enter OTP", "register_sabiman": "Register as Sabiman", "register_client": "Register as Client", "i_be": "I be:", "logout": "Logout", "hello": "Hello", "role": "Role", "fund_wallet": "Fund Wallet"},
    "Hausa": {"welcome": "Barka da Zuwa", "login": "Shiga", "join": "Yi Rajista Kyauta", "email": "Imel", "password": "Kalmar Sirri", "full_name": "Cikakken Suna", "phone": "Lambar Wayar", "nin": "NIN (Lambobi 11)", "send_otp": "Aika OTP", "enter_otp": "Shigar da OTP", "register_sabiman": "Yi Rajista a matsayin Sabiman", "register_client": "Yi Rajista a matsayin Client", "i_be": "Ni ne:", "logout": "Fita", "hello": "Sannu", "role": "Matsayi", "fund_wallet": "Cika Wallet"}
}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)
def generate_otp(): return str(random.randint(100000, 999))
def log_traffic(action): pass # Simplified

if 'language' not in st.session_state: st.session_state.language = "English"
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'otp_store' not in st.session_state: st.session_state.otp_store = {}
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'wallet_balance': 5000, 'phone': '08011111'},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'wallet_balance': 0, 'phone': '08022222', 'nin': '34567890123'},
    }
if 'jobs' not in st.session_state: st.session_state.jobs = []

# 4. YOUR SIDEBAR FUNCTION - CALLED ONCE
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🌍 {t('language')}")
        lang = st.selectbox("", ["English", "Hausa"], index=["English", "Hausa"].index(st.session_state.language), key="sidebar_lang_select")
        if lang!= st.session_state.language: st.session_state.language = lang; st.rerun()

        st.markdown("---"); st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("**I tanda like rock no shaking**"); st.markdown("---")

        if not st.session_state.logged_in:
            choice = st.radio(f"**{t('hello')}:**", [t("login"), t("join")], key="sidebar_auth_choice")
            if choice == t("login"):
                st.subheader(t("welcome"))
                email = st.text_input(f"**{t('email')}**", key="sidebar_login_email")
                password = st.text_input(f"**{t('password')}**", type="password", key="sidebar_login_pass")
                if st.button(t("login"), type="primary", use_container_width=True, key="sidebar_login_btn"):
                    if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                        st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                    else: st.error("Wrong credentials")
            else: # JOIN
                st.subheader(t("join"))
                role = st.selectbox(f"**{t('i_be')}**", ["Client", "Sabiman/Worker"], key="sidebar_join_role")
                name = st.text_input(f"**{t('full_name')}**", key="sidebar_join_name")
                new_email = st.text_input(f"**{t('email')}**", key="sidebar_join_email")
                new_pass = st.text_input(f"**{t('password')}**", type="password", key="sidebar_join_pass")
                phone = st.text_input(f"**{t('phone')}**", placeholder="08012345678", key="sidebar_join_phone")
                region = st.selectbox("Region", ["Abuja", "Lagos", "Kano"], key="sidebar_join_region")

                if role == "Sabiman/Worker":
                    nin = st.text_input(f"**{t('nin')}**", max_chars=11, key="sidebar_join_nin")
                    if st.button(t("send_otp"), disabled=not phone, key="sidebar_send_otp_btn"):
                        if len(phone) == 11: otp = generate_otp(); st.session_state.otp_store[phone] = otp; st.success(f"OTP: **{otp}**")
                        else: st.error("Valid 11-digit phone")
                    otp_input = st.text_input(f"**{t('enter_otp')}**", max_chars=6, key="sidebar_otp_input")
                    if st.button(t("register_sabiman"), type="primary", use_container_width=True, key="sidebar_reg_sabi_btn"):
                        if new_email in st.session_state.users: st.error("Email exists")
                        elif len(nin)!= 11: st.error("NIN must be 11 digits")
                        elif st.session_state.otp_store.get(phone)!= otp_input: st.error("Wrong OTP")
                        else:
                            st.session_state.users[new_email] = {'password': new_pass, 'role': 'sabiman', 'name': name, 'phone': phone, 'nin': nin, 'verified': True, 'region': region, 'is_activated': False, 'wallet_balance': 0}
                            st.success("✅ Verified! Login now. No upfront payment needed!"); st.balloons()
                else:
                    if st.button(t("register_client"), type="primary", use_container_width=True, key="sidebar_reg_client_btn"):
                        if new_email in st.session_state.users: st.error("Email exists")
                        elif name and new_email and new_pass and phone:
                            st.session_state.users[new_email] = {'password': new_pass, 'role': 'client', 'name': name, 'phone': phone, 'region': region, 'wallet_balance': 0}
                            st.success("✅ Registered! Login now")
                        else: st.error("Fill all fields")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"{t('hello')}, {user['name']}")
            st.write(f"**{t('role')}:** {user['role'].title()}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard", use_container_width=True, key="admin_dash_btn"): st.session_state.page = 'Dashboard'; st.rerun()
            st.markdown("---")
            if st.button(t("logout"), use_container_width=True, key="sidebar_logout_btn"):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()

render_sidebar() # 5. CALL IT ONCE HERE
# 6. HEADER
st.markdown("# WORK CHOP"); st.caption("Find Local Services in Nigeria"); st.markdown("---")

# 7. TOP NAV + PAGES
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if not st.session_state.logged_in:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Home", key="top_home"): st.session_state.page = 'Home'; st.rerun()
    with col2:
        if st.button("About", key="top_about"): st.session_state.page = 'About'; st.rerun()

    # YOUR HOME PAGE CONTENT
    if st.session_state.page == 'Home':
        st.markdown("""<div style='text-align: center; padding: 2rem 0;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1><h2>FOR HUMANITY, BY HUMANITY</h2><p><strong>I tanda like rock no shaking</strong></p></div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown("#### **33.3% Unemployment** \n23 million Nigerians dey jobless.")
        with col2: st.markdown("#### **Zero Risk Activation** \nSabimen join FREE with NIN.")
        with col3: st.markdown("#### **Escrow Protected** \nMoney dey safe.")

    elif st.session_state.page == 'About':
        st.markdown("# **About Work Chop**"); st.write("26 million skilled workers dey informal sector. No connection.")

else: # LOGGED IN
    if role == 'client':
        if st.button("Dashboard"): st.session_state.page = 'Dashboard'
        if st.session_state.page == 'Dashboard':
            st.title("Client Dashboard"); st.metric("Wallet", f"₦{user.get('wallet_balance', 0):,}")
            # 3 FUNDING OPTIONS FOR NAIJA
            tab1, tab2, tab3 = st.tabs(["💳 Card/Paystack", "🏦 Bank Transfer", "📱 USSD"])
            with tab1:
                if "PAYSTACK_SECRET_KEY" in st.secrets:
                    amount = st.number_input("Amount ₦", 100, 1000, key="ps_amt")
                    if st.button("Pay with Card"):
                        headers = {"Authorization": f"Bearer {st.secrets['PAYSTACK_SECRET_KEY']}"}
                        data = {"email": st.session_state.current_user, "amount": amount * 100, "reference": f"WC_{random.randint(10000,99999)}"}
                        r = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
                        if r.status_code == 200: st.markdown(f"[**Pay ₦{amount:,}**]({r.json()['data']['authorization_url']})")
                else: st.warning("Add PAYSTACK_SECRET_KEY to secrets.toml")
            with tab2: st.info("Acc: 1234567890 GTBank")
            with tab3: st.info("Dial: *737*1*1*1234567890#")

    elif role == 'sabiman':
        st.title("Sabiman Dashboard")
        if not user.get('is_activated'): st.warning("⚠️ Account Not Activated. First ₦500 job activates you FREE.")

    elif role == 'admin':
        st.title("Admin Dashboard"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
# END FILE
##########ADMINDSAHB)ARD
1. #PAGE CONFIG
st.set_page_config(page_title="Work Chop - For Humanity, By Humanity", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

# 2. CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap');
.stApp { background: #0f0f0f; font-family: 'Outfit', sans-serif; }
header[data-testid="stHeader"] { display: none; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #008751 0%, #059669 100%); padding-top: 1rem; min-width: 300px!important; }
section[data-testid="stSidebar"] * { color: white!important; }
</style>
""", unsafe_allow_html=True)

# 3. DB + SESSION + HELPERS
LANGUAGES = {"English": {"welcome": "Welcome Back", "login": "Login", "join": "Join Free", "email": "Email", "password": "Password", "full_name": "Full Name", "phone": "Phone", "nin": "NIN (11 digits)", "send_otp": "Send OTP", "enter_otp": "Enter OTP", "register_sabiman": "Register as Sabiman", "register_client": "Register as Client", "i_be": "I be:", "logout": "Logout", "hello": "Hello", "role": "Role", "fund_wallet": "Fund Wallet"}}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)
def generate_otp(): return str(random.randint(100000, 999))

if 'language' not in st.session_state: st.session_state.language = "English"
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard' # 2. ADD THIS
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'otp_store' not in st.session_state: st.session_state.otp_store = {}
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'wallet_balance': 5000, 'phone': '08011111', 'region': 'Abuja'},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'wallet_balance': 0, 'phone': '08022222', 'nin': '34567890123', 'available': True, 'region': 'Abuja'},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'is_activated': True, 'available': False, 'region': 'Lagos'},
    }
# 3. ADD SAMPLE PAID JOBS SO CHARTS NO GO EMPTY
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Sink', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Completed - Paid', 'commission': 3000, 'sabiman_payout': 12000, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman2@test.com', 'title': 'Sew Agbada', 'category': 'Tailoring', 'region': 'Lagos', 'amount': 50000, 'duration': 'Weekly', 'status': 'Completed - Paid', 'commission': 10000, 'sabiman_payout': 40000, 'paid_at': (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'category': 'Electrical', 'region': 'Abuja', 'amount': 35000, 'duration': 'Hourly', 'status': 'Completed - Paid', 'commission': 7000, 'sabiman_payout': 28000, 'paid_at': datetime.now().strftime("%Y-%m-%d")},
    ]

# 4. YOUR ADMIN DASHBOARD FUNCTION - PLUGGED IN
def admin_dashboard():
    st.markdown("""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;"><div><h1 style="margin: 0; color: white;">Work Chop Admin Dashboard</h1><p style="color: #9ca3af; margin: 0;">Real-Time Business Intelligence</p></div></div>""", unsafe_allow_html=True)

    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    total_revenue = sum([j['commission'] for j in paid_jobs])
    total_client_paid = sum([j['amount'] for j in paid_jobs])
    total_sabiman_paid = sum([j['sabiman_payout'] for j in paid_jobs])

    # BIG CARDS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white; border: 1px solid #10b981;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Total Revenue</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_revenue:,}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">↑ Commission</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Client Payments</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_client_paid:,}</h1><p style="color: #3b82f6; font-size: 0.9rem; margin: 0;">Total inflow</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Sabiman Payouts</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_sabiman_paid:,}</h1><p style="color: #ef4444; font-size: 0.9rem; margin: 0;">Paid to workers</p></div>""", unsafe_allow_html=True)
    with col4:
        active_sabimen = len([u for u in st.session_state.users.values() if u['role'] == 'sabiman' and u.get('available', False)])
        st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Active Sabimen</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{active_sabimen}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">Online now</p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CHARTS ROW 1
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("### 📊 Revenue by Duration")
        duration_types = ['Hourly', 'Daily', 'Weekly', 'Monthly', 'One-time']
        revenue_data = [sum([j['commission'] for j in paid_jobs if j['duration'] == dur]) for dur in duration_types]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=duration_types, y=revenue_data, marker_color='#10b981', text=[f'₦{x:,}' for x in revenue_data], textposition='auto'))
        fig.update_layout(height=350, showlegend=False, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💰 Payment Split")
        fig_donut = go.Figure(data=[go.Pie(labels=['Sabiman Payout', 'Commission'], values=[total_sabiman_paid, total_revenue], hole=.6, marker_colors=['#3b82f6', '#10b981'], textinfo='label+percent')])
        fig_donut.update_layout(height=350, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', legend=dict(font=dict(color='white')))
        st.plotly_chart(fig_donut, use_container_width=True)

    # CHARTS ROW 2
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Revenue Trend")
        last_7_days = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        revenue_trend = [sum([j['commission'] for j in paid_jobs if j.get('paid_at') and datetime.strptime(j['paid_at'], "%Y-%m-%d").date() == (datetime.now() - timedelta(days=i)).date()]) for i in range(6, -1, -1)]
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=last_7_days, y=revenue_trend, mode='lines+markers', line=dict(color='#10b981', width=3), fill='tozeroy', fillcolor='rgba(16,185,129,0.2)'))
        fig_line.update_layout(height=350, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("### 🌍 Top Regions")
        region_revenue = {}
        for job in paid_jobs: region_revenue[job.get('region', 'Unknown')] = region_revenue.get(job.get('region', 'Unknown'), 0) + job['commission']
        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(x=list(region_revenue.keys()), y=list(region_revenue.values()), marker_color='#8b5cf6', text=[f'₦{x:,}' for x in region_revenue.values()], textposition='auto'))
        fig_region.update_layout(height=350, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig_region, use_container_width=True)

# 5. SIDEBAR FUNCTION
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🌍 {t('language')}")
        lang = st.selectbox("", ["English"], index=0, key="sidebar_lang_select")
        st.markdown("---"); st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("**I tanda like rock no shaking**"); st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input(f"**{t('email')}**"); password = st.text_input(f"**{t('password')}**", type="password")
            if st.button(t("login"), type="primary", use_container_width=True):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                else: st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"{t('hello')}, {user['name']}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard", use_container_width=True): st.session_state.admin_page = 'Dashboard'; st.rerun()
                if st.button("👥 All Users", use_container_width=True): st.session_state.admin_page = 'Users'; st.rerun()
            st.markdown("---")
            if st.button(t("logout"), use_container_width=True):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
render_sidebar()

# 6. HEADER
st.markdown("# WORK CHOP"); st.caption("Find Local Services in Nigeria"); st.markdown("---")

# 7. MAIN PAGES
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if not st.session_state.logged_in:
    st.markdown("""<div style='text-align: center; padding: 2rem 0;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1><h2>FOR HUMANITY, BY HUMANITY</h2></div>""", unsafe_allow_html=True)

else: # LOGGED IN
    if role == 'admin':
        if st.session_state.admin_page == 'Dashboard':
            admin_dashboard() # 4. CALL THE FUNCTION HERE
        elif st.session_state.admin_page == 'Users':
            st.title("👥 All Users"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))

    elif role == 'client':
        st.title("Client Dashboard"); st.metric("Wallet", f"₦{user.get('wallet_balance', 0):,}")

    elif role == 'sabiman':
        st.title("Sabiman Dashboard")
        if not user.get('is_activated'): st.warning("⚠️ Account Not Activated.")
# END FILE

#_________________#
st.set_page_config(page_title="Work Chop", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>.stApp{background:#0f0f0f;} section[data-testid="stSidebar"]{background:linear-gradient(180deg,#008751 0%,#059669 100%);} section[data-testid="stSidebar"]*{color:white!important;}</style>""", unsafe_allow_html=True)

LANGUAGES = {"English": {"welcome": "Welcome Back", "login": "Login", "logout": "Logout", "hello": "Hello", "role": "Role"}}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)
def generate_otp(): return str(random.randint(100000, 999))

if 'language' not in st.session_state: st.session_state.language = "English"
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'otp_store' not in st.session_state: st.session_state.otp_store = {}
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'wallet_balance': 5000, 'phone': '08011111', 'region': 'Abuja', 'rating': 4.8, 'jobs_posted': 5, 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'available': True, 'region': 'Abuja', 'rating': 4.9, 'jobs_done': 47, 'phone': '08022222', 'nin': '34567890123', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'is_activated': True, 'available': False, 'region': 'Lagos', 'rating': 5.0, 'jobs_done': 62, 'phone': '08033333', 'last_active': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'is_activated': False, 'available': True, 'region': 'Port Harcourt', 'rating': 4.7, 'jobs_done': 0, 'phone': '08055555', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Completed - Paid', 'commission': 3000, 'sabiman_payout': 12000, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
        {'id': 2, 'region': 'Lagos', 'amount': 50000, 'duration': 'Weekly', 'status': 'Completed - Paid', 'commission': 10000, 'sabiman_payout': 40000, 'paid_at': (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")},
    ]
if 'admin_messages' not in st.session_state: st.session_state.admin_messages = []

# 1. YOUR TOP SABIMEN FUNCTION - PLUGGED IN
def show_top_sabimen():
    st.markdown("### ⭐ Top 5 Sabimen (5-Star Rated)")
    top_sabimen = sorted([u for u in st.session_state.users.values() if u['role'] == 'sabiman'], key=lambda x: (x['rating'], x['jobs_done']), reverse=True)[:5]
    if top_sabimen:
        df_top = pd.DataFrame([{
            'Name': u['name'], 'Rating': f"{u['rating']} ⭐", 'Jobs Done': u['jobs_done'],
            'Region': u.get('region', 'N/A'), 'Status': '🟢 Active' if u.get('available') else '🔴 Offline',
            'Activated': '✅' if u.get('is_activated') else '⏳'
        } for u in top_sabimen])
        st.dataframe(df_top, use_container_width=True, hide_index=True)

# 2. YOUR ACTIVE USERS FUNCTION - PLUGGED IN
def admin_active_users():
    st.markdown("# 👥 Active Sabimen & Clients")
    tab1, tab2 = st.tabs(["🟢 Active Sabimen", "🟢 Active Clients"])
    with tab1:
        st.markdown("### Active Sabimen (Available for Work)")
        active_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}
        if active_sabimen:
            for email, sabiman in active_sabimen.items():
                activation_badge = "✅ Activated" if sabiman.get('is_activated') else "⏳ Not Activated"
                st.markdown(f"""<div style="background:#1a1a1a; border-left:4px solid #10b981; padding:1rem; border-radius:8px; margin:0.5rem 0;">
                    <h4 style="color: white; margin: 0;">{sabiman['name']} ⭐ {sabiman['rating']} | {activation_badge}</h4>
                    <p style="color: #9ca3af; margin: 0.3rem 0;">📍 {sabiman.get('region', 'N/A')} | 📞 {sabiman['phone']} | {sabiman['jobs_done']} jobs done</p>
                    <p style="color: #10b981; margin: 0; font-size: 0.85rem;">Last active: {sabiman.get('last_active', 'Unknown')}</p>
                </div>""", unsafe_allow_html=True)
        else: st.info("No Sabimen currently available")
    with tab2:
        st.markdown("### Active Clients")
        active_clients = {k:v for k,v in st.session_state.users.items() if v['role'] == 'client'}
        if active_clients:
            for email, client in active_clients.items():
                st.markdown(f"""<div style="background:#1a1a1a; border-left:4px solid #3b82f6; padding:1rem; border-radius:8px; margin:0.5rem 0;">
                    <h4 style="color: white; margin: 0;">{client['name']} ⭐ {client['rating']}</h4>
                    <p style="color: #9ca3af; margin: 0.3rem 0;">📍 {client.get('region', 'N/A')} | 📞 {client['phone']} | {client['jobs_posted']} jobs posted</p>
                </div>""", unsafe_allow_html=True)

# 3. YOUR MESSAGE CENTER FUNCTION - PLUGGED IN
def admin_message_center():
    st.markdown("# 💬 Message Center - Send Reminders")
    st.caption("Send reminder messages to Sabimen and Clients")
    role = st.selectbox("Send to:", ["Sabiman", "Client"])
    msg = st.text_area("Message:", "Reminder: You have pending jobs. Please check your dashboard.")
    if st.button("Send Message"):
        st.session_state.admin_messages.append({"role": role, "msg": msg, "time": datetime.now().strftime("%H:%M")})
        st.success("✅ Message sent!")
    st.markdown("#### Sent Messages")
    st.dataframe(pd.DataFrame(st.session_state.admin_messages))

# 4. YOUR MAIN ADMIN DASHBOARD - NOW CALLS ALL 3
def admin_dashboard():
    st.markdown("""<h1 style="color: white;">Work Chop Admin Dashboard</h1><p style="color: #9ca3af;">Real-Time Business Intelligence</p>""", unsafe_allow_html=True)
    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    total_revenue = sum([j['commission'] for j in paid_jobs])
    total_client_paid = sum([j['amount'] for j in paid_jobs])
    total_sabiman_paid = sum([j['sabiman_payout'] for j in paid_jobs])
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue", f"₦{total_revenue:,}")
    with col2: st.metric("Client Payments", f"₦{total_client_paid:,}")
    with col3: st.metric("Sabiman Payouts", f"₦{total_sabiman_paid:,}")
    with col4: st.metric("Active Sabimen", len([u for u in st.session_state.users.values() if u['role'] == 'sabiman' and u.get('available', False)]))

    show_top_sabimen() # 5. CALL TOP 5 HERE

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(x=['One-time','Weekly'], y=[3000,10000], marker_color='#10b981'))
        fig.update_layout(height=300, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig_donut = go.Figure(data=[go.Pie(labels=['Sabiman','Commission'], values=[total_sabiman_paid, total_revenue], hole=.6)])
        fig_donut.update_layout(height=300, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig_donut, use_container_width=True)

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🌍 {t('language')}"); st.selectbox("", ["English"], key="sidebar_lang_select")
        st.markdown("---"); st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("**I tanda like rock no shaking**"); st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input(f"**{t('email')}**"); password = st.text_input(f"**{t('password')}**", type="password")
            if st.button(t("login"), type="primary", use_container_width=True):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                else: st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"{t('hello')}, {user['name']}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard", use_container_width=True): st.session_state.admin_page = 'Dashboard'; st.rerun()
                if st.button("👥 Active Users", use_container_width=True): st.session_state.admin_page = 'Active'; st.rerun()
                if st.button("💬 Message Center", use_container_width=True): st.session_state.admin_page = 'Messages'; st.rerun()
                if st.button("👤 All Users", use_container_width=True): st.session_state.admin_page = 'Users'; st.rerun()
            st.markdown("---")
            if st.button(t("logout"), use_container_width=True):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
render_sidebar()

st.markdown("# WORK CHOP"); st.markdown("---")

user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if not st.session_state.logged_in:
    st.markdown("""<div style='text-align: center;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1></div>""", unsafe_allow_html=True)
else:
    if role == 'admin':
        if st.session_state.admin_page == 'Dashboard': admin_dashboard()
        elif st.session_state.admin_page == 'Active': admin_active_users() # 6. CALL IT
        elif st.session_state.admin_page == 'Messages': admin_message_center() # 7. CALL IT
        elif st.session_state.admin_page == 'Users': st.title("👥 All Users"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
    elif role == 'client': st.title("Client Dashboard")
    elif role == 'sabiman': st.title("Sabiman Dashboard")
# END FILE
#______________#
st.set_page_config(page_title="Work Chop", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>.stApp{background:#0f0f0f;} section[data-testid="stSidebar"]{background:linear-gradient(180deg,#008751 0%,#059669 100%);} section[data-testid="stSidebar"]*{color:white!important;}</style>""", unsafe_allow_html=True)

LANGUAGES = {"English": {"welcome": "Welcome Back", "login": "Login", "logout": "Logout", "hello": "Hello", "role": "Role"}}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)
def generate_otp(): return str(random.randint(100000, 999))
def log_traffic(action): st.session_state.traffic_log.append({"action": action, "time": datetime.now().strftime("%H:%M")}) # FIX: Add log

if 'language' not in st.session_state: st.session_state.language = "English"
if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'admin_messages' not in st.session_state: st.session_state.admin_messages = []
if 'traffic_log' not in st.session_state: st.session_state.traffic_log = []
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin'},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'phone': '08011111', 'region': 'Abuja', 'rating': 4.8, 'jobs_posted': 5},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'available': True, 'region': 'Abuja', 'rating': 4.9, 'jobs_done': 47, 'phone': '08022222'},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'is_activated': True, 'available': False, 'region': 'Lagos', 'rating': 5.0, 'jobs_done': 62, 'phone': '08033333'},
    }
# ADD PENDING JOBS SO REMINDER SECTION NO GO EMPTY
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Sink', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Work Done - Awaiting Confirmation', 'commission': 3000, 'sabiman_payout': 12000, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), 'auto_release_at': (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M")},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman2@test.com', 'title': 'Sew Agbada', 'category': 'Tailoring', 'region': 'Lagos', 'amount': 50000, 'duration': 'Weekly', 'status': 'Accepted - In Progress', 'commission': 0, 'sabiman_payout': 0, 'auto_release_at': None},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'category': 'Electrical', 'region': 'Abuja', 'amount': 35000, 'duration': 'Hourly', 'status': 'Completed - Paid', 'commission': 7000, 'sabiman_payout': 28000, 'paid_at': datetime.now().strftime("%Y-%m-%d")},
    ]

# 1. TOP SABIMEN
def show_top_sabimen():
    st.markdown("### ⭐ Top 5 Sabimen")
    top_sabimen = sorted([u for u in st.session_state.users.values() if u['role'] == 'sabiman'], key=lambda x: (x['rating'], x['jobs_done']), reverse=True)[:5]
    df_top = pd.DataFrame([{'Name': u['name'], 'Rating': f"{u['rating']} ⭐", 'Jobs Done': u['jobs_done'], 'Region': u.get('region'), 'Status': '🟢' if u.get('available') else '🔴', 'Activated': '✅' if u.get('is_activated') else '⏳'} for u in top_sabimen])
    st.dataframe(df_top, use_container_width=True, hide_index=True)

# 2. ACTIVE USERS
def admin_active_users():
    st.markdown("# 👥 Active Sabimen & Clients")
    tab1, tab2 = st.tabs(["🟢 Active Sabimen", "🟢 Active Clients"])
    with tab1:
        active_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}
        for email, sabiman in active_sabimen.items():
            activation_badge = "✅ Activated" if sabiman.get('is_activated') else "⏳ Not Activated"
            st.markdown(f"""<div style="background:#1a1a1a; border-left:4px solid #10b981; padding:1rem;"><h4>{sabiman['name']} | {activation_badge}</h4></div>""", unsafe_allow_html=True)

# 3. MESSAGE CENTER + PENDING JOBS REMINDER - YOUR CODE PLUGGED IN
def admin_message_center():
    st.markdown("# 💬 Message Center")
    st.caption("Send reminder messages to Sabimen and Clients to follow up on jobs")

    # YOUR CODE STARTS HERE
    pending_jobs = [j for j in st.session_state.jobs if j['status'] in ['Requested - Awaiting Sabiman', 'Accepted - In Progress', 'Work Done - Awaiting Confirmation']]
    if pending_jobs:
        st.markdown("### 🔔 Jobs Needing Follow-Up")
        for job in pending_jobs:
            sabiman = st.session_state.users[job['sabiman']]; client = st.session_state.users[job['client']]
            time_left = ""
            if job.get('auto_release_at'):
                release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
                if release_time > datetime.now():
                    hours_left = (release_time - datetime.now()).seconds // 3600
                    time_left = f" | ⏰ Auto-release in {hours_left}hrs"
            st.markdown(f"""<div style="background:#1a1a1a; padding:1rem; border-radius:16px; margin:1rem 0; border:1px solid #374151;">
                <h4 style="color: white; margin: 0;">{job['title']}</h4>
                <p style="color: #d1d5db;">Status: <b style="color: #f59e0b;">{job['status']}</b> | Amount: ₦{job['amount']:,}{time_left}</p>
                <p style="color: #9ca3af; font-size: 0.9rem;">Sabiman: {sabiman['name']} | Client: {client['name']}</p>
            </div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                sabiman_msg = st.text_area(f"Message to {sabiman['name']}", key=f"sabi_msg_{job['id']}", placeholder="Oga, client dey wait...")
                if st.button(f"📤 Send to Sabiman", key=f"send_sabi_{job['id']}"):
                    if sabiman_msg:
                        st.session_state.admin_messages.append({'to': job['sabiman'], 'from': 'admin', 'message': sabiman_msg, 'job_id': job['id'], 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")})
                        log_traffic(f"Sent reminder to Sabiman for job {job['id']}"); st.success(f"✅ Sent"); st.rerun()
            with col2:
                client_msg = st.text_area(f"Message to {client['name']}", key=f"client_msg_{job['id']}", placeholder="Hello, please confirm...")
                if st.button(f"📤 Send to Client", key=f"send_client_{job['id']}"):
                    if client_msg:
                        st.session_state.admin_messages.append({'to': job['client'], 'from': 'admin', 'message': client_msg, 'job_id': job['id'], 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")})
                        log_traffic(f"Sent reminder to Client for job {job['id']}"); st.success(f"✅ Sent"); st.rerun()
    else: st.success("✅ All jobs are on track! No reminders needed")

    if st.session_state.admin_messages:
        st.markdown("---"); st.markdown("### 📜 Message History")
        for msg in reversed(st.session_state.admin_messages[-10:]):
            recipient = st.session_state.users[msg['to']]['name']
            st.markdown(f"""<div style="background: #1a1a1a; padding: 1rem; border-left: 3px solid #3b82f6;"><p style="color: #9ca3af; font-size: 0.8rem;">To: {recipient} | {msg['timestamp']}</p><p>{msg['message']}</p></div>""", unsafe_allow_html=True)

# 4. ANALYTICS - YOUR CODE PLUGGED IN
def admin_analytics():
    st.markdown("# 📈 Advanced Analytics & Tracking")
    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue", f"₦{sum([j['commission'] for j in paid_jobs]):,}")
    with col2: st.metric("Paid to Sabimen", f"₦{sum([j['sabiman_payout'] for j in paid_jobs]):,}")
    with col3: st.metric("Avg Job Value", f"₦{sum([j['amount'] for j in paid_jobs]) / len(paid_jobs):,.0f}" if paid_jobs else "₦0")
    with col4: st.metric("Completion Rate", f"{len(paid_jobs) / len(st.session_state.jobs) * 100:.1f}%" if st.session_state.jobs else "0%")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Revenue by Category")
        cat_revenue = {}; [cat_revenue.update({job['category']: cat_revenue.get(job['category'], 0) + job['commission']}) for job in paid_jobs]
        fig_cat = go.Figure(go.Bar(x=list(cat_revenue.keys()), y=list(cat_revenue.values()), marker_color='#10b981'))
        fig_cat.update_layout(height=400, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig_cat, use_container_width=True)
    with col2:
        st.markdown("### 🏆 Top 5 Sabimen by Earnings")
        sabiman_earnings = {}; [sabiman_earnings.update({job['sabiman']: sabiman_earnings.get(job['sabiman'], 0) + job['sabiman_payout']}) for job in paid_jobs]
        top_earners = sorted(sabiman_earnings.items(), key=lambda x: x[1], reverse=True)[:5]
        names = [st.session_state.users[email]['name'] for email, _ in top_earners]; earnings = [amt for _, amt in top_earners]
        fig_top = go.Figure(go.Bar(y=names, x=earnings, orientation='h', marker_color='#3b82f6'))
        fig_top.update_layout(height=400, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig_top, use_container_width=True)

# 5. MAIN DASHBOARD
def admin_dashboard():
    st.markdown("""<h1 style="color: white;">Work Chop Admin Dashboard</h1>""", unsafe_allow_html=True)
    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue", f"₦{sum([j['commission'] for j in paid_jobs]):,}")
    with col2: st.metric("Client Payments", f"₦{sum([j['amount'] for j in paid_jobs]):,}")
    with col3: st.metric("Sabiman Payouts", f"₦{sum([j['sabiman_payout'] for j in paid_jobs]):,}")
    with col4: st.metric("Active Sabimen", len([u for u in st.session_state.users.values() if u['role'] == 'sabiman' and u.get('available', False)]))
    show_top_sabimen()

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🌍 English"); st.markdown("---"); st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input("**Email**"); password = st.text_input("**Password**", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                else: st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"Hello, {user['name']}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard"): st.session_state.admin_page = 'Dashboard'; st.rerun()
                if st.button("👥 Active Users"): st.session_state.admin_page = 'Active'; st.rerun()
                if st.button("💬 Message Center"): st.session_state.admin_page = 'Messages'; st.rerun()
                if st.button("📈 Analytics"): st.session_state.admin_page = 'Analytics'; st.rerun() # 6. ADD THIS
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.rerun()
render_sidebar()

st.markdown("# WORK CHOP"); st.markdown("---")
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if st.session_state.logged_in and role == 'admin':
    if st.session_state.admin_page == 'Dashboard': admin_dashboard()
    elif st.session_state.admin_page == 'Active': admin_active_users()
    elif st.session_state.admin_page == 'Messages': admin_message_center() # 7. CALL IT
    elif st.session_state.admin_page == 'Analytics': admin_analytics() # 8. CALL IT
    else: st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
elif st.session_state.logged_in: st.title(f"{role.title()} Dashboard")
else: st.markdown("""<div style='text-align: center;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1></div>""", unsafe_allow_html=True)
# END FILE
#------------#
st.set_page_config(page_title="Work Chop", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>.stApp{background:#0f0f0f;} section[data-testid="stSidebar"]{background:linear-gradient(180deg,#008751 0%,#059669 100%);} section[data-testid="stSidebar"]*{color:white!important;}</style>""", unsafe_allow_html=True)

LANGUAGES = {"English": {"welcome": "Welcome Back", "login": "Login", "logout": "Logout", "hello": "Hello", "role": "Role"}}
def t(key): return LANGUAGES[st.session_state.language].get(key, key)
def generate_otp(): return str(random.randint(100000, 999))

if 'language' not in st.session_state: st.session_state.language = "English"
if 'page' not in st.session_state: st.session_state.page = 'Home'
if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'otp_store' not in st.session_state: st.session_state.otp_store = {}
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'wallet_balance': 5000, 'phone': '08011111', 'region': 'Abuja', 'rating': 4.8, 'jobs_posted': 5, 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'available': True, 'region': 'Abuja', 'rating': 4.9, 'jobs_done': 47, 'phone': '08022222', 'nin': '34567890123', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'is_activated': True, 'available': False, 'region': 'Lagos', 'rating': 5.0, 'jobs_done': 62, 'phone': '08033333', 'last_active': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'is_activated': False, 'available': True, 'region': 'Port Harcourt', 'rating': 4.7, 'jobs_done': 0, 'phone': '08055555', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Completed - Paid', 'commission': 3000, 'sabiman_payout': 12000, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
        {'id': 2, 'region': 'Lagos', 'amount': 50000, 'duration': 'Weekly', 'status': 'Completed - Paid', 'commission': 10000, 'sabiman_payout': 40000, 'paid_at': (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")},
    ]
if 'admin_messages' not in st.session_state: st.session_state.admin_messages = []

# 1. YOUR TOP SABIMEN FUNCTION - PLUGGED IN
def show_top_sabimen():
    st.markdown("### ⭐ Top 5 Sabimen (5-Star Rated)")
    top_sabimen = sorted([u for u in st.session_state.users.values() if u['role'] == 'sabiman'], key=lambda x: (x['rating'], x['jobs_done']), reverse=True)[:5]
    if top_sabimen:
        df_top = pd.DataFrame([{
            'Name': u['name'], 'Rating': f"{u['rating']} ⭐", 'Jobs Done': u['jobs_done'],
            'Region': u.get('region', 'N/A'), 'Status': '🟢 Active' if u.get('available') else '🔴 Offline',
            'Activated': '✅' if u.get('is_activated') else '⏳'
        } for u in top_sabimen])
        st.dataframe(df_top, use_container_width=True, hide_index=True)

# 2. YOUR ACTIVE USERS FUNCTION - PLUGGED IN
def admin_active_users():
    st.markdown("# 👥 Active Sabimen & Clients")
    tab1, tab2 = st.tabs(["🟢 Active Sabimen", "🟢 Active Clients"])
    with tab1:
        st.markdown("### Active Sabimen (Available for Work)")
        active_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}
        if active_sabimen:
            for email, sabiman in active_sabimen.items():
                activation_badge = "✅ Activated" if sabiman.get('is_activated') else "⏳ Not Activated"
                st.markdown(f"""<div style="background:#1a1a1a; border-left:4px solid #10b981; padding:1rem; border-radius:8px; margin:0.5rem 0;">
                    <h4 style="color: white; margin: 0;">{sabiman['name']} ⭐ {sabiman['rating']} | {activation_badge}</h4>
                    <p style="color: #9ca3af; margin: 0.3rem 0;">📍 {sabiman.get('region', 'N/A')} | 📞 {sabiman['phone']} | {sabiman['jobs_done']} jobs done</p>
                    <p style="color: #10b981; margin: 0; font-size: 0.85rem;">Last active: {sabiman.get('last_active', 'Unknown')}</p>
                </div>""", unsafe_allow_html=True)
        else: st.info("No Sabimen currently available")
    with tab2:
        st.markdown("### Active Clients")
        active_clients = {k:v for k,v in st.session_state.users.items() if v['role'] == 'client'}
        if active_clients:
            for email, client in active_clients.items():
                st.markdown(f"""<div style="background:#1a1a1a; border-left:4px solid #3b82f6; padding:1rem; border-radius:8px; margin:0.5rem 0;">
                    <h4 style="color: white; margin: 0;">{client['name']} ⭐ {client['rating']}</h4>
                    <p style="color: #9ca3af; margin: 0.3rem 0;">📍 {client.get('region', 'N/A')} | 📞 {client['phone']} | {client['jobs_posted']} jobs posted</p>
                </div>""", unsafe_allow_html=True)

# 3. YOUR MESSAGE CENTER FUNCTION - PLUGGED IN
def admin_message_center():
    st.markdown("# 💬 Message Center - Send Reminders")
    st.caption("Send reminder messages to Sabimen and Clients")
    role = st.selectbox("Send to:", ["Sabiman", "Client"])
    msg = st.text_area("Message:", "Reminder: You have pending jobs. Please check your dashboard.")
    if st.button("Send Message"):
        st.session_state.admin_messages.append({"role": role, "msg": msg, "time": datetime.now().strftime("%H:%M")})
        st.success("✅ Message sent!")
    st.markdown("#### Sent Messages")
    st.dataframe(pd.DataFrame(st.session_state.admin_messages))

# 4. YOUR MAIN ADMIN DASHBOARD - NOW CALLS ALL 3
def admin_dashboard():
    st.markdown("""<h1 style="color: white;">Work Chop Admin Dashboard</h1><p style="color: #9ca3af;">Real-Time Business Intelligence</p>""", unsafe_allow_html=True)
    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    total_revenue = sum([j['commission'] for j in paid_jobs])
    total_client_paid = sum([j['amount'] for j in paid_jobs])
    total_sabiman_paid = sum([j['sabiman_payout'] for j in paid_jobs])
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue", f"₦{total_revenue:,}")
    with col2: st.metric("Client Payments", f"₦{total_client_paid:,}")
    with col3: st.metric("Sabiman Payouts", f"₦{total_sabiman_paid:,}")
    with col4: st.metric("Active Sabimen", len([u for u in st.session_state.users.values() if u['role'] == 'sabiman' and u.get('available', False)]))

    show_top_sabimen() # 5. CALL TOP 5 HERE

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(x=['One-time','Weekly'], y=[3000,10000], marker_color='#10b981'))
        fig.update_layout(height=300, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig_donut = go.Figure(data=[go.Pie(labels=['Sabiman','Commission'], values=[total_sabiman_paid, total_revenue], hole=.6)])
        fig_donut.update_layout(height=300, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a'); st.plotly_chart(fig_donut, use_container_width=True)

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🌍 {t('language')}"); st.selectbox("", ["English"], key="sidebar_lang_select")
        st.markdown("---"); st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("**I tanda like rock no shaking**"); st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input(f"**{t('email')}**"); password = st.text_input(f"**{t('password')}**", type="password")
            if st.button(t("login"), type="primary", use_container_width=True):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                else: st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"{t('hello')}, {user['name']}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard", use_container_width=True): st.session_state.admin_page = 'Dashboard'; st.rerun()
                if st.button("👥 Active Users", use_container_width=True): st.session_state.admin_page = 'Active'; st.rerun()
                if st.button("💬 Message Center", use_container_width=True): st.session_state.admin_page = 'Messages'; st.rerun()
                if st.button("👤 All Users", use_container_width=True): st.session_state.admin_page = 'Users'; st.rerun()
            st.markdown("---")
            if st.button(t("logout"), use_container_width=True):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.session_state.page = 'Home'; st.rerun()
render_sidebar()

st.markdown("# WORK CHOP"); st.markdown("---")

user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if not st.session_state.logged_in:
    st.markdown("""<div style='text-align: center;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1></div>""", unsafe_allow_html=True)
else:
    if role == 'admin':
        if st.session_state.admin_page == 'Dashboard': admin_dashboard()
        elif st.session_state.admin_page == 'Active': admin_active_users() # 6. CALL IT
        elif st.session_state.admin_page == 'Messages': admin_message_center() # 7. CALL IT
        elif st.session_state.admin_page == 'Users': st.title("👥 All Users"); st.dataframe(pd.DataFrame.from_dict(st.session_state.users, orient='index'))
    elif role == 'client': st.title("Client Dashboard")
    elif role == 'sabiman': st.title("Sabiman Dashboard")


# END FILE
#--------------#
st.set_page_config(page_title="Work Chop", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>.stApp{background:#0f0f0f;} section[data-testid="stSidebar"]{background:linear-gradient(180deg,#008751 0%,#059669 100%);} section[data-testid="stSidebar"]*{color:white!important;}.highlight-box{background:#1e3a8a; border:2px solid #3b82f6; padding:1.5rem; border-radius:16px;}.available-card{background:#1a1a1a; border:2px solid #10b981; padding:1.5rem; border-radius:16px;}.message-box{background:#1f2937; padding:1.5rem; border-radius:16px; border:1px solid #374151;}</style>""", unsafe_allow_html=True)

def t(key): return "English"
def generate_otp(): return str(random.randint(100000, 999))
def log_traffic(action): st.session_state.traffic_log.append({"action": action, "time": datetime.now().strftime("%H:%M")})
def calculate_commission(amount): return int(amount * 0.2) # 20% commission - FIX 1

if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'admin_messages' not in st.session_state: st.session_state.admin_messages = []
if 'traffic_log' not in st.session_state: st.session_state.traffic_log = []
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'phone': '08011111', 'wallet_balance': 5000},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'activation_bonus_paid': False, 'jobs_completed_for_activation': 2, 'available': True, 'region': 'Abuja', 'rating': 4.9, 'jobs_done': 47, 'phone': '08022222', 'work_categories': ['Plumbing', 'AC Repair'], 'rates': {'hourly': 2000, 'daily': 15000, 'weekly': 0, 'monthly': 0}, 'portfolio': []},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Kitchen Sink', 'location': 'Wuse 2, Abuja', 'desc': 'Leaking pipe under sink', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Requested - Awaiting Sabiman', 'commission': 0, 'sabiman_payout': 0},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'location': 'Maitama, Abuja', 'desc': 'AC no dey cold', 'category': 'AC Repair', 'region': 'Abuja', 'amount': 35000, 'duration': 'Hourly', 'status': 'Work Done - Awaiting Confirmation', 'commission': 7000, 'sabiman_payout': 28000},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Pipe Work', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 25000, 'duration': 'Daily', 'status': 'Completed - Paid', 'commission': 5000, 'sabiman_payout': 20000},
    ]

# 1. YOUR FULL SABIMAN DASHBOARD - PLUGGED IN
def dashboard_page():
    user = st.session_state.users[st.session_state.current_user]
    if user['role'] == 'sabiman':
        log_traffic("View Dashboard")
        st.markdown("""<h1 style="color: white;">Sabiman Dashboard</h1><p style="color: #9ca3af;">Your Earnings Overview</p>""", unsafe_allow_html=True)

        # ZERO RISK ACTIVATION UI
        st.markdown("### 🔐 Account Activation Status")
        if not user.get('is_activated', False):
            st.markdown("""<div class="highlight-box"><h4>⚠️ Account Not Activated</h4><p style="color: #f59e0b;">Your first ₦500 earning will activate your account automatically. No upfront payment needed!</p></div>""", unsafe_allow_html=True)
        elif not user.get('activation_bonus_paid', False):
            remaining = 5 - user.get('jobs_completed_for_activation', 0)
            st.markdown(f"""<div class="available-card"><h4>🎁 Loyalty Bonus Progress</h4><p style="color: #10b981;">Complete {remaining} more jobs to unlock ₦500 Loyalty Bonus!</p></div>""", unsafe_allow_html=True)
            st.progress(user.get('jobs_completed_for_activation', 0) / 5)
        else:
            st.markdown("""<div class="available-card"><h4>✅ Fully Activated + Bonus Received</h4><p style="color: #10b981;">Your account is verified and you've received your ₦500 loyalty bonus!</p></div>""", unsafe_allow_html=True)
        st.markdown("---")

        # YOUR PROFILE SECTION - YOUR CODE
        st.markdown("### 👤 Your Profile & Portfolio")
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            st.markdown("**Profile Picture**")
            profile_pic = st.file_uploader("Selfie", type=['jpg', 'jpeg', 'png'], key="profile_upload")
            if profile_pic: st.image(profile_pic, width=150); st.session_state.users[st.session_state.current_user]['profile_pic'] = profile_pic.name; st.success("✅ Updated!")
            elif user.get('profile_pic'): st.caption(f"📷 {user['profile_pic']}")
        with col2:
            st.markdown("**Previous Work**")
            portfolio_pic = st.file_uploader("Portfolio", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="portfolio_upload")
            if portfolio_pic:
                for pic in portfolio_pic:
                    if pic.name not in user.get('portfolio', []): st.session_state.users[st.session_state.current_user].setdefault('portfolio', []).append(pic.name)
                st.success(f"✅ {len(portfolio_pic)} added!")
            if user.get('portfolio'): st.caption(f"📷 {len(user['portfolio'])} images")
        with col3:
            st.markdown("**Availability Status**")
            available = st.checkbox("✅ I am Available for Work", value=user.get('available', True), key="available_check")
            st.session_state.users[st.session_state.current_user]['available'] = available
            work_cats = st.multiselect("Work Categories", ['Plumbing', 'Electrical', 'Tailoring', 'Cleaning', 'AC Repair', 'Fashion', 'Solar', 'Carpentry'], default=user.get('work_categories', []), key="work_cats")
            st.session_state.users[st.session_state.current_user]['work_categories'] = work_cats
        st.markdown("---")

        # RATE CARD
        st.markdown("### 💰 Your Rate Card")
        col1, col2, col3, col4 = st.columns(4)
        rates = user.get('rates', {'hourly': 0, 'daily': 0, 'weekly': 0, 'monthly': 0})
        with col1: hourly = st.number_input("Hourly (₦)", value=rates['hourly'], step=500, key="rate_hourly")
        with col2: daily = st.number_input("Daily (₦)", value=rates['daily'], step=1000, key="rate_daily")
        with col3: weekly = st.number_input("Weekly (₦)", value=rates['weekly'], step=5000, key="rate_weekly")
        with col4: monthly = st.number_input("Monthly (₦)", value=rates['monthly'], step=10000, key="rate_monthly")
        if st.button("💾 Save Rates & Categories", use_container_width=True, key="save_rates"):
            st.session_state.users[st.session_state.current_user]['rates'] = {'hourly': hourly, 'daily': daily, 'weekly': weekly, 'monthly': monthly}
            st.success("✅ Rates updated! Clients can now see your pricing"); st.rerun()
        st.markdown("---")

        # METRICS - BIG CARDS
        my_jobs = [j for j in st.session_state.jobs if j.get('sabiman') == st.session_state.current_user]
        paid_jobs = [j for j in my_jobs if j['status'] == 'Completed - Paid']
        pending_jobs = [j for j in my_jobs if j['status'] == 'Work Done - Awaiting Confirmation']
        new_requests = [j for j in my_jobs if j['status'] == 'Requested - Awaiting Sabiman']
        total_earned = sum([j['sabiman_payout'] for j in paid_jobs])
        total_pending = sum([j['amount'] - calculate_commission(j['amount']) for j in pending_jobs]) # FIX 2
        jobs_done = len(paid_jobs); rating = user.get('rating', 5.0)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Paid", f"₦{total_earned:,}", "✓ In your account")
        with col2: st.metric("Pending Payment", f"₦{total_pending:,}", "⏳ Awaiting client")
        with col3: st.metric("Jobs Completed", jobs_done)
        with col4: st.metric("New Requests", len(new_requests))
        st.markdown("<br>", unsafe_allow_html=True)

        # NEW REQUESTS FROM CLIENTS
        if new_requests:
            st.markdown("### 🔔 New Job Requests")
            for job in new_requests:
                client_name = st.session_state.users[job['client']]['name']
                st.markdown(f"""<div class="available-card"><h3 style="color: white;">{job['title']}</h3><p>From: <b>{client_name}</b> | Location: {job['location']} | Budget: <b style="color: #10b981;">₦{job['amount']:,}</b></p><p style="color: #9ca3af;">{job['desc']}</p></div>""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Accept Job", key=f"accept_{job['id']}", use_container_width=True):
                        job['status'] = 'Accepted - In Progress'; log_traffic(f"Accepted job {job['id']}"); st.success("Job accepted!"); st.rerun()
                with col2:
                    if st.button(f"❌ Decline", key=f"decline_{job['id']}", use_container_width=True):
                        st.session_state.jobs.remove(job); st.info("Job declined"); st.rerun()

    # FIX 3: PAYSTACK BLOCK MOVED OUT. CHECK ROLE CORRECTLY
    if user['role'] == "client": # ✅ Double safe
        st.markdown("### 💰 Fund Wallet")
        with st.expander("Add Money to Wallet - Test Mode"):
            amount = st.number_input("Enter amount (₦)", min_value=100, value=1000, step=100)
            email = st.text_input("Email for receipt", value=st.session_state.current_user) # FIX: use current_user
            if st.button("Pay with Paystack", type="primary", key="paystack_btn"):
                headers = {"Authorization": f"Bearer {st.secrets.get('PAYSTACK_SECRET_KEY', 'sk_test_xxx')}", "Content-Type": "application/json"}
                data = {"email": email, "amount": amount * 100, "reference": f"WC_{random.randint(10000,99999)}"}
                response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
                if response.status_code == 200:
                    url = response.json()['data']['authorization_url']
                    st.success("Click below to pay with TEST CARD")
                    st.markdown(f"[**Pay ₦{amount:,} Now**]({url})")
                    st.caption("Test Card: 4081 | Expiry: 12/34 | CVV: 408 | PIN: 0000")
                else: st.error("Paystack error. Add key to secrets.toml")
        balance = user.get('wallet_balance', 0)
        st.metric("Wallet Balance", f"₦{balance:,}")

# 2. ADMIN FUNCTIONS - SHORTENED
def show_top_sabimen(): st.dataframe(pd.DataFrame([{'Name': u['name']} for u in st.session_state.users.values() if u['role'] == 'sabiman']), hide_index=True)
def admin_dashboard(): st.markdown("<h1>Admin Dashboard</h1>", unsafe_allow_html=True); show_top_sabimen()
def admin_active_users(): st.markdown("# 👥 Active Sabimen")
def admin_message_center(): st.markdown("# 💬 Message Center")
def admin_analytics(): st.markdown("# 📈 Analytics")
def admin_users(): st.markdown("# 👥 All Users")
def admin_create(): st.markdown("# ➕ Create User")
def admin_reports(): st.markdown("# 📄 Reports")

def render_sidebar():
    with st.sidebar:
        st.markdown("# 🇳🇬 WORK CHOP"); st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input("**Email**"); password = st.text_input("**Password**", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True; st.session_state.current_user = email; st.rerun()
                else: st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"Hello, {user['name']}")
            if user['role'] == 'admin':
                st.markdown("---"); st.markdown("### 🔐 Admin Tools")
                for page, label in [('Dashboard','📊 Dashboard'),('Active','👥 Active Users'),('Messages','💬 Message Center'),('Analytics','📈 Analytics'),('Users','👤 All Users'),('Create','➕ Create User'),('Reports','📄 Reports')]:
                    if st.button(label): st.session_state.admin_page = page; st.rerun()
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False; st.session_state.current_user = None; st.rerun()
render_sidebar()

st.markdown("# WORK CHOP"); st.markdown("---")
user = st.session_state.users.get(st.session_state.current_user, {}) if st.session_state.logged_in else {}
role = user.get('role')

if st.session_state.logged_in:
    if role == 'admin':
        {'Dashboard': admin_dashboard, 'Active': admin_active_users, 'Messages': admin_message_center, 'Analytics': admin_analytics, 'Users': admin_users, 'Create': admin_create, 'Reports': admin_reports}.get(st.session_state.admin_page, admin_dashboard)()
    elif role == 'sabiman': dashboard_page() # 3. CALL FULL SABIMAN DASH
    elif role == 'client': st.title("Client Dashboard")
else: st.markdown("""<div style='text-align: center;'><h1 style='font-size: 3.5rem; color: #14532D;'>WORK CHOP</h1></div>""", unsafe_allow_html=True)
# END FILE
##++++++
st.set_page_config(page_title="Work Chop", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>.stApp{background:#0f0f0f;} section[data-testid="stSidebar"]{background:linear-gradient(180deg,#008751 0%,#059669 100%);} section[data-testid="stSidebar"]*{color:white!important;}.highlight-box{background:#1e3a8a; border:2px solid #3b82f6; padding:1.5rem; border-radius:16px;}.available-card{background:#1a1a1a; border:2px solid #10b981; padding:1.5rem; border-radius:16px;}</style>""", unsafe_allow_html=True)

def t(key): return "English"
def generate_otp(): return str(random.randint(100000, 999))
def log_traffic(action): st.session_state.traffic_log.append({"action": action, "time": datetime.now().strftime("%H:%M")})
def calculate_commission(amount): return int(amount * 0.2) # 20% commission

# 1. FIX: ZERO RISK ACTIVATION PAYMENT LOGIC
def process_payment(job_id):
    job = next((j for j in st.session_state.jobs if j['id'] == job_id), None)
    if not job: return
    sabiman_email = job['sabiman']
    sabiman = st.session_state.users[sabiman_email]
    commission = calculate_commission(job['amount'])
    payout = job['amount'] - commission
    job['commission'] = commission; job['sabiman_payout'] = payout; job['status'] = 'Completed - Paid'; job['paid_at'] = datetime.now().strftime("%Y-%m-%d")
    sabiman['jobs_done'] += 1
    # ZERO RISK ACTIVATION LOGIC
    if not sabiman.get('is_activated'):
        sabiman['is_activated'] = True
        sabiman['jobs_completed_for_activation'] = 1
        st.toast(f"🎉 {sabiman['name']} account ACTIVATED! First ₦500 job complete.")
    elif not sabiman.get('activation_bonus_paid', False):
        sabiman['jobs_completed_for_activation'] = sabiman.get('jobs_completed_for_activation', 0) + 1
        if sabiman['jobs_completed_for_activation'] >= 5:
            sabiman['activation_bonus_paid'] = True
            st.toast(f"🎁 ₦500 Loyalty Bonus paid to {sabiman['name']}!")

if 'admin_page' not in st.session_state: st.session_state.admin_page = 'Dashboard'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'admin_messages' not in st.session_state: st.session_state.admin_messages = []
if 'traffic_log' not in st.session_state: st.session_state.traffic_log = []
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'wallet_balance': 0},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'phone': '08011111', 'region': 'Abuja', 'rating': 4.8, 'jobs_posted': 0, 'wallet_balance': 5000},
        'client2@test.com': {'password': 'client123', 'role': 'client', 'name': 'Aisha Client', 'phone': '08044444', 'region': 'Lagos', 'rating': 5.0, 'jobs_posted': 0, 'wallet_balance': 20000},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'is_activated': True, 'activation_bonus_paid': True, 'jobs_completed_for_activation': 5, 'available': True, 'region': 'Abuja', 'rating': 4.9, 'jobs_done': 47, 'phone': '08022222', 'bio': 'Expert plumber 10yrs', 'work_categories': ['Plumbing', 'AC Repair'], 'rates': {'hourly': 2000, 'daily': 15000, 'weekly': 0, 'monthly': 0}, 'portfolio': []},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'is_activated': True, 'activation_bonus_paid': False, 'jobs_completed_for_activation': 2, 'available': True, 'region': 'Lagos', 'rating': 5.0, 'jobs_done': 62, 'phone': '08033333', 'bio': 'Fashion designer', 'work_categories': ['Tailoring', 'Fashion'], 'rates': {'hourly': 0, 'daily': 20000, 'weekly': 0, 'monthly': 0}},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'is_activated': False, 'activation_bonus_paid': False, 'jobs_completed_for_activation': 0, 'available': True, 'region': 'Port Harcourt', 'rating': 5.0, 'jobs_done': 0, 'phone': '08055555', 'bio': 'New electrician', 'work_categories': ['Electrical'], 'rates': {'hourly': 1500, 'daily': 10000, 'weekly': 0, 'monthly': 0}},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix Kitchen Sink', 'location': 'Wuse 2, Abuja', 'desc': 'Leaking pipe', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'status': 'Requested - Awaiting Sabiman', 'created': datetime.now().strftime("%Y-%m-%d %H:%M"), 'commission': 0, 'sabiman_payout': 0, 'client_satisfied': False, 'sabiman_satisfied': False, 'paid_at': None, 'auto_release_at': None},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'location': 'Maitama, Abuja', 'desc': 'AC no dey cold', 'category': 'AC Repair', 'region': 'Abuja', 'amount': 35000, 'duration': 'Hourly', 'status': 'Accepted - In Progress', 'created': datetime.now().strftime("%Y-%m-%d %H:%M"), 'commission': 0, 'sabiman_payout': 0, 'client_satisfied': False, 'sabiman_satisfied': False, 'paid_at': None, 'auto_release_at': None},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Pipe Work', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 25000, 'duration': 'Daily', 'status': 'Work Done - Awaiting Confirmation', 'created': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), 'commission': 5000, 'sabiman_payout': 20000, 'client_satisfied': False, 'sabiman_satisfied': True, 'paid_at': None, 'auto_release_at': (datetime.now() + timedelta(hours=18)).strftime("%Y-%m-%d %H:%M")},
        {'id': 4, 'client': 'client2@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Bathroom Fix', 'category': 'Plumbing', 'region': 'Abuja', 'amount': 30000, 'duration': 'One-time', 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M"), 'commission': 6000, 'sabiman_payout': 24000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), 'auto_release_at': None},
    ]

from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Helper functions assumed to exist in your environment
# def calculate_commission(amount): ...
# def log_traffic(msg): ...
# def process_payment(job_id): ...


# 2. YOUR FULL DASHBOARD_PAGE WITH IN PROGRESS + AWAITING + CHART + CLIENT BROWSE
def dashboard_page():
    user = st.session_state.users[st.session_state.current_user]

    if user["role"] == "sabiman":
        log_traffic("View Dashboard")
        st.markdown(
            """<h1 style="color: white;">Sabiman Dashboard</h1>""",
            unsafe_allow_html=True,
        )

        # Base collections
        my_jobs = [
            j
            for j in st.session_state.jobs
            if j.get("sabiman") == st.session_state.current_user
        ]
        paid_jobs = [j for j in my_jobs if j["status"] == "Completed - Paid"]

        # Metric Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total Paid",
                f"₦{sum([j['sabiman_payout'] for j in paid_jobs]):,}",
            )
        with col2:
            pending_amt = sum(
                [
                    j["amount"] - calculate_commission(j["amount"])
                    for j in my_jobs
                    if j["status"] == "Work Done - Awaiting Confirmation"
                ]
            )
            st.metric("Pending Payment", f"₦{pending_amt:,}")
        with col3:
            st.metric("Jobs Completed", len(paid_jobs))
        with col4:
            st.metric(
                "New Requests",
                len(
                    [
                        j
                        for j in my_jobs
                        if j["status"] == "Requested - Awaiting Sabiman"
                    ]
                ),
            )

        # --- 🔨 JOBS IN PROGRESS SECTION ---
        in_progress = [
            j for j in my_jobs if j["status"] == "Accepted - In Progress"
        ]

        if in_progress:
            st.markdown("### 🔨 Jobs In Progress")

            for job in in_progress:
                client = job.get("client")

                # Safely fetch client name
                if client in st.session_state.users:
                    client_name = st.session_state.users[client].get(
                        "name", "Unknown Client"
                    )
                else:
                    client_name = "Unknown Client"

                # Render HTML highlight card
                st.markdown(
                    f"""
                    <div class="highlight-box">
                        <h3>{job.get('title', 'No Title')}</h3>
                        <p>
                            Client: <b>{client_name}</b> | 
                            Amount: 
                            <b style="color:#f59e0b;">
                                ₦{job.get('amount', 0):,}
                            </b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Unified Interaction Button
                if st.button(
                    "✅ Mark as Work Done", key=f"done_{job['id']}"
                ):
                    job["status"] = "Work Done - Awaiting Confirmation"
                    job["sabiman_satisfied"] = True
                    job["auto_release_at"] = (
                        datetime.now() + timedelta(hours=24)
                    ).strftime("%Y-%m-%d %H:%M")
                    job["reminder_sent"] = False

                    log_traffic(f"Marked job {job['id']} as done")
                    st.success("Client notified! 24hr timer started")
                    st.rerun()

        # --- 🔔 AWAITING CONFIRMATION SECTION ---
        awaiting_jobs = [
            j
            for j in my_jobs
            if j["status"] == "Work Done - Awaiting Confirmation"
        ]
        if awaiting_jobs:
            st.markdown("### 🔔 Jobs Awaiting Client Confirmation")
            for job in awaiting_jobs:
                client_name = st.session_state.users[job["client"]]["name"]
                time_left = ""

                if job.get("auto_release_at"):
                    release_time = datetime.strptime(
                        job["auto_release_at"], "%Y-%m-%d %H:%M"
                    )
                    if release_time > datetime.now():
                        hours_left = int(
                            (release_time - datetime.now()).total_seconds()
                            // 3600
                        )
                        time_left = f"<p style='color: #f59e0b;'>⏰ Auto-release in {hours_left}hrs</p>"

                st.markdown(
                    f"""
                    <div class="highlight-box">
                        <h3>{job['title']}</h3>
                        <p>Client: <b>{client_name}</b> | ₦{job['amount']:,}</p>
                        <p>Client Satisfied: {'✅' if job.get('client_satisfied') else '❌ Waiting'}</p>
                        {time_left}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # --- 📊 EARNINGS CHART SECTION ---
        col1, col2 = st.columns([2, 1])
        with col1:
            last_6_months = [
                (datetime.now() - timedelta(days=30 * i)).strftime("%b")
                for i in range(5, -1, -1)
            ]
            paid_data = [
                sum(
                    [
                        j["sabiman_payout"]
                        for j in paid_jobs
                        if j.get("paid_at")
                        and datetime.strptime(j["paid_at"], "%Y-%m-%d").strftime(
                            "%b"
                        )
                        == m
                    ]
                )
                for m in last_6_months
            ]
            fig = go.Figure(
                go.Scatter(
                    x=last_6_months,
                    y=paid_data,
                    line=dict(color="#10b981", width=3),
                    fill="tozeroy",
                )
            )
            fig.update_layout(
                height=350, plot_bgcolor="#1a1a1a", paper_bgcolor="#1a1a1a"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            this_week_paid = sum(
                [
                    j["sabiman_payout"]
                    for j in paid_jobs
                    if j.get("paid_at")
                    and datetime.strptime(j["paid_at"], "%Y-%m-%d")
                    >= datetime.now() - timedelta(days=7)
                ]
            )
            st.metric("This Week", f"₦{this_week_paid:,}")
            active_jobs = len(
                [
                    j
                    for j in my_jobs
                    if j["status"] not in ["Completed - Paid", "Cancelled"]
                ]
            )
            st.metric("Active Jobs", active_jobs)

    elif user["role"] == "client":
        st.markdown("# 📊 Client Dashboard")

        # --- 🔍 BROWSE SABIMEN CODE ---
        st.markdown("### 🔍 Find Sabimen & Request Work")
        available_sabimen = {
            k: v
            for k, v in st.session_state.users.items()
            if v["role"] == "sabiman" and v.get("available", False)
        }

        if available_sabimen:
            cols = st.columns(3)
            for idx, (email, sabiman) in enumerate(available_sabimen.items()):
                with cols[idx % 3]:
                    activation_status = (
                        "✅ Verified" if sabiman.get("is_activated") else "⏳ New"
                    )
                    st.markdown(
                        f"""
                        <div class="available-card">
                            <h4>{sabiman['name']} {activation_status}</h4>
                            <p>⭐ {sabiman['rating']} | {sabiman['jobs_done']} jobs</p>
                            <p><b>Skills:</b> {', '.join(sabiman.get('work_categories', [])[:2])}</p>
                            <p><b>Daily:</b> ₦{sabiman['rates']['daily']:,}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.expander(f"Request {sabiman['name']}"):
                        job_title = st.text_input(
                            "Job Title", key=f"req_title_{email}"
                        )
                        job_cat = st.selectbox(
                            "Category",
                            sabiman.get("work_categories", ["General"]),
                            key=f"req_cat_{email}",
                        )
                        job_location = st.text_input(
                            "Location", key=f"req_loc_{email}"
                        )
                        job_amount = st.number_input(
                            "Budget (₦)",
                            value=sabiman["rates"]["daily"],
                            step=1000,
                            key=f"req_amt_{email}",
                        )
                        job_desc = st.text_area(
                            "Description", key=f"req_desc_{email}"
                        )

                        if st.button(
                            "Send Request", key=f"req_btn_{email}"
                        ):
                            new_job = {
                                "id": len(st.session_state.jobs) + 1,
                                "client": st.session_state.current_user,
                                "sabiman": email,
                                "title": job_title,
                                "category": job_cat,
                                "location": job_location,
                                "region": user.get("region"),
                                "amount": job_amount,
                                "status": "Requested - Awaiting Sabiman",
                                "created": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                "commission": 0,
                                "sabiman_payout": 0,
                                "client_satisfied": False,
                                "sabiman_satisfied": False,
                                "paid_at": None,
                                "auto_release_at": None,
                            }
                            st.session_state.jobs.append(new_job)
                            st.session_state.users[
                                st.session_state.current_user
                            ]["jobs_posted"] += 1
                            st.success("✅ Request sent!")
                            st.rerun()
        else:
            st.info("No Sabimen available right now")

        # --- 🔔 CLIENT SIDE AWAITING CONFIRMATION ---
        st.markdown("### 🔔 Jobs Awaiting Your Confirmation")
        awaiting_confirmation = [
            j
            for j in st.session_state.jobs
            if j["client"] == st.session_state.current_user
            and j["status"] == "Work Done - Awaiting Confirmation"
        ]

        if awaiting_confirmation:
            for job in awaiting_confirmation:
                sabiman_name = st.session_state.users[job["sabiman"]]["name"]
                time_left = ""

                if job.get("auto_release_at"):
                    release_time = datetime.strptime(
                        job["auto_release_at"], "%Y-%m-%d %H:%M"
                    )
                    if release_time > datetime.now():
                        hours_left = int(
                            (release_time - datetime.now()).total_seconds()
                            // 3600
                        )
                        time_left = f"<p style='color: #f59e0b;'>⏰ Auto-releases in {hours_left}hrs</p>"

                st.markdown(
                    f"""
                    <div class="highlight-box">
                        <h3>{job['title']}</h3>
                        <p>Sabiman: <b>{sabiman_name}</b> | ₦{job['amount']:,}</p>
                        {time_left}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not job.get("client_satisfied"):
                    if st.button(
                        "✅ I am satisfied",
                        key=f"client_satisfy_{job['id']}",
                        type="primary",
                    ):
                        job["client_satisfied"] = True
                        if job.get("client_satisfied") and job.get(
                            "sabiman_satisfied"
                        ):
                            process_payment(job["id"])
                            st.success(
                                f"✅ Payment Released! ₦{job['sabiman_payout']:,} sent"
                            )
                            st.balloons()
                        st.rerun()
        else:
            st.info("No jobs awaiting your confirmation")


# 3. ADMIN FUNCTIONS
def show_top_sabimen():
    st.dataframe(
        pd.DataFrame(
            [
                {"Name": u["name"]}
                for u in st.session_state.users.values()
                if u["role"] == "sabiman"
            ]
        ),
        hide_index=True,
    )


def admin_dashboard():
    st.markdown("<h1>Admin Dashboard</h1>", unsafe_allow_html=True)
    show_top_sabimen()


def admin_active_users():
    st.markdown("# 👥 Active Sabimen")


def admin_message_center():
    st.markdown("# 💬 Message Center")


def admin_analytics():
    st.markdown("# 📈 Analytics")


def admin_users():
    st.markdown("# 👥 All Users")


def admin_create():
    st.markdown("# ➕ Create User")


def admin_reports():
    st.markdown("# 📄 Reports")


def render_sidebar():
    with st.sidebar:
        st.markdown("# 🇳🇬 WORK CHOP")
        st.markdown("---")
        if not st.session_state.logged_in:
            email = st.text_input("**Email**")
            password = st.text_input("**Password**", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if (
                    email in st.session_state.users
                    and st.session_state.users[email]["password"] == password
                ):
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.rerun()
                else:
                    st.error("Wrong credentials")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"Hello, {user['name']}")
            if user["role"] == "admin":
                st.markdown("---")
                st.markdown("### 🔐 Admin Tools")
                for page, label in [
                    ("Dashboard", "📊 Dashboard"),
                    ("Active", "👥 Active Users"),
                    ("Messages", "💬 Message Center"),
                    ("Analytics", "📈 Analytics"),
                    ("Users", "👤 All Users"),
                    ("Create", "➕ Create User"),
                    ("Reports", "📄 Reports"),
                ]:
                    if st.button(label):
                        st.session_state.admin_page = page
                        st.rerun()
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.rerun()


# --- APP RENDERING PIPELINE ---
render_sidebar()

st.markdown("# WORK CHOP")
st.markdown("---")
user = (
    st.session_state.users.get(st.session_state.current_user, {})
    if st.session_state.logged_in
    else {}
)
role = user.get("role")

if st.session_state.logged_in:
    if role == "admin":
        {
            "Dashboard": admin_dashboard,
            "Active": admin_active_users,
            "Messages": admin_message_center,
            "Analytics": admin_analytics,
            "Users": admin_users,
            "Create": admin_create,
            "Reports": admin_reports,
        }.get(st.session_state.admin_page, admin_dashboard)()
    else:
        dashboard_page()
else:
    st.markdown(
        """
    <div style="text-align: center; padding: 4rem;">
        <h1 style="color: white;">🇳🇬 WORK CHOP</h1>
        <p style="color: #6b7280;"><b>Test Logins:</b><br>
        Admin: admin@workchop.ng / admin123<br>
        Client: client@test.com / client123<br>
        Sabiman: sabiman@test.com / sabi123 [Activated]<br>
        Sabiman3: sabiman3@test.com / sabi123 [Not Activated - Test Zero Risk!]</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
