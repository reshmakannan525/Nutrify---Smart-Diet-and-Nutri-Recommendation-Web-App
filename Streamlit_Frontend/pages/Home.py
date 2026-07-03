import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="Home - Diet Recommendation",
    page_icon="🥗",
    layout="wide"
)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Hello.py")

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">',
    unsafe_allow_html=True,
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8f5e9; }

.avatar {
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg,#2e7d32,#66bb6a);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 700; color: white;
    margin-bottom: 6px; box-shadow: 0 3px 10px rgba(46,125,50,.35);
}
.user-name { font-size: 15px; font-weight: 700; color: #1b5e20; }
.user-sub  { font-size: 12px; color: #43a047; margin-bottom: 14px;
             display: flex; align-items: center; gap: 5px; }

/* ── banner ── */
.welcome-banner {
    border-radius: 18px; padding: 32px 36px;
    margin-bottom: 28px; display: flex;
    align-items: center; justify-content: space-between;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,.18);
}
.welcome-banner::before {
    content:""; position:absolute; top:-40px; right:180px;
    width:160px; height:160px; border-radius:50%;
    background:rgba(255,255,255,.08); pointer-events:none;
}
.welcome-banner::after {
    content:""; position:absolute; bottom:-50px; right:60px;
    width:220px; height:220px; border-radius:50%;
    background:rgba(255,255,255,.06); pointer-events:none;
}
.banner-morning   { background: linear-gradient(120deg,#e65100,#f57c00,#ffb74d); }
.banner-afternoon { background: linear-gradient(120deg,#1b5e20,#2e7d32,#66bb6a); }
.banner-evening   { background: linear-gradient(120deg,#1a237e,#283593,#5c6bc0); }
.banner-night     { background: linear-gradient(120deg,#0d0d1a,#1a1a2e,#2e2e4e); }
.welcome-left   { z-index:1; }
.welcome-text-h { font-size: 26px; font-weight: 800; color: #fff; margin-bottom: 6px; }
.welcome-text-s { font-size: 13px; color: rgba(255,255,255,.82);
                  display: flex; align-items: center; gap: 6px; }
.welcome-right  { z-index:1; display:flex; align-items:center; gap:18px; }
.bowl-wrap {
    width: 120px; height: 120px; border-radius: 50%;
    background: rgba(255,255,255,.18);
    display: flex; align-items: center; justify-content: center;
    font-size: 60px; box-shadow: 0 4px 20px rgba(0,0,0,.18);
}
.bottle-wrap {
    width: 70px; height: 70px; border-radius: 50%;
    background: rgba(255,255,255,.12);
    display: flex; align-items: center; justify-content: center;
    font-size: 32px;
}

/* ── stat cards ── */
.stat-box {
    background: #ffffff; border: 1.5px solid #e8f5e9;
    border-radius: 14px; padding: 18px 14px; text-align: center;
    transition: box-shadow .2s, border-color .2s;
    box-shadow: 0 2px 8px rgba(46,125,50,.07);
}
.stat-box:hover { border-color: #66bb6a; box-shadow: 0 4px 18px rgba(46,125,50,.15); }
.stat-icon-wrap {
    width: 44px; height: 44px; border-radius: 10px;
    background: #e8f5e9; display: flex; align-items: center;
    justify-content: center; margin: 0 auto 10px auto;
}
.stat-icon-wrap i { color: #2e7d32; font-size: 18px; }
.stat-lbl { font-size: 12px; color: #81c784; font-weight: 600;
            text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.stat-val { font-size: 22px; font-weight: 800; color: #1b5e20; }

/* ── feature cards ── */
.feat-card {
    background: #ffffff; border: 1.5px solid #e8f5e9;
    border-radius: 18px; overflow: hidden;
    box-shadow: 0 2px 10px rgba(46,125,50,.07);
    transition: box-shadow .25s, transform .2s, border-color .2s;
    display: flex; flex-direction: column;
    height: 100%;
}
.feat-card:hover {
    border-color: #66bb6a;
    box-shadow: 0 10px 32px rgba(46,125,50,.18);
    transform: translateY(-4px);
}
.feat-card-img {
    width: 100%; height: 160px; object-fit: cover;
    display: block; flex-shrink: 0;
}
.feat-card-body {
    padding: 18px 20px 12px 20px; flex: 1; display: flex; flex-direction: column;
}
.feat-card-title { font-size: 15px; font-weight: 800; color: #1b5e20; margin-bottom: 7px; }
.feat-card-desc  { font-size: 12px; color: #777; line-height: 1.65; flex: 1; }

/* ── feat card button: target the Streamlit button inside card columns ── */
div[data-testid="column"] .stButton > button {
    width: 100% !important;
    background: #2e7d32 !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 0 !important;
    font-size: 13px !important;
    margin-top: 10px !important;
    transition: background .2s !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: #1b5e20 !important;
}

.section-heading {
    font-size: 17px; font-weight: 800; color: #1b5e20;
    margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;
}

/* ── global buttons ── */
.stButton > button {
    border-radius: 9px; background: #2e7d32 !important;
    color: white !important; font-weight: 700; border: none; padding: 9px 22px;
}
.stButton > button:hover { background: #1b5e20 !important; }
.logout-wrap .stButton > button {
    background: transparent !important;
    color: #c62828 !important;
    border: 1.5px solid #ef9a9a !important;
    border-radius: 8px !important;
    width: 100%;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}
.logout-wrap .stButton > button:hover {
    background: #ffebee !important;
    border-color: #e57373 !important;
}
.logout-wrap .stButton > button svg,
.logout-wrap .stButton > button [data-testid="stIconMaterial"] {
    color: #c62828 !important;
    fill: #c62828 !important;
}
/* ── water tracker buttons ── */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important; font-size: 12px !important;
    padding: 6px 10px !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:first-child {
    background: #29b6f6 !important; color: #fff !important; border: none !important;
}
[data-testid="stSidebar"] .stButton > button:first-child:hover {
    background: #0288d1 !important;
}
[data-testid="stSidebar"] .stButton > button:last-child {
    background: transparent !important; color: #555 !important;
    border: 1px solid #ddd !important;
}

.info-footer { font-size: 12px; color: #aaa; margin-top: 8px;
               display: flex; align-items: center; gap: 6px; }

/* ── daily tip card ── */
.tip-card {
    background: #fffde7; border: 1.5px solid #fff176;
    border-radius: 14px; padding: 18px 22px;
    display: flex; align-items: flex-start; gap: 16px;
    margin-bottom: 28px;
    box-shadow: 0 2px 10px rgba(251,192,45,.12);
}
.tip-icon-wrap {
    width: 46px; height: 46px; border-radius: 12px;
    background: #fff9c4; display: flex; align-items: center;
    justify-content: center; font-size: 22px; flex-shrink: 0;
}
.tip-label { font-size: 11px; font-weight: 700; color: #f9a825;
             text-transform: uppercase; letter-spacing: .07em; margin-bottom: 4px; }
.tip-text  { font-size: 14px; color: #5d4037; line-height: 1.65; margin: 0; }
.tip-day   { font-size: 11px; color: #bcaaa4; margin-top: 5px; }

/* ── macro chart ── */
.macro-header {
    font-size: 17px; font-weight: 800; color: #1b5e20;
    margin: 0 0 4px 0; display: flex; align-items: center; gap: 8px;
}
.macro-sub { font-size: 12px; color: #81c784; margin-bottom: 16px; }
.macro-legend { display: flex; flex-direction: column; gap: 10px;
                justify-content: center; height: 100%; }
.macro-legend-item { display: flex; align-items: center; gap: 10px; }
.macro-dot { width: 13px; height: 13px; border-radius: 50%; flex-shrink: 0; }
.macro-legend-label { font-size: 13px; color: #555; }
.macro-legend-val   { font-size: 13px; font-weight: 700; color: #1b5e20; margin-left: auto; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TIME-OF-DAY LOGIC
# ═══════════════════════════════════════════════════════════════════════
hour = datetime.now().hour

if 5 <= hour < 12:
    greeting, sub_message, banner_emoji, bowl_icon, banner_class = (
        "Good morning", "Start your day with a nutritious meal", "🌅", "🍳", "banner-morning")
elif 12 <= hour < 17:
    greeting, sub_message, banner_emoji, bowl_icon, banner_class = (
        "Good afternoon", "Stay on track with your nutrition goals", "☀️", "🥗", "banner-afternoon")
elif 17 <= hour < 21:
    greeting, sub_message, banner_emoji, bowl_icon, banner_class = (
        "Good evening", "Wind down with a balanced dinner tonight", "🌇", "🍲", "banner-evening")
else:
    greeting, sub_message, banner_emoji, bowl_icon, banner_class = (
        "Still up?", "Healthy rest is part of the plan too", "🌙", "💤", "banner-night")

username = st.session_state.get("username", "User")

# ═══════════════════════════════════════════════════════════════════════
# DAILY HEALTH TIP
# ═══════════════════════════════════════════════════════════════════════
HEALTH_TIPS = [
    ("💧", "Drink water first thing", "Start your morning with a glass of water before anything else. It kickstarts your metabolism and rehydrates your body after sleep."),
    ("🥦", "Half your plate = vegetables", "Aim to fill at least half your plate with non-starchy vegetables at lunch and dinner. More colour means more nutrients."),
    ("🚶", "Walk after meals", "A 10–15 minute walk after eating helps lower blood sugar spikes and aids digestion. No gym needed!"),
    ("😴", "Sleep powers your diet", "Poor sleep increases hunger hormones (ghrelin) and reduces fullness hormones (leptin). Aim for 7–9 hours for better food choices."),
    ("🍽️", "Eat slowly, feel full sooner", "It takes about 20 minutes for your brain to register fullness. Put your fork down between bites to avoid overeating."),
    ("🥜", "Protein at every meal", "Including a protein source (eggs, legumes, chicken, tofu) at every meal helps you stay full longer and preserves muscle."),
    ("🫙", "Prep snacks in advance", "Pre-portioning healthy snacks like nuts, fruit, or yogurt removes the temptation to grab processed food when hunger hits."),
    ("🌿", "Herbs over salt", "Swap some salt for herbs and spices like turmeric, cumin, or oregano. You cut sodium and add anti-inflammatory benefits."),
    ("📏", "Mind your portions, not just ingredients", "Even healthy foods can lead to weight gain in large quantities. Use your hand as a rough guide — palm = protein, fist = veggies, cupped hand = carbs."),
    ("🧘", "Stress affects what you eat", "High stress raises cortisol, which triggers cravings for sugary, fatty foods. Even 5 minutes of deep breathing can help reset."),
    ("🥗", "Eat the rainbow", "Different coloured fruits and vegetables contain different antioxidants and vitamins. Try to include at least 3 colours in every meal."),
    ("⏰", "Don't skip breakfast", "A balanced breakfast stabilises blood sugar early in the day, reducing energy crashes and mid-morning snack cravings."),
    ("🫀", "Omega-3s for your heart", "Include fatty fish (salmon, sardines), walnuts, or flaxseeds a few times a week to support heart and brain health."),
    ("🍬", "Spot hidden sugar", "Sauces, flavoured yogurts, and fruit juices can contain as much sugar as a dessert. Check labels for 'added sugars'."),
    ("🥄", "Cook more, eat better", "Home-cooked meals average 30% fewer calories than restaurant meals. Even simple dishes give you full control over ingredients."),
]
today_index = date.today().toordinal() % len(HEALTH_TIPS)
tip_icon, tip_title, tip_text = HEALTH_TIPS[today_index]
tip_day = date.today().strftime("%A, %B %d")

# ═══════════════════════════════════════════════════════════════════════
# STREAK LOGIC
# ═══════════════════════════════════════════════════════════════════════
today_str = date.today().isoformat()

if "login_dates" not in st.session_state:
    st.session_state.login_dates = []
if today_str not in st.session_state.login_dates:
    st.session_state.login_dates.append(today_str)

def calculate_streak(login_dates):
    if not login_dates:
        return 0, 0
    unique_days = sorted(set(date.fromisoformat(d) for d in login_dates), reverse=True)
    run = 0
    prev = date.today()
    for d in unique_days:
        if (prev - d).days <= 1:
            run += 1
            prev = d
        else:
            break
    current = run
    run = 1
    longest = 1
    for i in range(1, len(unique_days)):
        if (unique_days[i - 1] - unique_days[i]).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    longest = max(longest, current)
    return current, longest

current_streak, longest_streak = calculate_streak(st.session_state.login_dates)

def streak_badge(n):
    if n >= 30: return "🏆"
    if n >= 14: return "🔥"
    if n >= 7:  return "⚡"
    if n >= 3:  return "✨"
    return "🌱"

streak_icon = streak_badge(current_streak)
streak_message = (
    "Amazing — keep it up!"  if current_streak >= 14 else
    "You're on a roll!"      if current_streak >= 7  else
    "Great consistency!"     if current_streak >= 3  else
    "Day 1 — let's go!"      if current_streak == 1  else
    "Come back tomorrow!"
)

# ═══════════════════════════════════════════════════════════════════════
# WATER TRACKER STATE
# ═══════════════════════════════════════════════════════════════════════
GLASSES_GOAL = 8
if "water_date" not in st.session_state or st.session_state.water_date != today_str:
    st.session_state.water_date   = today_str
    st.session_state.glasses_done = 0

# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    initial = username[0].upper() if username else "U"
    st.markdown(f"""
        <div style="padding:16px 4px 0 4px;">
            <div class="avatar">{initial}</div>
            <div class="user-name">{username}</div>
            <div class="user-sub">
                <i class="fa-solid fa-circle-check" style="color:#43a047;font-size:11px;"></i>
                Member
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Streak
    st.markdown(f"""
    <div style="background:#e8f5e9;border-radius:12px;padding:14px 16px;margin-bottom:12px;">
        <div style="font-size:11px;font-weight:700;color:#81c784;text-transform:uppercase;
             letter-spacing:.07em;margin-bottom:8px;">Login streak</div>
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="font-size:28px;line-height:1;">{streak_icon}</div>
            <div>
                <div style="font-size:24px;font-weight:800;color:#1b5e20;line-height:1.1;">
                    {current_streak} day{'s' if current_streak != 1 else ''}
                </div>
                <div style="font-size:11px;color:#558b2f;">{streak_message}</div>
            </div>
        </div>
        <div style="margin-top:10px;display:flex;justify-content:space-between;
             font-size:11px;color:#81c784;">
            <span>Best: <strong style="color:#1b5e20;">{longest_streak}d</strong></span>
            <span>Total logins: <strong style="color:#1b5e20;">{len(set(st.session_state.login_dates))}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Water tracker
    glasses   = st.session_state.glasses_done
    water_pct = int(glasses / GLASSES_GOAL * 100)
    water_color = "#2e7d32" if glasses >= GLASSES_GOAL else "#29b6f6"
    water_label = (
        "All done! Great job! 🎉" if glasses >= GLASSES_GOAL else
        f"{GLASSES_GOAL - glasses} glass{'es' if GLASSES_GOAL - glasses != 1 else ''} to go"
    )
    glass_icons = "".join(
        f'<span style="font-size:20px;line-height:1;{"" if i < glasses else "opacity:0.2;"}">💧</span>'
        for i in range(GLASSES_GOAL)
    )
    st.markdown(f"""
    <div style="background:#e3f2fd;border-radius:12px;padding:14px 16px;margin-bottom:10px;">
        <div style="font-size:11px;font-weight:700;color:#0288d1;text-transform:uppercase;
             letter-spacing:.07em;margin-bottom:10px;">💧 Water today</div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;">{glass_icons}</div>
        <div style="background:#fff;border-radius:8px;height:6px;margin-bottom:8px;overflow:hidden;">
            <div style="width:{water_pct}%;height:100%;background:{water_color};
                 border-radius:8px;transition:width .3s;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;">
            <span style="color:#0288d1;font-weight:600;">{glasses} / {GLASSES_GOAL} glasses</span>
            <span style="color:#90caf9;">{water_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("+ Add glass", use_container_width=True, disabled=glasses >= GLASSES_GOAL):
            st.session_state.glasses_done = min(glasses + 1, GLASSES_GOAL)
            st.rerun()
    with btn_col2:
        if st.button("↩ Undo", use_container_width=True, disabled=glasses == 0):
            st.session_state.glasses_done = max(glasses - 1, 0)
            st.rerun()

    st.divider()
    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button("Logout", icon=":material/logout:"):
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.switch_page("Hello.py")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# WELCOME BANNER
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="welcome-banner {banner_class}">
    <div class="welcome-left">
        <div class="welcome-text-h">{greeting}, {username}! {banner_emoji}</div>
        <div class="welcome-text-s">
            <i class="fa-solid fa-circle-check"></i>
            {sub_message}
        </div>
    </div>
    <div class="welcome-right">
        <div class="bottle-wrap">💧</div>
        <div class="bowl-wrap">{bowl_icon}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# DAILY HEALTH TIP CARD
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="tip-card">
    <div class="tip-icon-wrap">{tip_icon}</div>
    <div>
        <div class="tip-label">💡 Tip of the day</div>
        <p class="tip-text"><strong>{tip_title}.</strong> {tip_text}</p>
        <div class="tip-day">{tip_day}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# QUICK OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-heading"><i class="fa-solid fa-chart-bar" style="color:#43a047;"></i> Quick Overview</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("""<div class="stat-box">
        <div class="stat-icon-wrap"><i class="fa-solid fa-weight-scale"></i></div>
        <div class="stat-lbl">Healthy BMI</div><div class="stat-val">18.5–25</div>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown("""<div class="stat-box">
        <div class="stat-icon-wrap"><i class="fa-solid fa-clock"></i></div>
        <div class="stat-lbl">Meals / Day</div><div class="stat-val">3–5</div>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown("""<div class="stat-box">
        <div class="stat-icon-wrap"><i class="fa-solid fa-layer-group"></i></div>
        <div class="stat-lbl">Features</div><div class="stat-val">3</div>
    </div>""", unsafe_allow_html=True)
with s4:
    st.markdown(f"""<div class="stat-box">
        <div class="stat-icon-wrap"><div style="font-size:20px;line-height:1;">{streak_icon}</div></div>
        <div class="stat-lbl">Login Streak</div>
        <div class="stat-val">{current_streak}d</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# FEATURE CARDS  — fixed navigation using st.button + st.switch_page
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-heading"><i class="fa-solid fa-grid-2" style="color:#43a047;"></i> Choose a Feature</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feat-card">
        <img class="feat-card-img"
             src="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80"
             alt="Healthy meal bowl">
        <div class="feat-card-body">
            <div class="feat-card-title">💪 Diet Recommendation</div>
            <div class="feat-card-desc">Get personalised meal plans based on your age, weight,
            height, gender and activity level.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Plans", key="btn_diet", use_container_width=True):
        st.switch_page("pages/1_💪_Diet_Recommendation.py")

with c2:
    st.markdown("""
    <div class="feat-card">
        <img class="feat-card-img"
             src="https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600&q=80"
             alt="Recipe ingredients">
        <div class="feat-card-body">
            <div class="feat-card-title">🔍 Custom Food Recommendation</div>
            <div class="feat-card-desc">Search for recipes by specifying nutritional values and
            ingredients you want to include in your meals.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Find Recipes", key="btn_custom", use_container_width=True):
        st.switch_page("pages/2_🔍_Custom_Food_Recommendation.py")

with c3:
    st.markdown("""
    <div class="feat-card">
        <img class="feat-card-img"
             src="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&q=80"
             alt="Food photo tracking">
        <div class="feat-card-body">
            <div class="feat-card-title">📸 Image Food Tracking</div>
            <div class="feat-card-desc">Upload a food photo and let the AI detect the dish and
            display its full nutritional breakdown instantly.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Track Your Meals", key="btn_image", use_container_width=True):
        st.switch_page("pages/3_📸_Image_Food_Tracking.py")

st.page_link("pages/4_🥗_Daily_Nutrition_Tracker.py", label="Nutrition Tracker")
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# MACRO DOUGHNUT CHART
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="macro-header">
    <i class="fa-solid fa-chart-pie" style="color:#43a047;"></i>
    Today's Macro Breakdown
</div>
<div class="macro-sub">Adjust the sliders to match what you've eaten today</div>
""", unsafe_allow_html=True)

chart_col, controls_col = st.columns([1, 1], gap="large")

with controls_col:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    protein_g = st.slider("🥩 Protein (g)",       min_value=0, max_value=300, value=80,  step=5)
    carbs_g   = st.slider("🍚 Carbohydrates (g)", min_value=0, max_value=500, value=200, step=5)
    fat_g     = st.slider("🥑 Fat (g)",           min_value=0, max_value=200, value=60,  step=5)

    protein_kcal = protein_g * 4
    carbs_kcal   = carbs_g   * 4
    fat_kcal     = fat_g     * 9
    total_kcal   = protein_kcal + carbs_kcal + fat_kcal

    st.markdown(f"""
    <div style="background:#e8f5e9;border-radius:10px;padding:12px 16px;margin-top:12px;">
        <div style="font-size:11px;color:#81c784;font-weight:700;
             text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px;">
            Total estimated calories
        </div>
        <div style="font-size:26px;font-weight:800;color:#1b5e20;">{total_kcal} kcal</div>
        <div style="font-size:11px;color:#aaa;margin-top:2px;">
            Protein {protein_kcal} · Carbs {carbs_kcal} · Fat {fat_kcal}
        </div>
    </div>
    """, unsafe_allow_html=True)

with chart_col:
    if total_kcal == 0:
        st.info("Move the sliders to see your macro chart.")
    else:
        COLORS = ["#2e7d32", "#66bb6a", "#a5d6a7"]
        fig = go.Figure(go.Pie(
            labels=["Protein", "Carbs", "Fat"],
            values=[protein_kcal, carbs_kcal, fat_kcal],
            hole=0.62,
            marker=dict(colors=COLORS, line=dict(color="#ffffff", width=3)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} kcal (%{percent})<extra></extra>",
            sort=False,
        ))
        fig.add_annotation(
            text=f"<b>{total_kcal}</b><br><span style='font-size:11px'>kcal</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#1b5e20"), align="center",
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        pct = lambda v: round(v / total_kcal * 100) if total_kcal else 0
        st.markdown(f"""
        <div class="macro-legend">
            <div class="macro-legend-item">
                <div class="macro-dot" style="background:#2e7d32;"></div>
                <span class="macro-legend-label">Protein</span>
                <span class="macro-legend-val">{protein_g}g &nbsp;·&nbsp; {pct(protein_kcal)}%</span>
            </div>
            <div class="macro-legend-item">
                <div class="macro-dot" style="background:#66bb6a;"></div>
                <span class="macro-legend-label">Carbohydrates</span>
                <span class="macro-legend-val">{carbs_g}g &nbsp;·&nbsp; {pct(carbs_kcal)}%</span>
            </div>
            <div class="macro-legend-item">
                <div class="macro-dot" style="background:#a5d6a7;"></div>
                <span class="macro-legend-label">Fat</span>
                <span class="macro-legend-val">{fat_g}g &nbsp;·&nbsp; {pct(fat_kcal)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# 7-DAY CALORIE SPARKLINE
# ═══════════════════════════════════════════════════════════════════════
if "calorie_log" not in st.session_state:
    st.session_state.calorie_log = {}

today      = date.today()
week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
day_labels = [d.strftime("%a") for d in week_dates]
date_keys  = [d.isoformat() for d in week_dates]

calorie_values = [st.session_state.calorie_log.get(k, 0) for k in date_keys]
calorie_values[-1] = total_kcal
st.session_state.calorie_log[today.isoformat()] = total_kcal

DAILY_GOAL = 2000

st.markdown("""
<div class="section-heading" style="margin-bottom:4px;">
    <i class="fa-solid fa-chart-line" style="color:#43a047;"></i>
    7-Day Calorie History
</div>
<div style="font-size:12px;color:#81c784;margin-bottom:14px;">
    Today's total updates live from the macro sliders above
</div>
""", unsafe_allow_html=True)

spark_col, gap_col, log_col = st.columns([2.4, 0.2, 1.4])

with spark_col:
    filled_days = sum(1 for v in calorie_values if v > 0)
    avg_kcal    = round(sum(calorie_values) / filled_days) if filled_days else 0
    goal_line   = [DAILY_GOAL] * 7
    bar_colors  = ["#2e7d32" if v <= DAILY_GOAL else "#f57c00" for v in calorie_values]
    bar_colors[-1] = "#43a047" if calorie_values[-1] <= DAILY_GOAL else "#ff9800"

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=day_labels + day_labels[::-1], y=goal_line + [0] * 7,
        fill="toself", fillcolor="rgba(165,214,167,0.15)",
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", showlegend=False,
    ))
    fig2.add_trace(go.Bar(
        x=day_labels, y=calorie_values, marker_color=bar_colors,
        marker_line_width=0, width=0.55,
        hovertemplate="%{x}: <b>%{y} kcal</b><extra></extra>", showlegend=False,
    ))
    fig2.add_trace(go.Scatter(
        x=day_labels, y=goal_line, mode="lines",
        line=dict(color="#ef9a9a", width=1.5, dash="dot"),
        hovertemplate="Goal: <b>%{y} kcal</b><extra></extra>",
        showlegend=False, name="Goal",
    ))
    fig2.add_annotation(
        x=day_labels[-1], y=DAILY_GOAL,
        text=f"  goal {DAILY_GOAL}", showarrow=False,
        font=dict(size=10, color="#ef9a9a"), xanchor="left", yanchor="middle",
    )
    fig2.update_layout(
        height=220, margin=dict(t=10, b=0, l=0, r=60),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12, color="#555")),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,230,201,0.4)",
                   zeroline=False, tickfont=dict(size=11, color="#aaa"), rangemode="tozero"),
        bargap=0.3,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

with log_col:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    over_days = sum(1 for v in calorie_values if v > DAILY_GOAL)
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="background:#e8f5e9;border-radius:10px;padding:12px 16px;">
            <div style="font-size:11px;color:#81c784;font-weight:700;
                 text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px;">Weekly avg</div>
            <div style="font-size:22px;font-weight:800;color:#1b5e20;">{avg_kcal}</div>
            <div style="font-size:11px;color:#aaa;">kcal / day</div>
        </div>
        <div style="background:#{'fff3e0' if over_days > 0 else 'e8f5e9'};border-radius:10px;padding:12px 16px;">
            <div style="font-size:11px;color:#{'f57c00' if over_days > 0 else '81c784'};
                 font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px;">Over goal</div>
            <div style="font-size:22px;font-weight:800;color:#{'e65100' if over_days > 0 else '1b5e20'};">{over_days}</div>
            <div style="font-size:11px;color:#aaa;">day{'s' if over_days != 1 else ''} this week</div>
        </div>
        <div style="background:#e8f5e9;border-radius:10px;padding:12px 16px;">
            <div style="font-size:11px;color:#81c784;font-weight:700;
                 text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px;">Daily goal</div>
            <div style="font-size:22px;font-weight:800;color:#1b5e20;">{DAILY_GOAL}</div>
            <div style="font-size:11px;color:#aaa;">kcal target</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px;color:#555;font-weight:600;margin-bottom:4px;'>Log a past day</div>", unsafe_allow_html=True)
    log_day_label = st.selectbox("Day", options=day_labels[:-1], label_visibility="collapsed")
    log_kcal = st.number_input("kcal", min_value=0, max_value=5000, value=0, step=50,
                               label_visibility="collapsed", placeholder="Enter kcal…")
    if st.button("Save", use_container_width=True):
        idx = day_labels[:-1].index(log_day_label)
        st.session_state.calorie_log[date_keys[idx]] = log_kcal
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="info-footer">
    <i class="fa-solid fa-circle-info" style="color:#81c784;"></i>
    Use the sidebar to navigate between pages. Click <strong>Logout</strong> to sign out safely.
</div>
""", unsafe_allow_html=True)