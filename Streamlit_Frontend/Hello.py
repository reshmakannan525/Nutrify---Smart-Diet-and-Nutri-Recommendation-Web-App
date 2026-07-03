import streamlit as st
from auth import signup_user, login_user

st.set_page_config(
    page_title="Diet Recommendation System",
    page_icon="🥗",
    layout="centered"
)

# Load Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">', unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}

.hero {
    background: #1b5e20;
    border-radius: 14px;
    padding: 36px 24px 28px;
    text-align: center;
    margin-bottom: 28px;
}
.hero-icon-wrap {
    width: 64px; height: 64px; border-radius: 50%;
    background: rgba(255,255,255,0.15);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 14px;
}
.hero-icon-wrap i { color: #fff; font-size: 28px; }
.hero-title { font-size: 22px; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
.hero-sub   { font-size: 13px; color: #a5d6a7; }

.stTabs [data-baseweb="tab-list"] { gap: 0px; border-bottom: 2px solid #e8f5e9; }
.stTabs [data-baseweb="tab"] {
    flex: 1; justify-content: center;
    font-size: 14px; font-weight: 500;
    padding: 10px 0; color: #757575;
}
.stTabs [aria-selected="true"] {
    color: #2e7d32 !important;
    border-bottom: 2px solid #2e7d32 !important;
    background: transparent !important;
}
.section-title { font-size: 17px; font-weight: 600; color: #1b5e20; margin-bottom: 4px; }
.section-sub   { font-size: 13px; color: #757575; margin-bottom: 18px; }

.stTextInput > div > div > input {
    border-radius: 8px; border: 1.5px solid #c8e6c9;
    padding: 10px 14px; font-size: 14px;
}
.stTextInput > div > div > input:focus {
    border-color: #2e7d32; box-shadow: 0 0 0 2px #c8e6c9;
}
.stButton > button {
    width: 100%; border-radius: 8px;
    background-color: #2e7d32; color: white;
    font-size: 14px; font-weight: 600;
    padding: 11px; border: none; margin-top: 4px;
}
.stButton > button:hover { background-color: #1b5e20 !important; color: white !important; }

.input-icon-row {
    display: flex; align-items: center; gap: 10px;
    background: #f9fbe7; border: 1.5px solid #c8e6c9;
    border-radius: 8px; padding: 9px 12px; margin-bottom: 10px;
    font-size: 13px; color: #555;
}
.input-icon-row i { color: #2e7d32; font-size: 14px; width: 16px; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    st.switch_page("pages/Home.py")

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-icon-wrap">
        <i class="fa-solid fa-bowl-food"></i>
    </div>
    <div class="hero-title">Diet Recommendation System</div>
    <div class="hero-sub">Your personal AI-powered nutrition assistant</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "🔓  Login",
    "📝  Sign Up"
])
# -------------------------
# LOGIN TAB
# -------------------------
with tab1:
    st.markdown('<div class="section-title">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Login to access your diet dashboard</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-icon-row"><i class="fa-solid fa-user"></i> Username</div>', unsafe_allow_html=True)
    login_username = st.text_input("", key="login_user", placeholder="Enter your username", label_visibility="collapsed")

    st.markdown('<div class="input-icon-row"><i class="fa-solid fa-lock"></i> Password</div>', unsafe_allow_html=True)
    login_password = st.text_input("", type="password", key="login_pass", placeholder="Enter your password", label_visibility="collapsed")

    st.markdown('<i class="fa-solid fa-right-to-bracket" style="color:#2e7d32;font-size:13px;"></i>', unsafe_allow_html=True)
    if st.button("Login", key="login_btn"):
        if not login_username or not login_password:
            st.warning("Please fill in all fields.")
        else:
            success, message = login_user(login_username, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
                st.switch_page("pages/Home.py")
            else:
                st.error(message)

# -------------------------
# SIGNUP TAB
# -------------------------
with tab2:
    st.markdown('<div class="section-title">Create an account</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Start your nutrition journey today</div>', unsafe_allow_html=True)

    st.markdown('<div class="input-icon-row"><i class="fa-solid fa-user-pen"></i> Username</div>', unsafe_allow_html=True)
    signup_username = st.text_input("", key="signup_user", placeholder="Choose a username", label_visibility="collapsed")

    st.markdown('<div class="input-icon-row"><i class="fa-solid fa-lock"></i> Password</div>', unsafe_allow_html=True)
    signup_password = st.text_input("", type="password", key="signup_pass", placeholder="At least 6 characters", label_visibility="collapsed")

    st.markdown('<div class="input-icon-row"><i class="fa-solid fa-shield-halved"></i> Confirm Password</div>', unsafe_allow_html=True)
    signup_confirm = st.text_input("", type="password", key="signup_confirm", placeholder="Repeat your password", label_visibility="collapsed")

    st.markdown('<i class="fa-solid fa-user-plus" style="color:#2e7d32;font-size:13px;"></i>', unsafe_allow_html=True)
    if st.button("Create Account", key="signup_btn"):
        if not signup_username or not signup_password or not signup_confirm:
            st.warning("Please fill in all fields.")
        elif len(signup_password) < 6:
            st.warning("Password must be at least 6 characters.")
        elif signup_password != signup_confirm:
            st.error("Passwords do not match.")
        else:
            success, message = signup_user(signup_username, signup_password)
            if success:
                st.success("Account created successfully! Please login.")
            else:
                st.error(message)