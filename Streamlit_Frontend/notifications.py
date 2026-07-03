import streamlit as st
from datetime import datetime, timedelta
import json
import os

# ─────────────────────────────────────────
# Notification definitions
# ─────────────────────────────────────────

DAILY_CHALLENGES = [
    "Eat at least 30g of protein today",
    "Drink 8 full glasses of water today",
    "Include a green vegetable in every meal",
    "Avoid fried food for the whole day",
    "Eat 3 balanced meals — no skipping!",
    "Try one new Indian dish from the recommendations",
    "Keep your calorie intake under your daily target",
]

MEAL_TIMES = {
    "Breakfast": (7, 9),    # 7 AM – 9 AM
    "Lunch":     (12, 14),  # 12 PM – 2 PM
    "Dinner":    (19, 21),  # 7 PM – 9 PM
}

# ─────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────

def init_notifications():
    if "notif_dismissed"  not in st.session_state:
        st.session_state.notif_dismissed = {}   # {notif_id: dismissed_until (datetime or None)}
    if "water_glasses"    not in st.session_state:
        st.session_state.water_glasses = 0
    if "challenge_done"   not in st.session_state:
        st.session_state.challenge_done = False
    if "snooze_until"     not in st.session_state:
        st.session_state.snooze_until = {}      # {notif_id: datetime}

# ─────────────────────────────────────────
# Helper — check if notification is snoozed
# ─────────────────────────────────────────

def is_snoozed(notif_id):
    snooze = st.session_state.snooze_until.get(notif_id)
    if snooze and datetime.now() < snooze:
        return True
    return False

def is_dismissed(notif_id):
    return st.session_state.notif_dismissed.get(notif_id, False)

def dismiss(notif_id):
    st.session_state.notif_dismissed[notif_id] = True

def snooze(notif_id):
    st.session_state.snooze_until[notif_id] = datetime.now() + timedelta(hours=1)

# ─────────────────────────────────────────
# Build active notifications list
# ─────────────────────────────────────────

def get_active_notifications():
    now        = datetime.now()
    hour       = now.hour
    day_of_week = now.weekday()  # 6 = Sunday
    notifications = []

    # 1. Water intake reminder — every 2 hours
    water_notif_id = f"water_{hour // 2}"
    if not is_snoozed(water_notif_id) and not is_dismissed(water_notif_id):
        glasses = st.session_state.water_glasses
        if glasses < 8:
            notifications.append({
                "id":      water_notif_id,
                "type":    "water",
                "icon":    "fa-droplet",
                "color":   "#1565c0",
                "light":   "#e3f2fd",
                "border":  "#90caf9",
                "title":   "Hydration Reminder",
                "message": f"You've had {glasses}/8 glasses of water today. Time to drink up!",
                "action":  "Log a glass",
            })

    # 2. Meal time reminders
    for meal, (start, end) in MEAL_TIMES.items():
        notif_id = f"meal_{meal}_{now.date()}"
        if start <= hour < end:
            if not is_snoozed(notif_id) and not is_dismissed(notif_id):
                notifications.append({
                    "id":      notif_id,
                    "type":    "meal",
                    "icon":    "fa-utensils",
                    "color":   "#6eb52f",
                    "light":   "#f0f8e8",
                    "border":  "#c8e6a0",
                    "title":   f"{meal} Time!",
                    "message": f"It's time for your {meal.lower()}. Have you followed your meal plan today?",
                    "action":  "View meal plan",
                })

    # 3. Weekly nutrition report — every Sunday
    notif_id = f"weekly_report_{now.date()}"
    if day_of_week == 6 and not is_snoozed(notif_id) and not is_dismissed(notif_id):
        notifications.append({
            "id":      notif_id,
            "type":    "report",
            "icon":    "fa-chart-line",
            "color":   "#6a1b9a",
            "light":   "#f3e5f5",
            "border":  "#ce93d8",
            "title":   "Weekly Nutrition Report Ready",
            "message": "Your weekly nutrition summary is ready. Check how well you tracked your diet this week!",
            "action":  "View report",
        })

    # 4. Daily health challenge
    notif_id = f"challenge_{now.date()}"
    if not is_dismissed(notif_id) and not st.session_state.challenge_done:
        challenge = DAILY_CHALLENGES[now.day % len(DAILY_CHALLENGES)]
        notifications.append({
            "id":      notif_id,
            "type":    "challenge",
            "icon":    "fa-fire",
            "color":   "#e65100",
            "light":   "#fff3e0",
            "border":  "#ffcc80",
            "title":   "Daily Health Challenge",
            "message": challenge,
            "action":  "Mark complete",
        })

    return notifications

# ─────────────────────────────────────────
# Render notifications — floating popup style
# ─────────────────────────────────────────

