import streamlit as st
from Generate_Recommendations import Generator
from ImageFinder.ImageFinder import get_images_links as find_image
import pandas as pd

st.set_page_config(page_title="Custom Food Recommendation", page_icon="🔍", layout="wide")

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

/* Page title */
.page-title{
    text-align:center;
    font-weight:800;
    font-size:2.4rem;
    background:linear-gradient(90deg,var(--brand-dark),var(--accent));
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:0.1rem;
}
.page-subtitle{
    text-align:center;
    color:#6b7d6b;
    font-size:1rem;
    margin-bottom:1.8rem;
}

/* Form card */
div[data-testid="stForm"]{
    background:#ffffff;
    border:1px solid var(--brand-light);
    border-radius:18px;
    padding:1.6rem 1.8rem 1.2rem 1.8rem;
    box-shadow:0 4px 18px rgba(46,125,50,0.06);
}
div[data-testid="stForm"] h2, div[data-testid="stForm"] h3{
    color:var(--brand-dark);
}

/* Section headers inside form */
.section-label{
    font-weight:700;
    color:var(--brand-dark);
    font-size:1.05rem;
    margin:0.4rem 0 0.6rem 0;
    display:flex;
    align-items:center;
    gap:0.4rem;
}

/* Submit button */
button[kind="primaryFormSubmit"], div[data-testid="stFormSubmitButton"] button{
    background:linear-gradient(90deg,var(--brand),var(--accent)) !important;
    color:white !important;
    border:none !important;
    border-radius:10px !important;
    padding:0.6rem 1.4rem !important;
    font-weight:700 !important;
    width:100%;
    box-shadow:0 3px 10px rgba(46,125,50,0.25);
    transition:transform 0.15s ease;
}
div[data-testid="stFormSubmitButton"] button:hover{ transform:translateY(-1px); }

/* Recipe card */
.recipe-card{
    background:#ffffff;
    border:1px solid #e6efe6;
    border-radius:16px;
    overflow:hidden;
    margin-bottom:1.1rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
    transition:box-shadow 0.2s ease, transform 0.2s ease;
}
.recipe-card:hover{
    box-shadow:0 10px 24px rgba(46,125,50,0.15);
    transform:translateY(-2px);
}
.recipe-img-wrap{ width:100%; height:150px; overflow:hidden; background:var(--brand-light); }
.recipe-img-wrap img{ width:100%; height:100%; object-fit:cover; }
.recipe-title{
    font-weight:700;
    font-size:0.98rem;
    color:var(--brand-dark);
    padding:0.7rem 0.9rem 0.2rem 0.9rem;
    line-height:1.25rem;
    min-height:2.5rem;
}
.recipe-meta{
    display:flex;
    gap:0.5rem;
    flex-wrap:wrap;
    padding:0 0.9rem 0.7rem 0.9rem;
}
.time-badge{
    background:var(--brand-light);
    color:var(--brand-dark);
    font-size:0.72rem;
    font-weight:600;
    padding:0.18rem 0.55rem;
    border-radius:999px;
    white-space:nowrap;
}

/* Nutrition chips */
.chip-row{ display:flex; flex-wrap:wrap; gap:0.4rem; margin:0.4rem 0 0.8rem 0; }
.chip{
    background:var(--brand-light);
    border:1px solid #cfe8cf;
    color:var(--brand-dark);
    font-size:0.78rem;
    font-weight:600;
    padding:0.28rem 0.65rem;
    border-radius:999px;
}
.chip b{ color:var(--brand); }

/* Section sub-headers inside expander */
.mini-header{
    font-weight:700;
    color:var(--brand-dark);
    font-size:0.9rem;
    margin:0.7rem 0 0.3rem 0;
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

hr{ border-color:var(--brand-light); }
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

nutrition_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent',
                     'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']

nutrition_icons = {
    'Calories': '🔥', 'FatContent': '🧈', 'SaturatedFatContent': '🥓', 'CholesterolContent': '🩸',
    'SodiumContent': '🧂', 'CarbohydrateContent': '🍞', 'FiberContent': '🌾',
    'SugarContent': '🍬', 'ProteinContent': '🍗'
}

if 'generated' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None


# ----------------------------------------------------------------------------
# LOGIC
# ----------------------------------------------------------------------------
class Recommendation:
    def __init__(self, nutrition_list, nb_recommendations, ingredient_txt):
        self.nutrition_list = nutrition_list
        self.nb_recommendations = nb_recommendations
        self.ingredient_txt = ingredient_txt

    def generate(self):
        params = {'n_neighbors': self.nb_recommendations, 'return_distance': False}
        ingredients = self.ingredient_txt.split(';')
        generator = Generator(self.nutrition_list, ingredients, params)
        recommendations = generator.generate()
        recommendations = recommendations.json()['output']
        if recommendations is not None:
            for recipe in recommendations:
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations


