

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random 
from streamlit_carousel import carousel
import io
import gspread
import sqlite3  # Use SQLite first, forget gspread for now




# PAGE Config
st.set_page_config(
    page_title="Work Chop - For Humanity, By Humanity",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)  # FORCE SIDEBAR OPEN - no space before this line

# DATABASE - Use SQLite, no creds.json needed
conn = sqlite3.connect('workchop.db')
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
    # ========== 1. INIT STATE ==========

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
         # ========== 1. INIT STATE ==========
# SESSION STATE
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
        'admin@workchop.ng': {'password': 'admin123', 'role': 'admin', 'name': 'Admin', 'nin': '12345678901', 'phone': '08000000000', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'bio': 'Work Chop Founder & CEO', 'profile_pic': None, 'portfolio': [], 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client@test.com': {'password': 'client123', 'role': 'client', 'name': 'Musa Ibrahim', 'nin': '23456789012', 'phone': '08011111111', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.8, 'jobs_posted': 5, 'bio': 'Business owner in Abuja. Love fast service!', 'profile_pic': None, 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'client2@test.com': {'password': 'client123', 'role': 'client', 'name': 'Fatima Client', 'nin': '56789012345', 'phone': '08044444444', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_posted': 0, 'bio': 'New client ready to test', 'profile_pic': None, 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")},
        'sabiman@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Tunde Plumber', 'nin': '34567890123', 'phone': '08022222222', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.9, 'jobs_done': 47, 'bio': '10 years plumbing experience. I fix am well. No story!', 'skills': ['Plumbing', 'Electrical', 'AC Repair'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 3000, 'daily': 15000, 'weekly': 80000, 'monthly': 300000}, 'available': True, 'work_categories': ['Plumbing', 'Electrical'], 'region': 'Abuja', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            # WORK CHOP UPDATE: Zero Risk Activation fields - Already activated
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman2@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Aisha Tailor', 'nin': '45678901234', 'phone': '08033333333', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 62, 'bio': 'Fashion designer. I sew cloth wey go make you shine!', 'skills': ['Tailoring', 'Fashion Design', 'Embroidery'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 5000, 'daily': 25000, 'weekly': 120000, 'monthly': 400000}, 'available': True, 'work_categories': ['Tailoring', 'Fashion'], 'region': 'Lagos', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            # WORK CHOP UPDATE: Zero Risk Activation fields - Already activated
            'is_activated': True, 'activation_deposit': 500.00, 'jobs_completed_for_activation': 5, 'activation_bonus_paid': True},
        'sabiman3@test.com': {'password': 'sabi123', 'role': 'sabiman', 'name': 'Emeka Electrician', 'nin': '67890123456', 'phone': '08055555555', 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 4.7, 'jobs_done': 0, 'bio': 'New Sabiman ready to work. Electrical specialist!', 'skills': ['Electrical', 'Solar Installation'], 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 4000, 'daily': 20000, 'weekly': 100000, 'monthly': 350000}, 'available': True, 'work_categories': ['Electrical', 'Solar'], 'region': 'Port Harcourt', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            # WORK CHOP UPDATE: Zero Risk Activation fields - New sabiman starts unactivated
            'is_activated': False, 'activation_deposit': 0, 'jobs_completed_for_activation': 0, 'activation_bonus_paid': False},
    }
