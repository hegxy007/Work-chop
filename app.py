import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_carousel import carousel
import io

st.set_page_config(
    page_title="Work Chop - For Humanity, By Humanity",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LANGUAGE DICTIONARY
LANGUAGES = {
    "English": {
        "welcome": "Welcome Back", "login": "Login", "join": "Join Free", "email": "Email",
        "password": "Password", "full_name": "Full Name", "phone": "Phone", "nin": "NIN (11 digits)",
        "send_otp": "Send OTP", "enter_otp": "Enter OTP", "register_sabiman": "Register as Sabiman",
        "register_client": "Register as Client", "i_be": "I be:", "logout": "Logout", "hello": "Hello",
        "role": "Role", "rating": "Rating", "home": "Home", "about": "About Us", "gallery": "Gallery",
        "contact": "Contact Us", "help": "Help Center", "language": "Choose Your Language",
        "who_we_are": "Who We Are", "testimony": "Testimonies", "q_and_a": "Q & A"
    },
    "Hausa": {
        "welcome": "Barka da Zuwa", "login": "Shiga", "join": "Yi Rajista Kyauta", "email": "Imel",
        "password": "Kalmar Sirri", "full_name": "Cikakken Suna", "phone": "Lambar Wayar",
        "nin": "NIN (Lambobi 11)", "send_otp": "Aika OTP", "enter_otp": "Shigar da OTP",
        "register_sabiman": "Yi Rajista a matsayin Sabiman", "register_client": "Yi Rajista a matsayin Client",
        "i_be": "Ni ne:", "logout": "Fita", "hello": "Sannu", "role": "Matsayi", "rating": "Kimantawa",
        "home": "Gida", "about": "Game da Mu", "gallery": "Hotuna", "contact": "Tuntube Mu",
        "help": "Cibiyar Taimako", "language": "Zaɓi Harshenka", "who_we_are": "Wane ne Mu",
        "testimony": "Shaidu", "q_and_a": "Tambaya da Amsa"
    },
    "Igbo": {
        "welcome": "Nnọọ", "login": "Banye", "join": "Debanye aha n'efu", "email": "Email",
        "password": "Okwuntughe", "full_name": "Aha zuru ezu", "phone": "Nọmba ekwentị",
        "nin": "NIN (Ọnụọgụ 11)", "send_otp": "Zipu OTP", "enter_otp": "Tinye OTP",
        "register_sabiman": "Debanye aha dịka Sabiman", "register_client": "Debanye aha dịka Client",
        "i_be": "Abụ m:", "logout": "Pụọ", "hello": "Ndewo", "role": "Ọrụ", "rating": "Ntụle",
        "home": "Ụlọ", "about": "Gbasara Anyị", "gallery": "Foto", "contact": "Kpọtụrụ Anyị",
        "help": "Ebe Enyemaka", "language": "Họrọ Asụsụ Gị", "who_we_are": "Ndị Anyị Bụ",
        "testimony": "Akaebe", "q_and_a": "Ajụjụ na Azịza"
    },
    "Yoruba": {
        "welcome": "Kaabo", "login": "Wọle", "join": "Forukọsilẹ Ọfẹ", "email": "Imeeli",
        "password": "Ọrọigbaniwọle", "full_name": "Orukọ Kikun", "phone": "Nọmba Foonu",
        "nin": "NIN (Nọmba 11)", "send_otp": "Firanṣẹ OTP", "enter_otp": "Tẹ OTP sii",
        "register_sabiman": "Forukọsilẹ bi Sabiman", "register_client": "Forukọsilẹ bi Client",
        "i_be": "Mo jẹ:", "logout": "Jade", "hello": "Bawo", "role": "Ipa", "rating": "Iwọn",
        "home": "Ile", "about": "Nipa Wa", "gallery": "Awọn Aworan", "contact": "Kan si Wa",
        "help": "Ile-iṣẹ Iranlọwọ", "language": "Yan Ede Rẹ", "who_we_are": "Tani Wa",
        "testimony": "Ẹri", "q_and_a": "Ibeere ati Idahun"
    }
}

# SESSION STATE
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'about_tab' not in st.session_state:
    st.session_state.about_tab = 'Who We Are'
if 'help_tab' not in st.session_state:
    st.session_state.help_tab = 'Q & A'
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
if 'last_auto_release_check' not in st.session_state:
    st.session_state.last_auto_release_check = datetime.now()
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'nin': '12345678901', 'phone': '08000000000', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'bio': 'Work Chop Founder & CEO', 'profile_pic': None, 'portfolio': [], 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'nin': '23456789012', 'phone': '08011111111', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.8, 'jobs_posted': 5, 'bio': 'Business owner in Abuja. Love fast service!', 'profile_pic': None, 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client2@test.com': {'password': 'client123', 'role': 'client', 'name': 'Fatima Client', 'nin': '56789012345', 'phone': '08044444444', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_posted': 0, 'bio': 'New client ready to test', 'profile_pic': None, 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'nin': '34567890123', 'phone': '08022222222', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_done': 47, 'bio': '10 years plumbing experience. I fix am well. No story!', 'skills': ['Plumbing', 'Electrical', 'AC Repair'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 3000, 'daily': 15000, 'weekly': 80000, 'monthly': 300000}, 'available': True, 'work_categories': ['Plumbing', 'Electrical'], 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'nin': '45678901234', 'phone': '08033333333', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 62, 'bio': 'Fashion designer. I sew cloth wey go make you shine!', 'skills': ['Tailoring', 'Fashion Design', 'Embroidery'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 5000, 'daily': 25000, 'weekly': 120000, 'monthly': 400000}, 'available': True, 'work_categories': ['Tailoring', 'Fashion'], 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'nin': '67890123456', 'phone': '08055555555', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.7, 'jobs_done': 0, 'bio': 'New Sabiman ready to work. Electrical specialist!', 'skills': ['Electrical', 'Solar Installation'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 4000, 'daily': 20000, 'weekly': 100000, 'monthly': 350000}, 'available': True, 'work_categories': ['Electrical', 'Solar'], 'region': 'Port Harcourt', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
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
    return str(random.randint(100000, 999999))

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

# CSS - COLORFUL LANDING PAGE STYLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap');
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
    background-attachment: fixed;
    font-family: 'Outfit', sans-serif;
}
header[data-testid="stHeader"] { display: none; }
.main.block-container {
    padding-top: 1rem;
    background: rgba(15, 15, 15, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    margin: 1rem;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #008751 0%, #059669 100%);
    padding-top: 1rem;
    min-width: 300px!important;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: white!important; }
section[data-testid="stSidebar"].stButton>button { background: white!important; color: #008751!important; font-weight: 700!important; border: 2px solid white!important; }
h1, h2, h3, h4 { color: white!important; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
p, label,.stMarkdown { color: #f1f5f9!important; }
div[data-testid="stDataFrame"] { background: #1a1a1a; }
.stButton>button {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)!important;
    color: white!important;
    font-weight: 700!important;
    border-radius: 50px!important;
    padding: 0.75rem 2rem!important;
    border: none!important;
    box-shadow: 0 10px 25px rgba(240, 147, 251, 0.4);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(240, 147, 251, 0.6);
}
.highlight-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    border: 2px solid #60a5fa;
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
}
.available-card {
    background: rgba(26, 26, 26, 0.9);
    border: 2px solid #10b981;
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.available-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
}
.active-user {
    background: rgba(26, 26, 26, 0.9);
    border-left: 4px solid #10b981;
    padding: 1rem;
    border-radius: 12px;
    margin: 0.5rem 0;
}
.message-box {
    background: rgba(31, 41, 55, 0.9);
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    border: 1px solid #374151;
    backdrop-filter: blur(10px);
}
.hero-section {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 50%, rgba(240, 147, 251, 0.9) 100%);
    padding: 4rem 2rem;
    border-radius: 30px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(15px);
}
.company-logo {
    background: rgba(26, 26, 26, 0.9);
    padding: 1rem;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #374151;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
}
.disclaimer {
    background: rgba(31, 41, 55, 0.95);
    border: 2px solid #f59e0b;
    padding: 1.5rem;
    border-radius: 20px;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(245, 158, 11, 0.2);
}
</style>
""", unsafe_allow_html=True)

# ADMIN DASHBOARD
def admin_dashboard():
    st.markdown("""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;"><div><h1 style="margin: 0; color: white;">Work Chop Admin Dashboard</h1><p style="color: #9ca3af; margin: 0;">Real-Time Business Intelligence</p></div></div>""", unsafe_allow_html=True)

    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']
    total_revenue = sum([j['commission'] for j in paid_jobs])
    total_client_paid = sum([j['amount'] for j in paid_jobs])
    total_sabiman_paid = sum([j['sabiman_payout'] for j in paid_jobs])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; border: 1px solid #10b981; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Total Revenue</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_revenue:,}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">↑ Commission</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Client Payments</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_client_paid:,}</h1><p style="color: #3b82f6; font-size: 0.9rem; margin: 0;">Total inflow</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Sabiman Payouts</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_sabiman_paid:,}</h1><p style="color: #ef4444; font-size: 0.9rem; margin: 0;">Paid to workers</p></div>""", unsafe_allow_html=True)
    with col4:
        active_sabimen = len([u for u in st.session_state.users.values() if u['role'] == 'sabiman' and u.get('available', False)])
        st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Active Sabimen</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{active_sabimen}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">Online now</p></div>""", unsafe_allow_html=True)

# SIDEBAR
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🌍 {t('language')}")
        lang = st.selectbox("", ["English", "Hausa", "Igbo", "Yoruba"],
                           index=["English", "Hausa", "Igbo", "Yoruba"].index(st.session_state.language),
                           key="sidebar_lang_select")
        if lang!= st.session_state.language:
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
                        log_traffic("Login")
                        st.rerun()
                    else:
                        st.error("Wrong credentials")
            else:
                st.subheader(t("join"))
                role = st.selectbox(f"**{t('i_be')}**", ["Client", "Sabiman/Worker"], key="sidebar_join_role")
                name = st.text_input(f"**{t('full_name')}**", key="sidebar_join_name")
                new_email = st.text_input(f"**{t('email')}**", key="sidebar_join_email")
                new_pass = st.text_input(f"**{t('password')}**", type="password", key="sidebar_join_pass")
                phone = st.text_input(f"**{t('phone')}**", placeholder="08012345678", key="sidebar_join_phone")
                region = st.selectbox("Region", ["Abuja", "Lagos", "Port Harcourt", "Kano", "Ibadan", "Other"], key="sidebar_join_region")

                if role == "Sabiman/Worker":
                    st.markdown(f"**🔐 {t('nin')}**")
                    nin = st.text_input(f"**{t('nin')}**", max_chars=11, key="sidebar_join_nin")
                    if st.button(t("send_otp"), disabled=not phone, key="sidebar_send_otp_btn"):
                        if len(phone) == 11:
                            otp = generate_otp()
                            st.session_state.otp_store[phone] = otp
                            st.success(f"OTP: **{otp}**")
                        else:
                            st.error("Valid 11-digit phone")
                    otp_input = st.text_input(f"**{t('enter_otp')}**", max_chars=6, key="sidebar_otp_input")
                    if st.button(t("register_sabiman"), type="primary", use_container_width=True, key="sidebar_reg_sabi_btn"):
                        if new_email in st.session_state.users:
                            st.error("Email exists")
                        elif not (name and new_email and new_pass and phone and nin and otp_input):
                            st.error("Fill all fields")
                        elif len(nin)!= 11:
                            st.error("NIN must be 11 digits")
                        elif st.session_state.otp_store.get(phone)!= otp_input:
                            st.error("Wrong OTP")
                        else:
                            st.session_state.users[new_email] = {'password': new_pass, 'role': 'sabiman', 'name': name, 'phone': phone, 'nin': nin, 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'bio': 'New Sabiman', 'skills': [], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 0, 'daily': 0, 'weekly': 0, 'monthly': 0}, 'available': False, 'work_categories': [], 'region': region, 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'is_activated': False, 'activation_deposit': 0, 'jobs_completed_for_activation': 0, 'activation_bonus_paid': False}
                            st.success("✅ Verified! Login now. No upfront payment needed!")
                            st.balloons()
                else:
                    if st.button(t("register_client"), type="primary", use_container_width=True, key="sidebar_reg_client_btn"):
                        if new_email in st.session_state.users:
                            st.error("Email exists")
                        elif name and new_email and new_pass and phone:
                            st.session_state.users[new_email] = {'password': new_pass, 'role': 'client', 'name': name, 'phone': phone, 'nin': '', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_posted': 0, 'bio': 'New Client', 'profile_pic': None, 'region': region, 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")}
                            st.success("✅ Registered! Login now")
                        else:
                            st.error("Fill all fields")
        else:
            user = st.session_state.users[st.session_state.current_user]
            st.success(f"{t('hello')}, {user['name']}")
            st.write(f"**{t('role')}:** {user['role'].title()}")

            if user['role'] == 'admin':
                st.markdown("---")
                st.markdown("### 🔐 Admin Tools")
                if st.button("📊 Dashboard", use_container_width=True, key="admin_dash_btn"):
                    st.session_state.admin_page = 'Dashboard'
                    st.rerun()

            st.markdown("---")
            if st.button(t("logout"), use_container_width=True, key="sidebar_logout_btn"):
                log_traffic("Logout")
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.page = 'Home'
                st.rerun()

# HOME PAGE
def render_home_page():
    st.markdown("""
    <div class="hero-section">
        <h1 style="color: white; font-size: 3.5rem; margin: 0; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);">🇳🇬 WORK CHOP</h1>
        <h2 style="color: #f1f5f9; margin: 1rem 0; font-weight: 400;">For Humanity, By Humanity</h2>
        <p style="color: white; font-size: 1.2rem; max-width: 800px; margin: 0 auto;            line-height: 1.8;">
            <b>I tanda like rock no shaking</b> - In Nigeria today, over <b>26 million skilled and unskilled laborers</b> hustle daily without protection.
            More than <b>2.1 million undergraduates</b> graduate yearly with no jobs waiting. Work Chop bridges this gap.
            We connect honest hands with honest pay. No yahoo boy, no scam - just real work, real money, real dignity.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.expander(f"🏠 {t('home')}", expanded=False):
            if st.button("Go Home", use_container_width=True, key="nav_home"):
                st.session_state.page = 'Home'
                st.rerun()

    with col2:
        with st.expander(f"ℹ️ {t('about')}", expanded=False):
            if st.button(t('who_we_are'), use_container_width=True, key="nav_who"):
                st.session_state.about_tab = 'Who We Are'
                st.rerun()
            if st.button(f"👥 {t('testimony')}", use_container_width=True, key="nav_testimony"):
                st.session_state.about_tab = 'Testimonies'
                st.rerun()
            if st.button(f"📞 {t('contact')}", use_container_width=True, key="nav_contact"):
                st.session_state.about_tab = 'Contact Us'
                st.rerun()

    with col3:
        with st.expander(f"🆘 {t('help')}", expanded=False):
            if st.button(f"❓ {t('q_and_a')}", use_container_width=True, key="nav_qa"):
                st.session_state.help_tab = 'Q & A'
                st.rerun()

    with col4:
        with st.expander("🖼️ Gallery", expanded=False):
            st.info("Coming soon - Portfolio showcase")

    st.markdown("---")

    if st.session_state.about_tab == 'Who We Are':
        st.markdown("### 🌍 Who We Are")
        st.markdown("""
        <div class="highlight-box">
            <h4 style="color: white;">Our Mission: Dignity Through Work</h4>
            <p style="color: #d1d5db;">
                Work Chop was born from the streets of Nigeria. We saw electricians sleeping under bridges,
                tailors trekking 10km to find customers, and graduates selling recharge cards because no jobs dey.
            </p>
            <p style="color: #d1d5db;">
                <b>The Problem:</b> 26M+ skilled/unskilled workers + 2.1M new graduates yearly = massive unemployment.
                Yahoo boys dey chop, honest people dey suffer.
            </p>
            <p style="color: #10b981;">
                <b>We tanda like rock no shaking</b> - No upfront fees, no scam, just work chop.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.about_tab == 'Testimonies':
        st.markdown("### 👥 Client & Sabiman Testimonies")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="available-card">
                <h4 style="color: white;">⭐ Musa Ibrahim - Client</h4>
                <p style="color: #9ca3af;">Abuja</p>
                <p style="color: #d1d5db;">
                    "Before Work Chop, I dey call 10 plumbers before one go show. Now I post job,
                    Tunde accept am in 5 minutes. He fix my sink, I confirm, money go straight. No story!"
                </p>
                <p style="color: #10b981;">Rating: 4.8 ⭐</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="available-card">
                <h4 style="color: white;">⭐ Tunde Plumber - Sabiman</h4>
                <p style="color: #9ca3af;">Abuja</p>
                <p style="color: #d1d5db;">
                    "I join Work Chop free. First job pay ₦15,000 - dem hold ₦500 activate me.
                    After 5 jobs, I collect my ₦500 back as bonus! Now I dey chop ₦200k monthly. God bless Work Chop!"
                </p>
                <p style="color: #10b981;">Rating: 4.9 ⭐ | 47 Jobs Done</p>
            </div>
            """, unsafe_allow_html=True)

    elif st.session_state.about_tab == 'Contact Us':
        st.markdown("### 📞 Contact Us")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="message-box">
                <h4 style="color: white;">📍 Headquarters</h4>
                <p style="color: #d1d5db;">Plot 123, Work Chop Street<br>Wuse 2, Abuja, Nigeria</p>
                <h4 style="color: white; margin-top: 1rem;">📧 Email</h4>
                <p style="color: #3b82f6;">support@workchop.ng</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="message-box">
                <h4 style="color: white;">📱 Phone / WhatsApp</h4>
                <p style="color: #10b981;">+234 800 WORK CHOP</p>
                <h4 style="color: white; margin-top: 1rem;">🕐 Support Hours</h4>
                <p style="color: #d1d5db;">Monday - Saturday: 8AM - 8PM</p>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.help_tab == 'Q & A':
        st.markdown("### ❓ Questions & Answers")
        with st.expander("Q1: Is Work Chop free to join?", expanded=False):
            st.markdown("**A:** YES! 100% FREE to join for both Clients and Sabimen. No registration fee. Sabimen only pay ₦500 activation from their FIRST earning, not upfront.")
        with st.expander("Q2: How does Zero Risk Activation work?", expanded=False):
            st.markdown("**A:** New Sabimen join FREE. When you earn your first ₦500+, we hold it as deposit to verify you're real. Complete 5 jobs successfully, we return ₦500 as Loyalty Bonus. No upfront payment needed!")
        with st.expander("Q3: What if client refuses to confirm my work?", expanded=False):
            st.markdown("**A:** 24hr Auto-Release protects you. After you mark 'Work Done', if client no confirm in 24 hours, payment releases automatically. No client fit hold your money.")

    st.markdown("---")
    st.markdown("### 🏢 Trusted By Nigerian Companies")
    cols = st.columns(6)
    companies = ["🏗️ Julius Berger", "⚡ EKEDC", "🔧 Daewoo E&C", "👗 Ruff 'n' Tumble", "🏠 Dangote Cement", "🚰 Water Board"]
    for idx, company in enumerate(companies):
        with cols[idx]:
            st.markdown(f"""<div class="company-logo"><p style="color: white; font-size: 0.85rem; margin: 0;">{company}</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="text-align: center; padding: 2rem;"><h2 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">Ready to Chop Work?</h2><p style="color: #f1f5f9;">Join 26M+ Nigerians earning with dignity</p></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Join Free Now", type="primary", use_container_width=True, key="cta_join"):
            st.info("👆 Use the sidebar to register!")

# DASHBOARD PAGE WITH DISCLAIMERS
def dashboard_page():
    user = st.session_state.users[st.session_state.current_user]

    if user['role'] == 'sabiman':
        log_traffic("View Dashboard")
        st.markdown("""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;"><div><h1 style="margin: 0; color: white;">Sabiman Dashboard</h1><p style="color: #9ca3af; margin: 0;">Your Earnings Overview</p></div></div>""", unsafe_allow_html=True)

        st.markdown("### 🔐 Account Activation Status")
        if not user.get('is_activated', False):
            st.markdown("""<div class="highlight-box"><h4 style="color: white; margin: 0;">⚠️ Account Not Activated</h4><p style="color: #f59e0b;">Your first ₦500 earning will activate your account automatically. No upfront payment needed! Join FREE, earn first!</p></div>""", unsafe_allow_html=True)
        elif not user.get('activation_bonus_paid', False):
            remaining = 5 - user.get('jobs_completed_for_activation', 0)
            progress = user.get('jobs_completed_for_activation', 0) / 5
            st.markdown(f"""<div class="available-card"><h4 style="color: white; margin: 0;">🎁 Loyalty Bonus Progress</h4><p style="color: #10b981;">Complete {remaining} more jobs to unlock ₦500 Loyalty Bonus!</p></div>""", unsafe_allow_html=True)
            st.progress(progress)
        else:
            st.markdown("""<div class="available-card"><h4 style="color: white; margin: 0;">✅ Fully Activated + Bonus Received</h4><p style="color: #10b981;">Your account is verified and you've received your ₦500 loyalty bonus! Keep chopping!</p></div>""", unsafe_allow_html=True)

        st.markdown("---")

        my_jobs = [j for j in st.session_state.jobs if j.get('sabiman') == st.session_state.current_user]
        paid_jobs = [j for j in my_jobs if j['status'] == 'Completed - Paid']
        pending_jobs = [j for j in my_jobs if j['status'] == 'Work Done - Awaiting Confirmation']
        new_requests = [j for j in my_jobs if j['status'] == 'Requested - Awaiting Sabiman']

        total_earned = sum([j['sabiman_payout'] for j in paid_jobs])
        total_pending = sum([j['amount'] - calculate_commission(j['amount']) for j in pending_jobs])
        jobs_done = len(paid_jobs)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; border: 1px solid #10b981; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Total Paid</p><h1 style="color: #10b981; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_earned:,}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">✓ In your account</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; border: 1px solid #f59e0b; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Pending Payment</p><h1 style="color: #f59e0b; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_pending:,}</h1><p style="color: #f59e0b; font-size: 0.9rem; margin: 0;">⏳ Awaiting client</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Jobs Completed</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{jobs_done}</h1><p style="color: #3b82f6; font-size: 0.9rem; margin: 0;">All time</p></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div style="background: rgba(26, 26, 26, 0.9); padding: 2rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">New Requests</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{len(new_requests)}</h1><p style="color: #f59e0b; font-size: 0.9rem; margin: 0;">Awaiting you</p></div>""", unsafe_allow_html=True)

        # NEW JOB REQUESTS
        if new_requests:
            st.markdown("### 🔔 New Job Requests")
            for job in new_requests:
                client_name = st.session_state.users[job['client']]['name']
                st.markdown(f"""<div class="available-card"><h3 style="color: white; margin: 0;">{job['title']}</h3><p style="color: #d1d5db; margin: 0.5rem 0;">From: <b>{client_name}</b> | Location: {job['location']} | Budget: <b style="color: #10b981;">₦{job['amount']:,}</b></p><p style="color: #9ca3af;">{job['desc']}</p></div>""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Accept Job", key=f"accept_{job['id']}", use_container_width=True):
                        job['status'] = 'Accepted - In Progress'
                        log_traffic(f"Accepted job {job['id']}")
                        st.success("Job accepted! Start work now")
                        st.rerun()
                with col2:
                    if st.button(f"❌ Decline", key=f"decline_{job['id']}", use_container_width=True):
                        st.session_state.jobs.remove(job)
                        st.info("Job declined")
                        st.rerun()

        # JOBS IN PROGRESS
        in_progress = [j for j in my_jobs if j['status'] == 'Accepted - In Progress']
        if in_progress:
            st.markdown("### 🔨 Jobs In Progress")
            for job in in_progress:
                client_name = st.session_state.users[job['client']]['name']
                st.markdown(f"""<div class="highlight-box"><h3 style="color: white; margin: 0;">{job['title']}</h3><p style="color: #d1d5db; margin: 0.5rem 0;">Client: <b>{client_name}</b> | Amount: <b style="color: #f59e0b;">₦{job['amount']:,}</b></p></div>""", unsafe_allow_html=True)
                if st.button(f"✅ Mark as Work Done", key=f"done_{job['id']}", use_container_width=True):
                    job['status'] = 'Work Done - Awaiting Confirmation'
                    job['sabiman_satisfied'] = True
                    job['auto_release_at'] = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
                    job['reminder_sent'] = False
                    log_traffic(f"Marked job {job['id']} as done - 24hr timer started")
                    st.success("Client has been notified! Payment auto-releases in 24hrs if no dispute")
                    st.rerun()

        # AWAITING CONFIRMATION
        awaiting_jobs = [j for j in my_jobs if j['status'] == 'Work Done - Awaiting Confirmation']
        if awaiting_jobs:
            st.markdown("### ⏳ Jobs Awaiting Client Confirmation")
            for job in awaiting_jobs:
                client_name = st.session_state.users[job['client']]['name']
                time_left = ""
                if job.get('auto_release_at'):
                    release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
                    if release_time > datetime.now():
                        hours_left = int((release_time - datetime.now()).total_seconds() // 3600)
                        time_left = f"<p style='color: #f59e0b;'>⏰ Auto-release in {hours_left}hrs</p>"

                st.markdown(f"""<div class="highlight-box"><h3 style="color: white; margin: 0;">{job['title']}</h3><p style="color: #d1d5db; margin: 0.5rem 0;">Client: <b>{client_name}</b> | Amount: <b style="color: #f59e0b;">₦{job['amount']:,}</b></p><p style="color: #9ca3af;">Client Satisfied: {'✅' if job.get('client_satisfied') else '❌ Waiting'} | You Confirmed: ✅</p>{time_left}</div>""", unsafe_allow_html=True)

        # DISCLAIMER FOR SABIMAN
        st.markdown("""
        <div class="disclaimer">
            <h4 style="color: #f59e0b; margin: 0;">⚠️ Sabiman Disclaimer</h4>
            <p style="color: #d1d5db; font-size: 0.9rem; margin: 0.5rem 0;">
                Work Chop is a platform connecting you to clients. You are an independent contractor, not an employee of Work Chop.
                You are responsible for your own taxes, insurance, and quality of work. Work Chop holds payments in escrow for safety
                but is not liable for disputes beyond the 24hr auto-release period. Always verify job details before accepting.
                Complete 5 jobs successfully to unlock your ₦500 Loyalty Bonus. I tanda like rock no shaking.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif user['role'] == 'client':
        st.markdown("# 📊 Client Dashboard")
        st.markdown("### 🔍 Find Sabimen & Request Work")
        available_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}

        if available_sabimen:
            cols = st.columns(3)
            for idx, (email, sabiman) in enumerate(available_sabimen.items()):
                with cols[idx % 3]:
                    activation_status = "✅ Verified" if sabiman.get('is_activated') else "⏳ New"
                    st.markdown(f"""<div class="available-card"><h4 style="color: white; margin: 0;">{sabiman['name']} {activation_status}</h4><p style="color: #10b981; margin: 0.5rem 0;">⭐ {sabiman['rating']} | {sabiman['jobs_done']} jobs</p><p style="color: #9ca3af; font-size: 0.9rem;">{sabiman['bio'][:60]}...</p><p style="color: #d1d5db; font-size: 0.85rem;"><b>Skills:</b> {', '.join(sabiman.get('work_categories', [])[:2])}</p><p style="color: #f59e0b; font-size: 0.9rem;"><b>Daily:</b> ₦{sabiman['rates']['daily']:,}</p></div>""", unsafe_allow_html=True)

                    with st.expander(f"Request {sabiman['name']}"):
                        job_title = st.text_input("Job Title", key=f"req_title_{email}")
                        job_cat = st.selectbox("Category", sabiman.get('work_categories', ['General']), key=f"req_cat_{email}")
                        job_location = st.text_input("Location", key=f"req_loc_{email}")
                        job_amount = st.number_input("Budget (₦)", min_value=1000, value=sabiman['rates']['daily'], step=1000, key=f"req_amt_{email}")
                        job_desc = st.text_area("Description", key=f"req_desc_{email}")

                        if st.button(f"Send Request", key=f"req_btn_{email}", use_container_width=True):
                            new_job = {
                                'id': len(st.session_state.jobs) + 1,
                                'client': st.session_state.current_user,
                                'sabiman': email,
                                'title': job_title,
                                'category': job_cat,
                                'location': job_location,
                                'region': st.session_state.users[st.session_state.current_user].get('region', 'Unknown'),
                                'amount': job_amount,
                                'duration': 'One-time',
                                'desc': job_desc,
                                'status': 'Requested - Awaiting Sabiman',
                                'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'commission': 0,
                                'sabiman_payout': 0,
                                'client_satisfied': False,
                                'sabiman_satisfied': False,
                                'paid_at': None,
                                'job_type': 'client_request',
                                'auto_release_at': None, 'reminder_sent': False, 'disputed': False
                            }
                            st.session_state.jobs.append(new_job)
                            st.session_state.users[st.session_state.current_user]['jobs_posted'] += 1
                            log_traffic(f"Requested work from {sabiman['name']}")
                            st.success(f"✅ Request sent to {sabiman['name']}!")
                            st.rerun()
        else:
            st.info("No Sabimen available right now")

        # DISCLAIMER FOR CLIENT
        st.markdown("""
        <div class="disclaimer">
            <h4 style="color: #f59e0b; margin: 0;">⚠️ Client Disclaimer</h4>
            <p style="color: #d1d5db; font-size: 0.9rem; margin: 0.5rem 0;">
                Work Chop connects you to independent Sabimen. We verify NIN and hold payments in escrow for your protection.
                However, Work Chop is not liable for quality of work, damages, or injuries. Always inspect work before confirming.
                If unsatisfied, dispute within 24hrs or payment auto-releases to Sabiman. Commission fees apply: 5-20% based on job value.
                By using Work Chop, you agree to these terms. I tanda like rock no shaking.
            </p>
        </div>
        """, unsafe_allow_html=True)

# MAIN APP LOGIC
render_sidebar()

if st.session_state.logged_in:
    user = st.session_state.users[st.session_state.current_user]
    if user['role'] == 'admin':
        if st.session_state.admin_page == 'Dashboard':
            admin_dashboard()
    else:
        dashboard_page()
else:
    render_home_page()