# ----------------------------------------------------------------------------
# DISPLAY
# ----------------------------------------------------------------------------
class Display:
    def __init__(self):
        self.nutrition_values = nutrition_values

    def _empty_state(self):
        st.markdown("""
        <div class="empty-state">
            <div class="emoji">🙁</div>
            <h4>No recipes found</h4>
            <p>Try widening your nutrition ranges or removing an ingredient.</p>
        </div>
        """, unsafe_allow_html=True)

    def display_recommendation(self, recommendations):
        if not recommendations:
            self._empty_state()
            return

        st.markdown(f"##### {len(recommendations)} recipes matched your preferences")
        st.write("")

        cols_per_row = 5
        cols = st.columns(cols_per_row)

        for idx, recipe in enumerate(recommendations):
            col = cols[idx % cols_per_row]
            with col:
                recipe_name = recipe['Name']
                recipe_link = recipe['image_link']
                total_time = recipe.get('TotalTime', '—')

                st.markdown(f"""
                <div class="recipe-card">
                    <div class="recipe-img-wrap">
                        <img src="{recipe_link}" alt="{recipe_name}">
                    </div>
                    <div class="recipe-title">{recipe_name}</div>
                    <div class="recipe-meta">
                        <span class="time-badge">⏱ {total_time} min</span>
                        <span class="time-badge">🔥 {recipe.get('Calories', '—')} kcal</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("View details"):
                    chip_html = '<div class="chip-row">' + "".join(
                        f'<span class="chip">{nutrition_icons.get(v, "")} {v.replace("Content","")}: '
                        f'<b>{recipe[v]}</b></span>'
                        for v in nutrition_values
                    ) + '</div>'
                    st.markdown('<div class="mini-header">Nutritional Values</div>', unsafe_allow_html=True)
                    st.markdown(chip_html, unsafe_allow_html=True)

                    st.markdown('<div class="mini-header">Ingredients</div>', unsafe_allow_html=True)
                    for ingredient in recipe['RecipeIngredientParts']:
                        st.markdown(f"- {ingredient}")

                    st.markdown('<div class="mini-header">Instructions</div>', unsafe_allow_html=True)
                    for i, instruction in enumerate(recipe['RecipeInstructions'], 1):
                        st.markdown(f"{i}. {instruction}")

                    st.markdown('<div class="mini-header">Time</div>', unsafe_allow_html=True)
                    t1, t2, t3 = st.columns(3)
                    t1.metric("Cook", f"{recipe['CookTime']}m")
                    t2.metric("Prep", f"{recipe['PrepTime']}m")
                    t3.metric("Total", f"{recipe['TotalTime']}m")

    def display_overview(self, recommendations):
        if not recommendations:
            return

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_recipe_name = st.selectbox(
                '🍽️ Select a recipe to inspect',
                [recipe['Name'] for recipe in recommendations]
            )

        selected_recipe = next(r for r in recommendations if r['Name'] == selected_recipe_name)

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔥 Calories", f"{selected_recipe['Calories']}")
        m2.metric("🍗 Protein", f"{selected_recipe['ProteinContent']} g")
        m3.metric("🍞 Carbs", f"{selected_recipe['CarbohydrateContent']} g")
        m4.metric("🧈 Fat", f"{selected_recipe['FatContent']} g")

        st.markdown('<div class="mini-header">Full nutrition breakdown</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Nutrition": [n.replace("Content", "") for n in nutrition_values],
            "Values": [selected_recipe[n] for n in nutrition_values]
        })
        st.bar_chart(chart_data.set_index("Nutrition"), color="#2e7d32")


# ----------------------------------------------------------------------------
# PAGE
# ----------------------------------------------------------------------------
st.markdown('<div class="page-title">Custom Food Recommendation</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Dial in your nutrition targets and get recipes tailored to you</div>',
            unsafe_allow_html=True)

display = Display()

with st.form("recommendation_form"):
    st.markdown('<div class="section-label">🎯 Nutritional targets</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        Calories = st.slider('🔥 Calories', 0, 2000, 500)
        SodiumContent = st.slider('🧂 Sodium (mg)', 0, 2300, 400)
        FiberContent = st.slider('🌾 Fiber (g)', 0, 50, 10)
    with c2:
        FatContent = st.slider('🧈 Fat (g)', 0, 100, 50)
        CarbohydrateContent = st.slider('🍞 Carbohydrates (g)', 0, 325, 100)
        SugarContent = st.slider('🍬 Sugar (g)', 0, 40, 10)
    with c3:
        SaturatedFatContent = st.slider('🥓 Saturated Fat (g)', 0, 13, 0)
        CholesterolContent = st.slider('🩸 Cholesterol (mg)', 0, 300, 0)
        ProteinContent = st.slider('🍗 Protein (g)', 0, 40, 10)

    nutritions_values_list = [Calories, FatContent, SaturatedFatContent, CholesterolContent, SodiumContent,
                               CarbohydrateContent, FiberContent, SugarContent, ProteinContent]

    st.divider()
    st.markdown('<div class="section-label">⚙️ Recommendation options</div>', unsafe_allow_html=True)

    o1, o2 = st.columns([1, 2])
    with o1:
        nb_recommendations = st.slider('Number of recommendations', 5, 20, step=5)
    with o2:
        ingredient_txt = st.text_input(
            'Ingredients to include (separated by ";")',
            placeholder='Milk;eggs;butter;chicken...'
        )
        st.caption('Example: Milk;eggs;butter;chicken...')

    st.write("")
    generated = st.form_submit_button("✨ Generate recommendations")

if generated:
    with st.spinner('Cooking up your recommendations...'):
        recommendation = Recommendation(nutritions_values_list, nb_recommendations, ingredient_txt)
        recommendations = recommendation.generate()
        st.session_state.recommendations = recommendations
    st.session_state.generated = True

if st.session_state.generated:
    tab1, tab2 = st.tabs(["🍽️ Recommendations", "📊 Nutrition Overview"])
    with tab1:
        display.display_recommendation(st.session_state.recommendations)
    with tab2:
        display.display_overview(st.session_state.recommendations)