if 'jobs' not in st.session_state:
    st.session_state.jobs = [
        {'id': 1, 'client': 'client@test.com', 'sabiman': 'sabiman@test.com', 'title': 'Fix My Kitchen Sink', 'category': 'Plumbing', 'location': 'Wuse 2, Abuja', 'region': 'Abuja', 'amount': 15000, 'duration': 'One-time', 'desc': 'My sink dey leak water. Need urgent repair today.', 'status': 'Work Done - Awaiting Confirmation', 'created': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), 'commission': 0, 'sabiman_payout': 0, 'client_satisfied': False, 'sabiman_satisfied': False, 'paid_at': None, 'job_type': 'client_request',
         # WORK CHOP UPDATE: 24hr auto-release
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

# WORK CHOP UPDATE: Zero Risk Activation Logic
def process_payment(job_id):
    job = next((j for j in st.session_state.jobs if j['id'] == job_id), None)
    if job and job.get('client_satisfied') and job.get('sabiman_satisfied'):
        sabiman = st.session_state.users[job['sabiman']]
        commission = calculate_commission(job['amount'])
        activation_deposit = 0

        # Zero Risk Activation: First job sponsor
        if not sabiman.get('is_activated', False) and sabiman.get('activation_deposit', 0) == 0:
            activation_deposit = 500.00

        net_payout = job['amount'] - commission - activation_deposit

        # Update job
        job['commission'] = commission
        job['sabiman_payout'] = net_payout
        job['status'] = 'Completed - Paid'
        job['paid_at'] = datetime.now().strftime("%Y-%m-%d")

        # Update sabiman
        sabiman['jobs_done'] += 1

        # Handle activation deposit
        if activation_deposit > 0:
            sabiman['activation_deposit'] = activation_deposit
            sabiman['is_activated'] = True

        # Count job towards activation bonus
        if sabiman.get('is_activated') and not sabiman.get('activation_bonus_paid', False):
            sabiman['jobs_completed_for_activation'] = sabiman.get('jobs_completed_for_activation', 0) + 1

            # Check if eligible for ₦500 bonus refund
            if sabiman['jobs_completed_for_activation'] >= 5:
                sabiman['activation_bonus_paid'] = True
                # Add bonus to payout
                job['sabiman_payout'] += sabiman['activation_deposit']

        return True
    return False

# WORK CHOP UPDATE: 24hr Auto-Release
def process_auto_release():
    """Run this every hour via cron or Streamlit rerun"""
    current_time = datetime.now()
    for job in st.session_state.jobs:
        if (job['status'] == 'Work Done - Awaiting Confirmation'
            and not job.get('disputed', False)
            and job.get('auto_release_at')):

            release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
            if current_time >= release_time:
                # Auto-confirm client if no action
                if not job.get('client_satisfied'):
                    job['client_satisfied'] = True # Auto-confirm after 24hrs
                if not job.get('sabiman_satisfied'):
                    job['sabiman_satisfied'] = True

                process_payment(job['id'])
                log_traffic(f"Auto-released payment for job {job['id']}")

# WORK CHOP UPDATE: Run auto-release on every rerun (every 5 min)
if (datetime.now() - st.session_state.last_auto_release_check).seconds > 300:
    process_auto_release()
    st.session_state.last_auto_release_check = datetime.now()
    # TOP NAVIGATION BAR - PASTE THIS ON YOUR MAIN PAGE
# ========== INIT SESSION STATE ==========
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# ========== TOP NAVIGATION BAR - SHOW BASED ON LOGIN ==========
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
            st.session_state.page = 'Login'
            st.rerun()

else:
    # MODE 2: LOGGED IN NAV - Hide Home/About/Gallery
    if st.session_state.user_type == 'client':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="c_dash"):
                st.session_state.page = 'Dashboard'
                st.rerun()
        with col2:
            if st.button("My Jobs", use_container_width=True, key="c_jobs"):
                st.session_state.page = 'My Jobs'
                st.rerun()
        with col3:
            if st.button("Profile", use_container_width=True, key="c_profile"):
                st.session_state.page = 'Profile'
                st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="c_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.page = 'Home'
                st.rerun()
    
    elif st.session_state.user_type == 'admin':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="a_dash"):
                st.session_state.page = 'Dashboard'
                st.rerun()
        with col2:
            if st.button("Manage Users", use_container_width=True, key="a_users"):
                st.session_state.page = 'Manage Users'
                st.rerun()
        with col3:
            if st.button("Reports", use_container_width=True, key="a_reports"):
                st.session_state.page = 'Reports'
                st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="a_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.page = 'Home'
                st.rerun()
    
    # SABIMAN NAV - ADDED THIS TO FIX LINE 358 BUG
    elif st.session_state.user_type == 'sabiman':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Dashboard", use_container_width=True, key="s_dash"):
                st.session_state.page = 'Dashboard'
                st.rerun()
        with col2:
            if st.button("Find Jobs", use_container_width=True, key="s_jobs"):
                st.session_state.page = 'Find Jobs'
                st.rerun()
        with col3:
            if st.button("My Gigs", use_container_width=True, key="s_gigs"):
                st.session_state.page = 'My Gigs'
                st.rerun()
        with col4:
            if st.button("Logout", use_container_width=True, key="s_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.page = 'Home'
                st.rerun()

# ========== PAGE CONTENT WITH REDIRECT GUARDS ==========
if st.session_state.page == 'Home':
    if not st.session_state.logged_in:
        st.title("WORK CHOP - For Humanity, By Humanity")
        st.write("Public home page")
    else:
        st.session_state.page = 'Dashboard'
        st.rerun()

elif st.session_state.page == 'About':
    if not st.session_state.logged_in:
        st.title("About Us")
        st.write("Our story...")
    else:
        st.session_state.page = 'Dashboard'  # Block access after login
        st.rerun()

elif st.session_state.page == 'Gallery':
    if not st.session_state.logged_in:
        st.title("Gallery")
        st.write("Public portfolio")
    else:
        st.session_state.page = 'Dashboard'
        st.rerun()

elif st.session_state.page == 'Dashboard':
    if st.session_state.logged_in:
        user_type = st.session_state.user_type or "User"
        st.title(f"{user_type.title()} Dashboard")
        st.success("Home/About/Gallery don hide ✅")
    else:
        st.session_state.page = 'Home'
        st.rerun()
# PAGE CONTENT - SHOW BASED ON SELECTION
if st.session_state.page == 'Home':
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-family: Space Grotesk; font-size: 3.5rem; color: #14532D; margin-bottom: 0;'>
            WORK CHOP
        </h1>
        <h2 style='font-family: IBM Plex Mono; font-size: 1.2rem; color: #4A453E; letter-spacing: 2px; margin-top: 0.5rem;'>
            FOR HUMANITY, BY HUMANITY
        </h2>
        <p style='font-size: 1.1rem; color: #1C1A17; margin-top: 1.5rem;'>
            <strong>I tanda like rock no shaking</strong> - Connecting 26M+ Nigerian skilled workers with dignified jobs
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        #### **33.3% Unemployment**
        23 million Nigerians dey jobless. But we get skilled hands everywhere.
        """)
    with col2:
        st.markdown("""
        #### **Zero Risk Activation**
        Sabimen join FREE with NIN. No payment until you don earn. 
        """)
    with col3:
        st.markdown("""
        #### **Escrow Protected**
        Client money dey safe. Sabiman get paid 24hrs after job completion.
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### **How Work Chop Dey Work**
    
    **For Sabimen (Workers):**
    1. **Register FREE** - NIN verification only, no upfront fees
    2. **Get Hired** - Clients find you based on skill + location  
    3. **Do the Work** - Show your expertise, build your rating
    4. **Get Paid** - Money drops in your account 24hrs after client confirms
    
    **For Clients:**
    1. **Post Job FREE** - Describe wetin you need
    2. **Pick Sabiman** - Browse verified profiles with ratings
    3. **Pay Escrow** - Money held safe until work done
    4. **Confirm & Release** - Approve work, sabiman gets paid automatically
    
    > **This is not charity. This is business with a soul.**
    """)
    
elif st.session_state.page == 'About':
    st.markdown("# **About Work Chop**")
    st.markdown("### *The Story Behind Nigeria's Labor Revolution*")
    
    st.markdown("""
    #### **The Problem We Saw**
    Nigeria no get unemployment problem - we get **connection problem**. 
    
    26 million skilled workers dey the informal sector: tailors, plumbers, electricians, mechanics, carpenters. But clients no fit find them. Sabimen no fit find clients. Both sides dey suffer while middlemen chop commission.
    
    #### **The Solution We Built**
    **Work Chop** is Nigeria's first **Zero Risk Activation** platform for skilled labor.
    
    - **NIN-Verified Profiles** - Every sabiman verified with NIMC. No fake accounts.
    - **Escrow Protection** - Client money held safe. Sabiman paid only when work confirmed.
    - **No Upfront Cost** - Poor sabimen fit join free. We only chop commission after you earn.
    - **Bank-Level Security** - AES-256 encryption. Your data protected like Zenith Bank.
    
    #### **Our Mission**
    > To unlock dignified employment for 26 million Nigerians in the informal sector by 2030.
    
    #### **Our Values**
    1. **Humanity First** - Every sabiman deserves dignity, not exploitation
    2. **Trust by Design** - NIN + escrow + ratings = zero fraud
    3. **I Tanda Like Rock** - We no dey shake. Your money, your work, your reputation dey safe
    
    #### **The Founders**
    Built by Nigerians, for Nigerians. We understand the hustle because we don hustle.
    
    **Headquarters:** 15 Awolowo Road, Ikoyi, Lagos, Nigeria
    
    ---
    
    **Join the revolution. Work Chop - For Humanity, By Humanity.**
    """)
    
elif st.session_state.page == 'Gallery':
    st.markdown("# **Work Chop Gallery**")
    st.markdown("### *See Our Sabimen in Action*")
    st.markdown("see your self")
    st.info("📸 Gallery coming soon")
    
elif st.session_state.page == 'Contact':
    st.markdown("# **Contact Work Chop**")
    st.markdown("### *We dey here for you 24/7*")
    st.write("📍 15 Awolowo Road, Ikoyi, Lagos")
    st.write("📧 support@workchop.ng")
    st.write("📱 +234 800 WORK-CHOP")
    
elif st.session_state.page == 'Help':
    st.markdown("# **Help Center**")
    st.markdown("### *Frequently Asked Questions*")
    with st.expander("🔒 How does Zero Risk Activation work?"):
        st.write("You register FREE with your NIN. No payment needed. Start earning immediately.")

# CSS
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
.highlight-box { background: #1e3a8a; border: 2px solid #3b82f6; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; }
.available-card { background: #1a1a1a; border: 2px solid #10b981; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; }
.active-user { background: #1a1a1a; border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
.message-box { background: #1f2937; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; border: 1px solid #374151; }
</style>
""", unsafe_allow_html=True)

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
                            # WORK CHOP UPDATE: New sabiman starts unactivated
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
                if st.button("👥 Active Users", use_container_width=True, key="admin_active_btn"):
                    st.session_state.admin_page = 'Active'
                    st.rerun()
                if st.button("💬 Message Center", use_container_width=True, key="admin_msg_btn"):
                    st.session_state.admin_page = 'Messages'
                    st.rerun()
                if st.button("📈 Analytics", use_container_width=True, key="admin_analytics_btn"):
                    st.session_state.admin_page = 'Analytics'
                    st.rerun()
                if st.button("👤 All Users", use_container_width=True, key="admin_users_btn"):
                    st.session_state.admin_page = 'Users'
                    st.rerun()
                if st.button("➕ Create User", use_container_width=True, key="admin_create_btn"):
                    st.session_state.admin_page = 'Create'
                    st.rerun()
                if st.button("📄 Reports", use_container_width=True, key="admin_report_btn"):
                    st.session_state.admin_page = 'Reports'
                    st.rerun()

            st.markdown("---")
            if st.button(t("logout"), use_container_width=True, key="sidebar_logout_btn"):
                log_traffic("Logout")
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.page = 'Home'
                st.rerun()

