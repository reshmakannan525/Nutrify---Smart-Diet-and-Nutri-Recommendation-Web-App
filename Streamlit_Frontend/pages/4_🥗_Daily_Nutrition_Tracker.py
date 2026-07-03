import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import io
import sys
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Nutrition Tracker",
    page_icon="🥗",
    layout="wide"
)

# ── Auth guard ────────────────────────────────────────────────
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Hello.py")

# ── Font Awesome ──────────────────────────────────────────────
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">', unsafe_allow_html=True)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
[data-testid="stAppViewContainer"] { background: #f0f4f0; }
[data-testid="stHeader"] { display: none; }
.block-container { padding: 1.5rem 2rem !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e8f5e9 !important; }
[data-testid="stSidebarNav"] { display: none; }
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

/* Page header */
.page-header { background: linear-gradient(135deg, #1b5e20, #6eb52f); border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; }
.page-header-left h1 { font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 6px; }
.page-header-left p { font-size: 13px; color: #d4edaa; margin: 0; }
.page-header-icon { width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; }
.page-header-icon i { color: #fff; font-size: 30px; }

/* Section title */
.sec-title { font-size: 16px; font-weight: 700; color: #1b5e20; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; border-left: 4px solid #6eb52f; padding-left: 10px; }
.sec-title i { color: #6eb52f; }

/* Glassmorphism cards */
.glass-card { background: rgba(255,255,255,0.85); backdrop-filter: blur(10px); border: 1px solid rgba(110,181,47,0.2); border-radius: 16px; padding: 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.07); margin-bottom: 16px; }

/* Nutrient cards grid */
.nutrient-grid { display: grid; grid-template-columns: repeat(6, minmax(0,1fr)); gap: 10px; margin-bottom: 20px; }
.nutrient-card { background: #fff; border-radius: 12px; padding: 14px 10px; text-align: center; border: 1.5px solid #e8f5e9; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.nutrient-card:hover { border-color: #6eb52f; transform: translateY(-2px); transition: all 0.2s; }
.nutrient-icon { font-size: 20px; margin-bottom: 6px; }
.nutrient-val { font-size: 18px; font-weight: 800; color: #1b5e20; margin-bottom: 2px; }
.nutrient-unit { font-size: 10px; color: #81c784; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.nutrient-lbl { font-size: 11px; color: #555; }

/* Progress bars */
.prog-wrap { margin-bottom: 14px; }
.prog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.prog-label { font-size: 13px; font-weight: 600; color: #333; display: flex; align-items: center; gap: 7px; }
.prog-label i { color: #6eb52f; font-size: 13px; }
.prog-values { font-size: 12px; color: #666; }
.prog-bar-bg { background: #e8f5e9; border-radius: 99px; height: 10px; overflow: hidden; }
.prog-bar-fill { border-radius: 99px; height: 10px; transition: width 0.5s ease; }
.prog-pct { font-size: 11px; color: #81c784; margin-top: 3px; text-align: right; }

/* Health status */
.status-card { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; margin-bottom: 8px; }
.status-excellent { background: #e8f5e9; border: 1px solid #c8e6c9; }
.status-warning    { background: #fff3e0; border: 1px solid #ffcc80; }
.status-danger     { background: #ffebee; border: 1px solid #ef9a9a; }
.status-ok         { background: #e3f2fd; border: 1px solid #90caf9; }
.status-icon { font-size: 18px; }
.status-text { font-size: 13px; font-weight: 600; }
.status-excellent .status-text { color: #2e7d32; }
.status-warning    .status-text { color: #e65100; }
.status-danger     .status-text { color: #c62828; }
.status-ok         .status-text { color: #1565c0; }

/* Dashboard mini cards */
.dash-grid { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 10px; margin-bottom: 20px; }
.dash-card { background: #fff; border-radius: 12px; padding: 14px; border: 1.5px solid #e8f5e9; text-align: center; }
.dash-val { font-size: 20px; font-weight: 800; color: #1b5e20; margin-bottom: 2px; }
.dash-lbl { font-size: 11px; color: #81c784; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.dash-remain { font-size: 11px; color: #aaa; margin-top: 3px; }

/* Meal log */
.meal-section { background: #fff; border-radius: 14px; padding: 18px; border: 1.5px solid #e8f5e9; margin-bottom: 12px; }
.meal-title { font-size: 14px; font-weight: 700; color: #1b5e20; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.meal-title i { color: #6eb52f; }
.food-tag { display: inline-block; background: #e8f5e9; color: #2e7d32; border-radius: 99px; padding: 3px 10px; font-size: 11px; font-weight: 600; margin: 3px; }

/* History table */
.history-card { background: #fff; border-radius: 14px; padding: 18px; border: 1.5px solid #e8f5e9; }

/* Buttons */
.stButton > button { border-radius: 8px !important; background-color: #6eb52f !important; color: white !important; font-weight: 600 !important; border: none !important; }
.stButton > button:hover { background-color: #5a9a24 !important; }

/* Step badge */
.step-badge { background: #6eb52f; color: #fff; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-block; margin-bottom: 8px; }

/* Circular progress container */
.circ-row { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; }

/* Medical condition tip cards */                                              /* 🆕 */
.medcond-card { background:#fff; border-radius:12px; padding:14px 18px; border:1.5px solid #e8f5e9; border-left:4px solid #6eb52f; margin-bottom:10px; }
.medcond-name { font-size:13px; font-weight:700; color:#1b5e20; margin-bottom:4px; }
.medcond-tip  { font-size:12px; color:#555; }
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ─────────────────────────────
username = st.session_state.get("username", "User")
today_str = date.today().isoformat()

defaults = {
    "tracker_calculated":  False,
    "tracker_goals":       {},
    "tracker_meals":       {"Breakfast": [], "Morning Snack": [], "Lunch": [], "Evening Snack": [], "Dinner": []},
    "tracker_consumed":    {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "sugar": 0, "water": 0},
    "tracker_history":     {},
    "tracker_date":        today_str,
    "tracker_medical_conditions": [],   # 🆕
    "toast_message": None,              # 🆕 queued toast shown right after a rerun
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 🆕 Show a queued toast (set right before the st.rerun() that triggered
# this run, since st.toast() calls made right before rerun get lost).
if st.session_state.get("toast_message"):
    st.toast(st.session_state.toast_message, icon="✅")
    st.session_state.toast_message = None

# Reset if new day
if st.session_state.tracker_date != today_str:
    st.session_state.tracker_date    = today_str
    st.session_state.tracker_meals   = {m: [] for m in ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"]}
    st.session_state.tracker_consumed = {k: 0 for k in ["calories", "protein", "carbs", "fat", "fiber", "sugar", "water"]}

# ── Food database ─────────────────────────────────────────────
FOOD_DB = {
    "Roti (Whole Wheat)":     {"calories": 120, "protein": 3.5, "carbs": 22,  "fat": 1.5, "fiber": 3.0, "sugar": 0.5, "water": 0.0},
    "Rice (White, Cooked)":   {"calories": 200, "protein": 4.0, "carbs": 45,  "fat": 0.5, "fiber": 0.6, "sugar": 0.1, "water": 0.1},
    "Dal Tadka":              {"calories": 180, "protein": 9.0, "carbs": 20,  "fat": 8.0, "fiber": 5.0, "sugar": 2.0, "water": 0.2},
    "Chole Masala":           {"calories": 220, "protein": 8.0, "carbs": 30,  "fat": 9.0, "fiber": 6.0, "sugar": 3.0, "water": 0.2},
    "Butter Chicken":         {"calories": 350, "protein": 20,  "carbs": 10,  "fat": 25,  "fiber": 1.0, "sugar": 4.0, "water": 0.1},
    "Paneer Butter Masala":   {"calories": 300, "protein": 12,  "carbs": 15,  "fat": 22,  "fiber": 2.0, "sugar": 5.0, "water": 0.1},
    "Palak Paneer":           {"calories": 250, "protein": 10,  "carbs": 15,  "fat": 18,  "fiber": 3.0, "sugar": 3.0, "water": 0.2},
    "Chicken Biryani":        {"calories": 400, "protein": 20,  "carbs": 50,  "fat": 15,  "fiber": 2.0, "sugar": 2.0, "water": 0.1},
    "Vegetable Biryani":      {"calories": 300, "protein": 8.0, "carbs": 50,  "fat": 8.0, "fiber": 4.0, "sugar": 3.0, "water": 0.1},
    "Idli":                   {"calories": 140, "protein": 4.0, "carbs": 28,  "fat": 1.0, "fiber": 1.5, "sugar": 0.5, "water": 0.3},
    "Dosa (Plain)":           {"calories": 160, "protein": 4.0, "carbs": 30,  "fat": 2.0, "fiber": 1.0, "sugar": 0.5, "water": 0.1},
    "Masala Dosa":            {"calories": 250, "protein": 6.0, "carbs": 40,  "fat": 8.0, "fiber": 2.0, "sugar": 1.0, "water": 0.1},
    "Poha":                   {"calories": 180, "protein": 4.0, "carbs": 30,  "fat": 5.0, "fiber": 2.0, "sugar": 2.0, "water": 0.1},
    "Upma":                   {"calories": 200, "protein": 5.0, "carbs": 35,  "fat": 5.0, "fiber": 2.5, "sugar": 1.5, "water": 0.1},
    "Aloo Paratha":           {"calories": 280, "protein": 6.0, "carbs": 40,  "fat": 12,  "fiber": 3.0, "sugar": 1.0, "water": 0.0},
    "Samosa":                 {"calories": 260, "protein": 4.0, "carbs": 30,  "fat": 14,  "fiber": 2.0, "sugar": 1.0, "water": 0.0},
    "Dhokla":                 {"calories": 150, "protein": 5.0, "carbs": 25,  "fat": 4.0, "fiber": 2.0, "sugar": 3.0, "water": 0.1},
    "Rajma Masala":           {"calories": 200, "protein": 8.0, "carbs": 30,  "fat": 6.0, "fiber": 7.0, "sugar": 2.0, "water": 0.2},
    "Pav Bhaji":              {"calories": 250, "protein": 6.0, "carbs": 35,  "fat": 10,  "fiber": 3.0, "sugar": 4.0, "water": 0.1},
    "Vada Pav":               {"calories": 250, "protein": 5.0, "carbs": 35,  "fat": 10,  "fiber": 2.0, "sugar": 2.0, "water": 0.0},
    "Pani Puri":              {"calories": 150, "protein": 3.0, "carbs": 25,  "fat": 5.0, "fiber": 2.0, "sugar": 3.0, "water": 0.1},
    "Fish Curry (Rohu)":      {"calories": 220, "protein": 18,  "carbs": 8.0, "fat": 12,  "fiber": 1.0, "sugar": 2.0, "water": 0.2},
    "Mutton Rogan Josh":      {"calories": 350, "protein": 20,  "carbs": 10,  "fat": 25,  "fiber": 1.0, "sugar": 2.0, "water": 0.1},
    "Paratha (Plain)":        {"calories": 220, "protein": 5.0, "carbs": 30,  "fat": 9.0, "fiber": 2.0, "sugar": 0.5, "water": 0.0},
    "Egg Bhurji":             {"calories": 200, "protein": 14,  "carbs": 5.0, "fat": 14,  "fiber": 0.5, "sugar": 1.0, "water": 0.0},
    "Banana":                 {"calories": 89,  "protein": 1.1, "carbs": 23,  "fat": 0.3, "fiber": 2.6, "sugar": 12,  "water": 0.1},
    "Apple":                  {"calories": 52,  "protein": 0.3, "carbs": 14,  "fat": 0.2, "fiber": 2.4, "sugar": 10,  "water": 0.2},
    "Milk (1 glass)":         {"calories": 120, "protein": 6.0, "carbs": 12,  "fat": 5.0, "fiber": 0.0, "sugar": 12,  "water": 0.25},
    "Curd / Yogurt":          {"calories": 100, "protein": 5.0, "carbs": 10,  "fat": 4.0, "fiber": 0.0, "sugar": 8.0, "water": 0.2},
    "Tea (with milk)":        {"calories": 40,  "protein": 1.0, "carbs": 5.0, "fat": 1.5, "fiber": 0.0, "sugar": 4.0, "water": 0.15},
    "Coffee (with milk)":     {"calories": 50,  "protein": 1.5, "carbs": 6.0, "fat": 2.0, "fiber": 0.0, "sugar": 5.0, "water": 0.15},
    "Water (1 glass)":        {"calories": 0,   "protein": 0.0, "carbs": 0.0, "fat": 0.0, "fiber": 0.0, "sugar": 0.0, "water": 0.25},
    "Boiled Eggs (2)":        {"calories": 155, "protein": 13,  "carbs": 1.1, "fat": 11,  "fiber": 0.0, "sugar": 1.0, "water": 0.0},
    "Oats":                   {"calories": 150, "protein": 5.0, "carbs": 27,  "fat": 2.5, "fiber": 4.0, "sugar": 1.0, "water": 0.1},
    "Almonds (handful)":      {"calories": 160, "protein": 6.0, "carbs": 6.0, "fat": 14,  "fiber": 3.5, "sugar": 1.0, "water": 0.0},
    "Orange":                 {"calories": 62,  "protein": 1.2, "carbs": 15,  "fat": 0.2, "fiber": 3.1, "sugar": 12,  "water": 0.2},

    # ── 🆕 Healthy additions (no fried snacks, no desserts/sweets) ──
    # Breakfast
    "Besan Chilla (2 pcs)":       {"calories": 160, "protein": 8.0,  "carbs": 18,  "fat": 6.0,  "fiber": 3.0, "sugar": 2.0, "water": 0.1},
    "Sabudana Khichdi":           {"calories": 250, "protein": 4.0,  "carbs": 40,  "fat": 8.0,  "fiber": 2.0, "sugar": 1.0, "water": 0.1},
    "Sprouts Salad":              {"calories": 120, "protein": 8.0,  "carbs": 18,  "fat": 2.0,  "fiber": 6.0, "sugar": 3.0, "water": 0.2},
    "Bread Omelette (2 Egg)":     {"calories": 220, "protein": 14,   "carbs": 18,  "fat": 11,   "fiber": 1.0, "sugar": 2.0, "water": 0.0},
    "Moong Dal Cheela (2 pcs)":   {"calories": 180, "protein": 10,   "carbs": 22,  "fat": 5.0,  "fiber": 4.0, "sugar": 1.0, "water": 0.1},
    "Vegetable Oats":             {"calories": 180, "protein": 6.0,  "carbs": 28,  "fat": 4.0,  "fiber": 5.0, "sugar": 2.0, "water": 0.2},
    "Ragi Dosa":                  {"calories": 150, "protein": 4.0,  "carbs": 28,  "fat": 2.5,  "fiber": 3.0, "sugar": 1.0, "water": 0.1},
    "Multigrain Toast (2 slices)":{"calories": 160, "protein": 6.0,  "carbs": 28,  "fat": 3.0,  "fiber": 4.0, "sugar": 2.0, "water": 0.0},

    # South Indian
    "Sambar":                     {"calories": 150, "protein": 6.0,  "carbs": 20,  "fat": 5.0,  "fiber": 5.0, "sugar": 3.0, "water": 0.3},
    "Uttapam (Plain)":            {"calories": 180, "protein": 5.0,  "carbs": 32,  "fat": 3.0,  "fiber": 2.0, "sugar": 1.0, "water": 0.1},
    "Rava Idli (3 pcs)":          {"calories": 170, "protein": 5.0,  "carbs": 30,  "fat": 3.0,  "fiber": 1.5, "sugar": 1.0, "water": 0.2},
    "Curd Rice":                  {"calories": 200, "protein": 6.0,  "carbs": 32,  "fat": 5.0,  "fiber": 1.0, "sugar": 4.0, "water": 0.3},
    "Lemon Rice":                 {"calories": 210, "protein": 4.0,  "carbs": 38,  "fat": 5.0,  "fiber": 1.5, "sugar": 1.0, "water": 0.1},
    "Bisi Bele Bath":             {"calories": 260, "protein": 7.0,  "carbs": 42,  "fat": 7.0,  "fiber": 4.0, "sugar": 2.0, "water": 0.2},

    # Protein sources
    "Paneer Tikka (Grilled)":     {"calories": 220, "protein": 15,   "carbs": 6.0, "fat": 15,   "fiber": 1.0, "sugar": 2.0, "water": 0.1},
    "Grilled Chicken Breast":     {"calories": 250, "protein": 40,   "carbs": 0.0, "fat": 8.0,  "fiber": 0.0, "sugar": 0.0, "water": 0.1},
    "Grilled Fish (Pomfret)":     {"calories": 200, "protein": 30,   "carbs": 0.0, "fat": 8.0,  "fiber": 0.0, "sugar": 0.0, "water": 0.1},
    "Chicken Tikka":              {"calories": 220, "protein": 28,   "carbs": 4.0, "fat": 10,   "fiber": 0.5, "sugar": 1.0, "water": 0.1},
    "Sprouts Chaat":              {"calories": 130, "protein": 8.0,  "carbs": 18,  "fat": 2.5,  "fiber": 6.0, "sugar": 4.0, "water": 0.2},
    "Protein Shake (Whey)":       {"calories": 120, "protein": 24,   "carbs": 3.0, "fat": 1.5,  "fiber": 0.0, "sugar": 1.0, "water": 0.2},
    "Soya Chunks Curry":          {"calories": 200, "protein": 20,   "carbs": 15,  "fat": 8.0,  "fiber": 5.0, "sugar": 2.0, "water": 0.2},
    "Tofu Stir-fry":              {"calories": 180, "protein": 14,   "carbs": 10,  "fat": 10,   "fiber": 3.0, "sugar": 2.0, "water": 0.1},
    "Peanut Butter (1 tbsp)":     {"calories": 95,  "protein": 4.0,  "carbs": 3.0, "fat": 8.0,  "fiber": 1.0, "sugar": 1.0, "water": 0.0},
    "Boiled Chickpeas (Chana)":   {"calories": 165, "protein": 9.0,  "carbs": 27,  "fat": 2.5,  "fiber": 8.0, "sugar": 5.0, "water": 0.2},
    "Boiled Moong":               {"calories": 105, "protein": 7.0,  "carbs": 19,  "fat": 0.4,  "fiber": 7.0, "sugar": 2.0, "water": 0.2},
    "Egg Whites (2, Boiled)":     {"calories": 34,  "protein": 7.0,  "carbs": 0.5, "fat": 0.1,  "fiber": 0.0, "sugar": 0.5, "water": 0.0},

    # Beverages
    "Buttermilk (Chaas)":         {"calories": 40,  "protein": 2.0,  "carbs": 4.0, "fat": 1.5,  "fiber": 0.0, "sugar": 3.0, "water": 0.25},
    "Fresh Lime Water (No Sugar)":{"calories": 10,  "protein": 0.1,  "carbs": 2.5, "fat": 0.0,  "fiber": 0.2, "sugar": 1.0, "water": 0.25},
    "Coconut Water":              {"calories": 45,  "protein": 1.7,  "carbs": 9.0, "fat": 0.5,  "fiber": 2.6, "sugar": 6.0, "water": 0.24},
    "Green Tea":                  {"calories": 2,   "protein": 0.0,  "carbs": 0.5, "fat": 0.0,  "fiber": 0.0, "sugar": 0.0, "water": 0.24},
    "Vegetable Juice":            {"calories": 50,  "protein": 2.0,  "carbs": 10,  "fat": 0.2,  "fiber": 2.0, "sugar": 6.0, "water": 0.25},

    # Fruits & veg
    "Mango":                      {"calories": 99,  "protein": 1.4,  "carbs": 25,  "fat": 0.6,  "fiber": 2.6, "sugar": 23,  "water": 0.15},
    "Grapes (1 cup)":             {"calories": 104, "protein": 1.1,  "carbs": 27,  "fat": 0.2,  "fiber": 1.4, "sugar": 23,  "water": 0.15},
    "Papaya":                     {"calories": 59,  "protein": 0.9,  "carbs": 15,  "fat": 0.2,  "fiber": 2.5, "sugar": 11,  "water": 0.2},
    "Pomegranate":                {"calories": 83,  "protein": 1.7,  "carbs": 19,  "fat": 1.2,  "fiber": 4.0, "sugar": 14,  "water": 0.15},
    "Watermelon (1 cup)":         {"calories": 46,  "protein": 0.9,  "carbs": 12,  "fat": 0.2,  "fiber": 0.6, "sugar": 9.0, "water": 0.3},
    "Cucumber (Salad)":           {"calories": 16,  "protein": 0.7,  "carbs": 4.0, "fat": 0.1,  "fiber": 0.5, "sugar": 2.0, "water": 0.3},
    "Mixed Vegetable Salad":      {"calories": 90,  "protein": 3.0,  "carbs": 14,  "fat": 3.0,  "fiber": 5.0, "sugar": 5.0, "water": 0.3},
    "Guava":                      {"calories": 68,  "protein": 2.6,  "carbs": 14,  "fat": 1.0,  "fiber": 5.0, "sugar": 8.0, "water": 0.2},
    "Carrot Sticks":              {"calories": 41,  "protein": 0.9,  "carbs": 10,  "fat": 0.2,  "fiber": 2.8, "sugar": 5.0, "water": 0.2},

    # Continental / global healthy staples
    "Grilled Chicken Salad":      {"calories": 280, "protein": 30,   "carbs": 12,  "fat": 12,   "fiber": 4.0, "sugar": 4.0, "water": 0.2},
    "Vegetable Soup":             {"calories": 90,  "protein": 3.0,  "carbs": 15,  "fat": 2.0,  "fiber": 3.0, "sugar": 4.0, "water": 0.4},
    "Quinoa Salad":               {"calories": 220, "protein": 8.0,  "carbs": 35,  "fat": 6.0,  "fiber": 5.0, "sugar": 2.0, "water": 0.15},
    "Brown Rice (Cooked)":        {"calories": 215, "protein": 5.0,  "carbs": 45,  "fat": 1.8,  "fiber": 3.5, "sugar": 0.5, "water": 0.1},
    "Steamed Mixed Vegetables":   {"calories": 70,  "protein": 3.0,  "carbs": 12,  "fat": 0.5,  "fiber": 4.0, "sugar": 4.0, "water": 0.3},
    "Whole Wheat Veg Sandwich":   {"calories": 220, "protein": 8.0,  "carbs": 35,  "fat": 6.0,  "fiber": 5.0, "sugar": 3.0, "water": 0.1},
    "Greek Yogurt":               {"calories": 100, "protein": 17,   "carbs": 6.0, "fat": 0.5,  "fiber": 0.0, "sugar": 6.0, "water": 0.15},
}

MEAL_ICONS = {
    "Breakfast":     "fa-sun",
    "Morning Snack": "fa-apple-whole",
    "Lunch":         "fa-bowl-food",
    "Evening Snack": "fa-cookie-bite",
    "Dinner":        "fa-moon",
}

# ============================================================
# 🆕 MEDICAL CONDITIONS CONFIG (mirrors the Diet Recommendation
# page, but adjustments target THIS page's nutrient keys:
# calories, protein, carbs, fat, fiber, sugar, sodium — plus
# direct micronutrient target overrides for calcium, iron,
# vitd, vitc, vitb12, potassium where relevant).
# Selecting nothing reproduces the exact old behavior.
# ============================================================
MEDICAL_CONDITIONS_BY_CATEGORY = {
    "Nutrient Deficiencies": {
        'Iron Deficiency (Anemia)': {
            'adjustments': {'protein': 1.20},
            'micronutrient_targets': {'iron': 27},
            'tip': 'Higher protein target and a raised iron target. Prioritize iron-rich foods (spinach, lentils, chickpeas, lean red meat, tofu) with Vitamin C to boost absorption.',
        },
        'Vitamin B12 Deficiency': {
            'adjustments': {'protein': 1.15},
            'micronutrient_targets': {'vitb12': 2.8},
            'tip': 'Raised B12 target. Favor animal-based or fortified foods — eggs, dairy, fish, fortified cereals/plant milk (especially important if vegetarian/vegan).',
        },
        'Vitamin D Deficiency': {
            'adjustments': {'fat': 1.05},
            'micronutrient_targets': {'vitd': 800},
            'tip': 'Slightly higher fat target (Vitamin D is fat-soluble) and a raised D target. Favor fatty fish, egg yolks, fortified milk, and get sensible sun exposure.',
        },
        'Calcium Deficiency': {
            'adjustments': {},
            'micronutrient_targets': {'calcium': 1200},
            'tip': 'Raised calcium target. Favor dairy, fortified plant milk, tofu, almonds, and leafy greens like kale.',
        },
        'Vitamin C Deficiency': {
            'adjustments': {},
            'micronutrient_targets': {'vitc': 120},
            'tip': 'Raised Vitamin C target. Favor citrus fruits, bell peppers, strawberries, and broccoli.',
        },
        'Folate (Vitamin B9) Deficiency': {
            'adjustments': {'fiber': 1.10},
            'tip': 'Slightly higher fiber target, since folate-rich foods overlap with fiber-rich ones. Favor leafy greens, legumes, and citrus.',
        },
        'Zinc Deficiency': {
            'adjustments': {'protein': 1.10},
            'tip': 'Higher protein target (zinc isn\'t tracked directly here). Favor meat, shellfish, seeds (pumpkin, sesame), and legumes.',
        },
        'Magnesium Deficiency': {
            'adjustments': {'fiber': 1.10},
            'tip': 'Slightly higher fiber target (magnesium isn\'t tracked directly here). Favor nuts, seeds, whole grains, and leafy greens.',
        },
        'Protein-Energy Malnutrition': {
            'adjustments': {'calories': 1.15, 'protein': 1.30},
            'tip': 'Higher calorie and protein targets to support rebuilding energy and muscle reserves.',
        },
        'Omega-3 Deficiency': {
            'adjustments': {'fat': 1.05},
            'tip': 'Slightly higher fat target (omega-3 isn\'t tracked separately here). Favor fatty fish, walnuts, flaxseed, and chia seeds.',
        },
    },
    "Metabolic & Hormonal": {
        'PCOD/PCOS': {
            'adjustments': {'carbs': 0.85, 'sugar': 0.55, 'protein': 1.15, 'fiber': 1.25},
            'tip': 'Lower-glycemic targets with extra fiber and protein can help support insulin sensitivity and hormone balance.',
        },
        'Diabetes (Type 2)': {
            'adjustments': {'carbs': 0.75, 'sugar': 0.40, 'fiber': 1.30},
            'tip': 'Reduced carb & sugar targets with higher fiber help support steadier blood sugar.',
        },
        'Prediabetes / Insulin Resistance': {
            'adjustments': {'carbs': 0.85, 'sugar': 0.60, 'fiber': 1.20},
            'tip': 'Milder carb/sugar reduction than diabetes, with a fiber boost, to help support insulin sensitivity.',
        },
        'Hypothyroidism': {
            'adjustments': {'sodium': 0.85, 'fiber': 1.15},
            'tip': 'Slightly reduced sodium and increased fiber to support metabolic and digestive health.',
        },
        'Hyperthyroidism': {
            'adjustments': {'calories': 1.10, 'protein': 1.15},
            'tip': 'Higher calorie and protein targets to help offset an elevated metabolic rate.',
        },
        'Obesity': {
            'adjustments': {'calories': 0.85, 'fat': 0.85, 'sugar': 0.70, 'fiber': 1.20},
            'tip': 'Lower calorie, fat, and sugar targets with more fiber to support satiety on fewer calories.',
        },
    },
    "Heart & Blood Pressure": {
        'Hypertension (High BP)': {
            'adjustments': {'sodium': 0.55},
            'tip': 'Sodium target is meaningfully reduced to support healthy blood pressure.',
        },
        'High Cholesterol': {
            'adjustments': {'fat': 0.75},
            'tip': 'Fat target is reduced, with a focus on cutting saturated fat specifically, to support heart health.',
        },
        'Heart Disease': {
            'adjustments': {'fat': 0.75, 'sodium': 0.70, 'fiber': 1.20},
            'tip': 'Reduced fat and sodium targets, with more fiber, to support cardiovascular health.',
        },
    },
    "Digestive & Organ Health": {
        'Fatty Liver Disease': {
            'adjustments': {'sugar': 0.50, 'fat': 0.80, 'carbs': 0.85},
            'tip': 'Lower sugar, fat, and refined carb targets to reduce strain on the liver.',
        },
        'Kidney Disease (CKD)': {
            'adjustments': {'protein': 0.75, 'sodium': 0.60},
            'micronutrient_targets': {'potassium': 2000},
            'tip': 'Lower protein and sodium targets, plus a lowered potassium target. CKD diets are highly individual — please follow your nephrologist/dietitian\'s guidance closely.',
        },
        'Gout': {
            'adjustments': {'protein': 0.80},
            'tip': 'Lower protein target since purine-rich foods (red/organ meat, shellfish) can trigger flares. Favor plant proteins, and limit alcohol.',
        },
        'IBS (Irritable Bowel Syndrome)': {
            'adjustments': {'fat': 0.90},
            'tip': 'Slightly reduced fat target. Consider a low-FODMAP approach and identify your personal trigger foods.',
        },
        'Acid Reflux / GERD': {
            'adjustments': {'fat': 0.80},
            'tip': 'Lower fat target, since fatty/spicy/acidic foods commonly trigger reflux. Avoid large meals close to bedtime.',
        },
        'Lactose Intolerance': {
            'adjustments': {},
            'tip': 'Dairy isn\'t tracked separately here — watch for milk, cheese, and cream in what you log, or choose lactose-free alternatives.',
        },
        'Celiac / Gluten Sensitivity': {
            'adjustments': {},
            'tip': 'Gluten isn\'t tracked here — check ingredients for wheat, barley, and rye, and choose certified gluten-free options where needed.',
        },
    },
    "Bone Health": {
        'Osteoporosis': {
            'adjustments': {'protein': 1.10},
            'micronutrient_targets': {'calcium': 1200, 'vitd': 800},
            'tip': 'Higher protein, calcium, and Vitamin D targets to support bone density and muscle mass.',
        },
    },
    "Life Stage": {
        'Pregnancy': {
            'adjustments': {'calories': 1.15, 'protein': 1.20, 'fiber': 1.10},
            'micronutrient_targets': {'iron': 27, 'calcium': 1000},
            'tip': 'Higher calorie, protein, fiber, iron, and calcium targets. Consult your doctor for prenatal-specific needs (folate in particular).',
        },
        'Lactation / Breastfeeding': {
            'adjustments': {'calories': 1.25, 'protein': 1.20},
            'micronutrient_targets': {'calcium': 1000},
            'tip': 'Higher calorie, protein, and calcium targets to support milk production and recovery.',
        },
    },
}

MEDICAL_CONDITION_TIPS = {
    condition: data['tip']
    for category in MEDICAL_CONDITIONS_BY_CATEGORY.values()
    for condition, data in category.items()
}


def apply_medical_adjustments(goals, medical_conditions):
    """🆕 Adjusts calorie/macro targets and raises relevant micronutrient
    targets based on selected medical conditions. No conditions selected
    -> goals returned unchanged (exact old behavior).

    Multiple conditions touching the same macro are averaged then
    clamped to [0.5x, 1.6x] so they can't compound into an unrealistic
    target. Micronutrient target overrides take the HIGHEST value among
    selected conditions (the more cautious target)."""
    if not medical_conditions:
        return goals

    factor_lists = {}
    micronutrient_overrides = {}
    for condition in medical_conditions:
        data = None
        for category in MEDICAL_CONDITIONS_BY_CATEGORY.values():
            if condition in category:
                data = category[condition]
                break
        if not data:
            continue
        for nutrient, factor in data.get('adjustments', {}).items():
            factor_lists.setdefault(nutrient, []).append(factor)
        for micro, val in data.get('micronutrient_targets', {}).items():
            micronutrient_overrides.setdefault(micro, []).append(val)

    adjusted = dict(goals)
    for nutrient, factors in factor_lists.items():
        if nutrient not in adjusted:
            continue
        avg_factor = sum(factors) / len(factors)
        avg_factor = max(0.5, min(1.6, avg_factor))  # clamp — no runaway stacking
        if nutrient == 'water':
            adjusted[nutrient] = round(max(adjusted[nutrient] * avg_factor, 0.0), 1)
        else:
            adjusted[nutrient] = round(max(adjusted[nutrient] * avg_factor, 0.0))

    for micro, vals in micronutrient_overrides.items():
        adjusted[micro] = max(adjusted.get(micro, 0), max(vals))

    return adjusted

# ── Calculation functions ─────────────────────────────────────
def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity):
    factors = {
        "Sedentary (no exercise)":           1.2,
        "Light Exercise (1-3 days/wk)":      1.375,
        "Moderate Exercise (3-5 days/wk)":   1.55,
        "Heavy Exercise (6-7 days/wk)":      1.725,
        "Athlete (2x training/day)":         1.9,
    }
    return bmr * factors.get(activity, 1.55)

def calculate_goals(tdee, weight, goal):
    adjustments = {
        "Maintain Weight": 0,
        "Weight Loss":     -500,
        "Weight Gain":     +500,
        "Muscle Gain":     +300,
    }
    calories = tdee + adjustments.get(goal, 0)

    protein_multipliers = {"Weight Loss": 2.2, "Muscle Gain": 2.4, "Weight Gain": 1.8, "Maintain Weight": 1.6}
    protein = weight * protein_multipliers.get(goal, 1.8)

    fat     = (calories * 0.25) / 9
    carbs   = (calories - (protein * 4) - (fat * 9)) / 4
    fiber   = 30 if goal in ["Weight Loss", "Maintain Weight"] else 25
    sugar   = 25 if goal == "Weight Loss" else 37.5
    water   = round(weight * 0.033, 1)

    return {
        "calories": round(calories),
        "protein":  round(protein),
        "carbs":    round(max(carbs, 50)),
        "fat":      round(fat),
        "fiber":    fiber,
        "sugar":    sugar,
        "water":    water,
        "calcium":  1000,
        "iron":     18 if goal == "Muscle Gain" else 14,
        "vitd":     600,
        "vitc":     90,
        "vitb12":   2.4,
        "potassium":3500,
        "sodium":   2300,
    }

def recalculate_consumed():
    consumed = {k: 0.0 for k in ["calories", "protein", "carbs", "fat", "fiber", "sugar", "water"]}
    for meal_foods in st.session_state.tracker_meals.values():
        for food in meal_foods:
            nutrients = FOOD_DB.get(food, {})
            for k in consumed:
                consumed[k] += nutrients.get(k, 0)
    st.session_state.tracker_consumed = {k: round(v, 1) for k, v in consumed.items()}

def get_progress_color(pct):
    """⚠️ DEPRECATED — kept only so nothing else importing this name
    breaks. Do not use for new code: it colored the bar red as soon as
    ANY nutrient hit 100% (including ones where 100% is the goal, like
    Protein/Fiber/Water), which contradicts the health-status verdicts.
    Use classify_nutrient() below instead."""
    if pct >= 100: return "#ef5350"
    if pct >= 80:  return "#6eb52f"
    if pct >= 50:  return "#ffa726"
    return "#90caf9"

# ============================================================
# 🔧 FIXED: single source of truth for "is this nutrient's intake
# good, borderline, or bad" — shared by BOTH the Step 4 progress bars
# and the Step 7 health-status cards, so they can no longer disagree
# with each other the way get_progress_color() vs get_health_status()
# used to (progress bar said "100% = danger", status card said
# "100% = excellent", for the exact same number).
#
# Each nutrient is either:
#   - a TARGET (calories, protein, carbs, fat, fiber, water): you want
#     to land inside [low%, high%] of goal. Below low = undershooting.
#     Above high = overshooting — which the old progress-bar logic
#     couldn't distinguish from "on target" at all (it capped at 100%).
#   - a CEILING (sugar): goal is a limit, not something to hit 100% of.
#     0% is fine; only going OVER the limit is bad.
# ============================================================
NUTRIENT_RANGES = {
    "calories": (90, 110, False),
    "protein":  (80, 120, False),
    "carbs":    (70, 120, False),
    "fat":      (60, 110, False),
    "fiber":    (70, 120, False),
    "water":    (70, 120, False),
    "sugar":    (0,  100, True),
}

STATUS_COLOR = {
    "excellent": "#6eb52f",  # green  — right in the target range
    "ok":        "#90caf9",  # blue   — a bit under, but reasonable
    "warning":   "#ffa726",  # orange — meaningfully under OR over
    "danger":    "#ef5350",  # red    — well under, or well over
}

def classify_nutrient(key, cons_val, goal_val):
    """Returns (status, direction, pct) for one nutrient, where status
    is one of excellent/ok/warning/danger, direction is over/under/in_range
    (used to pick the right message wording), and pct is the RAW,
    UNCAPPED percentage of goal — so callers can still tell a person is
    at 105% vs 300% instead of both being clamped to the same number."""
    if goal_val == 0:
        return None
    low, high, is_ceiling = NUTRIENT_RANGES.get(key, (70, 120, False))
    pct = (cons_val / goal_val) * 100

    if is_ceiling:
        if pct > high:
            return ("danger", "over", pct)
        elif pct > high * 0.8:
            return ("warning", "over", pct)
        else:
            return ("ok", "in_range", pct)

    if pct > high * 1.3:
        return ("danger", "over", pct)
    elif pct > high:
        return ("warning", "over", pct)
    elif pct >= low:
        return ("excellent", "in_range", pct)
    elif pct >= low * (2 / 3):
        return ("ok", "under", pct)
    elif pct >= low * (1 / 3):
        return ("warning", "under", pct)
    else:
        return ("danger", "under", pct)

def get_health_status(consumed, goals):
    statuses = []
    labels = [
        ("calories", "Calories",  "fa-fire"),
        ("protein",  "Protein",   "fa-dumbbell"),
        ("carbs",    "Carbs",     "fa-wheat-awn"),
        ("fat",      "Fat",       "fa-droplet"),
        ("fiber",    "Fiber",     "fa-leaf"),
        ("water",    "Water",     "fa-glass-water"),
        ("sugar",    "Sugar",     "fa-candy-cane"),
    ]
    for key, label, icon in labels:
        goal_val = goals.get(key, 1)
        cons_val = consumed.get(key, 0)
        result = classify_nutrient(key, cons_val, goal_val)
        if result is None:
            continue
        status, direction, pct = result
        is_ceiling = NUTRIENT_RANGES.get(key, (70, 120, False))[2]
        disp_val = f"{cons_val:.0f}g" if is_ceiling else cons_val
        disp_goal = f"{goal_val}g" if is_ceiling else goal_val

        if is_ceiling:
            if status == "danger":
                msg = f"⚠ {label} is too high ({disp_val} / {disp_goal})"
            elif status == "warning":
                msg = f"⚠ {label} is approaching the limit ({disp_val} / {disp_goal})"
            else:
                msg = f"✓ {label} within limit ({disp_val} / {disp_goal})"
        else:
            if status == "danger" and direction == "over":
                msg = f"⚠ {label} intake is well above target ({cons_val} / {goal_val})"
            elif status == "warning" and direction == "over":
                msg = f"⚠ {label} intake is above target ({cons_val} / {goal_val})"
            elif status == "excellent":
                msg = f"✅ Excellent {label} intake ({cons_val} / {goal_val})"
            elif status == "ok":
                msg = f"✓ {label} is on track ({cons_val} / {goal_val})"
            elif status == "warning":
                msg = f"⚠ {label} is below target ({cons_val} / {goal_val})"
            else:
                msg = f"⚠ Low {label} intake ({cons_val} / {goal_val})"
        statuses.append((status, msg, icon))
    return statuses

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    initial = st.session_state.username[0].upper()
    st.markdown(f"""
        <div style="width:48px;height:48px;border-radius:50%;
        background:#2e7d32;display:flex;align-items:center;
        justify-content:center;font-size:20px;font-weight:700;
        color:white;margin-bottom:8px;">{initial}</div>
        <div style="font-size:15px;font-weight:600;color:#1b5e20;">
        {st.session_state.username}</div>
        <div style="font-size:12px;color:#558b2f;margin-bottom:12px;">
        Member</div>
    """, unsafe_allow_html=True)
    st.divider()
    st.page_link("pages/Home.py",                            label="🏠  Home")
    st.page_link("pages/1_💪_Diet_Recommendation.py",        label="💪  Diet Recommendation")
    st.page_link("pages/2_🔍_Custom_Food_Recommendation.py", label="🔍  Custom Food")
    st.page_link("pages/3_📸_Image_Food_Tracking.py",        label="📸  Image Food Tracking")
    st.page_link("pages/4_🥗_Daily_Nutrition_Tracker.py",    label="🥗  Nutrition Tracker")
    st.divider()
    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button("Logout", icon=":material/logout:"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Hello.py")
    st.markdown('</div>', unsafe_allow_html=True)
# ── Page header ───────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-header-left">
        <h1><i class="fa-solid fa-chart-pie" style="margin-right:10px;"></i>Daily Nutrition Tracker</h1>
        <p>Track your daily nutrition, log meals and monitor your health goals — {date.today().strftime("%A, %d %B %Y")}</p>
    </div>
    <div class="page-header-icon"><i class="fa-solid fa-bowl-food"></i></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 1 & 2 — Calculator + Goals
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-calculator"></i> Step 1 — Your Daily Calorie & Nutrient Goals</div>', unsafe_allow_html=True)

with st.expander("⚙ Set up your profile to calculate goals", expanded=not st.session_state.tracker_calculated):
    with st.form("calculator_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            age    = st.number_input("Age", min_value=10, max_value=100, value=25)
            gender = st.radio("Gender", ["Male", "Female"])
        with c2:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=165)
            weight = st.number_input("Weight (kg)", min_value=30,  max_value=200, value=65)
        with c3:
            activity = st.selectbox("Activity Level", [
                "Sedentary (no exercise)",
                "Light Exercise (1-3 days/wk)",
                "Moderate Exercise (3-5 days/wk)",
                "Heavy Exercise (6-7 days/wk)",
                "Athlete (2x training/day)",
            ])
        with c4:
            goal = st.selectbox("Health Goal", [
                "Maintain Weight", "Weight Loss", "Weight Gain", "Muscle Gain"
            ])

        # 🆕 Medical conditions — optional, grouped by category. Leaving
        # everything unselected reproduces the exact old goal numbers.
        st.markdown("---")
        st.markdown("**Medical Conditions (optional)** — select any that apply, e.g. PCOD/PCOS, diabetes, thyroid issues. This fine-tunes your daily targets. Not medical advice; please consult your doctor.")
        medical_conditions = []
        for category_name, conditions in MEDICAL_CONDITIONS_BY_CATEGORY.items():
            with st.expander(f"{category_name}"):
                selected = st.multiselect(
                    category_name,
                    list(conditions.keys()),
                    label_visibility="collapsed",
                    key=f"tracker_medcond_{category_name}"
                )
                medical_conditions.extend(selected)

        submitted = st.form_submit_button("Calculate My Goals", use_container_width=True)
        if submitted:
            bmi  = round(weight / ((height / 100) ** 2), 1)
            bmr  = calculate_bmr(weight, height, age, gender)
            tdee = calculate_tdee(bmr, activity)
            goals = calculate_goals(tdee, weight, goal)
            goals = apply_medical_adjustments(goals, medical_conditions)  # 🆕
            goals["bmi"]  = bmi
            goals["bmr"]  = round(bmr)
            goals["tdee"] = round(tdee)
            goals["goal"] = goal
            st.session_state.tracker_goals       = goals
            st.session_state.tracker_calculated  = True
            st.session_state.tracker_medical_conditions = medical_conditions  # 🆕
            st.rerun()

if not st.session_state.tracker_calculated:
    st.info("Fill in your details above and click **Calculate My Goals** to get started.")
    st.stop()

goals    = st.session_state.tracker_goals
consumed = st.session_state.tracker_consumed

# ── BMI display ────────────────────────────────────────────────
bmi = goals["bmi"]
if bmi < 18.5:
    bmi_cat, bmi_color = "Underweight", "#ef5350"
elif bmi < 25:
    bmi_cat, bmi_color = "Normal",      "#6eb52f"
elif bmi < 30:
    bmi_cat, bmi_color = "Overweight",  "#ffa726"
else:
    bmi_cat, bmi_color = "Obese",       "#ef5350"

st.markdown(f"""
<div style="background:#fff;border-radius:14px;padding:16px 24px;
border:1.5px solid #e8f5e9;margin-bottom:20px;display:flex;align-items:center;gap:24px;">
    <div style="text-align:center;">
        <div style="font-size:32px;font-weight:800;color:{bmi_color};">{bmi}</div>
        <div style="font-size:11px;color:#999;font-weight:600;">BMI</div>
        <div style="font-size:13px;font-weight:700;color:{bmi_color};">{bmi_cat}</div>
    </div>
    <div style="width:1px;height:60px;background:#e8f5e9;"></div>
    <div style="flex:1;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
        <div><div style="font-size:11px;color:#81c784;font-weight:600;">BMR</div>
             <div style="font-size:18px;font-weight:700;color:#1b5e20;">{goals['bmr']} kcal</div></div>
        <div><div style="font-size:11px;color:#81c784;font-weight:600;">TDEE</div>
             <div style="font-size:18px;font-weight:700;color:#1b5e20;">{goals['tdee']} kcal</div></div>
        <div><div style="font-size:11px;color:#81c784;font-weight:600;">Goal</div>
             <div style="font-size:18px;font-weight:700;color:#1b5e20;">{goals['goal']}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Weight feedback (BMI-based) ─────────────────────────────── 🆕
# Simple, non-numeric feedback on whether the entered weight is in a
# healthy range for the given height — feedback only, doesn't change
# any calorie/macro targets.
WEIGHT_FEEDBACK = {
    "Underweight": ("info",    "Your weight is a little below the healthy range for your height."),
    "Normal":      ("success", "Your weight is in a healthy range for your height. Keep it up!"),
    "Overweight":  ("warning", "Your weight is a little above the healthy range for your height."),
    "Obese":       ("warning", "Your weight is well above the healthy range for your height — consider talking to a doctor."),
}
feedback_type, feedback_msg = WEIGHT_FEEDBACK[bmi_cat]
getattr(st, feedback_type)(feedback_msg)

# ── Medical considerations panel ────────────────────────────── 🆕
active_conditions = st.session_state.get("tracker_medical_conditions", [])
if active_conditions:
    st.markdown('<div class="sec-title"><i class="fa-solid fa-notes-medical"></i> Medical Considerations</div>', unsafe_allow_html=True)
    st.caption("These targets are general-wellness adjustments, not medical advice. Please consult your doctor or dietitian for personalized guidance.")
    for condition in active_conditions:
        tip = MEDICAL_CONDITION_TIPS.get(condition, '')
        st.markdown(f"""
        <div class="medcond-card">
            <div class="medcond-name">{condition}</div>
            <div class="medcond-tip">{tip}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Nutrient goal cards ────────────────────────────────────────
st.markdown('<div class="sec-title"><i class="fa-solid fa-bullseye"></i> Step 2 — Your Daily Nutrient Requirements</div>', unsafe_allow_html=True)

nutrient_display = [
    ("🔥", goals["calories"],  "kcal",  "Calories"),
    ("💪", goals["protein"],   "g",     "Protein"),
    ("🍚", goals["carbs"],     "g",     "Carbs"),
    ("🥑", goals["fat"],       "g",     "Fat"),
    ("🌿", goals["fiber"],     "g",     "Fiber"),
    ("🍬", goals["sugar"],     "g",     "Sugar"),
    ("💧", goals["water"],     "L",     "Water"),
    ("🦴", goals["calcium"],   "mg",    "Calcium"),
    ("🩸", goals["iron"],      "mg",    "Iron"),
    ("☀️", goals["vitd"],      "IU",    "Vitamin D"),
    ("🍊", goals["vitc"],      "mg",    "Vitamin C"),
    ("⚡", goals["vitb12"],    "mcg",   "Vitamin B12"),
    ("🫀", goals["potassium"], "mg",    "Potassium"),
    ("🧂", goals["sodium"],    "mg",    "Sodium"),
]

# Split into rows of 7
rows = [nutrient_display[:7], nutrient_display[7:]]
for row in rows:
    cols = st.columns(len(row))
    for col, (icon, val, unit, label) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class="nutrient-card">
                <div class="nutrient-icon">{icon}</div>
                <div class="nutrient-val">{val}</div>
                <div class="nutrient-unit">{unit}</div>
                <div class="nutrient-lbl">{label}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 3 — Food Logger
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-utensils"></i> Step 3 — Log Your Meals</div>', unsafe_allow_html=True)

meal_cols = st.columns(5)
meal_names = list(st.session_state.tracker_meals.keys())

for col, meal in zip(meal_cols, meal_names):
    with col:
        icon = MEAL_ICONS[meal]
        st.markdown(f'<div class="meal-section"><div class="meal-title"><i class="fa-solid {icon}"></i>{meal}</div>', unsafe_allow_html=True)

        # Show logged foods, each with its own remove button 🆕
        logged = st.session_state.tracker_meals[meal]
        if logged:
            for idx, food in enumerate(logged):
                kcal = FOOD_DB.get(food, {}).get("calories", 0)
                tag_col, remove_col = st.columns([5, 1])
                with tag_col:
                    st.markdown(f'<div class="food-tag">{food} ({kcal} kcal)</div>', unsafe_allow_html=True)
                with remove_col:
                    if st.button("✕", key=f"remove_{meal}_{idx}", help=f"Remove {food}"):
                        st.session_state.tracker_meals[meal].pop(idx)
                        recalculate_consumed()
                        st.session_state.toast_message = f"Removed {food} from {meal}"
                        st.rerun()
        else:
            st.markdown('<div style="font-size:11px;color:#ccc;text-align:center;">Nothing logged yet</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        food_choice = st.selectbox(
            f"Add to {meal}",
            ["-- Select food --"] + sorted(FOOD_DB.keys()),
            key=f"select_{meal}",
            label_visibility="collapsed"
        )

        # Live nutrition preview of the highlighted food, before adding
        if food_choice != "-- Select food --":
            n = FOOD_DB.get(food_choice, {})
            st.caption(f"{n.get('calories',0)} kcal · P {n.get('protein',0)}g · C {n.get('carbs',0)}g · F {n.get('fat',0)}g")

        if st.button(f"Add", key=f"add_{meal}"):
            if food_choice != "-- Select food --":
                st.session_state.tracker_meals[meal].append(food_choice)
                recalculate_consumed()
                st.session_state.toast_message = f"Added {food_choice} to {meal}"  # 🆕
                st.rerun()

if st.button("🗑 Clear all meals", key="clear_meals"):
    st.session_state.tracker_meals   = {m: [] for m in meal_names}
    st.session_state.tracker_consumed = {k: 0 for k in ["calories", "protein", "carbs", "fat", "fiber", "sugar", "water"]}
    st.session_state.toast_message = "All meals cleared"  # 🆕
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 5 — Dashboard
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-gauge-high"></i> Step 5 — Today\'s Dashboard</div>', unsafe_allow_html=True)

remain_cal   = max(0, goals["calories"] - consumed["calories"])
remain_pro   = max(0, goals["protein"]  - consumed["protein"])
remain_water = max(0, goals["water"]    - consumed["water"])

dash_items = [
    ("🔥", f"{consumed['calories']} kcal", "Calories eaten",  f"{remain_cal} kcal left"),
    ("💪", f"{consumed['protein']}g",       "Protein eaten",   f"{remain_pro}g left"),
    ("🍚", f"{consumed['carbs']}g",         "Carbs eaten",     f"{max(0, goals['carbs'] - consumed['carbs'])}g left"),
    ("🥑", f"{consumed['fat']}g",           "Fat eaten",       f"{max(0, goals['fat'] - consumed['fat'])}g left"),
    ("💧", f"{consumed['water']}L",         "Water consumed",  f"{remain_water}L left"),
    ("📊", f"{goals['bmi']}",               "Your BMI",        bmi_cat),
    ("🎯", goals["goal"],                   "Health Goal",     "Active"),
    ("🔥", f"{remain_cal} kcal",            "Remaining Cal",   "to eat today"),
    ("💪", f"{remain_pro}g",                "Remaining Prot",  "to reach goal"),
    ("💧", f"{remain_water}L",              "Remaining Water", "to reach goal"),
]

rows_dash = [dash_items[:5], dash_items[5:]]
for row in rows_dash:
    cols = st.columns(5)
    for col, (icon, val, lbl, sub) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class="dash-card">
                <div style="font-size:20px;margin-bottom:4px;">{icon}</div>
                <div class="dash-val">{val}</div>
                <div class="dash-lbl">{lbl}</div>
                <div class="dash-remain">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 4 — Progress Tracker
# ═══════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="sec-title"><i class="fa-solid fa-bars-progress"></i> Step 4 — Progress Tracker</div>', unsafe_allow_html=True)

    progress_items = [
        ("fa-fire",        "Calories",  "calories", "kcal"),
        ("fa-dumbbell",    "Protein",   "protein",  "g"),
        ("fa-wheat-awn",   "Carbs",     "carbs",    "g"),
        ("fa-droplet",     "Fat",       "fat",      "g"),
        ("fa-leaf",        "Fiber",     "fiber",    "g"),
        ("fa-glass-water", "Water",     "water",    "L"),
        ("fa-candy-cane",  "Sugar",     "sugar",    "g"),
    ]

    for icon, label, key, unit in progress_items:
        goal_val = goals.get(key, 1)
        cons_val = consumed.get(key, 0)
        result = classify_nutrient(key, cons_val, goal_val)  # 🔧 same classifier as the health-status cards
        if result is None:
            continue
        status, direction, raw_pct = result
        color    = STATUS_COLOR[status]
        bar_pct  = min(100, round(raw_pct))   # cap only the BAR WIDTH (can't draw >100% of a box)
        disp_pct = round(raw_pct)             # 🔧 label shows the real number, so 300% still reads as 300%, not 100%

        st.markdown(f"""
        <div class="prog-wrap">
            <div class="prog-header">
                <div class="prog-label"><i class="fa-solid {icon}"></i>{label}</div>
                <div class="prog-values">{cons_val} / {goal_val} {unit}</div>
            </div>
            <div class="prog-bar-bg">
                <div class="prog-bar-fill" style="width:{bar_pct}%;background:{color};"></div>
            </div>
            <div class="prog-pct">{disp_pct}% of daily goal</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 6 — Pie Charts
# ═══════════════════════════════════════════════════════════════
with right_col:
    st.markdown('<div class="sec-title"><i class="fa-solid fa-chart-pie"></i> Step 6 — Macro Breakdown</div>', unsafe_allow_html=True)

    protein_kcal = consumed["protein"] * 4
    carbs_kcal   = consumed["carbs"]   * 4
    fat_kcal     = consumed["fat"]     * 9
    total_macro  = protein_kcal + carbs_kcal + fat_kcal

    if total_macro > 0:
        fig_macro = go.Figure(go.Pie(
            labels=["Protein", "Carbs", "Fat"],
            values=[protein_kcal, carbs_kcal, fat_kcal],
            hole=0.6,
            marker=dict(colors=["#2e7d32", "#66bb6a", "#a5d6a7"], line=dict(color="#fff", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:.0f} kcal (%{percent})<extra></extra>",
        ))
        fig_macro.add_annotation(
            text=f"<b>{round(total_macro)}</b><br>kcal",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#1b5e20"), align="center",
        )
        fig_macro.update_layout(
            showlegend=True, height=260,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(size=12)),
        )
        st.plotly_chart(fig_macro, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Log some meals to see your macro breakdown chart.")

    # Nutrient consumed vs goal bar chart
    st.markdown('<div style="margin-top:8px;font-size:13px;font-weight:600;color:#1b5e20;margin-bottom:8px;">Consumed vs Goal</div>', unsafe_allow_html=True)
    chart_keys   = ["calories", "protein", "carbs", "fat", "fiber", "water"]
    chart_labels = ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Water"]
    consumed_vals = [consumed[k] for k in chart_keys]
    goal_vals     = [goals[k]    for k in chart_keys]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Goal",     x=chart_labels, y=goal_vals,     marker_color="#c8e6c9", opacity=0.7))
    fig_bar.add_trace(go.Bar(name="Consumed", x=chart_labels, y=consumed_vals, marker_color="#2e7d32"))
    fig_bar.update_layout(
        barmode="overlay", height=220,
        margin=dict(t=10, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,230,201,0.4)", tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 7 — Health Status
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-heart-pulse"></i> Step 7 — Health Status</div>', unsafe_allow_html=True)

statuses = get_health_status(consumed, goals)
status_cols = st.columns(2)
for i, (status_type, message, icon) in enumerate(statuses):
    with status_cols[i % 2]:
        st.markdown(f"""
        <div class="status-card status-{status_type}">
            <i class="fa-solid {icon} status-icon"></i>
            <div class="status-text">{message}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 8 — Daily History
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-clock-rotate-left"></i> Step 8 — Nutrition History</div>', unsafe_allow_html=True)

# Save today to history
if any(v > 0 for v in consumed.values()):
    st.session_state.tracker_history[today_str] = {**consumed, "goal": goals["goal"]}

history = st.session_state.tracker_history
period  = st.radio("View period", ["Today", "Last 7 Days", "Last 30 Days"], horizontal=True)

if period == "Today":
    days = [today_str]
elif period == "Last 7 Days":
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
else:
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]

hist_data = []
for d in days:
    if d in history:
        row = history[d]
        hist_data.append({
            "Date":     d,
            "Calories": row.get("calories", 0),
            "Protein":  row.get("protein",  0),
            "Carbs":    row.get("carbs",    0),
            "Fat":      row.get("fat",      0),
            "Water":    row.get("water",    0),
        })

if hist_data:
    df_hist = pd.DataFrame(hist_data)
    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    if len(hist_data) > 1:
        fig_hist = px.line(
            df_hist, x="Date", y="Calories",
            title="Calorie Trend",
            color_discrete_sequence=["#6eb52f"],
            markers=True,
        )
        fig_hist.update_layout(
            height=250, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, b=0, l=0, r=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(200,230,201,0.4)"),
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("No history yet. Log meals today and come back tomorrow to see trends.")

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 9 — Export Report
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title"><i class="fa-solid fa-file-export"></i> Step 9 — Export Your Report</div>', unsafe_allow_html=True)

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    st.markdown("**📊 Today's Nutrition Report (CSV)**")
    today_data = {
        "Nutrient":  ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Sugar", "Water"],
        "Consumed":  [consumed["calories"], consumed["protein"], consumed["carbs"],
                      consumed["fat"], consumed["fiber"], consumed["sugar"], consumed["water"]],
        "Goal":      [goals["calories"], goals["protein"], goals["carbs"],
                      goals["fat"], goals["fiber"], goals["sugar"], goals["water"]],
        "Unit":      ["kcal", "g", "g", "g", "g", "g", "L"],
    }
    df_today = pd.DataFrame(today_data)
    df_today["% Achieved"] = (df_today["Consumed"] / df_today["Goal"] * 100).round(1)
    csv_today = df_today.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Today's Report",
        data=csv_today,
        file_name=f"nutrition_report_{today_str}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_col2:
    st.markdown("**🍽 Meal Summary (CSV)**")
    meal_rows = []
    for meal_name, foods in st.session_state.tracker_meals.items():
        for food in foods:
            n = FOOD_DB.get(food, {})
            meal_rows.append({
                "Meal":     meal_name,
                "Food":     food,
                "Calories": n.get("calories", 0),
                "Protein":  n.get("protein",  0),
                "Carbs":    n.get("carbs",    0),
                "Fat":      n.get("fat",      0),
            })
    if meal_rows:
        df_meals = pd.DataFrame(meal_rows)
        csv_meals = df_meals.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Meal Summary",
            data=csv_meals,
            file_name=f"meal_summary_{today_str}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Log meals first to export meal summary.")

with exp_col3:
    st.markdown("**📈 Weekly Progress (CSV)**")
    if hist_data:
        df_weekly = pd.DataFrame(hist_data)
        csv_weekly = df_weekly.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Weekly Progress",
            data=csv_weekly,
            file_name=f"weekly_progress_{today_str}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No history yet to export.")

# ── Footer ────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#1a1a2e;border-radius:12px;padding:14px 20px;
margin-top:24px;display:flex;align-items:center;gap:12px;">
    <i class="fa-solid fa-heart-pulse" style="color:#6eb52f;font-size:16px;"></i>
    <span style="font-size:12px;color:#888;font-style:italic;">
        "Take care of your body. It's the only place you have to live." — Jim Rohn
        <strong style="color:#6eb52f;"> Keep going, {username}!</strong>
    </span>
</div>
""", unsafe_allow_html=True)