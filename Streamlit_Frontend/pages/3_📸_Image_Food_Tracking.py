import streamlit as st
import pandas as pd
import os
import difflib
from PIL import Image
from transformers import pipeline

st.set_page_config(page_title="Image Food Detection", page_icon="📸", layout="wide")

# ----------------------------------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------------------------------
st.markdown("""
<style>
:root{
    --brand:#2e7d32;
    --brand-dark:#1b5e20;
    --brand-light:#e8f5e9;
    --accent:#66bb6a;
    --text-soft:#558b2f;
}

[data-testid="stSidebar"] { background:#ffffff !important; border-right:1px solid var(--brand-light) !important; }
[data-testid="stSidebarNav"] { display:none; }
.stApp { background:#f7faf7; }

.page-title{
    text-align:center;
    font-weight:800;
    font-size:2.3rem;
    background:linear-gradient(90deg,var(--brand-dark),var(--accent));
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:0.1rem;
}
.page-subtitle{
    text-align:center;
    color:#6b7d6b;
    font-size:1rem;
    margin-bottom:1.6rem;
}

/* Upload zone */
div[data-testid="stFileUploader"]{
    background:#ffffff;
    border:2px dashed #cfe8cf;
    border-radius:16px;
    padding:1rem 1rem 0.6rem 1rem;
}
div[data-testid="stFileUploader"]:hover{ border-color:var(--accent); }

/* Result card */
.result-card{
    background:#ffffff;
    border:1px solid #e6efe6;
    border-radius:18px;
    padding:1.3rem 1.5rem;
    box-shadow:0 4px 16px rgba(46,125,50,0.06);
    margin-bottom:1rem;
}
.detected-label{
    font-size:1.3rem;
    font-weight:800;
    color:var(--brand-dark);
    margin-bottom:0.2rem;
}
.confidence-text{
    font-size:0.85rem;
    color:var(--text-soft);
    font-weight:600;
    margin-bottom:0.4rem;
}
.conf-bar-bg{
    width:100%;
    background:var(--brand-light);
    border-radius:999px;
    height:10px;
    overflow:hidden;
    margin-bottom:0.2rem;
}
.conf-bar-fill{
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,var(--brand),var(--accent));
}

/* Rank chips for top predictions */
.rank-row{
    display:flex;
    align-items:center;
    gap:0.6rem;
    padding:0.45rem 0.6rem;
    border-radius:10px;
    margin-bottom:0.4rem;
    background:#f7faf7;
    border:1px solid #eef5ee;
}
.rank-num{
    width:22px; height:22px; border-radius:50%;
    background:var(--brand); color:white;
    font-size:0.72rem; font-weight:700;
    display:flex; align-items:center; justify-content:center;
    flex-shrink:0;
}
.rank-label{ font-weight:600; color:#2c3e2c; flex-grow:1; font-size:0.9rem; }
.rank-score{ font-weight:700; color:var(--brand-dark); font-size:0.85rem; }

/* Nutrition mini cards */
.nutri-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:0.8rem;
    margin-top:0.6rem;
}
.nutri-card{
    background:linear-gradient(160deg,#ffffff,var(--brand-light));
    border:1px solid #d9edd9;
    border-radius:14px;
    padding:0.9rem;
    text-align:center;
}
.nutri-card .icon{ font-size:1.4rem; }
.nutri-card .val{ font-size:1.15rem; font-weight:800; color:var(--brand-dark); }
.nutri-card .lbl{ font-size:0.75rem; color:var(--text-soft); font-weight:600; text-transform:uppercase; letter-spacing:0.03em; }

/* Section header */
.mini-header{
    font-weight:700;
    color:var(--brand-dark);
    font-size:1rem;
    margin:0.9rem 0 0.5rem 0;
    border-left:4px solid var(--accent);
    padding-left:0.5rem;
}

/* Empty state */
.empty-state{
    text-align:center;
    padding:3rem 1rem;
    background:#ffffff;
    border-radius:16px;
    border:1px dashed #cfe8cf;
    color:#6b7d6b;
}
.empty-state .emoji{ font-size:2.6rem; }
</style>
""", unsafe_allow_html=True)