# ADMIN DASHBOARD - UPGRADED WITH VISUALIZATIONS
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
        st.markdown("### 📊 Revenue by Duration (Bar Chart)")
        duration_types = ['Hourly', 'Daily', 'Weekly', 'Monthly', 'One-time']
        revenue_data = []
        for dur in duration_types:
            jobs_dur = [j for j in paid_jobs if j['duration'] == dur]
            revenue_data.append(sum([j['commission'] for j in jobs_dur]))
        fig = go.Figure()
        fig.add_trace(go.Bar(x=duration_types, y=revenue_data, name='Commission', marker_color='#10b981', text=[f'₦{x:,}' for x in revenue_data], textposition='auto'))
        fig.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💰 Payment Split (Pie Chart)")
        fig_donut = go.Figure(data=[go.Pie(labels=['Sabiman Payout', 'Commission'], values=[total_sabiman_paid, total_revenue], hole=.6, marker_colors=['#3b82f6', '#10b981'], textinfo='label+percent')])
        fig_donut.update_layout(height=350, showlegend=True, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', legend=dict(font=dict(color='white')))
        st.plotly_chart(fig_donut, use_container_width=True)

    # CHARTS ROW 2
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Revenue Trend (Line Chart)")
        last_7_days = []
        revenue_trend = []
        for i in range(6, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime("%b %d")
            last_7_days.append(day_str)
            day_revenue = sum([j['commission'] for j in paid_jobs if j.get('paid_at') and datetime.strptime(j['paid_at'], "%Y-%m-%d").date() == day.date()])
            revenue_trend.append(day_revenue)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=last_7_days, y=revenue_trend, mode='lines+markers', line=dict(color='#10b981', width=3), fill='tozeroy', fillcolor='rgba(16,185,129,0.2)'))
        fig_line.update_layout(height=350, showlegend=False)
        fig_line.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("### 🌍 Top Performing Regions (Bar Chart)")
        region_revenue = {}
        for job in paid_jobs:
            region = job.get('region', 'Unknown')
            region_revenue[region] = region_revenue.get(region, 0) + job['commission']
        regions = list(region_revenue.keys())
        revenues = list(region_revenue.values())
        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(x=regions, y=revenues, marker_color='#8b5cf6', text=[f'₦{x:,}' for x in revenues], textposition='auto'))
        fig_region.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig_region, use_container_width=True)

    # TOP SABIMEN
    st.markdown("### ⭐ Top 5 Sabimen (5-Star Rated)")
    top_sabimen = sorted([u for u in st.session_state.users.values() if u['role'] == 'sabiman'], key=lambda x: (x['rating'], x['jobs_done']), reverse=True)[:5]
    if top_sabimen:
        df_top = pd.DataFrame([{
            'Name': u['name'],
            'Rating': f"{u['rating']} ⭐",
            'Jobs Done': u['jobs_done'],
            'Region': u.get('region', 'N/A'),
            'Status': '🟢 Active' if u.get('available') else '🔴 Offline',
            # WORK CHOP UPDATE: Show activation status
            'Activated': '✅' if u.get('is_activated') else '⏳'
        } for u in top_sabimen])
        st.dataframe(df_top, use_container_width=True, hide_index=True)