def render_notifications():
    init_notifications()

    # Font Awesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .notif-container {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 340px;
        width: 340px;
    }
    .notif-popup {
        background: #fff;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: 0.5px solid #eee;
        animation: slideIn 0.3s ease;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(40px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    .notif-header {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .notif-ico {
        width: 36px; height: 36px;
        border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .notif-ico i { font-size: 15px; }
    .notif-title-text {
        font-size: 13px;
        font-weight: 700;
        color: #1a1a2e;
        flex: 1;
    }
    .notif-msg {
        font-size: 12px;
        color: #555;
        line-height: 1.5;
        padding-left: 46px;
    }
    .notif-btns {
        display: flex;
        gap: 6px;
        padding-left: 46px;
    }
    .notif-btn-action {
        font-size: 11px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 99px;
        cursor: pointer;
    }
    .notif-btn-snooze {
        font-size: 11px;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 99px;
        background: #f0f0f5;
        color: #555;
        cursor: pointer;
    }
    .notif-btn-dismiss {
        font-size: 11px;
        color: #bbb;
        padding: 5px 8px;
        cursor: pointer;
        margin-left: auto;
    }

    /* Bell icon toggle */
    .notif-bell-wrap {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9998;
    }
    .notif-bell {
        width: 48px; height: 48px;
        border-radius: 50%;
        background: #6eb52f;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 16px rgba(110,181,47,0.4);
        cursor: pointer;
    }
    .notif-bell i { color: #fff; font-size: 20px; }
    .notif-count {
        position: absolute;
        top: -2px; right: -2px;
        width: 18px; height: 18px;
        border-radius: 50%;
        background: #c62828;
        color: #fff;
        font-size: 10px;
        font-weight: 700;
        display: flex; align-items: center; justify-content: center;
        border: 2px solid #fff;
    }

    /* Water tracker */
    .water-track {
        display: flex; gap: 4px; padding-left: 46px;
    }
    .water-glass {
        width: 18px; height: 22px;
        border-radius: 3px;
        border: 1.5px solid #90caf9;
        background: #e3f2fd;
        display: flex; align-items: center; justify-content: center;
        font-size: 8px;
    }
    .water-glass.filled { background: #1565c0; border-color: #1565c0; }
    .water-glass.filled::after { content: ""; }
    </style>
    """, unsafe_allow_html=True)

    notifications = get_active_notifications()

    if not notifications:
        return

    # Show bell icon with count
    count = len(notifications)
    st.markdown(f"""
    <div style="position:fixed;bottom:24px;right:24px;z-index:9998;">
        <div style="width:48px;height:48px;border-radius:50%;background:#6eb52f;
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 4px 16px rgba(110,181,47,0.4);position:relative;">
            <i class="fa-solid fa-bell" style="color:#fff;font-size:20px;"></i>
            <div style="position:absolute;top:-2px;right:-2px;width:18px;height:18px;
            border-radius:50%;background:#c62828;color:#fff;font-size:10px;font-weight:700;
            display:flex;align-items:center;justify-content:center;border:2px solid #fff;">
                {count}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show notification popups
    st.markdown('<div class="notif-container">', unsafe_allow_html=True)

    for notif in notifications:
        nid   = notif["id"]
        color = notif["color"]
        light = notif["light"]
        bord  = notif["border"]

        # Water glasses tracker visual
        water_html = ""
        if notif["type"] == "water":
            glasses = st.session_state.water_glasses
            glasses_html = "".join([
                f'<div class="water-glass {"filled" if i < glasses else ""}"></div>'
                for i in range(8)
            ])
            water_html = f'<div class="water-track">{glasses_html}</div>'

        st.markdown(f"""
        <div class="notif-popup" id="notif-{nid}">
            <div class="notif-header">
                <div class="notif-ico" style="background:{light};border:0.5px solid {bord};">
                    <i class="fa-solid {notif['icon']}" style="color:{color};"></i>
                </div>
                <div class="notif-title-text">{notif['title']}</div>
            </div>
            <div class="notif-msg">{notif['message']}</div>
            {water_html}
        </div>
        """, unsafe_allow_html=True)

        # Action buttons using Streamlit buttons
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if st.button(
                f"✓  {notif['action']}",
                key=f"action_{nid}",
                use_container_width=True
            ):
                # Handle specific actions
                if notif["type"] == "water":
                    st.session_state.water_glasses = min(8, st.session_state.water_glasses + 1)
                elif notif["type"] == "challenge":
                    st.session_state.challenge_done = True
                dismiss(nid)
                st.rerun()

        with col2:
            if st.button(
                "⏰  Snooze 1hr",
                key=f"snooze_{nid}",
                use_container_width=True
            ):
                snooze(nid)
                st.rerun()

        with col3:
            if st.button(
                "✕",
                key=f"dismiss_{nid}",
                use_container_width=True
            ):
                dismiss(nid)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# Notification bell + panel for sidebar
# ─────────────────────────────────────────

def render_notification_summary():
    """Show a compact summary in sidebar or home page."""
    init_notifications()
    notifications = get_active_notifications()

    if not notifications:
        st.markdown("""
        <div style="background:#f0f8e8;border-radius:10px;padding:12px 14px;
        border:0.5px solid #c8e6a0;font-size:12px;color:#2e7d32;text-align:center;">
            <i class="fa-solid fa-circle-check" style="margin-right:6px;"></i>
            All caught up! No reminders right now.
        </div>
        """, unsafe_allow_html=True)
        return

    for notif in notifications[:2]:  # Show max 2 in summary
        color = notif["color"]
        light = notif["light"]
        bord  = notif["border"]
        st.markdown(f"""
        <div style="background:{light};border-radius:10px;padding:12px 14px;
        border:0.5px solid {bord};margin-bottom:8px;display:flex;gap:10px;align-items:flex-start;">
            <i class="fa-solid {notif['icon']}" style="color:{color};font-size:14px;margin-top:2px;flex-shrink:0;"></i>
            <div>
                <div style="font-size:12px;font-weight:600;color:#1a1a2e;margin-bottom:2px;">{notif['title']}</div>
                <div style="font-size:11px;color:#555;line-height:1.5;">{notif['message'][:80]}...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)