# ADD THIS BLOCK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Hello.py")

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# PAGE TITLE
# ----------------------------------------------------------------------------
st.markdown('<div class="page-title">📸 AI Food Detection + Nutrition Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Upload a photo of your meal and let AI identify it and pull its nutrition facts</div>',
            unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def normalize_food_name(text):
    """Lowercase, drop underscores/parentheses/extra spaces so labels like
    'paneer_butter_masala' line up with dish names like 'Paneer Butter
    Masala (Restaurant Style)'."""
    text = text.lower().replace("_", " ").replace("-", " ")
    text = text.split("(")[0]
    return " ".join(text.split()).strip()


def find_best_dish_match(label, dish_names):
    """Try exact/substring match first (fast, precise), then fall back to
    fuzzy matching so near-misses in spelling/wording still resolve."""
    label_norm = normalize_food_name(label)
    if not label_norm:
        return None

    # 1) direct substring match either way
    for name in dish_names:
        name_norm = normalize_food_name(name)
        if label_norm in name_norm or name_norm in label_norm:
            return name

    # 2) fuzzy match on normalized names
    normalized_map = {}
    for name in dish_names:
        normalized_map.setdefault(normalize_food_name(name), name)
    close = difflib.get_close_matches(label_norm, normalized_map.keys(), n=1, cutoff=0.6)
    if close:
        return normalized_map[close[0]]

    return None


def render_nutrition_grid(food_data):
    st.markdown(f"""
    <div class="nutri-grid">
        <div class="nutri-card"><div class="icon">🔥</div><div class="val">{food_data['calories']}</div><div class="lbl">Calories (kcal)</div></div>
        <div class="nutri-card"><div class="icon">💪</div><div class="val">{food_data['protein']}</div><div class="lbl">Protein (g)</div></div>
        <div class="nutri-card"><div class="icon">🥑</div><div class="val">{food_data['fats']}</div><div class="lbl">Fat (g)</div></div>
        <div class="nutri-card"><div class="icon">🍞</div><div class="val">{food_data['carbohydrates']}</div><div class="lbl">Carbs (g)</div></div>
        <div class="nutri-card"><div class="icon">🍬</div><div class="val">{food_data['free_sugar']}</div><div class="lbl">Sugar (g)</div></div>
        <div class="nutri-card"><div class="icon">🌾</div><div class="val">{food_data['fibre']}</div><div class="lbl">Fibre (g)</div></div>
    </div>
    """, unsafe_allow_html=True)

    chart_data = pd.DataFrame({
        "Macro": ["Protein", "Fat", "Carbs", "Sugar", "Fibre"],
        "Grams": [food_data['protein'], food_data['fats'], food_data['carbohydrates'],
                  food_data['free_sugar'], food_data['fibre']]
    })
    st.markdown('<div class="mini-header">Macro breakdown</div>', unsafe_allow_html=True)
    st.bar_chart(chart_data.set_index("Macro"), color="#2e7d32")


# ----------------------------------------------------------------------------
# LOAD DATASET
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "..", "Data", "Indian_Food_Nutrition_Processed.csv")
        data = pd.read_csv(file_path, encoding="latin1")
        data.columns = (
            data.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"\(.*\)", "", regex=True)
            .str.rstrip("_")
        )
        return data
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# ----------------------------------------------------------------------------
# LOAD AI MODEL
# ----------------------------------------------------------------------------
@st.cache_resource
def load_model():
    try:
        # dima806/indian_food_image_detection is fine-tuned on 80 Indian food
        # classes (~75% val accuracy) — the previous model ("nateraw/food")
        # was trained on Food-101, which is almost entirely Western/international
        # dishes and rarely overlaps with the Indian_Food_Nutrition dataset,
        # which is why detections were off and nutrition matches kept failing.
        classifier = pipeline(
            "image-classification",
            model="dima806/indian_food_image_detection",
            top_k=3
        )
        return classifier
    except Exception as e:
        st.error(f"❌ Model loading failed: {e}")
        return None

with st.spinner("🔄 Loading AI model... (first time may take a minute)"):
    classifier = load_model()

if classifier is None:
    st.stop()

# ----------------------------------------------------------------------------
# UPLOAD + DETECTION
# ----------------------------------------------------------------------------
left, right = st.columns([1, 1.4], gap="large")

with left:
    st.markdown('<div class="mini-header">📤 Upload your food photo</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Food Image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Food Image", use_container_width=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">📷</div>
            <h4>No image yet</h4>
            <p>Drag and drop a photo of your meal to get started.</p>
        </div>
        """, unsafe_allow_html=True)

with right:
    if uploaded_file:
        try:
            with st.spinner("🤖 AI is detecting your food..."):
                try:
                    results = classifier(image)
                except Exception as e:
                    st.error(f"❌ Prediction failed: {e}")
                    st.stop()

            top = results[0]
            predicted_food = top["label"].replace("_", " ")
            confidence = top["score"] * 100

            st.markdown(f"""
            <div class="result-card">
                <div class="detected-label">✅ {predicted_food.title()}</div>
                <div class="confidence-text">Confidence: {confidence:.1f}%</div>
                <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{confidence:.1f}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔍 See all top predictions"):
                for i, r in enumerate(results, 1):
                    st.markdown(f"""
                    <div class="rank-row">
                        <div class="rank-num">{i}</div>
                        <div class="rank-label">{r['label'].replace('_',' ').title()}</div>
                        <div class="rank-score">{r['score']*100:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            # -----------------------------------
            # Match Nutrition Dataset
            # -----------------------------------
            try:
                all_dish_names = df["dish_name"].dropna().unique().tolist()
                matched_dish_name = None
                for r in results:
                    label = r["label"].replace("_", " ")
                    matched_dish_name = find_best_dish_match(label, all_dish_names)
                    if matched_dish_name:
                        predicted_food = label
                        break

                match = df[df["dish_name"] == matched_dish_name] if matched_dish_name else pd.DataFrame()

                if not match.empty:
                    food_data = match.iloc[0]
                    st.markdown('<div class="mini-header">🍽 Nutrition Summary</div>', unsafe_allow_html=True)
                    render_nutrition_grid(food_data)
                    st.success("✅ Nutrition data matched successfully!")
                else:
                    st.warning(f"⚠ '{predicted_food}' not found in Indian food dataset.")
                    st.markdown('<div class="mini-header">💡 Select manually instead</div>', unsafe_allow_html=True)

                    selected_food = st.selectbox("Select food manually:", sorted(all_dish_names), label_visibility="collapsed")

                    if selected_food:
                        manual_match = df[df["dish_name"] == selected_food].iloc[0]
                        st.markdown('<div class="mini-header">🍽 Nutrition Summary</div>', unsafe_allow_html=True)
                        render_nutrition_grid(manual_match)

            except Exception as e:
                st.error(f"❌ Dataset matching error: {e}")

        except Exception as e:
            st.error(f"❌ Image processing failed: {e}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">🍎</div>
            <h4>Results will appear here</h4>
            <p>Upload a photo on the left to see the detected food and its nutrition facts.</p>
        </div>
        """, unsafe_allow_html=True)