def admin_active_users():
    st.markdown("# 👥 Active Sabimen & Clients")

    tab1, tab2 = st.tabs(["🟢 Active Sabimen", "🟢 Active Clients"])

    with tab1:
        st.markdown("### Active Sabimen (Available for Work)")
        active_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}
        if active_sabimen:
            for email, sabiman in active_sabimen.items():
                last_active = sabiman.get('last_active', 'Unknown')
                # WORK CHOP UPDATE: Show activation badge
                activation_badge = "✅ Activated" if sabiman.get('is_activated') else "⏳ Not Activated"
                st.markdown(f"""
                <div class="active-user">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="color: white; margin: 0;">{sabiman['name']} ⭐ {sabiman['rating']} | {activation_badge}</h4>
                            <p style="color: #9ca3af; margin: 0.3rem 0; font-size: 0.9rem;">📍 {sabiman.get('region', 'N/A')} | 📞 {sabiman['phone']} | {sabiman['jobs_done']} jobs done</p>
                            <p style="color: #10b981; margin: 0; font-size: 0.85rem;">Last active: {last_active}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No Sabimen currently available")

    with tab2:
        st.markdown("### Active Clients")
        active_clients = {k:v for k,v in st.session_state.users.items() if v['role'] == 'client'}
        if active_clients:
            for email, client in active_clients.items():
                last_active = client.get('last_active', 'Unknown')
                st.markdown(f"""
                <div class="active-user">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="color: white; margin: 0;">{client['name']} ⭐ {client['rating']}</h4>
                            <p style="color: #9ca3af; margin: 0.3rem 0; font-size: 0.9rem;">📍 {client.get('region', 'N/A')} | 📞 {client['phone']} | {client['jobs_posted']} jobs posted</p>
                            <p style="color: #10b981; margin: 0; font-size: 0.85rem;">Last active: {last_active}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

def admin_message_center():
    st.markdown("# 💬 Message Center - Send Reminders")
    st.caption("Send reminder messages to Sabimen and Clients to follow up on jobs")

    # Show pending jobs that need reminders
    pending_jobs = [j for j in st.session_state.jobs if j['status'] in ['Requested - Awaiting Sabiman', 'Accepted - In Progress', 'Work Done - Awaiting Confirmation']]

    if pending_jobs:
        st.markdown("### 🔔 Jobs Needing Follow-Up")
        for job in pending_jobs:
            sabiman = st.session_state.users[job['sabiman']]
            client = st.session_state.users[job['client']]
            # WORK CHOP UPDATE: Show time left for auto-release
            time_left = ""
            if job.get('auto_release_at'):
                release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
                if release_time > datetime.now():
                    hours_left = (release_time - datetime.now()).seconds // 3600
                    time_left = f" | ⏰ Auto-release in {hours_left}hrs"

            st.markdown(f"""
            <div class="message-box">
                <h4 style="color: white; margin: 0;">{job['title']}</h4>
                <p style="color: #d1d5db; margin: 0.5rem 0;">Status: <b style="color: #f59e0b;">{job['status']}</b> | Amount: ₦{job['amount']:,}{time_left}</p>
                <p style="color: #9ca3af; font-size: 0.9rem;">Sabiman: {sabiman['name']} ({sabiman['phone']}) | Client: {client['name']} ({client['phone']})</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                sabiman_msg = st.text_area(f"Message to {sabiman['name']}", key=f"sabi_msg_{job['id']}", placeholder="e.g., Oga, client dey wait for you. Abeg complete the work sharp!")
                if st.button(f"📤 Send to Sabiman", key=f"send_sabi_{job['id']}", use_container_width=True):
                    if sabiman_msg:
                        st.session_state.admin_messages.append({
                            'to': job['sabiman'],
                            'from': 'admin',
                            'message': sabiman_msg,
                            'job_id': job['id'],
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        log_traffic(f"Sent reminder to Sabiman for job {job['id']}")
                        st.success(f"✅ Message sent to {sabiman['name']}")
                        st.rerun()

            with col2:
                client_msg = st.text_area(f"Message to {client['name']}", key=f"client_msg_{job['id']}", placeholder="e.g., Hello, please confirm if you are satisfied with the service")
                if st.button(f"📤 Send to Client", key=f"send_client_{job['id']}", use_container_width=True):
                    if client_msg:
                        st.session_state.admin_messages.append({
                            'to': job['client'],
                            'from': 'admin',
                            'message': client_msg,
                            'job_id': job['id'],
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        log_traffic(f"Sent reminder to Client for job {job['id']}")
                        st.success(f"✅ Message sent to {client['name']}")
                        st.rerun()
    else:
        st.success("✅ All jobs are on track! No reminders needed")

    # Message History
    if st.session_state.admin_messages:
        st.markdown("---")
        st.markdown("### 📜 Message History")
        for msg in reversed(st.session_state.admin_messages[-10:]):
            recipient = st.session_state.users[msg['to']]['name']
            st.markdown(f"""
            <div style="background: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #3b82f6;">
                <p style="color: #9ca3af; font-size: 0.8rem; margin: 0;">To: {recipient} | {msg['timestamp']}</p>
                <p style="color: white; margin: 0.5rem 0;">{msg['message']}</p>
            </div>
            """, unsafe_allow_html=True)

def admin_analytics():
    st.markdown("# 📈 Advanced Analytics & Tracking")

    paid_jobs = [j for j in st.session_state.jobs if j['status'] == 'Completed - Paid']

    # TOP METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_revenue = sum([j['commission'] for j in paid_jobs])
        st.metric("Total Revenue", f"₦{total_revenue:,}", "Commission earned")
    with col2:
        total_paid_out = sum([j['sabiman_payout'] for j in paid_jobs])
        st.metric("Paid to Sabimen", f"₦{total_paid_out:,}")
    with col3:
        avg_job_value = sum([j['amount'] for j in paid_jobs]) / len(paid_jobs) if paid_jobs else 0
        st.metric("Avg Job Value", f"₦{avg_job_value:,.0f}")
    with col4:
        completion_rate = len(paid_jobs) / len(st.session_state.jobs) * 100 if st.session_state.jobs else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # CHART 1: Revenue by Category
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Revenue by Category")
        cat_revenue = {}
        for job in paid_jobs:
            cat = job['category']
            cat_revenue[cat] = cat_revenue.get(cat, 0) + job['commission']
        fig_cat = go.Figure(data=[go.Bar(x=list(cat_revenue.keys()), y=list(cat_revenue.values()), marker_color='#10b981', text=[f'₦{x:,}' for x in cat_revenue.values()], textposition='auto')])
        fig_cat.update_layout(height=400, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown("### 🏆 Top 5 Sabimen by Earnings")
        sabiman_earnings = {}
        for job in paid_jobs:
            sabiman_email = job['sabiman']
            sabiman_earnings[sabiman_email] = sabiman_earnings.get(sabiman_email, 0) + job['sabiman_payout']
        top_earners = sorted(sabiman_earnings.items(), key=lambda x: x[1], reverse=True)[:5]
        names = [st.session_state.users[email]['name'] for email, _ in top_earners]
        earnings = [amt for _, amt in top_earners]
        fig_top = go.Figure(data=[go.Bar(y=names, x=earnings, orientation='h', marker_color='#3b82f6', text=[f'₦{x:,}' for x in earnings], textposition='auto')])
        fig_top.update_layout(height=400, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white'))
        st.plotly_chart(fig_top, use_container_width=True)

    # CHART 2: Performance Metrics
    st.markdown("### 📈 Sabiman Performance Matrix")
    sabiman_stats = []
    for email, user in st.session_state.users.items():
        if user['role'] == 'sabiman':
            jobs_done = user['jobs_done']
            rating = user['rating']
            sabiman_stats.append({'Name': user['name'], 'Jobs': jobs_done, 'Rating': rating})

    if sabiman_stats:
        df_perf = pd.DataFrame(sabiman_stats)
        fig_scatter = px.scatter(df_perf, x='Jobs', y='Rating', text='Name', title='Jobs Done vs Rating',
                                 color='Rating', color_continuous_scale='RdYlGn', size='Jobs', size_max=20)
        fig_scatter.update_layout(height=400, plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a',
                                 xaxis=dict(color='white', gridcolor='#374151'),
                                 yaxis=dict(color='white', gridcolor='#374151'),
                                 title_font_color='white')
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

def admin_users():
    st.markdown("# 👥 All Users")
    tab1, tab2, tab3 = st.tabs(["Clients", "Sabimen", "Admins"])
    with tab1:
        clients = {k:v for k,v in st.session_state.users.items() if v['role'] == 'client'}
        if clients:
            df = pd.DataFrame.from_dict(clients, orient='index')
            st.dataframe(df[['name', 'phone', 'rating', 'jobs_posted', 'region', 'created']], use_container_width=True)
    with tab2:
        sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman'}
        if sabimen:
            df = pd.DataFrame.from_dict(sabimen, orient='index')
            # WORK CHOP UPDATE: Show activation status
            df['activated'] = df.apply(lambda x: '✅' if x.get('is_activated') else '⏳', axis=1)
            st.dataframe(df[['name', 'phone', 'rating', 'jobs_done', 'region', 'available', 'activated', 'created']], use_container_width=True)
    with tab3:
        admins = {k:v for k,v in st.session_state.users.items() if v['role'] == 'admin'}
        df = pd.DataFrame.from_dict(admins, orient='index')
        st.dataframe(df[['name', 'phone', 'created']], use_container_width=True)

def admin_create():
    st.markdown("# ➕ Create New User")
    role = st.selectbox("User Type", ["Admin", "Client", "Sabiman"], key="create_role")
    name = st.text_input("Full Name", key="create_name")
    email = st.text_input("Email", key="create_email")
    password = st.text_input("Password", type="password", key="create_pass")
    phone = st.text_input("Phone", placeholder="08012345678", key="create_phone")
    region = st.selectbox("Region", ["Abuja", "Lagos", "Port Harcourt", "Kano", "Ibadan", "Other"], key="create_region")
    nin = ""
    if role == "Sabiman":
        nin = st.text_input("NIN (11 digits)", max_chars=11, key="create_nin")
    if st.button("Create User", type="primary", use_container_width=True, key="create_btn"):
        if email in st.session_state.users:
            st.error("Email already exists")
        elif not (name and email and password and phone):
            st.error("Fill all required fields")
        else:
            user_data = {'password': password, 'role': role.lower(), 'name': name, 'phone': phone, 'nin': nin, 'verified': True, 'created': datetime.now().strftime("%Y-%m-%d"), 'rating': 5.0, 'jobs_done': 0, 'jobs_posted': 0, 'bio': f'New {role}', 'profile_pic': None, 'portfolio': [], 'rates': {'hourly': 0, 'daily': 0, 'weekly': 0, 'monthly': 0}, 'available': False, 'work_categories': [], 'region': region, 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M")}
            # WORK CHOP UPDATE: Add activation fields for new Sabiman
            if role.lower() == 'sabiman':
                user_data.update({'is_activated': False, 'activation_deposit': 0, 'jobs_completed_for_activation': 0, 'activation_bonus_paid': False})
            st.session_state.users[email] = user_data
            st.success(f"✅ {role} created successfully!")
            st.balloons()

def admin_reports():
    st.markdown("# 📄 Generate Reports & Receipts")
    col1, col2 = st.columns(2)
    with col1:
        report_type = st.selectbox("Report Period", ["Weekly", "Monthly"], key="report_period")
    with col2:
        report_date = st.date_input("End Date", datetime.now(), key="report_date")
    if st.button("Generate Report", type="primary", key="gen_report_btn"):
        if report_type == "Weekly":
            start_date = report_date - timedelta(days=7)
        else:
            start_date = report_date - timedelta(days=30)
        filtered_jobs = []
        for j in st.session_state.jobs:
            if j.get('paid_at'):
                job_date = datetime.strptime(j['paid_at'], "%Y-%m-%d").date()
                if start_date <= job_date <= report_date:
                    filtered_jobs.append(j)
        if filtered_jobs:
            df = pd.DataFrame(filtered_jobs)
            total_rev = df['commission'].sum()
            st.success(f"Report: {start_date} to {report_date}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Jobs", len(df))
            col2.metric("Total Revenue", f"₦{total_rev:,}")
            col3.metric("Total Volume", f"₦{df['amount'].sum():,}")
            st.dataframe(df[['id', 'title', 'client', 'sabiman', 'amount', 'commission', 'sabiman_payout', 'paid_at', 'region']], use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, f"workchop_report_{report_date}.csv", "text/csv")
        else:
            st.warning("No transactions in selected period")

# DASHBOARD PAGE - WITH ZERO RISK ACTIVATION
def dashboard_page():
    user = st.session_state.users[st.session_state.current_user]

    if user['role'] == 'sabiman':
        log_traffic("View Dashboard")

        st.markdown("""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;"><div><h1 style="margin: 0; color: white;">Sabiman Dashboard</h1><p style="color: #9ca3af; margin: 0;">Your Earnings Overview</p></div></div>""", unsafe_allow_html=True)

        # WORK CHOP UPDATE: Zero Risk Activation UI
        st.markdown("### 🔐 Account Activation Status")
        if not user.get('is_activated', False):
            st.markdown("""
            <div class="highlight-box">
                <h4 style="color: white; margin: 0;">⚠️ Account Not Activated</h4>
                <p style="color: #f59e0b;">Your first ₦500 earning will activate your account automatically. No upfront payment needed! Join FREE, earn first!</p>
            </div>
            """, unsafe_allow_html=True)
        elif not user.get('activation_bonus_paid', False):
            remaining = 5 - user.get('jobs_completed_for_activation', 0)
            progress = user.get('jobs_completed_for_activation', 0) / 5
            st.markdown(f"""
            <div class="available-card">
                <h4 style="color: white; margin: 0;">🎁 Loyalty Bonus Progress</h4>
                <p style="color: #10b981;">Complete {remaining} more jobs to unlock ₦500 Loyalty Bonus!</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress)
        else:
            st.markdown("""
            <div class="available-card">
                <h4 style="color: white; margin: 0;">✅ Fully Activated + Bonus Received</h4>
                <p style="color: #10b981;">Your account is verified and you've received your ₦500 loyalty bonus! Keep chopping!</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # PROFILE SECTION
        st.markdown("### 👤 Your Profile & Portfolio")
        col1, col2, col3 = st.columns([1,1,2])

        with col1:
            st.markdown("**Profile Picture**")
            profile_pic = st.file_uploader("Selfie", type=['jpg', 'jpeg', 'png'], key="profile_upload")
            if profile_pic:
                st.image(profile_pic, width=150)
                st.session_state.users[st.session_state.current_user]['profile_pic'] = profile_pic.name
                st.success("✅ Updated!")
            elif user.get('profile_pic'):
                st.caption(f"📷 {user['profile_pic']}")

        with col2:
            st.markdown("**Previous Work**")
            portfolio_pic = st.file_uploader("Portfolio", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="portfolio_upload")
            if portfolio_pic:
                for pic in portfolio_pic:
                    if pic.name not in user.get('portfolio', []):
                        st.session_state.users[st.session_state.current_user].setdefault('portfolio', []).append(pic.name)
                st.success(f"✅ {len(portfolio_pic)} added!")
            if user.get('portfolio'):
                st.caption(f"📷 {len(user['portfolio'])} images")

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

        with col1:
            hourly = st.number_input("Hourly (₦)", value=rates['hourly'], step=500, key="rate_hourly")
        with col2:
            daily = st.number_input("Daily (₦)", value=rates['daily'], step=1000, key="rate_daily")
        with col3:
            weekly = st.number_input("Weekly (₦)", value=rates['weekly'], step=5000, key="rate_weekly")
        with col4:
            monthly = st.number_input("Monthly (₦)", value=rates['monthly'], step=10000, key="rate_monthly")

        if st.button("💾 Save Rates & Categories", use_container_width=True, key="save_rates"):
            st.session_state.users[st.session_state.current_user]['rates'] = {
                'hourly': hourly, 'daily': daily, 'weekly': weekly, 'monthly': monthly
            }
            st.success("✅ Rates updated! Clients can now see your pricing")
            st.rerun()

        st.markdown("---")

        # METRICS
        my_jobs = [j for j in st.session_state.jobs if j.get('sabiman') == st.session_state.current_user]
        paid_jobs = [j for j in my_jobs if j['status'] == 'Completed - Paid']
        pending_jobs = [j for j in my_jobs if j['status'] == 'Work Done - Awaiting Confirmation']
        new_requests = [j for j in my_jobs if j['status'] == 'Requested - Awaiting Sabiman']

        total_earned = sum([j['sabiman_payout'] for j in paid_jobs])
        total_pending = sum([j['amount'] - calculate_commission(j['amount']) for j in pending_jobs])
        jobs_done = len(paid_jobs)
        rating = user.get('rating', 5.0)

        # BIG CARDS
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white; border: 1px solid #10b981;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Total Paid</p><h1 style="color: #10b981; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_earned:,}</h1><p style="color: #10b981; font-size: 0.9rem; margin: 0;">✓ In your account</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white; border: 1px solid #f59e0b;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Pending Payment</p><h1 style="color: #f59e0b; margin: 0.5rem 0; font-size: 2.5rem;">₦{total_pending:,}</h1><p style="color: #f59e0b; font-size: 0.9rem; margin: 0;">⏳ Awaiting client</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Jobs Completed</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{jobs_done}</h1><p style="color: #3b82f6; font-size: 0.9rem; margin: 0;">All time</p></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div style="background: #1a1a1a; padding: 2rem; border-radius: 16px; color: white;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">New Requests</p><h1 style="color: white; margin: 0.5rem 0; font-size: 2.5rem;">{len(new_requests)}</h1><p style="color: #f59e0b; font-size: 0.9rem; margin: 0;">Awaiting you</p></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # NEW REQUESTS FROM CLIENTS
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
                    # WORK CHOP UPDATE: Set 24hr auto-release timer
                    job['auto_release_at'] = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
                    job['reminder_sent'] = False
                    log_traffic(f"Marked job {job['id']} as done - 24hr timer started")
                    st.success("Client has been notified! Payment auto-releases in 24hrs if no dispute")
                    st.rerun()

        # JOBS AWAITING CONFIRMATION
        awaiting_jobs = [j for j in my_jobs if j['status'] == 'Work Done - Awaiting Confirmation']
        if awaiting_jobs:
            st.markdown("### 🔔 Jobs Awaiting Client Confirmation")
            for job in awaiting_jobs:
                client_name = st.session_state.users[job['client']]['name']
                # WORK CHOP UPDATE: Show countdown
                time_left = ""
                if job.get('auto_release_at'):
                    release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
                    if release_time > datetime.now():
                        hours_left = int((release_time - datetime.now()).total_seconds() // 3600)
                        time_left = f"<p style='color: #f59e0b;'>⏰ Auto-release in {hours_left}hrs</p>"

                st.markdown(f"""<div class="highlight-box"><h3 style="color: white; margin: 0;">{job['title']}</h3><p style="color: #d1d5db; margin: 0.5rem 0;">Client: <b>{client_name}</b> | Amount: <b style="color: #f59e0b;">₦{job['amount']:,}</b></p><p style="color: #9ca3af;">Client Satisfied: {'✅' if job.get('client_satisfied') else '❌ Waiting'} | You Confirmed: ✅</p>{time_left}</div>""", unsafe_allow_html=True)

        st.markdown("---")

        # CHART
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("""<div style="background: #1a1a1a; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;"><h3 style="color: white; margin: 0;">Earnings Trend</h3></div>""", unsafe_allow_html=True)
            last_6_months = []
            paid_data = []
            for i in range(5, -1, -1):
                month_date = datetime.now() - timedelta(days=30*i)
                month_str = month_date.strftime("%b")
                last_6_months.append(month_str)
                month_paid = sum([j['sabiman_payout'] for j in paid_jobs if j.get('paid_at') and datetime.strptime(j['paid_at'], "%Y-%m-%d").strftime("%b") == month_str])
                paid_data.append(month_paid)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=last_6_months, y=paid_data, name='Paid', line=dict(color='#10b981', width=3), fill='tozeroy', fillcolor='rgba(16,185,129,0.2)'))
            fig.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            this_week_paid = sum([j['sabiman_payout'] for j in paid_jobs if j.get('paid_at') and datetime.strptime(j['paid_at'], "%Y-%m-%d") >= datetime.now() - timedelta(days=7)])
            st.markdown(f"""<div style="background: #1a1a1a; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">This Week</p><h2 style="color: #10b981; margin: 0.5rem 0;">₦{this_week_paid:,}</h2></div>""", unsafe_allow_html=True)
            active_jobs = len([j for j in my_jobs if j['status'] not in ['Completed - Paid', 'Cancelled']])
            st.markdown(f"""<div style="background: #1a1a1a; padding: 1.5rem; border-radius: 16px;"><p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">Active Jobs</p><h2 style="color: white; margin: 0.5rem 0;">{active_jobs}</h2></div>""", unsafe_allow_html=True)

        # RECENT JOBS TABLE
        st.markdown("### Recent Jobs")
        if my_jobs:
            df = pd.DataFrame(my_jobs)
            def status_color(status):
                if status == 'Completed - Paid':
                    return f'<span style="color: #10b981; font-weight: 600;">✓ PAID</span>'
                elif status == 'Work Done - Awaiting Confirmation':
                    return f'<span style="color: #f59e0b; font-weight: 600;">⏳ PENDING</span>'
                elif status == 'Requested - Awaiting Sabiman':
                    return f'<span style="color: #3b82f6; font-weight: 600;">📩 NEW REQUEST</span>'
                elif status == 'Accepted - In Progress':
                    return f'<span style="color: #8b5cf6; font-weight: 600;">🔨 IN PROGRESS</span>'
                else:
                    return f'<span style="color: #6b7280;">{status}</span>'
            df['Status'] = df['status'].apply(status_color)
            df['Amount'] = df['amount'].apply(lambda x: f"₦{x:,}")
            df['Your Cut'] = df.apply(lambda row: f'<span style="color: #10b981; font-weight: 600;">₦{row["sabiman_payout"]:,}</span>' if row["status"] == "Completed - Paid" else f'<span style="color: #f59e0b;">₦{row["amount"] - calculate_commission(row["amount"]):,}</span>', axis=1)
            st.markdown(df[['title', 'Status', 'Amount', 'Your Cut', 'created']].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No jobs yet. Post your availability!")

    elif user['role'] == 'client':
        st.markdown("# 📊 Client Dashboard")

        # FEATURE: BROWSE AVAILABLE SABIMEN & REQUEST WORK
        st.markdown("### 🔍 Find Sabimen & Request Work")
        available_sabimen = {k:v for k,v in st.session_state.users.items() if v['role'] == 'sabiman' and v.get('available', False)}

        if available_sabimen:
            cols = st.columns(3)
            for idx, (email, sabiman) in enumerate(available_sabimen.items()):
                with cols[idx % 3]:
                    # WORK CHOP UPDATE: Show if Sabiman activated
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
                                # WORK CHOP UPDATE: 24hr auto-release fields
                                'auto_release_at': None, 'reminder_sent': False, 'disputed': False
                            }
                            st.session_state.jobs.append(new_job)
                            st.session_state.users[st.session_state.current_user]['jobs_posted'] += 1
                            log_traffic(f"Requested work from {sabiman['name']}")
                            st.success(f"✅ Request sent to {sabiman['name']}!")
                            st.rerun()
        else:
            st.info("No Sabimen available right now")

        st.markdown("---")

        # JOBS AWAITING YOUR CONFIRMATION
        st.markdown("### 🔔 Jobs Awaiting Your Confirmation")
        client_jobs = [j for j in st.session_state.jobs if j['client'] == st.session_state.current_user]
        awaiting_confirmation = [j for j in client_jobs if j['status'] == 'Work Done - Awaiting Confirmation']

        if awaiting_confirmation:
            for job in awaiting_confirmation:
                sabiman_name = st.session_state.users[job['sabiman']]['name']
                # WORK CHOP UPDATE: Show auto-release countdown
                time_left = ""
                if job.get('auto_release_at'):
                    release_time = datetime.strptime(job['auto_release_at'], "%Y-%m-%d %H:%M")
                    if release_time > datetime.now():
                        hours_left = int((release_time - datetime.now()).total_seconds() // 3600)
                        time_left = f"<p style='color: #f59e0b;'>⏰ Auto-releases in {hours_left}hrs if no action</p>"

                st.markdown(f"""<div class="highlight-box"><h3 style="color: white; margin: 0;">{job['title']}</h3><p style="color: #d1d5db; margin: 0.5rem 0;">Sabiman: <b>{sabiman_name}</b> | Amount: <b style="color: #f59e0b;">₦{job['amount']:,}</b></p><p style="color: #9ca3af;">{job['desc']}</p><p style="color: #d1d5db;">Sabiman says: {'✅ Work Done' if job.get('sabiman_satisfied') else '⏳ Working'}</p>{time_left}</div>""", unsafe_allow_html=True)

                if not job.get('client_satisfied'):
                    if st.button(f"✅ I am satisfied with your service", key=f"client_satisfy_{job['id']}", use_container_width=True, type="primary"):
                        job['client_satisfied'] = True
                        log_traffic(f"Client confirmed job {job['id']}")
                        if job.get('client_satisfied') and job.get('sabiman_satisfied'):
                            # WORK CHOP UPDATE: Use new process_payment with activation logic
                            process_payment(job['id'])
                            st.success(f"✅ Payment Released! ₦{job['sabiman_payout']:,} sent to Sabiman. Commission: ₦{job['commission']:,}")
                            st.balloons()
                        st.rerun()
        else:
            st.info("No jobs awaiting your confirmation")

        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jobs Posted", user.get('jobs_posted', 0))
        with col2:
            total_spent = sum([j['amount'] for j in st.session_state.jobs if j['client'] == st.session_state.current_user and j['status'] == 'Completed - Paid'])
            st.metric("Total Spent", f"₦{total_spent:,}")
        with col3:
            st.metric("Your Rating", user.get('rating', 5.0))

        st.markdown("### Your Jobs")
        if client_jobs:
            df = pd.DataFrame(client_jobs)
            df['Amount'] = df['amount'].apply(lambda x: f"₦{x:,}")
            st.dataframe(df[['title', 'status', 'Amount', 'created']], use_container_width=True, hide_index=True)
        else:
            st.info("No jobs yet. Request work from Sabimen above!")

# MAIN APP LOGIC
render_sidebar()

if st.session_state.logged_in:
    user = st.session_state.users[st.session_state.current_user]
    if user['role'] == 'admin':
        if st.session_state.admin_page == 'Dashboard':
            admin_dashboard()
        elif st.session_state.admin_page == 'Active':
            admin_active_users()
        elif st.session_state.admin_page == 'Messages':
            admin_message_center()
        elif st.session_state.admin_page == 'Analytics':
            admin_analytics()
        elif st.session_state.admin_page == 'Users':
            admin_users()
        elif st.session_state.admin_page == 'Create':
            admin_create()
        elif st.session_state.admin_page == 'Reports':
            admin_reports()
    else:
        dashboard_page()
else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem;">
        <h1 style="color: white;">🇳🇬 WORK CHOP</h1>
        <p style="font-size: 1.2rem; color: #9ca3af;">For Humanity, By Humanity</p>
        <p style="color: #6b7280;"><b>Test Logins:</b><br>
        Admin: admin@workchop.ng / admin123<br>
        Client 1: client@test.com / client123<br>
        Client 2: client2@test.com / client123<br>
        Sabiman 1: sabiman@test.com / sabi123 (Activated)<br>
        Sabiman 2: sabiman2@test.com / sabi123 (Activated)<br>
        Sabiman 3: sabiman3@test.com / sabi123 (Not Activated - Test Zero Risk!)</p>
    </div>
    """, unsafe_allow_html=True)
    
