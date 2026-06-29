import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import io
import sqlite3

# ==========================================
# 1. PAGE CONFIGURATION & FORCE SIDEBAR STYLE
# ==========================================
st.set_page_config(
    page_title="Work Chop - For Humanity, By Humanity",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force Sidebar Open via Custom CSS
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

# ==========================================
# 2. DATABASE SETUP (Local SQLite)
# ==========================================
conn = sqlite3.connect('workchop.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        user_type TEXT
    )
''')
conn.commit()

# ==========================================
# 3. LANGUAGE DICTIONARIES
# ==========================================
LANGUAGES = {
   "English": {
       "welcome": "Welcome Back", "login": "Login", "join": "Join Free", "email": "Email",
       "password": "Password", "full_name": "Full Name", "phone": "Phone", "nin": "NIN (11 digits)",
       "send_otp": "Send OTP", "enter_otp": "Enter OTP", "register_sabiman": "Register as Sabiman",
       "register_client": "Register as Client", "i_be": "I be:", "logout": "Logout", "hello": "Hello",
       "role": "Role", "rating": "Rating", "home": "Home", "about": "About Us", "gallery": "Gallery",
       "contact": "Contact Us", "help": "Help Center", "language": "Choose Your Language"
    },
    "Hausa": {
       "welcome": "Barka da Zuwa", "login": "Shiga", "join": "Yi Rajista Kyauta", "email": "Imel",
       "password": "Kalmar Sirri", "full_name": "Cikakken Suna", "phone": "Lambar Wayar",
       "nin": "NIN (Lambobi 11)", "send_otp": "Aika OTP", "enter_otp": "Shigar da OTP",
       "register_sabiman": "Yi Rajista a matsayin Sabiman", "register_client": "Yi Rajista a matsayin Client",
       "i_be": "Ni ne:", "logout": "Fita", "hello": "Sannu", "role": "Matsayi", "rating": "Kimantawa",
       "home": "Gida", "about": "Game da Mu", "gallery": "Hotuna", "contact": "Tuntube Mu",
       "help": "Cibiyar Taimako", "language": "Zaɓi Harshenka"
    },
    "Igbo": {
       "welcome": "Nnọọ", "login": "Banye", "join": "Debanye aha n'efu", "email": "Email",
       "password": "Okwuntughe", "full_name": "Aha zuru ezu", "phone": "Nọmba ekwentị",
       "nin": "NIN (Ọnụọgụ 11)", "send_otp": "Zipu OTP", "enter_otp": "Tinye OTP",
       "register_sabiman": "Debanye aha dịka Sabiman", "register_client": "Debanye aha dịka Client",
       "i_be": "Abụ m:", "logout": "Pụọ", "hello": "Ndewo", "role": "Ọrụ", "rating": "Ntụle",
       "home": "Ụlọ", "about": "Gbasara Anyị", "gallery": "Foto", "contact": "Kpọtụrụ Anyị",
       "help": "Ebe Enyemaka", "language": "Họrọ Asụsụ Gị"
    },
   "Yoruba": {
       "welcome": "Kaabo", "login": "Wọle", "join": "Forukọsilẹ Ọfẹ", "email": "Imeeli",
       "password": "Ọrọigbaniwọle", "full_name": "Orukọ Kikun", "phone": "Nọmba Foonu",
       "nin": "NIN (Nọmba 11)", "send_otp": "Firanṣẹ OTP", "enter_otp": "Tẹ OTP sii",
       "register_sabiman": "Forukọsilẹ bi Sabiman", "register_client": "Forukọsilẹ bi Client",
       "i_be": "Mo jẹ:", "logout": "Jade", "hello": "Bawo", "role": "Ipa", "rating": "Iwọn",
       "home": "Ile", "about": "Nipa Wa", "gallery": "Awọn Aworan", "contact": "Kan si Wa",
       "help": "Ile-iṣẹ Iranlọwọ", "language": "Yan Ede Rẹ"
    }
}

# ==========================================
# 4. SESSION STATE INITIALIZATION
# ==========================================
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'otp_store' not in st.session_state:
    st.session_state.otp_store = {}
if 'traffic_log' not in st.session_state:
    st.session_state.traffic_log = []
if 'last_auto_release_check' not in st.session_state:
    st.session_state.last_auto_release_check = datetime.now()

if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'nin': '12345678901', 'phone': '08000000000', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'bio': 'Work Chop Founder & CEO', 'profile_pic': None, 'portfolio': [], 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'nin': '23456789012', 'phone': '08011111111', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.8, 'jobs_posted': 5, 'bio': 'Business owner in Abuja. Love fast service!', 'profile_pic': None, 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client2@test.com': {'password': 'client123', 'role': 'client', 'name': 'Fatima Client', 'nin': '56789012345', 'phone': '08044444444', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_posted': 0, 'bio': 'New client ready to test', 'profile_pic': None, 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'nin': '34567890123', 'phone': '08022222222', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_done': 47, 'bio': '10 years plumbing experience.', 'skills': ['Plumbing', 'Electrical'], 'rates': {'hourly': 3000}, 'available': True, 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'nin': '45678901234', 'phone': '08033333333', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 62, 'bio': 'Fashion designer.', 'skills': ['Tailoring'], 'rates': {'hourly': 5000}, 'available': True, 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True}
    }

if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix My Kitchen Sink', 'category': 'Plumbing', 'location': 'Wuse 2, Abuja', 'region': 'Abuja', 'amount': 15000, 'status': 'Work Done - Awaiting Confirmation', 'created': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), 'commission': 3000, 'sabiman_payout': 12000, 'client_satisfied': False, 'sabiman_satisfied': False, 'auto_release_at': (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")},
        {'id': 2, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'House Cleaning', 'category': 'Cleaning', 'location': 'Lekki, Lagos', 'region': 'Lagos', 'amount': 25000, 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), 'commission': 5000, 'sabiman_payout': 20000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")},
        {'id': 3, 'client': 'client@test.com', 'sabiman': 'sabiman2@test.com', 'title': 'Sew Agbada', 'category': 'Tailoring', 'location': 'Ikeja, Lagos', 'region': 'Lagos', 'amount': 50000, 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M"), 'commission': 10000, 'sabiman_payout': 40000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")},
        {'id': 4, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'AC Repair', 'category': 'Electrical', 'location': 'Gwarinpa, Abuja', 'region': 'Abuja', 'amount': 35000, 'status': 'Completed - Paid', 'created': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), 'commission': 7000, 'sabiman_payout': 28000, 'client_satisfied': True, 'sabiman_satisfied': True, 'paid_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
    ]

# ==========================================
# 5. CORE HELPER FUNCTIONS
# ==========================================
def t(key):
    return LANGUAGES[st.session_state.language].get(key, key)

def log_traffic(action):
    if st.session_state.logged_in:
        st.session_state.users[st.session_state.current_user]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.traffic_log.append({
            'user': st.session_state.current_user,
            'role': st.session_state.user_type,
            'action': action,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        })

def calculate_commission(amount):
    if amount >= 10000: return amount * 0.20
    elif amount >= 5000: return amount * 0.10
    else: return amount * 0.05

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
        return True
    return False

def process_auto_release():
    current_time = datetime.now()
    for job in st.session_state.jobs:
        if job['status'] == 'Work Done - Awaiting Confirmation' and job.get('auto_release_at'):
            release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
            if current_time >= release_time:
                job['client_satisfied'] = True
                job['sabiman_satisfied'] = True
                process_payment(job['id'])
                log_traffic(f"Auto-released payment for job {job['id']}")

if (datetime.now() - st.session_state.last_auto_release_check).seconds > 300:
    process_auto_release()
    st.session_state.last_auto_release_check = datetime.now()

# ==========================================
# 6. HEADER LOGO & GENERAL APPLICATION BRANDING
# ==========================================
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("## 🇳🇬")
with col2:
    st.markdown("# WORK CHOP")
    st.caption("Find Local Services in Nigeria")
st.markdown("---")

# ==========================================
# 7. TOP NAVIGATION BAR (CONDITIONAL)
# ==========================================
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
        if st.button("Login", use_container_width=True, key="top_login"): st.session_state.page = 'Login'; st.rerun()
else:
    if st.session_state.user_type == 'client':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="c_dash"): st.session_state.page = 'Dashboard'; st.rerun()
        with col2:
            if st.button("My Jobs", use_container_width=True, key="c_jobs"): st.session_state.page = 'My Jobs'; st.rerun()
        with col3:
            if st.button("Profile", use_container_width=True, key="c_profile"): st.session_state.page = 'Profile'; st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="c_logout"): 
                st.session_state.logged_in = False; st.session_state.user_type = None; st.session_state.page = 'Home'; st.rerun()
                
    elif st.session_state.user_type == 'admin':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="a_dash"): st.session_state.page = 'Dashboard'; st.rerun()
        with col2:
            if st.button("Manage Users", use_container_width=True, key="a_users"): st.session_state.page = 'Manage Users'; st.rerun()
        with col3:
            if st.button("Reports & Visualizations", use_container_width=True, key="a_reports"): st.session_state.page = 'Reports'; st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="a_logout"): 
                st.session_state.logged_in = False; st.session_state.user_type = None; st.session_state.page = 'Home'; st.rerun()

    elif st.session_state.user_type == 'sabiman':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="s_dash"): st.session_state.page = 'Dashboard'; st.rerun()
        with col2:
            if st.button("Find Jobs", use_container_width=True, key="s_jobs"): st.session_state.page = 'Find Jobs'; st.rerun()
        with col3:
            if st.button("My Gigs", use_container_width=True, key="s_gigs"): st.session_state.page = 'My Gigs'; st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="s_logout"): 
                st.session_state.logged_in = False; st.session_state.user_type = None; st.session_state.page = 'Home'; st.rerun()

# ==========================================
# 8. PUBLIC AND USER MAIN BODY CONTENT
# ==========================================
if st.session_state.page == 'Home':
    st.markdown("""
     <div style='text-align: center; padding: 2rem 0;'>
         <h1 style='font-family: Space Grotesk; font-size: 3.5rem; color: #14532D; margin-bottom: 0;'>WORK CHOP</h1>
         <h2 style='font-family: IBM Plex Mono; font-size: 1.2rem; color: #4A453E; letter-spacing: 2px; margin-top: 0.5rem;'>FOR HUMANITY, BY HUMANITY</h2>
         <p style='font-size: 1.1rem; color: #d1d5db; margin-top: 1.5rem;'>
             <strong>I tanda like rock no shaking</strong> - Connecting 26M+ Nigerian skilled workers with dignified jobs
         </p>
     </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.markdown("#### **33.3% Unemployment**\n23 million Nigerians dey jobless. But we get skilled hands everywhere.")
    c2.markdown("#### **Zero Risk Activation**\nSabimen join FREE with NIN. No payment until you don earn.")
    c3.markdown("#### **Escrow Protected**\nClient money dey safe. Sabiman get paid 24hrs after job completion.")

elif st.session_state.page == 'About':
    st.markdown("# **About Work Chop**")
    st.markdown("### *The Story Behind Nigeria's Labor Revolution*")
    st.write("Nigeria no get unemployment problem - we get connection problem. Work Chop breaks the barrier.")

elif st.session_state.page == 'Gallery':
    st.markdown("# **Work Chop Gallery**")
    st.info("📸 Gallery metrics coming soon")

elif st.session_state.page == 'Contact':
    st.markdown("# **Contact Work Chop**")
    st.write("📍 15 Awolowo Road, Ikoyi, Lagos | 📧 support@workchop.ng")

elif st.session_state.page == 'Dashboard':
    st.title(f"{str(st.session_state.user_type).title()} Dashboard")
    st.success("Welcome back to your dashboard workspace.")
    
    # Paystack Test Gateway simulation inside Client Panel
    if st.session_state.user_type == "client":
        st.markdown("### 💰 Fund Wallet")
        balance = st.session_state.get('wallet_balance', 0)
        st.metric("Wallet Balance", f"₦{balance:,}")

# ==========================================
# 9. VISUALIZATION AND PLOTLY CHARTS (REPORTS PAGE)
# ==========================================
elif st.session_state.page == 'Reports':
    st.title("📈 System Analytics & Visualizations")
    st.write("Real-time system breakdown metrics for platform transactions.")
    
    # Parsing active layout logs into Plotly charts
    df_jobs = pd.DataFrame(st.session_state.jobs)
    
    if not df_jobs.empty:
        col_charts1, col_charts2 = st.columns(2)
        
        with col_charts1:
            st.subheader("Transaction Volume By Industry Segment")
            fig1 = px.bar(df_jobs, x="category", y="amount", color="status", title="Job Values Broken Down by Skill Set Category")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_charts2:
            st.subheader("Regional Platform Escrow Distributions")
            fig2 = px.pie(df_jobs, values="amount", names="region", title="Regional Income Generation Shares", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No active structural transaction data found inside local registers.")

# ==========================================
# 10. SIDEBAR RENDERING EXECUTION
# ==========================================
with st.sidebar:
    st.markdown(f"### 🌍 {t('language')}")
    lang = st.selectbox("", ["English", "Hausa", "Igbo", "Yoruba"],
                        index=["English", "Hausa", "Igbo", "Yoruba"].index(st.session_state.language),
                        key="sidebar_lang_select")
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()

    st.markdown("---")
    st.markdown("# 🇳🇬 WORK CHOP")
    st.markdown("**I tanda like rock no shaking**")
    st.markdown("---")

    if not st.session_state.logged_in:
        choice = st.radio(f"**{t('hello')}:**", [t("login"), t("join")], key="sidebar_auth_choice")
        if choice == t("login"):
            st.subheader(t("welcome"))
            email = st.text_input(f"**{t('email')}**", key="sidebar_login_email")
            password = st.text_input(f"**{t('password')}**", type="password", key="sidebar_login_pass")
            if st.button(t("login"), type="primary", use_container_width=True, key="sidebar_login_btn"):
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.session_state.user_type = st.session_state.users[email]['role']
                    log_traffic("Login")
                    st.session_state.page = 'Dashboard'
                    st.rerun()
                else:
                    st.error("Wrong credentials")
    else:
        st.write(f"Logged in as: **{st.session_state.current_user}**")
        st.write(f"Role Group: `{st.session_state.user_type}`")

# Global UI Custom Finishes
st.markdown("""
<style>
.stApp { background: #0f0f0f; font-family: 'Outfit', sans-serif; }
header[data-testid="stHeader"] { display: none; }
h1, h2, h3, h4 { color: white !important; font-weight: 700; }
p, label, .stMarkdown { color: #d1d5db !important; }
</style>
""", unsafe_allow_html=True)
