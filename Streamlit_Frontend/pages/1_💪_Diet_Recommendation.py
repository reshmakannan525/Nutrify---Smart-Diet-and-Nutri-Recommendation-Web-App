import streamlit as st
import pandas as pd
import random  # for seeded RNG (deterministic recommendations)
import hashlib  # for building a stable seed from the person's profile
import re  # for whole-word keyword matching + splitting "avoid ingredients" input
import datetime
from Generate_Recommendations import Generator
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Automatic Diet Recommendation", page_icon="💪", layout="wide")

# ============================================================
# GLOBAL STYLE — shared visual language (gradient header, glass
# cards, badges, stat grid) so this page matches the rest of the app.
# ============================================================
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e8f5e9 !important; }
[data-testid="stSidebarNav"] { display: none; }
.logout-wrap .stButton > button {
    background-color: #6eb52f !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    width: 100%;
    font-weight: 600 !important;
    padding: 10px 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}
.logout-wrap .stButton > button:hover { background-color: #5a9a24 !important; }
.logout-wrap .stButton > button svg,
.logout-wrap .stButton > button [data-testid="stIconMaterial"] {
    color: #ffffff !important;
    fill: #ffffff !important;
}

.page-header {
    background: linear-gradient(135deg, #6eb52f 0%, #2e7d32 100%);
    padding: 30px 34px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 6px 22px rgba(46,125,50,0.25);
}
.page-header h1 { margin: 0; font-size: 30px; }
.page-header p { margin: 8px 0 0 0; opacity: 0.92; font-size: 14.5px; }

.glass-card {
    background: rgba(255,255,255,0.75);
    border: 1px solid #e8f5e9;
    border-radius: 16px;
    padding: 22px 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.section-title {
    display: flex; align-items: center; gap: 8px;
    font-size: 19px; font-weight: 800; color: #1b5e20; margin-bottom: 12px;
}

.badge {
    display: inline-block; padding: 3px 11px; border-radius: 20px;
    font-size: 12px; font-weight: 700; margin-right: 6px; margin-bottom: 6px;
}
.badge-cal   { background: #fff3e0; color: #e65100; }
.badge-protein { background: #e8f5e9; color: #2e7d32; }
.badge-time  { background: #e3f2fd; color: #1565c0; }
.badge-why   { background: #fce4ec; color: #ad1457; }
.badge-rest  { background: #eceff1; color: #546e7a; }

.stat-grid { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 22px; }
.stat-card {
    flex: 1; min-width: 150px; background: white; border-radius: 14px;
    padding: 16px 18px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.stat-card .stat-value { font-size: 24px; font-weight: 800; color: #2e7d32; }
.stat-card .stat-label { font-size: 12px; color: #667; margin-top: 3px; }

.recipe-card {
    background: white; border-radius: 14px; padding: 14px 16px 4px 16px;
    margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.recipe-card img { border-radius: 10px; }

.day-card {
    background: white; border-radius: 14px; padding: 12px; min-height: 210px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 10px;
}
.day-card h6 { margin: 0 0 8px 0; color: #1b5e20; font-weight: 800; }
.day-card .split-tag {
    display:inline-block; background:#e8f5e9; color:#2e7d32; font-size:11px;
    font-weight:700; padding:2px 8px; border-radius:10px; margin-bottom:8px;
}
.day-card.rest { opacity: 0.65; }

/* 🆕 Generate button — make it the clear visual anchor of the form */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #8bd44e 0%, #2e7d32 100%) !important;
    color: #ffffff !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    letter-spacing: 0.3px;
    padding: 16px 0 !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 8px 22px rgba(46,125,50,0.40) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 10px 28px rgba(46,125,50,0.55) !important;
}
[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) scale(0.99) !important;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Hello.py")

# Sidebar navigation
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

nutritions_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent',
                     'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']

# ============================================================
# MEDICAL CONDITIONS CONFIG
# ============================================================
MEDICAL_CONDITIONS_BY_CATEGORY = {
    "Nutrient Deficiencies": {
        'Iron Deficiency (Anemia)': {
            'adjustments': {'ProteinContent': 1.20},
            'tip': 'Extra protein target set. Prioritize iron-rich ingredients (spinach, lentils, chickpeas, lean red meat, tofu) and pair with Vitamin C (citrus, tomato) to boost absorption.',
        },
        'Vitamin B12 Deficiency': {
            'adjustments': {'ProteinContent': 1.15},
            'tip': 'B12 is not tracked in this dataset. Favor animal-based or fortified ingredients — eggs, dairy, fish, fortified cereals/plant milk (especially important if vegetarian/vegan).',
        },
        'Vitamin D Deficiency': {
            'adjustments': {'FatContent': 1.05},
            'tip': 'Vitamin D is fat-soluble, so a slightly higher healthy-fat target is set. Look for fatty fish, egg yolks, fortified milk, and get regular sensible sun exposure.',
        },
        'Calcium Deficiency': {
            'adjustments': {},
            'tip': 'Calcium is not tracked in this dataset. Favor dairy, fortified plant milk, tofu, almonds, and leafy greens like kale.',
        },
        'Vitamin C Deficiency': {
            'adjustments': {},
            'tip': 'Vitamin C is not tracked in this dataset. Favor citrus fruits, bell peppers, strawberries, and broccoli.',
        },
        'Folate (Vitamin B9) Deficiency': {
            'adjustments': {'FiberContent': 1.10},
            'tip': 'Slightly higher fiber target, since folate-rich foods overlap with fiber-rich ones. Favor leafy greens, legumes, and citrus.',
        },
        'Zinc Deficiency': {
            'adjustments': {'ProteinContent': 1.10},
            'tip': 'Zinc is not tracked in this dataset. Favor meat, shellfish, seeds (pumpkin, sesame), and legumes.',
        },
        'Magnesium Deficiency': {
            'adjustments': {'FiberContent': 1.10},
            'tip': 'Magnesium is not tracked in this dataset. Favor nuts, seeds, whole grains, and leafy greens.',
        },
        'Protein-Energy Malnutrition': {
            'adjustments': {'Calories': 1.15, 'ProteinContent': 1.30},
            'tip': 'Higher calorie and protein targets set to support rebuilding energy and muscle reserves.',
        },
        'Omega-3 Deficiency': {
            'adjustments': {'FatContent': 1.05},
            'tip': 'Omega-3 isn\'t tracked separately in this dataset. Favor fatty fish, walnuts, flaxseed, and chia seeds.',
        },
    },
    "Metabolic & Hormonal": {
        'PCOD/PCOS': {
            'adjustments': {'CarbohydrateContent': 0.85, 'SugarContent': 0.55, 'ProteinContent': 1.15, 'FiberContent': 1.25},
            'tip': 'Lower-glycemic meals with extra fiber and protein can help support insulin sensitivity.',
        },
        'Diabetes (Type 2)': {
            'adjustments': {'CarbohydrateContent': 0.75, 'SugarContent': 0.40, 'FiberContent': 1.30},
            'tip': 'Reduced carbohydrate & sugar targets with higher fiber help support steadier blood sugar.',
        },
        'Prediabetes / Insulin Resistance': {
            'adjustments': {'CarbohydrateContent': 0.85, 'SugarContent': 0.60, 'FiberContent': 1.20},
            'tip': 'Milder carb/sugar reduction than diabetes, with a fiber boost, to help support insulin sensitivity.',
        },
        'Hypothyroidism': {
            'adjustments': {'SodiumContent': 0.85, 'FiberContent': 1.15},
            'tip': 'Slightly reduced sodium and increased fiber to support metabolic and digestive health.',
        },
        'Hyperthyroidism': {
            'adjustments': {'Calories': 1.10, 'ProteinContent': 1.15},
            'tip': 'Higher calorie and protein targets to help offset an elevated metabolic rate.',
        },
        'Obesity': {
            'adjustments': {'Calories': 0.85, 'FatContent': 0.85, 'SugarContent': 0.70, 'FiberContent': 1.20},
            'tip': 'Lower calorie, fat, and sugar targets with more fiber to support satiety on fewer calories.',
        },
    },
    "Heart & Blood Pressure": {
        'Hypertension (High BP)': {
            'adjustments': {'SodiumContent': 0.55, 'SaturatedFatContent': 0.80},
            'tip': 'Sodium and saturated fat targets are reduced to support healthy blood pressure.',
        },
        'High Cholesterol': {
            'adjustments': {'SaturatedFatContent': 0.60, 'CholesterolContent': 0.60},
            'tip': 'Saturated fat and cholesterol targets are reduced to support heart health.',
        },
        'Heart Disease': {
            'adjustments': {'SaturatedFatContent': 0.60, 'SodiumContent': 0.70, 'CholesterolContent': 0.60, 'FiberContent': 1.20},
            'tip': 'Meaningful reductions in saturated fat, sodium, and cholesterol, with more fiber, to support cardiovascular health.',
        },
    },
    "Digestive & Organ Health": {
        'Fatty Liver Disease': {
            'adjustments': {'SugarContent': 0.50, 'FatContent': 0.80, 'CarbohydrateContent': 0.85},
            'tip': 'Lower sugar, fat, and refined carb targets to reduce strain on the liver.',
        },
        'Kidney Disease (CKD)': {
            'adjustments': {'ProteinContent': 0.75, 'SodiumContent': 0.60},
            'tip': 'Lower protein and sodium targets set. Potassium and phosphorus aren\'t tracked in this dataset — please check labels for those separately, as CKD diets are highly individual.',
        },
        'Gout': {
            'adjustments': {'ProteinContent': 0.80},
            'tip': 'Lower protein target since purine-rich foods (red/organ meat, shellfish) can trigger flares. Favor plant proteins, and limit alcohol.',
        },
        'IBS (Irritable Bowel Syndrome)': {
            'adjustments': {'FatContent': 0.90},
            'tip': 'Slightly reduced fat target. Consider a low-FODMAP approach and identify your personal trigger foods.',
        },
        'Acid Reflux / GERD': {
            'adjustments': {'FatContent': 0.80},
            'tip': 'Lower fat target, since fatty/spicy/acidic foods commonly trigger reflux. Avoid large meals close to bedtime.',
        },
        'Lactose Intolerance': {
            'adjustments': {},
            'tip': 'Dairy content isn\'t tracked separately in this dataset — watch recipe ingredients for milk, cheese, and cream, or choose lactose-free alternatives.',
        },
        'Celiac / Gluten Sensitivity': {
            'adjustments': {},
            'tip': 'Gluten isn\'t tracked in this dataset — check ingredients for wheat, barley, and rye, and choose certified gluten-free options where needed.',
        },
    },
    "Bone Health": {
        'Osteoporosis': {
            'adjustments': {'ProteinContent': 1.10},
            'tip': 'Slightly higher protein target for bone-supporting muscle mass. Favor calcium- and Vitamin D-rich foods (dairy, fortified plant milk, leafy greens, sunlight).',
        },
    },
    "Life Stage": {
        'Pregnancy': {
            'adjustments': {'Calories': 1.15, 'ProteinContent': 1.20, 'FiberContent': 1.10},
            'tip': 'Higher calorie, protein, and fiber targets. Ensure adequate folate and iron — consult your doctor for prenatal-specific needs.',
        },
        'Lactation / Breastfeeding': {
            'adjustments': {'Calories': 1.25, 'ProteinContent': 1.20},
            'tip': 'Higher calorie and protein targets to support milk production and recovery.',
        },
    },
}

MEDICAL_CONDITION_ADJUSTMENTS = {
    condition: data['adjustments']
    for category in MEDICAL_CONDITIONS_BY_CATEGORY.values()
    for condition, data in category.items()
}
MEDICAL_CONDITION_TIPS = {
    condition: data['tip']
    for category in MEDICAL_CONDITIONS_BY_CATEGORY.values()
    for condition, data in category.items()
}
MEDICAL_CONDITION_OPTIONS = list(MEDICAL_CONDITION_ADJUSTMENTS.keys())

# ============================================================
# DIETARY PREFERENCE (Veg / Non-Veg / Eggetarian / Vegan)
# ============================================================
MEAT_FISH_KEYWORDS = [
    'chicken', 'mutton', 'beef', 'pork', 'lamb', 'turkey', 'bacon', 'ham',
    'sausage', 'fish', 'salmon', 'tuna', 'shrimp', 'prawn', 'crab', 'lobster',
    'anchovy', 'oyster', 'squid', 'gelatin', 'meat', 'veal', 'duck', 'clam',
    'scallop', 'mussel', 'worcestershire', 'lard', 'suet', 'isinglass',
    'chorizo', 'pepperoni', 'salami', 'prosciutto', 'foie gras'
]
EGG_KEYWORDS = ['egg', 'eggs']
DAIRY_KEYWORDS = [
    'milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt', 'ghee',
    'paneer', 'curd', 'whey', 'casein', 'rennet'
]
HONEY_KEYWORDS = ['honey']

DIET_PREFERENCE_OPTIONS = ['No Preference (Show All)', 'Vegetarian', 'Eggetarian', 'Non-Vegetarian', 'Vegan']

DIET_PREFERENCE_EXCLUDE_KEYWORDS = {
    'No Preference (Show All)': [],
    'Non-Vegetarian': [],
    'Vegetarian': MEAT_FISH_KEYWORDS + EGG_KEYWORDS,
    'Eggetarian': MEAT_FISH_KEYWORDS,
    'Vegan': MEAT_FISH_KEYWORDS + EGG_KEYWORDS + DAIRY_KEYWORDS + HONEY_KEYWORDS,
}

ALLERGEN_KEYWORDS = {
    'Peanuts': ['peanut', 'peanuts', 'groundnut'],
    'Tree Nuts': ['almond', 'cashew', 'walnut', 'pecan', 'pistachio', 'hazelnut', 'macadamia'],
    'Shellfish': ['shrimp', 'prawn', 'crab', 'lobster', 'clam', 'scallop', 'mussel', 'oyster', 'squid'],
    'Soy': ['soy', 'soya', 'tofu', 'edamame'],
    'Gluten (Wheat)': ['wheat', 'barley', 'rye', 'flour', 'bread', 'pasta'],
    'Dairy': DAIRY_KEYWORDS,
    'Sesame': ['sesame', 'tahini'],
    'Eggs': EGG_KEYWORDS,
}
ALLERGEN_OPTIONS = list(ALLERGEN_KEYWORDS.keys())

KEYWORD_FALSE_POSITIVES = {
    'egg': ['eggplant', 'nutmeg'],
    'ham': ['shampoo'],
    'soy': ['soybean oil free'],
}

# ============================================================
# 🆕 CUISINE PREFERENCE (South Indian, etc.)
# ============================================================
# Best-effort filter: the recipe dataset isn't tagged by cuisine, so we
# match recipe name + ingredients + instructions against a keyword list
# of dishes, ingredients, and techniques strongly associated with South
# Indian cooking. This is inclusive (a recipe must match at least one
# keyword), unlike the allergy/diet lists above which are exclusive.
SOUTH_INDIAN_KEYWORDS = [
    # dishes
    'dosa', 'idli', 'idly', 'vada', 'wada', 'uttapam', 'uthappam', 'appam',
    'sambar', 'sambhar', 'rasam', 'payasam', 'kheer', 'pongal', 'upma',
    'poha', 'avial', 'aviyal', 'poriyal', 'kootu', 'thoran', 'koottu',
    'chutney', 'pachadi', 'kuzhambu', 'kulambu', 'bisibelebath', 'bisi bele',
    'biryani', 'pulao', 'pulav', 'curd rice', 'lemon rice', 'tamarind rice',
    'coconut rice', 'puliyodarai', 'medu vada', 'rava', 'semiya',
    'payasa', 'kesari', 'obbattu', 'holige', 'puran poli',
    'pesarattu', 'adai', 'paniyaram', 'kozhukattai', 'modak',
    'thayir sadam', 'vatha kuzhambu', 'mor kuzhambu', 'erissery',
    'olan', 'kaalan', 'moru curry', 'meen curry', 'fish curry',
    'chettinad', 'hyderabadi', 'andhra', 'malabar', 'kerala', 'karnataka',
    'tamil', 'udupi',
    # ingredients / techniques common to South Indian cooking
    'curry leaves', 'curry leaf', 'coconut', 'tamarind', 'urad dal',
    'toor dal', 'toor daal', 'mustard seeds', 'asafoetida', 'hing',
    'gunpowder', 'podi', 'jaggery', 'coconut oil', 'coconut milk',
    'black gram', 'coconut chutney',
]
CUISINE_OPTIONS = ['No Preference (All Cuisines)', 'South Indian']
CUISINE_KEYWORDS = {
    'No Preference (All Cuisines)': [],
    'South Indian': SOUTH_INDIAN_KEYWORDS,
}


def recipe_matches_cuisine(recipe, cuisine_keywords):
    """Returns True if no cuisine filter is set, or if the recipe's
    name/ingredients/instructions contain at least one cuisine keyword."""
    if not cuisine_keywords:
        return True
    ingredients_text = ' '.join(recipe.get('RecipeIngredientParts', []) or [])
    instructions_text = ' '.join(recipe.get('RecipeInstructions', []) or [])
    combined_text = f"{recipe.get('Name', '')} {ingredients_text} {instructions_text}".lower()
    return any(keyword in combined_text for keyword in cuisine_keywords)


def singularize(word):
    if word.endswith('ies') and len(word) > 4:
        return word[:-3] + 'y'
    if word.endswith(('ches', 'shes', 'xes', 'oes')) and len(word) > 4:
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss') and len(word) > 3:
        return word[:-1]
    return word


def build_exclude_keyword_list(diet_preference, allergies=None, avoid_ingredients_text=''):
    exclude = list(DIET_PREFERENCE_EXCLUDE_KEYWORDS.get(diet_preference, []))
    for allergy in (allergies or []):
        exclude.extend(ALLERGEN_KEYWORDS.get(allergy, []))
    custom_words = []
    if avoid_ingredients_text:
        raw_words = [
            w.strip().lower()
            for w in re.split(r'[,;&\n]+|\band\b', avoid_ingredients_text.lower())
            if w.strip()
        ]
        custom_words = [singularize(w) for w in raw_words]
        exclude.extend(custom_words)
    seen = set()
    deduped = []
    for kw in exclude:
        if kw not in seen:
            seen.add(kw)
            deduped.append(kw)
    return deduped, custom_words


def recipe_excluded_by(recipe, exclude_keywords):
    if not exclude_keywords:
        return None
    ingredients_text = ' '.join(recipe.get('RecipeIngredientParts', []) or [])
    combined_text = f"{recipe.get('Name', '')} {ingredients_text}".lower()
    for keyword in exclude_keywords:
        text_for_check = combined_text
        for false_positive in KEYWORD_FALSE_POSITIVES.get(keyword, []):
            text_for_check = text_for_check.replace(false_positive, '')
        pattern = rf'\b{re.escape(keyword)}(?:es|s)?\b'
        if re.search(pattern, text_for_check):
            return keyword
    return None


def recipe_passes_filters(recipe, exclude_keywords):
    return recipe_excluded_by(recipe, exclude_keywords) is None

# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None
    st.session_state.person = None
    st.session_state.weight_loss_option = None
st.session_state.setdefault('favorites', [])          # ❤️ saved recipes
st.session_state.setdefault('nutrition_log', [])       # 📝 entries pushed to the Nutrition Tracker
st.session_state.setdefault('last_profile', {})        # 💾 last submitted form values, for "Load my last profile"
st.session_state.setdefault('swap_nonce', {})           # 🔄 per-meal swap counters


class Person:
    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss,
                 medical_conditions=None, diet_preference='No Preference (Show All)',
                 allergies=None, avoid_ingredients_text='', shuffle_variety=False,
                 cuisine_preference='No Preference (All Cuisines)'):  # 🆕
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss
        self.medical_conditions = medical_conditions or []
        self.diet_preference = diet_preference or 'No Preference (Show All)'
        self.allergies = allergies or []
        self.avoid_ingredients_text = avoid_ingredients_text or ''
        self.shuffle_variety = shuffle_variety
        self.cuisine_preference = cuisine_preference or 'No Preference (All Cuisines)'  # 🆕
        self.exclude_match_counts = {}
        self.custom_avoid_words = []
        self.nutrient_why_tags = {}  # 🆕 nutrient -> list of (condition, pct_change) for "why" badges
        self.cuisine_fallback_used = {}  # 🆕 meal -> True if the cuisine filter had to be relaxed

    def calculate_bmi(self):
        return round(self.weight / ((self.height / 100) ** 2), 2)

    def display_result(self):
        bmi = self.calculate_bmi()
        bmi_string = f'{bmi} kg/m²'
        if bmi < 18.5:
            category, color = 'Underweight', 'Red'
        elif 18.5 <= bmi < 25:
            category, color = 'Normal', 'Green'
        elif 25 <= bmi < 30:
            category, color = 'Overweight', 'Yellow'
        else:
            category, color = 'Obesity', 'Red'
        return bmi_string, category, color

    def calculate_bmr(self):
        if self.gender == 'Male':
            return 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        return 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

    def calories_calculator(self):
        activites = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)',
                     'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activites.index(self.activity)]
        return self.calculate_bmr() * weight

    def _build_rng(self, meal_name, nonce=0):
        seed_parts = [
            self.age, self.height, self.weight, self.gender, self.activity,
            self.weight_loss, sorted(self.medical_conditions), self.diet_preference,
            sorted(self.allergies), self.avoid_ingredients_text, self.cuisine_preference, meal_name,
        ]
        if self.shuffle_variety:
            seed_parts.append(random.random())
        seed_parts.append(nonce)
        seed_string = str(seed_parts)
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2 ** 32)
        return random.Random(seed)

    def apply_medical_adjustments(self, recommended_nutrition):
        if not self.medical_conditions:
            return recommended_nutrition
        nutrient_factor_lists = {}
        why_tags = {}
        for condition in self.medical_conditions:
            factors = MEDICAL_CONDITION_ADJUSTMENTS.get(condition, {})
            for nutrient, factor in factors.items():
                if nutrient in nutritions_values:
                    nutrient_factor_lists.setdefault(nutrient, []).append(factor)
                    why_tags.setdefault(nutrient, []).append((condition, factor))
        adjusted = list(recommended_nutrition)
        for nutrient, factors in nutrient_factor_lists.items():
            idx = nutritions_values.index(nutrient)
            avg_factor = sum(factors) / len(factors)
            avg_factor = max(0.5, min(1.6, avg_factor))
            adjusted[idx] = max(adjusted[idx] * avg_factor, 0.0)
        self.nutrient_why_tags = why_tags  # 🆕 saved for "why" badges
        return adjusted

    def _base_nutrition_target(self, meal, meal_calories, rng):
        if meal == 'breakfast':
            return [meal_calories, rng.uniform(10, 30), rng.uniform(0, 4), rng.uniform(0, 30),
                    rng.uniform(0, 400), rng.uniform(40, 75), rng.uniform(4, 10), rng.uniform(0, 10), rng.uniform(30, 100)]
        elif meal in ('lunch', 'dinner'):
            return [meal_calories, rng.uniform(20, 40), rng.uniform(0, 4), rng.uniform(0, 30),
                    rng.uniform(0, 400), rng.uniform(40, 75), rng.uniform(4, 20), rng.uniform(0, 10), rng.uniform(50, 175)]
        else:
            return [meal_calories, rng.uniform(10, 30), rng.uniform(0, 4), rng.uniform(0, 30),
                    rng.uniform(0, 400), rng.uniform(40, 75), rng.uniform(4, 10), rng.uniform(0, 10), rng.uniform(30, 100)]

    def _fetch_candidate_pool(self, base_target, rng, num_calls=3):
        combined = {}
        any_success = False
        for _ in range(num_calls):
            jittered_target = [max(v * rng.uniform(0.9, 1.1), 0.0) for v in base_target]
            generator = Generator(jittered_target)
            response = generator.generate()
            if response is None:
                continue
            any_success = True
            try:
                recipes = response.json()['output']
            except Exception:
                continue
            for recipe in recipes:
                combined[recipe.get('Name')] = recipe
        return list(combined.values()), any_success

    def _generate_meal(self, meal, total_calories, nonce=0):
        """🆕 Generates recommendations for a single meal. Shared by the
        full-plan generator and the per-recipe 'Swap' button (which calls
        this again with an incremented nonce to get a different result)."""
        meal_calories = self.meals_calories_perc[meal] * total_calories
        rng = self._build_rng(meal, nonce=nonce)

        recommended_nutrition = self._base_nutrition_target(meal, meal_calories, rng)
        recommended_nutrition = self.apply_medical_adjustments(recommended_nutrition)

        exclude_keywords, custom_avoid_words = build_exclude_keyword_list(
            self.diet_preference, self.allergies, self.avoid_ingredients_text
        )
        self.custom_avoid_words = custom_avoid_words
        cuisine_keywords = CUISINE_KEYWORDS.get(self.cuisine_preference, [])

        # 🆕 Cast a wider net when a cuisine filter is active — South
        # Indian (or any cuisine) dishes are a minority of a generic
        # recipe dataset, so more candidate calls improve the odds of
        # finding real matches instead of falling back too often.
        num_calls = 6 if cuisine_keywords else 3
        candidate_pool, any_success = self._fetch_candidate_pool(recommended_nutrition, rng, num_calls=num_calls)
        if not any_success:
            return [], False, {}

        filtered_recipes = []
        match_counts = {kw: 0 for kw in exclude_keywords}
        for recipe in candidate_pool:
            matched_keyword = recipe_excluded_by(recipe, exclude_keywords)
            if matched_keyword:
                match_counts[matched_keyword] += 1
            else:
                filtered_recipes.append(recipe)

        if not filtered_recipes:
            filtered_recipes = candidate_pool  # fall back to unfiltered pool if the exclude filter wiped everything

        # 🆕 Apply the cuisine filter on top of the diet/allergy filter.
        # If nothing survives, fall back to the diet-filtered pool and
        # flag it so the UI can tell the user we couldn't find a strict
        # cuisine match this time.
        self.cuisine_fallback_used[meal] = False
        if cuisine_keywords:
            cuisine_matched = [r for r in filtered_recipes if recipe_matches_cuisine(r, cuisine_keywords)]
            if cuisine_matched:
                recommended_recipes = cuisine_matched
            elif filtered_recipes:
                recommended_recipes = filtered_recipes
                self.cuisine_fallback_used[meal] = True
            else:
                recommended_recipes = []
        else:
            recommended_recipes = filtered_recipes if filtered_recipes else candidate_pool

        for recipe in recommended_recipes:
            recipe['image_link'] = find_image(recipe['Name'])

        return recommended_recipes, True, match_counts

    def generate_recommendations(self, status=None):
        total_calories = self.weight_loss * self.calories_calculator()
        recommendations = []
        exclude_match_counts_total = {}

        for meal in self.meals_calories_perc:
            if status is not None:
                status.update(label=f"Matching recipes for {meal}...")
            recipes, ok, match_counts = self._generate_meal(meal, total_calories, nonce=0)
            if not ok:
                st.error("Could not connect to the backend. Make sure FastAPI is running.")
                return []
            if not recipes:
                st.warning(f"No recipes could be found for {meal}. Try relaxing your filters.")
            elif self.cuisine_fallback_used.get(meal):
                st.info(f"Couldn't find enough {self.cuisine_preference} matches for {meal} — showing the closest options instead.")
            elif recipe_excluded_by(recipes[0], []) is None and any(match_counts.values()) and len(recipes) == 0:
                pass
            for kw, n in match_counts.items():
                exclude_match_counts_total[kw] = exclude_match_counts_total.get(kw, 0) + n
            recommendations.append(recipes)

        self.exclude_match_counts = exclude_match_counts_total
        return recommendations

    def swap_meal(self, meal_name, meal_index):
        """🆕 Regenerate just one meal's recipes with a fresh nonce."""
        total_calories = self.weight_loss * self.calories_calculator()
        nonce = st.session_state.swap_nonce.get(meal_name, 0) + 1
        st.session_state.swap_nonce[meal_name] = nonce
        recipes, ok, _ = self._generate_meal(meal_name, total_calories, nonce=nonce)
        if ok and recipes:
            st.session_state.recommendations[meal_index] = recipes
        elif not ok:
            st.error("Could not connect to the backend to swap this meal.")
        else:
            st.warning(f"No alternate recipes found for {meal_name}.")


class Display:
    def __init__(self):
        self.plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
        self.weights = [1, 0.9, 0.8, 0.6]
        self.losses = ['-0 kg/week', '-0.25 kg/week', '-0.5 kg/week', '-1 kg/week']

    # ---------- 🆕 header + stat scorecard ----------
    def display_page_header(self):
        st.markdown("""
        <div class="page-header">
            <h1>💪 Automatic Diet & Exercise Recommendation</h1>
            <p>One profile, one click — a personalized meal plan and workout plan, together.</p>
        </div>
        """, unsafe_allow_html=True)

    def display_scorecard(self, person, exercise_plan):
        bmi_string, category, _ = person.display_result()
        maintain_calories = person.calories_calculator()
        target_calories = round(maintain_calories * person.weight_loss)
        num_meals = len(person.meals_calories_perc)
        workout_days = len(exercise_plan) if exercise_plan else 0
        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-card"><div class="stat-value">{bmi_string}</div><div class="stat-label">BMI · {category}</div></div>
            <div class="stat-card"><div class="stat-value">{target_calories}</div><div class="stat-label">Daily Calorie Target</div></div>
            <div class="stat-card"><div class="stat-value">{num_meals}</div><div class="stat-label">Meals Planned</div></div>
            <div class="stat-card"><div class="stat-value">{workout_days}</div><div class="stat-label">Workout Days/Week</div></div>
        </div>
        """, unsafe_allow_html=True)

    def display_bmi(self, person):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📏 BMI Calculator</div>', unsafe_allow_html=True)
        bmi_string, category, color = person.display_result()
        st.metric(label="Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 22px; font-weight:700;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.caption("Healthy BMI range: 18.5 kg/m² – 25 kg/m².")
        st.markdown('</div>', unsafe_allow_html=True)

    def display_calories(self, person):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔥 Calories Calculator</div>', unsafe_allow_html=True)
        maintain_calories = person.calories_calculator()
        st.caption('Daily calorie estimates for maintaining, losing, or gaining weight at different rates.')
        for plan, weight, loss, col in zip(self.plans, self.weights, self.losses, st.columns(4)):
            with col:
                st.metric(label=plan, value=f'{round(maintain_calories * weight)} Calories/day',
                          delta=loss, delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)

    def display_medical_conditions(self, person):
        if not person.medical_conditions:
            return
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🩺 Medical Considerations</div>', unsafe_allow_html=True)
        st.caption("These targets are general-wellness adjustments, not medical advice. Please consult your doctor or dietitian for personalized guidance.")
        for condition in person.medical_conditions:
            tip = MEDICAL_CONDITION_TIPS.get(condition, '')
            st.markdown(f"**{condition}** — {tip}")
        st.markdown('</div>', unsafe_allow_html=True)

    def display_exclusion_feedback(self, person):
        if not person.exclude_match_counts:
            return
        active = {kw: n for kw, n in person.exclude_match_counts.items() if n > 0}
        zero_hit_custom = [w for w in person.custom_avoid_words if person.exclude_match_counts.get(w, 0) == 0]
        if not active and not zero_hit_custom:
            return
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧾 Filtering Summary</div>', unsafe_allow_html=True)
        if active:
            summary = ", ".join(f"**{kw}** ({n})" for kw, n in sorted(active.items(), key=lambda x: -x[1]))
            st.caption(f"Recipes excluded by keyword: {summary}")
        if zero_hit_custom:
            words = ", ".join(f"'{w}'" for w in zero_hit_custom)
            st.info(f"Heads up: {words} didn't match any recipe — double check the spelling, or it just isn't in this dataset.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- 🆕 "why" badges for a meal, based on active medical conditions ----------
    def _why_badges_for_meal(self, person):
        if not person.nutrient_why_tags:
            return ""
        pieces = []
        for nutrient, tags in person.nutrient_why_tags.items():
            for condition, factor in tags:
                direction = "↑" if factor > 1 else "↓"
                pct = abs(round((factor - 1) * 100))
                nice_nutrient = nutrient.replace('Content', '')
                pieces.append(f'<span class="badge badge-why">{nice_nutrient} {direction}{pct}% — {condition}</span>')
        # de-dupe, cap so it doesn't overwhelm the card
        seen = set()
        unique_pieces = []
        for p in pieces:
            if p not in seen:
                seen.add(p)
                unique_pieces.append(p)
        return "".join(unique_pieces[:3])

    # ---------- 🆕 card-based recipe display with badges + action buttons ----------
    def display_recommendation(self, person, recommendations):
        st.markdown('<div class="section-title">🍽️ Diet Recommendator</div>', unsafe_allow_html=True)
        filter_bits = []
        if getattr(person, 'diet_preference', 'No Preference (Show All)') != 'No Preference (Show All)':
            filter_bits.append(person.diet_preference)
        if getattr(person, 'cuisine_preference', 'No Preference (All Cuisines)') != 'No Preference (All Cuisines)':
            filter_bits.append(person.cuisine_preference)
        if filter_bits:
            st.caption(f"Filtered for: **{' · '.join(filter_bits)}**")

        why_badges_html = self._why_badges_for_meal(person)
        if why_badges_html:
            st.markdown(f"Adjusted for your medical conditions: {why_badges_html}", unsafe_allow_html=True)

        meals = list(person.meals_calories_perc.keys())
        for meal_index, (meal_name, column) in enumerate(zip(meals, st.columns(len(meals)))):
            with column:
                st.markdown(f'##### {meal_name.upper()}')
                recommendation = recommendations[meal_index]

                if st.button("🔄 Swap this meal", key=f"swap_{meal_name}", use_container_width=True):
                    with st.spinner(f"Finding a different {meal_name}..."):
                        person.swap_meal(meal_name, meal_index)
                    st.rerun()

                for recipe in recommendation:
                    recipe_name = recipe['Name']
                    calories = round(recipe.get('Calories', 0))
                    protein = round(recipe.get('ProteinContent', 0))
                    total_time = recipe.get('TotalTime', '—')

                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    if recipe.get('image_link'):
                        st.markdown(
                            f'<div><center><img src="{recipe["image_link"]}" alt="{recipe_name}" '
                            f'style="max-height:140px;object-fit:cover;"></center></div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown(f"**{recipe_name}**")
                    st.markdown(
                        f'<span class="badge badge-cal">🔥 {calories} kcal</span>'
                        f'<span class="badge badge-protein">💪 {protein}g protein</span>'
                        f'<span class="badge badge-time">⏱️ {total_time} min</span>',
                        unsafe_allow_html=True,
                    )

                    action_cols = st.columns(2)
                    fav_key = f"fav_{meal_name}_{recipe_name}"
                    log_key = f"log_{meal_name}_{recipe_name}"
                    with action_cols[0]:
                        if st.button("❤️ Save", key=fav_key, use_container_width=True):
                            if recipe_name not in [f['Name'] for f in st.session_state.favorites]:
                                st.session_state.favorites.append(recipe)
                                st.toast(f"Saved '{recipe_name}' to favorites!")
                    with action_cols[1]:
                        if st.button("📝 Log", key=log_key, use_container_width=True):
                            st.session_state.nutrition_log.append({
                                'date': datetime.date.today().isoformat(),
                                'meal': meal_name,
                                'name': recipe_name,
                                **{v: recipe.get(v, 0) for v in nutritions_values},
                            })
                            st.toast(f"Logged '{recipe_name}' to your Nutrition Tracker!")

                    with st.expander("Details"):
                        nutritions_df = pd.DataFrame({value: [recipe.get(value, 0)] for value in nutritions_values})
                        st.markdown('<h6 style="text-align:center;">Nutritional Values (g):</h6>', unsafe_allow_html=True)
                        st.dataframe(nutritions_df, use_container_width=True)
                        st.markdown('<h6 style="text-align:center;">Ingredients:</h6>', unsafe_allow_html=True)
                        for ingredient in recipe.get('RecipeIngredientParts', []):
                            st.markdown(f"- {ingredient}")
                        st.markdown('<h6 style="text-align:center;">Recipe Instructions:</h6>', unsafe_allow_html=True)
                        for instruction in recipe.get('RecipeInstructions', []):
                            st.markdown(f"- {instruction}")
                        st.markdown(f"""
                            - Cook Time: {recipe.get('CookTime', '—')} min
                            - Prep Time: {recipe.get('PrepTime', '—')} min
                            - Total Time: {recipe.get('TotalTime', '—')} min
                        """)
                    st.markdown('</div>', unsafe_allow_html=True)

    def display_meal_choices(self, person, recommendations):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Choose Your Meal Composition</div>', unsafe_allow_html=True)

        meal_names = list(person.meals_calories_perc.keys())
        columns = st.columns(len(meal_names))
        choices = []
        for meal_name, column, recommendation in zip(meal_names, columns, recommendations):
            with column:
                if recommendation:
                    choice = st.selectbox(f'Choose your {meal_name}:', [recipe['Name'] for recipe in recommendation],
                                           key=f"choice_{meal_name}")
                else:
                    choice = None
                choices.append(choice)

        total_nutrition_values = {nutrition_value: 0 for nutrition_value in nutritions_values}
        for choice, meals_ in zip(choices, recommendations):
            for meal in meals_:
                if meal['Name'] == choice:
                    for nutrition_value in nutritions_values:
                        total_nutrition_values[nutrition_value] += meal[nutrition_value]

        total_calories_chose = total_nutrition_values['Calories']
        loss_calories_chose = round(person.calories_calculator() * person.weight_loss)

        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Total Calories in Recipes vs {st.session_state.weight_loss_option} Calories:</h5>', unsafe_allow_html=True)
        total_calories_graph_options = {
            "xAxis": {
                "type": "category",
                "data": ['Total Calories you chose', f"{st.session_state.weight_loss_option} Calories"],
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": [
                        {"value": total_calories_chose, "itemStyle": {"color": ["#33FF8D", "#FF3333"][total_calories_chose > loss_calories_chose]}},
                        {"value": loss_calories_chose, "itemStyle": {"color": "#3339FF"}},
                    ],
                    "type": "bar",
                }
            ],
        }
        st_echarts(options=total_calories_graph_options, height="400px")

        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>', unsafe_allow_html=True)
        nutritions_graph_options = {
            "tooltip": {"trigger": "item"},
            "legend": {"top": "5%", "left": "center"},
            "series": [
                {
                    "name": "Nutritional Values",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {"borderRadius": 10, "borderColor": "#fff", "borderWidth": 2},
                    "label": {"show": False, "position": "center"},
                    "emphasis": {"label": {"show": True, "fontSize": "40", "fontWeight": "bold"}},
                    "labelLine": {"show": False},
                    "data": [{"value": round(total_nutrition_values[v]), "name": v} for v in total_nutrition_values],
                }
            ],
        }
        st_echarts(options=nutritions_graph_options, height="500px")
        st.markdown('</div>', unsafe_allow_html=True)

    def display_favorites(self):
        if not st.session_state.favorites:
            return
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">❤️ Saved Favorites</div>', unsafe_allow_html=True)
        cols = st.columns(min(4, len(st.session_state.favorites)))
        for i, recipe in enumerate(st.session_state.favorites):
            with cols[i % len(cols)]:
                st.markdown(f"**{recipe['Name']}**")
                st.caption(f"🔥 {round(recipe.get('Calories', 0))} kcal · 💪 {round(recipe.get('ProteinContent', 0))}g protein")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# EXERCISE PLAN DATA & HELPERS
# ============================================================
EXERCISES = [
    {'name': 'Jumping Jacks', 'desc': 'Jump feet out while raising arms overhead, then jump back to start.',       'split': 'Full Body', 'equipment': 'Bodyweight', 'level': 1, 'met': 8.0, 'avoid_if': ['Knee']},
    {'name': 'Bodyweight Squats', 'desc': 'Feet shoulder-width apart, sit hips back and down, then stand.',   'split': 'Legs',       'equipment': 'Bodyweight', 'level': 1, 'met': 5.0, 'avoid_if': ['Knee']},
    {'name': 'Walking Lunges', 'desc': 'Step forward, lower back knee toward the floor, push through the front foot.',      'split': 'Legs',       'equipment': 'Bodyweight', 'level': 2, 'met': 6.0, 'avoid_if': ['Knee']},
    {'name': 'Glute Bridges', 'desc': 'Lie on your back, knees bent, lift hips up by squeezing your glutes.',       'split': 'Legs',       'equipment': 'Bodyweight', 'level': 1, 'met': 4.0, 'avoid_if': ['Lower Back']},
    {'name': 'Wall Sit', 'desc': 'Back against a wall, slide down until knees are at 90°, hold.',            'split': 'Legs',       'equipment': 'Bodyweight', 'level': 1, 'met': 4.0, 'avoid_if': ['Knee']},
    {'name': 'Calf Raises', 'desc': 'Stand tall, rise up onto the balls of your feet, lower slowly.',         'split': 'Legs',       'equipment': 'Bodyweight', 'level': 1, 'met': 3.5, 'avoid_if': []},
    {'name': 'Push-Ups', 'desc': 'Hands under shoulders, lower chest to the floor, push back up.',            'split': 'Push',       'equipment': 'Bodyweight', 'level': 1, 'met': 8.0, 'avoid_if': ['Wrist', 'Shoulder']},
    {'name': 'Incline Push-Ups', 'desc': 'Hands on a raised surface (bench/counter), lower and push up.',    'split': 'Push',       'equipment': 'Bodyweight', 'level': 1, 'met': 6.0, 'avoid_if': ['Wrist']},
    {'name': 'Tricep Dips (Chair)', 'desc': 'Hands on a chair edge behind you, bend elbows to lower, push up.', 'split': 'Push',       'equipment': 'Bodyweight', 'level': 2, 'met': 6.0, 'avoid_if': ['Shoulder', 'Wrist']},
    {'name': 'Pike Push-Ups', 'desc': 'Hips high in an inverted-V, bend elbows to lower head toward the floor.',       'split': 'Push',       'equipment': 'Bodyweight', 'level': 3, 'met': 7.0, 'avoid_if': ['Shoulder', 'Wrist']},
    {'name': 'Superman Hold', 'desc': 'Lie face-down, lift arms and legs off the floor together, hold.',       'split': 'Pull',       'equipment': 'Bodyweight', 'level': 1, 'met': 3.5, 'avoid_if': ['Lower Back']},
    {'name': 'Plank', 'desc': 'Forearms and toes on the floor, body in a straight line, brace your core.',               'split': 'Core',       'equipment': 'Bodyweight', 'level': 1, 'met': 4.0, 'avoid_if': ['Wrist', 'Lower Back']},
    {'name': 'Side Plank', 'desc': 'Balance on one forearm and the side of one foot, hips lifted, hold.',          'split': 'Core',       'equipment': 'Bodyweight', 'level': 2, 'met': 4.0, 'avoid_if': ['Wrist', 'Shoulder']},
    {'name': 'Bicycle Crunches', 'desc': 'Lying on your back, alternate touching elbow to opposite knee.',    'split': 'Core',       'equipment': 'Bodyweight', 'level': 2, 'met': 5.5, 'avoid_if': ['Lower Back']},
    {'name': 'Dead Bug', 'desc': 'Lying on your back, extend opposite arm and leg while keeping your low back flat.',            'split': 'Core',       'equipment': 'Bodyweight', 'level': 1, 'met': 3.5, 'avoid_if': []},
    {'name': 'Mountain Climbers', 'desc': 'In a plank, drive knees toward your chest one at a time, quickly.',   'split': 'Full Body',  'equipment': 'Bodyweight', 'level': 2, 'met': 8.0, 'avoid_if': ['Wrist', 'Shoulder']},
    {'name': 'Burpees', 'desc': 'Squat, kick back to a plank, push-up, jump feet in, then jump up.',             'split': 'Full Body',  'equipment': 'Bodyweight', 'level': 3, 'met': 10.0, 'avoid_if': ['Knee', 'Wrist', 'Shoulder']},
    {'name': 'Brisk Walk', 'desc': 'Walk at a pace that raises your heart rate but lets you still talk.',          'split': 'Cardio',     'equipment': 'Bodyweight', 'level': 1, 'met': 4.5, 'avoid_if': []},
    {'name': 'Jogging', 'desc': 'Steady, sustained running pace you can hold for the full duration.',             'split': 'Cardio',     'equipment': 'Bodyweight', 'level': 2, 'met': 7.5, 'avoid_if': ['Knee']},
    {'name': 'High Knees', 'desc': 'Jog in place driving your knees up toward waist height, quickly.',          'split': 'Cardio',     'equipment': 'Bodyweight', 'level': 2, 'met': 8.0, 'avoid_if': ['Knee']},
    {'name': 'Dumbbell Goblet Squat', 'desc': 'Hold a dumbbell at chest height, squat down keeping chest up.',  'split': 'Legs', 'equipment': 'Dumbbells', 'level': 1, 'met': 6.0, 'avoid_if': ['Knee']},
    {'name': 'Dumbbell Romanian Deadlift', 'desc': 'Hinge at the hips, lower dumbbells along your legs, keep back flat.', 'split': 'Legs', 'equipment': 'Dumbbells', 'level': 2, 'met': 6.0, 'avoid_if': ['Lower Back']},
    {'name': 'Dumbbell Lunges', 'desc': 'Holding dumbbells at your sides, step forward into a lunge, alternate legs.',        'split': 'Legs', 'equipment': 'Dumbbells', 'level': 2, 'met': 6.5, 'avoid_if': ['Knee']},
    {'name': 'Dumbbell Bench Press', 'desc': 'Lying on a bench, press dumbbells up from chest level.',   'split': 'Push', 'equipment': 'Dumbbells', 'level': 2, 'met': 6.0, 'avoid_if': ['Shoulder', 'Wrist']},
    {'name': 'Dumbbell Shoulder Press', 'desc': 'Press dumbbells overhead from shoulder height, control the descent.','split': 'Push', 'equipment': 'Dumbbells', 'level': 2, 'met': 6.0, 'avoid_if': ['Shoulder', 'Wrist']},
    {'name': 'Dumbbell Lateral Raise', 'desc': 'Raise dumbbells out to the sides until arms are level with shoulders.', 'split': 'Push', 'equipment': 'Dumbbells', 'level': 2, 'met': 4.0, 'avoid_if': ['Shoulder']},
    {'name': 'Dumbbell Bent-Over Row', 'desc': 'Hinge forward, pull dumbbells toward your ribs, squeeze shoulder blades.', 'split': 'Pull', 'equipment': 'Dumbbells', 'level': 2, 'met': 6.0, 'avoid_if': ['Lower Back', 'Shoulder']},
    {'name': 'Dumbbell Bicep Curl', 'desc': 'Curl dumbbells up toward shoulders, keeping elbows close to your body.',    'split': 'Pull', 'equipment': 'Dumbbells', 'level': 1, 'met': 4.0, 'avoid_if': ['Wrist']},
    {'name': 'Dumbbell Farmer Carry', 'desc': 'Hold a dumbbell in each hand, walk with tall posture and braced core.',  'split': 'Full Body', 'equipment': 'Dumbbells', 'level': 1, 'met': 5.0, 'avoid_if': ['Wrist', 'Lower Back']},
    {'name': 'Band Squats', 'desc': 'Stand on the band, handles at shoulders, squat down and stand back up.',          'split': 'Legs', 'equipment': 'Resistance Bands', 'level': 1, 'met': 4.5, 'avoid_if': ['Knee']},
    {'name': 'Band Lateral Walk', 'desc': 'Band around your legs, step sideways keeping tension on the band.',    'split': 'Legs', 'equipment': 'Resistance Bands', 'level': 1, 'met': 4.0, 'avoid_if': ['Knee']},
    {'name': 'Band Chest Press', 'desc': 'Anchor the band behind you, press handles forward at chest height.',     'split': 'Push', 'equipment': 'Resistance Bands', 'level': 1, 'met': 4.0, 'avoid_if': ['Shoulder']},
    {'name': 'Band Row', 'desc': 'Anchor the band in front, pull handles toward your ribs, squeeze back.',             'split': 'Pull', 'equipment': 'Resistance Bands', 'level': 1, 'met': 4.0, 'avoid_if': ['Lower Back']},
    {'name': 'Band Pull-Apart', 'desc': 'Hold band at shoulder height, pull it apart by squeezing shoulder blades.',      'split': 'Pull', 'equipment': 'Resistance Bands', 'level': 1, 'met': 3.0, 'avoid_if': ['Shoulder']},
    {'name': 'Band Bicep Curl', 'desc': 'Stand on the band, curl handles up toward shoulders.',      'split': 'Pull', 'equipment': 'Resistance Bands', 'level': 1, 'met': 3.5, 'avoid_if': ['Wrist']},
    {'name': 'Barbell Back Squat', 'desc': 'Bar across your upper back, squat down keeping chest up, drive back up.',   'split': 'Legs', 'equipment': 'Barbell', 'level': 3, 'met': 6.0, 'avoid_if': ['Knee', 'Lower Back']},
    {'name': 'Barbell Deadlift', 'desc': 'Hinge down, grip the bar, stand up by driving through your heels.',     'split': 'Pull', 'equipment': 'Barbell', 'level': 3, 'met': 6.0, 'avoid_if': ['Lower Back']},
    {'name': 'Barbell Bench Press', 'desc': 'Lying on a bench, lower the bar to chest, press back up.',  'split': 'Push', 'equipment': 'Barbell', 'level': 3, 'met': 6.0, 'avoid_if': ['Shoulder', 'Wrist']},
    {'name': 'Barbell Overhead Press', 'desc': 'Press the bar from shoulder height straight overhead.', 'split': 'Push', 'equipment': 'Barbell', 'level': 3, 'met': 6.0, 'avoid_if': ['Shoulder']},
    {'name': 'Barbell Row', 'desc': 'Hinge forward, pull the bar toward your torso, squeeze shoulder blades.',          'split': 'Pull', 'equipment': 'Barbell', 'level': 3, 'met': 6.0, 'avoid_if': ['Lower Back']},
    {'name': 'Leg Press Machine', 'desc': 'Seated, push the platform away by extending your legs, control the return.',    'split': 'Legs', 'equipment': 'Gym Machines', 'level': 2, 'met': 5.0, 'avoid_if': ['Knee']},
    {'name': 'Leg Curl Machine', 'desc': 'Lying or seated, curl the pad toward your glutes against resistance.',     'split': 'Legs', 'equipment': 'Gym Machines', 'level': 1, 'met': 4.0, 'avoid_if': ['Knee']},
    {'name': 'Lat Pulldown Machine', 'desc': 'Pull the bar down to chest height, squeeze shoulder blades together.', 'split': 'Pull', 'equipment': 'Gym Machines', 'level': 1, 'met': 5.0, 'avoid_if': ['Shoulder']},
    {'name': 'Seated Cable Row', 'desc': 'Pull the handle toward your torso, keep your back straight, squeeze back.',     'split': 'Pull', 'equipment': 'Gym Machines', 'level': 1, 'met': 5.0, 'avoid_if': ['Lower Back']},
    {'name': 'Chest Press Machine', 'desc': 'Push the handles forward from chest height until arms extend.',  'split': 'Push', 'equipment': 'Gym Machines', 'level': 1, 'met': 5.0, 'avoid_if': ['Shoulder']},
    {'name': 'Shoulder Press Machine', 'desc': 'Press the handles up overhead from shoulder height.', 'split': 'Push', 'equipment': 'Gym Machines', 'level': 2, 'met': 5.0, 'avoid_if': ['Shoulder']},
    {'name': 'Cable Crunch', 'desc': 'Kneel facing the cable, crunch down by curling your torso toward your hips.',         'split': 'Core', 'equipment': 'Gym Machines', 'level': 2, 'met': 4.0, 'avoid_if': ['Lower Back']},
    {'name': 'Treadmill (Steady Pace)', 'desc': 'Walk or jog at a steady, moderate pace for the full duration.', 'split': 'Cardio', 'equipment': 'Cardio Machines', 'level': 1, 'met': 7.0, 'avoid_if': ['Knee']},
    {'name': 'Stationary Bike', 'desc': 'Pedal at a steady resistance and cadence for the full duration.',      'split': 'Cardio', 'equipment': 'Cardio Machines', 'level': 1, 'met': 6.0, 'avoid_if': []},
    {'name': 'Elliptical Trainer', 'desc': 'Maintain a smooth, steady stride at moderate resistance.',   'split': 'Cardio', 'equipment': 'Cardio Machines', 'level': 1, 'met': 6.0, 'avoid_if': []},
    {'name': 'Rowing Machine', 'desc': 'Drive with your legs, lean back slightly, pull the handle to your ribs.',       'split': 'Cardio', 'equipment': 'Cardio Machines', 'level': 2, 'met': 7.0, 'avoid_if': ['Lower Back', 'Shoulder']},
]

EQUIPMENT_OPTIONS = ['Bodyweight', 'Dumbbells', 'Resistance Bands', 'Barbell', 'Gym Machines', 'Cardio Machines']
LIMITATION_OPTIONS = ['Knee', 'Lower Back', 'Shoulder', 'Wrist']
LEVEL_MAP = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}

SPLIT_TEMPLATES = {
    2: ['Full Body', 'Full Body'],
    3: ['Full Body', 'Full Body', 'Full Body'],
    4: ['Push', 'Pull', 'Legs', 'Full Body'],
    5: ['Push', 'Pull', 'Legs', 'Cardio', 'Full Body'],
    6: ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Legs'],
}

SPLIT_SOURCE_GROUPS = {
    'Full Body': ['Push', 'Pull', 'Legs', 'Core', 'Full Body'],
    'Cardio': ['Cardio'],
    'Push': ['Push'],
    'Pull': ['Pull'],
    'Legs': ['Legs'],
    'Core': ['Core'],
}

EXERCISES_PER_DAY = {'Beginner': 4, 'Intermediate': 5, 'Advanced': 6}
SETS_REPS_BY_LEVEL = {
    'Beginner': '2 sets x 10-12 reps',
    'Intermediate': '3 sets x 10-12 reps',
    'Advanced': '4 sets x 8-12 reps',
}
CARDIO_DURATION_MIN = {'Beginner': 15, 'Intermediate': 20, 'Advanced': 25}

WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def build_weekly_plan(fitness_level, equipment_available, days_per_week, limitations, weight_kg):
    level_num = LEVEL_MAP[fitness_level]
    pool = [
        ex for ex in EXERCISES
        if ex['equipment'] in equipment_available
        and ex['level'] <= level_num
        and not any(lim in ex['avoid_if'] for lim in limitations)
    ]

    template = SPLIT_TEMPLATES[days_per_week]
    plan = []
    exercises_per_day = EXERCISES_PER_DAY[fitness_level]

    for day_index, split_name in enumerate(template, start=1):
        source_groups = SPLIT_SOURCE_GROUPS[split_name]
        day_candidates = [ex for ex in pool if ex['split'] in source_groups]

        if split_name == 'Cardio':
            chosen = day_candidates[:2] if day_candidates else []
            duration_min = CARDIO_DURATION_MIN[fitness_level]
            day_calories = sum(ex['met'] * weight_kg * (duration_min / 60) for ex in chosen) if chosen else 0
            entries = [
                {'name': ex['name'], 'desc': ex.get('desc', ''), 'detail': f'{duration_min} min, moderate effort',
                 'calories': round(ex['met'] * weight_kg * (duration_min / 60))}
                for ex in chosen
            ]
        else:
            grouped = {g: [ex for ex in day_candidates if ex['split'] == g] for g in source_groups}
            chosen = []
            i = 0
            while len(chosen) < exercises_per_day and any(grouped.values()):
                group = source_groups[i % len(source_groups)]
                if grouped.get(group):
                    chosen.append(grouped[group].pop(0))
                i += 1
                if i > exercises_per_day * len(source_groups):
                    break
            set_reps = SETS_REPS_BY_LEVEL[fitness_level]
            est_minutes_per_exercise = 6
            entries = [
                {'name': ex['name'], 'desc': ex.get('desc', ''), 'detail': set_reps,
                 'calories': round(ex['met'] * weight_kg * (est_minutes_per_exercise / 60))}
                for ex in chosen
            ]
            day_calories = sum(e['calories'] for e in entries)

        plan.append({
            'day': f'Day {day_index}',
            'split': split_name,
            'exercises': entries,
            'total_calories': round(day_calories),
        })

    return plan


def build_calendar_slots(plan, days_per_week):
    """🆕 Spreads training days evenly across a 7-day week, filling the
    rest with 'Rest' slots, so the plan can render as a real calendar."""
    total_slots = 7
    slots = [None] * total_slots
    for i, day in enumerate(plan):
        pos = min(int(i * total_slots / max(days_per_week, 1)), total_slots - 1)
        slots[pos] = day
    return slots


def build_ics_calendar(plan, days_per_week):
    """🆕 Builds a minimal .ics file scheduling each training day for the
    next 7 days, so users can drop their workout days into their own
    calendar app."""
    slots = build_calendar_slots(plan, days_per_week)
    today = datetime.date.today()
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Diet Recommendation App//EN"]
    for offset, slot in enumerate(slots):
        if slot is None:
            continue
        event_date = today + datetime.timedelta(days=offset)
        date_str = event_date.strftime("%Y%m%d")
        summary = f"Workout: {slot['split']} Day ({slot['day']})"
        description = ", ".join(e['name'] for e in slot['exercises']) or "Rest / light activity"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{date_str}-{slot['day'].replace(' ', '')}@diet-recommendation-app",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"DTEND;VALUE=DATE:{date_str}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\n".join(lines)


def build_plan_summary_markdown(person, recommendations, exercise_plan, meta):
    lines = ["# Your Diet & Exercise Plan", ""]
    bmi_string, category, _ = person.display_result()
    lines.append(f"**BMI:** {bmi_string} ({category})")
    lines.append(f"**Daily Calorie Target:** {round(person.calories_calculator() * person.weight_loss)} kcal")
    lines.append("")
    lines.append("## Meals")
    for meal_name, recipes in zip(person.meals_calories_perc.keys(), recommendations):
        lines.append(f"### {meal_name.title()}")
        for recipe in recipes[:3]:
            lines.append(f"- **{recipe['Name']}** — {round(recipe.get('Calories', 0))} kcal, "
                         f"{round(recipe.get('ProteinContent', 0))}g protein")
        lines.append("")
    if exercise_plan:
        lines.append("## Weekly Workout Plan")
        lines.append(f"Level: {meta['fitness_level']} · {meta['days_per_week']} day(s)/week")
        for day in exercise_plan:
            lines.append(f"### {day['day']} — {day['split']} (~{day['total_calories']} kcal)")
            for ex in day['exercises']:
                lines.append(f"- {ex['name']}: {ex['detail']}")
            lines.append("")
    return "\n".join(lines)


def display_exercise_calendar(plan, meta):
    st.markdown('<div class="section-title">🗓️ Your Weekly Workout Calendar</div>', unsafe_allow_html=True)
    slots = build_calendar_slots(plan, meta['days_per_week'])
    cols = st.columns(7)
    for i, (col, label, slot) in enumerate(zip(cols, WEEKDAY_LABELS, slots)):
        with col:
            if slot is None:
                st.markdown(f"""
                <div class="day-card rest">
                    <h6>{label}</h6>
                    <span class="badge badge-rest">Rest</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="day-card">
                    <h6>{label}</h6>
                    <span class="split-tag">{slot['split']}</span>
                </div>
                """, unsafe_allow_html=True)
                for ex in slot['exercises']:
                    done_key = f"exdone_{i}_{ex['name']}"
                    st.checkbox(ex['name'], key=done_key, help=f"{ex['detail']} · ~{ex['calories']} kcal")

    done_count = sum(1 for k, v in st.session_state.items() if k.startswith("exdone_") and v)
    total_count = sum(len(s['exercises']) for s in slots if s is not None)
    if total_count:
        st.progress(done_count / total_count, text=f"{done_count}/{total_count} exercises marked done this week")


# ============================================================
# PAGE LAYOUT
# ============================================================
display = Display()
display.display_page_header()

# ---------- 🆕 Load my last profile ----------
if st.session_state.last_profile:
    if st.button("💾 Load my last profile", help="Prefill the form below with what you submitted last time."):
        st.session_state.update({f"prefill_{k}": v for k, v in st.session_state.last_profile.items()})
        st.toast("Loaded your last profile into the form below.")

lp = st.session_state.last_profile  # shorthand for prefill defaults


def _default(key, fallback):
    return lp.get(key, fallback)


with st.form("recommendation_form"):
    st.write("Fill out each section below, then click **Generate** to get your meal plan and workout plan together.")

    with st.expander("👤 Personal Details", expanded=True):
        age = st.number_input('Age', min_value=2, max_value=120, step=1, value=_default('age', 25))
        height = st.number_input('Height(cm)', min_value=50, max_value=300, step=1, value=_default('height', 170))
        weight = st.number_input('Weight(kg)', min_value=10, max_value=300, step=1, value=_default('weight', 70))
        gender = st.radio('Gender', ('Male', 'Female'), index=('Male', 'Female').index(_default('gender', 'Male')))
        activity_options = [
            'Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)',
            'Very active (6-7 days/wk)', 'Extra active (very active & physical job)'
        ]
        activity = st.select_slider('Activity', options=activity_options,
                                     value=_default('activity', activity_options[0]))

    with st.expander("🥗 Diet Preferences", expanded=True):
        diet_preference = st.selectbox('Dietary Preference', DIET_PREFERENCE_OPTIONS,
                                        index=DIET_PREFERENCE_OPTIONS.index(_default('diet_preference', DIET_PREFERENCE_OPTIONS[0])))
        cuisine_preference = st.selectbox(
            'Cuisine', CUISINE_OPTIONS,
            index=CUISINE_OPTIONS.index(_default('cuisine_preference', CUISINE_OPTIONS[0])),
            help="South Indian matches recipes whose name/ingredients include dishes like dosa, idli, sambar, rasam, "
                 "or staples like curry leaves, coconut, and tamarind. It's a best-effort keyword match, not a "
                 "verified cuisine tag, so results may occasionally fall back to the closest available recipe."
        )
        option = st.selectbox('Choose your weight loss plan:', display.plans,
                               index=display.plans.index(_default('weight_loss_option', display.plans[0])))
        st.session_state.weight_loss_option = option
        weight_loss = display.weights[display.plans.index(option)]
        number_of_meals = st.slider('Meals per day', min_value=3, max_value=5, step=1,
                                     value=_default('number_of_meals', 3))
        if number_of_meals == 3:
            meals_calories_perc = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.25}
        elif number_of_meals == 4:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40, 'dinner': 0.25}
        else:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40,
                                    'afternoon snack': 0.05, 'dinner': 0.20}

    with st.expander("🩺 Medical Conditions & Allergies (optional)"):
        st.caption("Selecting conditions fine-tunes calorie/macro targets for both your meals and your workouts. Not medical advice; please consult your doctor.")
        medical_conditions = []
        for category_name, conditions in MEDICAL_CONDITIONS_BY_CATEGORY.items():
            with st.expander(f"{category_name}"):
                selected = st.multiselect(
                    category_name,
                    list(conditions.keys()),
                    default=[c for c in _default('medical_conditions', []) if c in conditions],
                    label_visibility="collapsed",
                    key=f"medcond_{category_name}"
                )
                medical_conditions.extend(selected)

        st.markdown("---")
        allergies = st.multiselect('Allergies', ALLERGEN_OPTIONS, default=_default('allergies', []))
        avoid_ingredients_text = st.text_input(
            'Other ingredients to avoid',
            value=_default('avoid_ingredients_text', ''),
            placeholder="e.g. mushroom, cilantro and olives; peanuts",
            help="Separate with commas, semicolons, '&', or the word 'and'. Plurals are handled automatically (e.g. 'tomato' also catches 'tomatoes')."
        )
        shuffle_variety = st.checkbox(
            'Shuffle for a different set of recipes each time',
            value=_default('shuffle_variety', False),
            help="Off (default): same inputs always give the same recommendations. On: get a fresh, varied set every time you click Generate."
        )

    with st.expander("🏋️ Exercise Preferences", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            fitness_level = st.select_slider('Fitness Level', options=['Beginner', 'Intermediate', 'Advanced'],
                                              value=_default('fitness_level', 'Beginner'))
            days_per_week = st.slider('Workout Days per Week', min_value=2, max_value=6,
                                       value=_default('days_per_week', 3), step=1)
        with col2:
            equipment_available = st.multiselect('Available Equipment', EQUIPMENT_OPTIONS,
                                                  default=_default('equipment_available', ['Bodyweight']))
            limitations = st.multiselect(
                'Injuries / Limitations (optional)',
                LIMITATION_OPTIONS,
                default=_default('limitations', []),
                help="Exercises that stress these areas will be excluded from your plan."
            )

    generated = st.form_submit_button("✨ Generate My Plan", use_container_width=True, type="primary")

if generated:
    if not equipment_available:
        st.warning("Select at least one type of equipment for your workout plan (Bodyweight works with none at all). Meal plan will still generate below.")

    # 🆕 remember this submission for "Load my last profile"
    st.session_state.last_profile = {
        'age': age, 'height': height, 'weight': weight, 'gender': gender, 'activity': activity,
        'diet_preference': diet_preference, 'cuisine_preference': cuisine_preference,
        'weight_loss_option': option, 'number_of_meals': number_of_meals,
        'medical_conditions': medical_conditions, 'allergies': allergies,
        'avoid_ingredients_text': avoid_ingredients_text, 'shuffle_variety': shuffle_variety,
        'fitness_level': fitness_level, 'days_per_week': days_per_week,
        'equipment_available': equipment_available, 'limitations': limitations,
    }

    st.session_state.generated = True
    person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss,
                     medical_conditions=medical_conditions, diet_preference=diet_preference,
                     allergies=allergies, avoid_ingredients_text=avoid_ingredients_text,
                     shuffle_variety=shuffle_variety, cuisine_preference=cuisine_preference)

    # 🆕 staged status feedback instead of one generic spinner
    with st.status("Analyzing your profile...", expanded=True) as status:
        status.update(label="Analyzing your profile...")
        recommendations = person.generate_recommendations(status=status)
        st.session_state.recommendations = recommendations
        st.session_state.person = person

        if equipment_available:
            status.update(label="Building your workout plan...")
            condition_notes = []
            if 'Heart Disease' in medical_conditions or 'Hypertension (High BP)' in medical_conditions:
                condition_notes.append("A heart condition or high blood pressure is on file — keep intensity moderate and avoid heavy straining (e.g. holding your breath during lifts). Check with your doctor before starting a new program.")
            if 'Pregnancy' in medical_conditions:
                condition_notes.append("Pregnancy is on file — avoid exercises lying flat on your back after the first trimester and any high fall-risk or abdominal-strain moves. Confirm this plan with your doctor.")
            if 'Osteoporosis' in medical_conditions:
                condition_notes.append("Osteoporosis is on file — avoid high-impact and spine-flexion movements (e.g. deep sit-ups); favor controlled, low-impact strength work.")
            if age >= 65:
                condition_notes.append("Balance and joint-friendly pacing is recommended given your age — warm up thoroughly and prioritize form over load.")

            st.session_state.exercise_plan = build_weekly_plan(fitness_level, equipment_available, days_per_week, limitations, weight)
            st.session_state.exercise_plan_meta = {
                'fitness_level': fitness_level, 'days_per_week': days_per_week,
                'limitations': limitations, 'notes': condition_notes,
            }
        else:
            st.session_state.exercise_plan = None

        status.update(label="Done! Your plan is ready.", state="complete")

if st.session_state.generated:
    person = st.session_state.person
    exercise_plan = st.session_state.get('exercise_plan')
    exercise_meta = st.session_state.get('exercise_plan_meta', {})

    display.display_scorecard(person, exercise_plan)

    with st.container():
        display.display_bmi(person)
    with st.container():
        display.display_calories(person)
    with st.container():
        display.display_medical_conditions(person)
    with st.container():
        display.display_exclusion_feedback(person)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.container():
        display.display_recommendation(person, st.session_state.recommendations)
        st.success('Meal Plan Generated Successfully!', icon="✅")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        display.display_meal_choices(person, st.session_state.recommendations)

    display.display_favorites()

    if exercise_plan:
        st.markdown("---")
        st.markdown("<h1 style='text-align: center;'>Exercises For You</h1>", unsafe_allow_html=True)
        st.caption("Rule-based exercise picks based on your details above. Not a substitute for advice from a doctor, physiotherapist, or certified trainer — especially with injuries or medical conditions.")

        if exercise_meta.get('notes'):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⚠️ Things to Keep in Mind</div>', unsafe_allow_html=True)
            for note in exercise_meta['notes']:
                st.warning(note)
            st.markdown('</div>', unsafe_allow_html=True)

        st.caption(f"{exercise_meta.get('fitness_level')} level · {exercise_meta.get('days_per_week')} day(s)/week" +
                   (f" · Avoiding: {', '.join(exercise_meta['limitations'])}" if exercise_meta.get('limitations') else ""))

        total_week_calories = sum(day['total_calories'] for day in exercise_plan)
        st.metric("Estimated Calories Burned This Week", f"{total_week_calories} kcal")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        display_exercise_calendar(exercise_plan, exercise_meta)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<h5 style="text-align: center;font-family:sans-serif;">Estimated Calories Burned Per Day:</h5>', unsafe_allow_html=True)
        weekly_chart_options = {
            "xAxis": {"type": "category", "data": [day['day'] for day in exercise_plan]},
            "yAxis": {"type": "value", "name": "kcal"},
            "series": [{
                "data": [day['total_calories'] for day in exercise_plan],
                "type": "bar",
                "itemStyle": {"color": "#6eb52f"},
            }],
        }
        st_echarts(options=weekly_chart_options, height="350px")

        # ---------- 🆕 export options ----------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⬇️ Export Your Plan</div>', unsafe_allow_html=True)
        export_cols = st.columns(2)
        with export_cols[0]:
            summary_md = build_plan_summary_markdown(person, st.session_state.recommendations, exercise_plan, exercise_meta)
            st.download_button("📄 Download Plan Summary (.md)", data=summary_md,
                                file_name="diet_and_exercise_plan.md", mime="text/markdown",
                                use_container_width=True)
        with export_cols[1]:
            ics_content = build_ics_calendar(exercise_plan, exercise_meta.get('days_per_week', 3))
            st.download_button("🗓️ Add Workout Days to Calendar (.ics)", data=ics_content,
                                file_name="workout_schedule.ics", mime="text/calendar",
                                use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif not equipment_available:
        st.info("No exercise plan generated — select at least one equipment option above and click Generate again.")