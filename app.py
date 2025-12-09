import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
import streamlit as st
import altair as alt


# =========================
# Nebula Paw Kitchen - Theme
# =========================

APP_TITLE = "Nebula Paw Kitchen™"
APP_SUBTITLE = "Premium Fresh Meal Intelligence for Dogs"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* --- Global background --- */
.stApp {
    background:
        radial-gradient(1200px 800px at 10% 10%, rgba(120, 140, 255, 0.16), transparent 60%),
        radial-gradient(1200px 800px at 90% 20%, rgba(255, 120, 220, 0.12), transparent 60%),
        radial-gradient(900px 700px at 20% 90%, rgba(120, 255, 200, 0.10), transparent 60%),
        linear-gradient(135deg, #070812 0%, #0a0c1a 40%, #0a0b14 100%);
    color: #F5F7FF;
}

/* --- Headers --- */
h1, h2, h3, h4 {
    letter-spacing: 0.4px;
}

/* --- Sidebar styling --- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* --- Cards --- */
.nebula-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px 18px 12px 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* --- Subtle glow separators --- */
.nebula-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    margin: 14px 0 18px 0;
}

/* --- Buttons --- */
.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    background: linear-gradient(135deg, rgba(120,140,255,0.20), rgba(255,120,220,0.18));
    color: white;
    font-weight: 600;
}
.stButton > button:hover {
    border: 1px solid rgba(255,255,255,0.25);
    transform: translateY(-1px);
}

/* --- Inputs --- */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.04) !important;
    border-radius: 10px;
}

/* --- Tables --- */
thead tr th {
    background-color: rgba(255,255,255,0.06) !important;
}

/* --- Small badge --- */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    margin-left: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================
# Data Models
# =========================

@dataclass(frozen=True)
class Ingredient:
    name: str
    category: str  # Meat, Veg, Carb, Oil, Treat
    kcal_per_100g: float
    protein_g: float
    fat_g: float
    carbs_g: float
    micronote: str
    benefits: List[str]
    cautions: List[str]


@dataclass(frozen=True)
class RatioPreset:
    key: str
    label: str
    meat_pct: int
    veg_pct: int
    carb_pct: int
    note: str


# =========================
# Ingredient Knowledge Base
# Approximate values for cooked food.
# =========================

def build_ingredients() -> Dict[str, Ingredient]:
    items = [
        # --- Meats ---
        Ingredient(
            name="Chicken (lean, cooked)",
            category="Meat",
            kcal_per_100g=165, protein_g=31, fat_g=3.6, carbs_g=0,
            micronote="B vitamins, selenium.",
            benefits=["High-quality protein for muscle maintenance",
                      "Generally well tolerated",
                      "Good base protein for rotation diets"],
            cautions=["Avoid if chicken allergy suspected",
                      "Remove skin to reduce fat if pancreatitis risk"]
        ),
        Ingredient(
            name="Turkey (lean, cooked)",
            category="Meat",
            kcal_per_100g=150, protein_g=29, fat_g=2.0, carbs_g=0,
            micronote="Niacin, selenium.",
            benefits=["Lean protein option",
                      "Useful for weight-aware plans",
                      "Mild flavor for picky dogs"],
            cautions=["Monitor sodium if using deli-style products (avoid those)"]
        ),
        Ingredient(
            name="Beef (lean, cooked)",
            category="Meat",
            kcal_per_100g=200, protein_g=26, fat_g=10, carbs_g=0,
            micronote="Iron, zinc, B12.",
            benefits=["Supports red blood cell health",
                      "Rich in iron and zinc",
                      "Great for active adult dogs"],
            cautions=["Higher fat than poultry depending on cut",
                      "Avoid if beef allergy suspected"]
        ),
        Ingredient(
            name="Lamb (lean, cooked)",
            category="Meat",
            kcal_per_100g=206, protein_g=25, fat_g=12, carbs_g=0,
            micronote="Zinc, carnitine.",
            benefits=["Alternative protein for rotation",
                      "Palatable for picky eaters",
                      "Useful if poultry sensitivity"],
            cautions=["Can be richer; adjust for pancreatitis risk"]
        ),
        Ingredient(
            name="Pork (lean, cooked)",
            category="Meat",
            kcal_per_100g=195, protein_g=27, fat_g=9, carbs_g=0,
            micronote="Thiamine.",
            benefits=["Thiamine-rich protein",
                      "Good rotation option",
                      "Often highly palatable"],
            cautions=["Use lean cuts; avoid processed pork"]
        ),
        Ingredient(
            name="Salmon (cooked)",
            category="Meat",
            kcal_per_100g=208, protein_g=20, fat_g=13, carbs_g=0,
            micronote="Omega-3, vitamin D.",
            benefits=["Supports skin/coat health",
                      "Anti-inflammatory fatty acids",
                      "Great for senior/joint-focused plans"],
            cautions=["Higher fat; portion carefully",
                      "Remove bones; cook thoroughly"]
        ),
        Ingredient(
            name="White Fish (cod, cooked)",
            category="Meat",
            kcal_per_100g=105, protein_g=23, fat_g=0.9, carbs_g=0,
            micronote="Iodine, selenium.",
            benefits=["Very lean protein",
                      "Good for sensitive stomach",
                      "Helpful for weight management"],
            cautions=["Ensure it is plain without seasoning"]
        ),

        # --- Veggies ---
        Ingredient(
            name="Pumpkin (cooked)",
            category="Veg",
            kcal_per_100g=26, protein_g=1, fat_g=0.1, carbs_g=6.5,
            micronote="Beta-carotene, soluble fiber.",
            benefits=["Supports stool quality",
                      "Gentle fiber for GI health",
                      "Helpful in transition periods"],
            cautions=["Too much can reduce calorie density"]
        ),
        Ingredient(
            name="Carrot (cooked)",
            category="Veg",
            kcal_per_100g=35, protein_g=0.8, fat_g=0.2, carbs_g=8,
            micronote="Beta-carotene.",
            benefits=["Antioxidant support",
                      "Crunchy option when lightly cooked",
                      "Low calorie nutrient boost"],
            cautions=["Chop/soften for small dogs"]
        ),
        Ingredient(
            name="Broccoli (cooked)",
            category="Veg",
            kcal_per_100g=34, protein_g=2.8, fat_g=0.4, carbs_g=7,
            micronote="Vitamin C, K, sulforaphane.",
            benefits=["Antioxidant-rich",
                      "Adds micronutrient diversity",
                      "Good rotation vegetable"],
            cautions=["Large amounts may cause gas"]
        ),
        Ingredient(
            name="Zucchini (cooked)",
            category="Veg",
            kcal_per_100g=17, protein_g=1.2, fat_g=0.3, carbs_g=3.1,
            micronote="Hydration-friendly veggie.",
            benefits=["Great for volumizing meals",
                      "Very low calorie",
                      "Mild taste for picky dogs"],
            cautions=["Avoid seasoning"]
        ),
        Ingredient(
            name="Spinach (cooked, small portions)",
            category="Veg",
            kcal_per_100g=23, protein_g=2.9, fat_g=0.4, carbs_g=3.6,
            micronote="Folate, magnesium.",
            benefits=["Adds micronutrient variety",
                      "Useful in rotation plans",
                      "Supports overall antioxidant intake"],
            cautions=["Use small portions due to oxalates"]
        ),
        Ingredient(
            name="Green Beans (cooked)",
            category="Veg",
            kcal_per_100g=31, protein_g=1.8, fat_g=0.1, carbs_g=7,
            micronote="Fiber and low-calorie bulk.",
            benefits=["Helpful for weight management",
                      "Gentle fiber",
                      "Good texture variety"],
            cautions=[]
        ),

        # --- Carbs ---
        Ingredient(
            name="Sweet Potato (cooked)",
            category="Carb",
            kcal_per_100g=86, protein_g=1.6, fat_g=0.1, carbs_g=20,
            micronote="Beta-carotene, potassium.",
            benefits=["Energy source with micronutrients",
                      "Often very palatable",
                      "Good for active dogs in controlled portions"],
            cautions=["Portion for weight control"]
        ),
        Ingredient(
            name="Brown Rice (cooked)",
            category="Carb",
            kcal_per_100g=123, protein_g=2.7, fat_g=1.0, carbs_g=25.6,
            micronote="B vitamins, gentle starch.",
            benefits=["Easy-to-digest base carb",
                      "Good for transition diets",
                      "Neutral flavor"],
            cautions=["Lower carb if diabetic/overweight plan"]
        ),
        Ingredient(
            name="Oats (cooked)",
            category="Carb",
            kcal_per_100g=71, protein_g=2.5, fat_g=1.4, carbs_g=12,
            micronote="Soluble fiber (beta-glucans).",
            benefits=["Supports satiety",
                      "Gentle energy source",
                      "Useful in cold-season calorie boosts"],
            cautions=["Introduce slowly for sensitive stomachs"]
        ),
        Ingredient(
            name="Quinoa (cooked)",
            category="Carb",
            kcal_per_100g=120, protein_g=4.4, fat_g=1.9, carbs_g=21.3,
            micronote="Higher protein for a carb.",
            benefits=["Good option for variety",
                      "Adds amino acid diversity",
                      "Often well tolerated"],
            cautions=["Rinse well before cooking"]
        ),

        # --- Oils ---
        Ingredient(
            name="Fish Oil (supplemental)",
            category="Oil",
            kcal_per_100g=900, protein_g=0, fat_g=100, carbs_g=0,
            micronote="EPA/DHA omega-3s.",
            benefits=["Skin/coat support",
                      "Anti-inflammatory support",
                      "May benefit cognitive and joint health"],
            cautions=["Dose carefully; can loosen stool",
                      "Check with vet if on blood thinners"]
        ),
        Ingredient(
            name="Olive Oil (small amounts)",
            category="Oil",
            kcal_per_100g=884, protein_g=0, fat_g=100, carbs_g=0,
            micronote="Monounsaturated fats.",
            benefits=["Palatability booster",
                      "Helps calorie density for thin dogs"],
            cautions=["Too much fat may trigger GI upset"]
        ),
    ]
    return {i.name: i for i in items}


INGREDIENTS = build_ingredients()


# =========================
# Breed & Life Stage Helpers
# =========================

BREED_LIST = [
    # toy/small
    "Chihuahua", "Pomeranian", "Yorkshire Terrier", "Maltese", "Toy Poodle",
    "Shih Tzu", "Dachshund (Mini)", "Papillon",
    # medium
    "Beagle", "French Bulldog", "Cocker Spaniel", "Border Collie", "Shetland Sheepdog",
    "Shiba Inu", "Schnauzer (Standard)", "Bulldog",
    # large/giant
    "Labrador Retriever", "Golden Retriever", "German Shepherd", "Siberian Husky",
    "Boxer", "Doberman", "Great Dane", "Bernese Mountain Dog",
    # mixed
    "Mixed Breed / Unknown",
]

BREED_SIZE_MAP = {
    # toy/small
    "Chihuahua": "Toy/Small",
    "Pomeranian": "Toy/Small",
    "Yorkshire Terrier": "Toy/Small",
    "Maltese": "Toy/Small",
    "Toy Poodle": "Toy/Small",
    "Shih Tzu": "Toy/Small",
    "Dachshund (Mini)": "Toy/Small",
    "Papillon": "Toy/Small",
    # medium
    "Beagle": "Medium",
    "French Bulldog": "Medium",
    "Cocker Spaniel": "Medium",
    "Border Collie": "Medium",
    "Shetland Sheepdog": "Medium",
    "Shiba Inu": "Medium",
    "Schnauzer (Standard)": "Medium",
    "Bulldog": "Medium",
    # large/giant
    "Labrador Retriever": "Large/Giant",
    "Golden Retriever": "Large/Giant",
    "German Shepherd": "Large/Giant",
    "Siberian Husky": "Large/Giant",
    "Boxer": "Large/Giant",
    "Doberman": "Large/Giant",
    "Great Dane": "Large/Giant",
    "Bernese Mountain Dog": "Large/Giant",
    # mixed default
    "Mixed Breed / Unknown": "Unknown",
}


def age_to_life_stage(age_years: float) -> str:
    if age_years < 1:
        return "Puppy"
    if age_years < 7:
        return "Adult"
    return "Senior"


def calc_rer(weight_kg: float) -> float:
    # Resting Energy Requirement
    # widely used equation in veterinary nutrition
    return 70 * (weight_kg ** 0.75)


def mer_factor(life_stage: str, activity: str, neutered: bool) -> float:
    # Conservative and adjustable multipliers.
    base = 1.6 if neutered else 1.8

    if life_stage == "Puppy":
        # Puppies vary widely; we provide a safer lower band.
        base = 2.2 if neutered else 2.4
    elif life_stage == "Senior":
        base = 1.3 if neutered else 1.4

    activity_boost = {
        "Low": 0.9,
        "Normal": 1.0,
        "High": 1.2,
        "Athletic/Working": 1.35,
    }.get(activity, 1.0)

    return base * activity_boost


# =========================
# Ratio Presets (Cooked Fresh)
# =========================

RATIO_PRESETS = [
    RatioPreset(
        key="balanced",
        label="Balanced Cooked Fresh (default)",
        meat_pct=50, veg_pct=35, carb_pct=15,
        note="A practical cooked-fresh ratio emphasizing lean protein and diverse vegetables."
    ),
    RatioPreset(
        key="weight",
        label="Weight-Aware & Satiety",
        meat_pct=45, veg_pct=45, carb_pct=10,
        note="Higher vegetable volume and slightly reduced energy density."
    ),
    RatioPreset(
        key="active",
        label="Active Adult Energy",
        meat_pct=55, veg_pct=25, carb_pct=20,
        note="More energy support for high activity while keeping vegetables present."
    ),
    RatioPreset(
        key="senior",
        label="Senior Gentle Balance",
        meat_pct=48, veg_pct=40, carb_pct=12,
        note="Fiber and micronutrient focus, moderate carbs."
    ),
    RatioPreset(
        key="puppy",
        label="Puppy Growth (cooked baseline)",
        meat_pct=55, veg_pct=30, carb_pct=15,
        note="Growth needs are complex; ensure calcium/vitamin balance with veterinary guidance."
    ),
]


# =========================
# Supplement Guidance
# =========================

SUPPLEMENTS = [
    {
        "name": "Omega-3 (Fish Oil)",
        "why": "Supports skin/coat, joint comfort, and inflammatory balance.",
        "best_for": ["Dry/itchy skin", "Senior dogs", "Joint support plans"],
        "cautions": "Dose carefully; excessive fat may loosen stool. Check with vet if on medications affecting clotting.",
        "pairing": "Pairs well with lean proteins and antioxidant-rich vegetables."
    },
    {
        "name": "Probiotics",
        "why": "May improve gut resilience and stool stability.",
        "best_for": ["Sensitive stomach", "Diet transitions", "Stress-related GI changes"],
        "cautions": "Choose veterinary-formulated options when possible.",
        "pairing": "Works nicely with pumpkin, oats, and gentle proteins."
    },
    {
        "name": "Calcium Support (for home-cooked)",
        "why": "Home-cooked diets often need calcium balancing.",
        "best_for": ["Puppies", "Dogs on long-term cooked fresh diets"],
        "cautions": "Over- or under-supplementation can be risky—confirm strategy with a vet nutritionist.",
        "pairing": "Especially crucial if not feeding balanced commercial formulations."
    },
    {
        "name": "Multivitamin (Canine)",
        "why": "Helps cover micronutrient gaps in simplified home recipes.",
        "best_for": ["Long-term home cooking", "Limited ingredient variety"],
        "cautions": "Avoid human multivitamins unless a vet approves.",
        "pairing": "Use with rotation-based weekly menus."
    },
    {
        "name": "Joint Support (Glucosamine/Chondroitin/UC-II)",
        "why": "May support mobility and cartilage health.",
        "best_for": ["Large breeds", "Senior dogs", "Highly active dogs"],
        "cautions": "Effects vary; benefits are often gradual.",
        "pairing": "Pairs with omega-3 and controlled body weight plans."
    },
]


# =========================
# Pantry & Planner Utilities
# =========================

def ingredient_df() -> pd.DataFrame:
    rows = []
    for ing in INGREDIENTS.values():
        rows.append({
            "Ingredient": ing.name,
            "Category": ing.category,
            "kcal/100g": ing.kcal_per_100g,
            "Protein(g)": ing.protein_g,
            "Fat(g)": ing.fat_g,
            "Carbs(g)": ing.carbs_g,
            "Micro-note": ing.micronote,
            "Benefits": " • ".join(ing.benefits),
            "Cautions": " • ".join(ing.cautions) if ing.cautions else "",
        })
    df = pd.DataFrame(rows)
    df = df.sort_values(["Category", "Ingredient"]).reset_index(drop=True)
    return df


def filter_ingredients_by_category(cat: str) -> List[str]:
    return [i.name for i in INGREDIENTS.values() if i.category == cat]


def compute_daily_energy(
    weight_kg: float,
    age_years: float,
    activity: str,
    neutered: bool,
    special_flags: List[str]
) -> Tuple[float, float, float, str]:
    stage = age_to_life_stage(age_years)
    rer = calc_rer(weight_kg)
    factor = mer_factor(stage, activity, neutered)
    mer = rer * factor

    # Conservative adjustments for special conditions
    # (These are gentle multipliers, not medical prescriptions.)
    adj = 1.0
    rationale = []

    if "Overweight / Weight loss goal" in special_flags:
        adj *= 0.85
        rationale.append("Reduced target for weight loss.")
    if "Very picky eater" in special_flags:
        # doesn't change calories, but we mention in notes
        rationale.append("Consider palatability strategies.")
    if "Pancreatitis risk / Needs lower fat" in special_flags:
        adj *= 0.95
        rationale.append("Slightly conservative energy target.")
    if "Kidney concern (vet-managed)" in special_flags:
        adj *= 0.95
        rationale.append("Energy target kept conservative; protein strategy should be vet-guided.")

    mer_adj = mer * adj
    explanation = stage
    if rationale:
        explanation += " | " + " ".join(rationale)

    return rer, mer, mer_adj, explanation


def default_ratio_for_context(preset_key: str) -> Tuple[int, int, int]:
    preset = next((p for p in RATIO_PRESETS if p.key == preset_key), RATIO_PRESETS[0])
    return preset.meat_pct, preset.veg_pct, preset.carb_pct


def ensure_ratio_sum(meat_pct: int, veg_pct: int, carb_pct: int) -> Tuple[int, int, int]:
    total = meat_pct + veg_pct + carb_pct
    if total == 100:
        return meat_pct, veg_pct, carb_pct
    # Normalize gracefully
    meat = round(meat_pct / total * 100)
    veg = round(veg_pct / total * 100)
    carb = 100 - meat - veg
    carb = max(0, carb)
    # small correction if rounding goes weird
    if meat + veg + carb != 100:
        diff = 100 - (meat + veg + carb)
        meat = max(0, meat + diff)
    return meat, veg, carb


def estimate_food_grams_from_energy(
    daily_kcal: float,
    assumed_kcal_per_g: float
) -> float:
    # Many cooked fresh mixes land roughly around 1.1–1.6 kcal/g depending on fat/carb.
    return daily_kcal / assumed_kcal_per_g


def pick_rotation(
    pantry_meats: List[str],
    pantry_vegs: List[str],
    pantry_carbs: List[str],
    days: int = 7,
    seed: Optional[int] = None
) -> List[Dict[str, str]]:
    rng = random.Random(seed if seed is not None else 42)

    def safe_choice(lst: List[str], fallback_pool: List[str]) -> str:
        if lst:
            return rng.choice(lst)
        return rng.choice(fallback_pool)

    all_meats = filter_ingredients_by_category("Meat")
    all_vegs = filter_ingredients_by_category("Veg")
    all_carbs = filter_ingredients_by_category("Carb")

    plan = []
    # Create gentle rotation: avoid same meat in consecutive days if possible
    last_meat = None
    for d in range(days):
        meat_pool = pantry_meats if pantry_meats else all_meats
        veg_pool = pantry_vegs if pantry_vegs else all_vegs
        carb_pool = pantry_carbs if pantry_carbs else all_carbs

        meat = safe_choice(meat_pool, all_meats)
        if len(meat_pool) > 1 and meat == last_meat:
            # try one re-roll
            meat = safe_choice([m for m in meat_pool if m != last_meat], all_meats)

        veg = safe_choice(veg_pool, all_vegs)
        carb = safe_choice(carb_pool, all_carbs)

        plan.append({"Meat": meat, "Veg": veg, "Carb": carb})
        last_meat = meat

    return plan


def grams_for_day(
    total_grams: float,
    meat_pct: int,
    veg_pct: int,
    carb_pct: int
) -> Tuple[float, float, float]:
    meat_g = total_grams * meat_pct / 100
    veg_g = total_grams * veg_pct / 100
    carb_g = total_grams * carb_pct / 100
    return meat_g, veg_g, carb_g


def day_nutrition_estimate(meat: str, veg: str, carb: str, meat_g: float, veg_g: float, carb_g: float) -> Dict[str, float]:
    def calc(ing_name: str, grams: float) -> Dict[str, float]:
        ing = INGREDIENTS[ing_name]
        factor = grams / 100.0
        return {
            "kcal": ing.kcal_per_100g * factor,
            "protein": ing.protein_g * factor,
            "fat": ing.fat_g * factor,
            "carbs": ing.carbs_g * factor,
        }

    a = calc(meat, meat_g)
    b = calc(veg, veg_g)
    c = calc(carb, carb_g)

    return {
        "kcal": a["kcal"] + b["kcal"] + c["kcal"],
        "protein": a["protein"] + b["protein"] + c["protein"],
        "fat": a["fat"] + b["fat"] + c["fat"],
        "carbs": a["carbs"] + b["carbs"] + c["carbs"],
    }


# =========================
# Session State
# =========================

if "taste_log" not in st.session_state:
    st.session_state.taste_log = []  # list of dict entries


# =========================
# Sidebar - Dog Profile
# =========================

st.sidebar.markdown(f"## 🐾 {APP_TITLE}")
st.sidebar.caption("Cosmic-grade fresh feeding intelligence")

breed = st.sidebar.selectbox("Breed", BREED_LIST, index=len(BREED_LIST)-1)

col_a, col_b = st.sidebar.columns(2)
with col_a:
    age_years = st.sidebar.number_input("Age (years)", min_value=0.1, max_value=25.0, value=3.0, step=0.1)
with col_b:
    weight_kg = st.sidebar.number_input("Weight (kg)", min_value=0.5, max_value=90.0, value=10.0, step=0.1)

neutered = st.sidebar.toggle("Neutered/Spayed", value=True)
activity = st.sidebar.select_slider(
    "Activity level",
    options=["Low", "Normal", "High", "Athletic/Working"],
    value="Normal"
)

special_flags = st.sidebar.multiselect(
    "Special considerations",
    [
        "None",
        "Overweight / Weight loss goal",
        "Sensitive stomach",
        "Pancreatitis risk / Needs lower fat",
        "Skin/coat concern",
        "Very picky eater",
        "Kidney concern (vet-managed)",
        "Food allergy suspected",
        "Joint/mobility support focus",
    ],
    default=["None"]
)
if "None" in special_flags and len(special_flags) > 1:
    special_flags = [f for f in special_flags if f != "None"]

assumed_kcal_per_g = st.sidebar.slider(
    "Assumed energy density (kcal per gram of cooked mix)",
    min_value=1.0, max_value=1.8, value=1.35, step=0.05,
    help="Cooked fresh mixes vary widely. This helps convert calories into total daily grams."
)

st.sidebar.markdown("---")
st.sidebar.caption("Educational tool; not a substitute for veterinary nutrition advice.")


# =========================
# Top Banner
# =========================

st.markdown(
    f"""
    <div class="nebula-card">
      <h1>🌌 {APP_TITLE}</h1>
      <p style="font-size: 1.05rem; opacity: 0.9;">
        {APP_SUBTITLE} <span class="badge">Cooked Fresh Focus</span>
      </p>
      <div class="nebula-divider"></div>
      <p style="opacity: 0.85;">
        This app builds a high-end, rotation-based cooked fresh plan using your dog's profile and your home pantry.
        It also explains why each ingredient matters and how ratios shape outcomes.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# Tabs (App Sections)
# =========================

tab_home, tab_ingredients, tab_ratio, tab_planner, tab_supp, tab_feedback = st.tabs(
    [
        "🚀 Command Deck",
        "🥩🥦 Ingredient Cosmos",
        "⚖️ Ratio Lab",
        "📅 7-Day Intelligent Plan",
        "💊 Supplement Observatory",
        "😋 Taste & Notes"
    ]
)


# =========================
# 1) Command Deck
# =========================

with tab_home:
    st.markdown("### Dog Profile Snapshot")

    size_class = BREED_SIZE_MAP.get(breed, "Unknown")
    stage = age_to_life_stage(age_years)

    rer, mer, mer_adj, explanation = compute_daily_energy(
        weight_kg=weight_kg,
        age_years=age_years,
        activity=activity,
        neutered=neutered,
        special_flags=special_flags
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Breed size class", size_class)
    c2.metric("Life stage", stage)
    c3.metric("RER (kcal/day)", f"{rer:.0f}")
    c4.metric("Target MER (adjusted)", f"{mer_adj:.0f}")

    st.caption(f"Context note: {explanation}")

    st.markdown("### What this app can reveal")
    show_system_map = st.toggle("Show Nebula System Map", value=True)
    if show_system_map:
        st.markdown(
            """
            <div class="nebula-card">
              <h4>🧭 Your navigation paths</h4>
              <ul>
                <li><b>Ingredient Cosmos</b> — filter meats/veg/carbs/oils, see benefits and cautions.</li>
                <li><b>Ratio Lab</b> — visualize macro energy contributions and compare presets.</li>
                <li><b>7-Day Intelligent Plan</b> — generate a weekly menu from your pantry with gram targets.</li>
                <li><b>Supplement Observatory</b> — learn safe, conservative pairing logic for cooked diets.</li>
                <li><b>Taste & Notes</b> — track preferences so future iterations become more personalized.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Safety-first cooking principles")
    with st.expander("Open safety notes (important)"):
        st.write(
            """
            - This tool is designed for **cooked fresh meal inspiration**.
            - Avoid seasoning (salt, onion, garlic, spicy sauces).
            - Ensure proteins are fully cooked and deboned.
            - Long-term home-cooked feeding typically needs **calcium + micronutrient balancing**.
            - If your dog has a medical condition (kidney disease, pancreatitis, diabetes),
              treat this as a **discussion starter** with a vet or board-certified nutritionist.
            """
        )


# =========================
# 2) Ingredient Cosmos
# =========================

with tab_ingredients:
    st.markdown("### Ingredient Encyclopedia")

    df = ingredient_df()

    col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 2])
    with col_f1:
        cat_filter = st.selectbox("Category filter", ["All", "Meat", "Veg", "Carb", "Oil"])
    with col_f2:
        sort_key = st.selectbox("Sort by", ["Category", "Ingredient", "kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"])
    with col_f3:
        search_text = st.text_input("Search ingredient name or notes", value="")

    df_view = df.copy()
    if cat_filter != "All":
        df_view = df_view[df_view["Category"] == cat_filter]

    if search_text.strip():
        mask = (
            df_view["Ingredient"].str.contains(search_text, case=False, na=False) |
            df_view["Micro-note"].str.contains(search_text, case=False, na=False) |
            df_view["Benefits"].str.contains(search_text, case=False, na=False)
        )
        df_view = df_view[mask]

    df_view = df_view.sort_values(sort_key).reset_index(drop=True)

    st.dataframe(df_view, use_container_width=True, height=360)

    st.markdown("### Visual Nutrition Lens")
    show_chart = st.toggle("Show interactive nutrition chart", value=True)
    if show_chart and not df_view.empty:
        chart_df = df_view[["Ingredient", "Category", "kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"]].copy()

        metric = st.radio(
            "Metric",
            ["kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"],
            horizontal=True
        )

        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Ingredient:N", sort="-y"),
                y=alt.Y(f"{metric}:Q"),
                tooltip=["Ingredient", "Category", "kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"],
                column=alt.Column("Category:N", header=alt.Header(labelAngle=0))
            )
            .properties(height=240)
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("### Deep-dive cards")
    selected_ing = st.selectbox("Pick an ingredient to explore", df["Ingredient"].tolist())
    ing_obj = INGREDIENTS[selected_ing]

    st.markdown(
        f"""
        <div class="nebula-card">
          <h3>{ing_obj.name}</h3>
          <p><b>Category:</b> {ing_obj.category}</p>
          <p><b>Approx nutrition (per 100g cooked):</b>
             {ing_obj.kcal_per_100g:.0f} kcal ·
             P {ing_obj.protein_g:.1f}g ·
             F {ing_obj.fat_g:.1f}g ·
             C {ing_obj.carbs_g:.1f}g
          </p>
          <p><b>Micro-note:</b> {ing_obj.micronote}</p>
          <div class="nebula-divider"></div>
          <p><b>Benefits</b></p>
          <ul>
            {''.join([f'<li>{b}</li>' for b in ing_obj.benefits])}
          </ul>
          <p><b>Cautions</b></p>
          <ul>
            {''.join([f'<li>{c}</li>' for c in ing_obj.cautions]) if ing_obj.cautions else '<li>No major general cautions listed for standard cooked use.</li>'}
          </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# 3) Ratio Lab
# =========================

with tab_ratio:
    st.markdown("### Ratio Presets and Custom Physics")

    preset_labels = {p.label: p.key for p in RATIO_PRESETS}
    preset_choice_label = st.selectbox("Choose a ratio preset", list(preset_labels.keys()))
    preset_key = preset_labels[preset_choice_label]
    preset_obj = next(p for p in RATIO_PRESETS if p.key == preset_key)

    st.info(preset_obj.note)

    use_custom = st.toggle("Override with custom ratios", value=False)

    if not use_custom:
        meat_pct, veg_pct, carb_pct = preset_obj.meat_pct, preset_obj.veg_pct, preset_obj.carb_pct
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            meat_pct = st.slider("Meat %", 30, 70, preset_obj.meat_pct)
        with c2:
            veg_pct = st.slider("Veg %", 15, 55, preset_obj.veg_pct)
        with c3:
            carb_pct = st.slider("Carb %", 0, 30, preset_obj.carb_pct)

        meat_pct, veg_pct, carb_pct = ensure_ratio_sum(meat_pct, veg_pct, carb_pct)
        st.caption(f"Normalized ratio: Meat {meat_pct}% · Veg {veg_pct}% · Carb {carb_pct}%")

    rer, mer, mer_adj, explanation = compute_daily_energy(
        weight_kg=weight_kg,
        age_years=age_years,
        activity=activity,
        neutered=neutered,
        special_flags=special_flags
    )
    daily_grams = estimate_food_grams_from_energy(mer_adj, assumed_kcal_per_g)

    meat_g, veg_g, carb_g = grams_for_day(daily_grams, meat_pct, veg_pct, carb_pct)

    st.markdown("### Daily gram target (based on your energy assumptions)")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Total cooked mix (g/day)", f"{daily_grams:.0f}")
    g2.metric("Meat target (g)", f"{meat_g:.0f}")
    g3.metric("Veg target (g)", f"{veg_g:.0f}")
    g4.metric("Carb target (g)", f"{carb_g:.0f}")

    st.markdown("### Macro energy lens (conceptual)")

    # Create a conceptual macro estimate using representative category averages
    cat_means = ingredient_df().groupby("Category")[["kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"]].mean()

    def est_cat_kcal(cat: str, grams: float) -> float:
        if cat not in cat_means.index:
            return 0.0
        return float(cat_means.loc[cat, "kcal/100g"]) * grams / 100.0

    est_meat_kcal = est_cat_kcal("Meat", meat_g)
    est_veg_kcal = est_cat_kcal("Veg", veg_g)
    est_carb_kcal = est_cat_kcal("Carb", carb_g)

    ratio_kcal_df = pd.DataFrame([
        {"Component": "Meat (avg)", "kcal": est_meat_kcal},
        {"Component": "Veg (avg)", "kcal": est_veg_kcal},
        {"Component": "Carb (avg)", "kcal": est_carb_kcal},
    ])

    chart = (
        alt.Chart(ratio_kcal_df)
        .mark_arc(innerRadius=50)
        .encode(
            theta="kcal:Q",
            color="Component:N",
            tooltip=["Component", alt.Tooltip("kcal:Q", format=".0f")]
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Interpretation guide"):
        st.write(
            """
            - This is a **conceptual lens** based on category averages.
            - Real energy will shift with specific cuts (fat content) and chosen carbs.
            - For dogs needing strict medical diets, consult a professional for precise formulation.
            """
        )


# =========================
# 4) 7-Day Intelligent Plan
# =========================

with tab_planner:
    st.markdown("### Pantry-driven weekly generation")

    all_meats = filter_ingredients_by_category("Meat")
    all_vegs = filter_ingredients_by_category("Veg")
    all_carbs = filter_ingredients_by_category("Carb")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        pantry_meats = st.multiselect("Meats you have", all_meats, default=[])
    with col_p2:
        pantry_vegs = st.multiselect("Vegetables you have", all_vegs, default=[])
    with col_p3:
        pantry_carbs = st.multiselect("Carbs you have", all_carbs, default=[])

    st.markdown("### Ratio configuration for the planner")

    preset_labels = {p.label: p.key for p in RATIO_PRESETS}
    planner_preset_label = st.selectbox("Planner ratio preset", list(preset_labels.keys()), index=0)
    planner_preset_key = preset_labels[planner_preset_label]
    planner_preset_obj = next(p for p in RATIO_PRESETS if p.key == planner_preset_key)

    planner_custom = st.toggle("Fine-tune planner ratio", value=False)

    if not planner_custom:
        meat_pct, veg_pct, carb_pct = planner_preset_obj.meat_pct, planner_preset_obj.veg_pct, planner_preset_obj.carb_pct
    else:
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            meat_pct = st.slider("Planner Meat %", 30, 70, planner_preset_obj.meat_pct, key="planner_meat")
        with cc2:
            veg_pct = st.slider("Planner Veg %", 15, 55, planner_preset_obj.veg_pct, key="planner_veg")
        with cc3:
            carb_pct = st.slider("Planner Carb %", 0, 30, planner_preset_obj.carb_pct, key="planner_carb")

        meat_pct, veg_pct, carb_pct = ensure_ratio_sum(meat_pct, veg_pct, carb_pct)

    rer, mer, mer_adj, explanation = compute_daily_energy(
        weight_kg=weight_kg,
        age_years=age_years,
        activity=activity,
        neutered=neutered,
        special_flags=special_flags
    )
    daily_grams = estimate_food_grams_from_energy(mer_adj, assumed_kcal_per_g)
    meat_g, veg_g, carb_g = grams_for_day(daily_grams, meat_pct, veg_pct, carb_pct)

    st.caption(
        f"Daily targets (based on your assumptions): "
        f"{daily_grams:.0f}g total → Meat {meat_g:.0f}g · Veg {veg_g:.0f}g · Carb {carb_g:.0f}g"
    )

    seed = st.slider("Rotation randomness seed", 1, 999, 42, help="Change this to reshuffle the weekly rotation.")
    generate = st.button("✨ Generate 7-Day Nebula Plan")

    if generate:
        rotation = pick_rotation(pantry_meats, pantry_vegs, pantry_carbs, days=7, seed=seed)

        rows = []
        for i, combo in enumerate(rotation, start=1):
            mg, vg, cg = grams_for_day(daily_grams, meat_pct, veg_pct, carb_pct)
            nut = day_nutrition_estimate(combo["Meat"], combo["Veg"], combo["Carb"], mg, vg, cg)

            rows.append({
                "Day": f"Day {i}",
                "Meat": combo["Meat"],
                "Veg": combo["Veg"],
                "Carb": combo["Carb"],
                "Meat (g)": round(mg),
                "Veg (g)": round(vg),
                "Carb (g)": round(cg),
                "Est kcal": round(nut["kcal"]),
                "Protein (g)": round(nut["protein"], 1),
                "Fat (g)": round(nut["fat"], 1),
                "Carbs (g)": round(nut["carbs"], 1),
            })

        plan_df = pd.DataFrame(rows)

        st.markdown("### Your weekly plan")
        st.dataframe(plan_df, use_container_width=True, height=340)

        st.markdown("### Weekly nutrient trend (approx)")
        melt = plan_df.melt(
            id_vars=["Day"],
            value_vars=["Est kcal", "Protein (g)", "Fat (g)", "Carbs (g)"],
            var_name="Metric",
            value_name="Value"
        )
        line = (
            alt.Chart(melt)
            .mark_line(point=True)
            .encode(
                x="Day:N",
                y="Value:Q",
                color="Metric:N",
                tooltip=["Day", "Metric", "Value"]
            )
            .properties(height=260)
        )
        st.altair_chart(line, use_container_width=True)

        with st.expander("Cooking & serving protocol for this plan"):
            st.write(
                """
                - Cook proteins plainly; remove skin and visible excess fat if needed.
                - Steam/boil veggies; chop finely for small breeds.
                - Cook carbs thoroughly.
                - Mix, cool, portion.
                - For long-term feeding, consider:
                  **canine multivitamin + calcium strategy + omega-3** after professional review.
                """
            )

        with st.expander("Why rotation matters (science-lite)"):
            st.write(
                """
                Rotation helps reduce over-reliance on a single protein or plant,
                improves micronutrient diversity, and can make meals more engaging for dogs.
                """
            )


# =========================
# 5) Supplement Observatory
# =========================

with tab_supp:
    st.markdown("### Conservative supplement pairing guide")

    st.markdown(
        """
        Supplements can help fill gaps in simplified cooked diets, but the best choice depends on your dog's health.
        This section provides **non-prescriptive** educational guidance.
        """
    )

    supp_df = pd.DataFrame(SUPPLEMENTS)
    st.dataframe(
        supp_df[["name", "why", "cautions", "pairing"]],
        use_container_width=True,
        height=260
    )

    st.markdown("### Personalized supplement lens")
    focus = st.multiselect(
        "What do you want to prioritize?",
        ["Skin/Coat", "Gut", "Joint/Mobility", "Puppy Growth Support", "Senior Vitality", "Weight Management"],
        default=[]
    )

    suggestions = []
    if "Skin/Coat" in focus:
        suggestions.append("Omega-3 (Fish Oil)")
    if "Gut" in focus:
        suggestions.append("Probiotics")
    if "Joint/Mobility" in focus:
        suggestions.append("Joint Support (Glucosamine/Chondroitin/UC-II)")
        suggestions.append("Omega-3 (Fish Oil)")
    if "Puppy Growth Support" in focus:
        suggestions.append("Calcium Support (for home-cooked)")
        suggestions.append("Multivitamin (Canine)")
    if "Senior Vitality" in focus:
        suggestions.append("Omega-3 (Fish Oil)")
        suggestions.append("Joint Support (Glucosamine/Chondroitin/UC-II)")
        suggestions.append("Probiotics")
    if "Weight Management" in focus:
        suggestions.append("Probiotics")

    suggestions = list(dict.fromkeys(suggestions))  # dedupe preserve order

    if suggestions:
        st.markdown(
            f"""
            <div class="nebula-card">
              <h4>Suggested educational focus</h4>
              <ul>
                {''.join([f'<li>{s}</li>' for s in suggestions])}
              </ul>
              <div class="nebula-divider"></div>
              <p style="opacity: 0.85;">
                For dosing and long-term plans, confirm with a veterinarian,
                especially if your dog has a medical condition or takes medication.
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.caption("Select a priority to see a conservative educational highlight list.")


# =========================
# 6) Taste & Notes
# =========================

with tab_feedback:
    st.markdown("### Taste tracking capsule")

    st.write(
        """
        Record how your dog responds to different proteins and vegetables.
        This log stays in your session and helps you refine future plan generations.
        """
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        log_meat = st.selectbox("Observed meat", ["(skip)"] + filter_ingredients_by_category("Meat"))
    with col_t2:
        log_veg = st.selectbox("Observed vegetable", ["(skip)"] + filter_ingredients_by_category("Veg"))
    with col_t3:
        love_level = st.select_slider(
            "Preference",
            options=["Dislike", "Neutral", "Like", "Love"],
            value="Like"
        )

    notes = st.text_input("Optional notes (stool, energy, itching, etc.)")

    if st.button("🧪 Add taste entry"):
        entry = {
            "Breed": breed,
            "Age (y)": round(age_years, 2),
            "Weight (kg)": round(weight_kg, 2),
            "Meat": None if log_meat == "(skip)" else log_meat,
            "Veg": None if log_veg == "(skip)" else log_veg,
            "Preference": love_level,
            "Notes": notes.strip(),
        }
        st.session_state.taste_log.append(entry)
        st.success("Entry added to session log.")

    if st.session_state.taste_log:
        log_df = pd.DataFrame(st.session_state.taste_log)

        st.markdown("### Session taste log")
        st.dataframe(log_df, use_container_width=True, height=260)

        st.markdown("### Preference summary")

        # Build simple counts for meats and vegs
        def pref_score(p: str) -> int:
            return {"Dislike": 0, "Neutral": 1, "Like": 2, "Love": 3}.get(p, 1)

        meat_records = log_df.dropna(subset=["Meat"]).copy()
        veg_records = log_df.dropna(subset=["Veg"]).copy()

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            if not meat_records.empty:
                meat_records["Score"] = meat_records["Preference"].map(pref_score)
                meat_rank = meat_records.groupby("Meat")["Score"].mean().sort_values(ascending=False).reset_index()
                meat_rank.columns = ["Meat", "Avg Preference Score"]

                bar = (
                    alt.Chart(meat_rank)
                    .mark_bar()
                    .encode(
                        x=alt.X("Avg Preference Score:Q", scale=alt.Scale(domain=[0, 3])),
                        y=alt.Y("Meat:N", sort="-x"),
                        tooltip=["Meat", alt.Tooltip("Avg Preference Score:Q", format=".2f")]
                    )
                    .properties(height=240, title="Meat preference (session)")
                )
                st.altair_chart(bar, use_container_width=True)
            else:
                st.caption("No meat preference entries yet.")

        with col_s2:
            if not veg_records.empty:
                veg_records["Score"] = veg_records["Preference"].map(pref_score)
                veg_rank = veg_records.groupby("Veg")["Score"].mean().sort_values(ascending=False).reset_index()
                veg_rank.columns = ["Vegetable", "Avg Preference Score"]

                bar = (
                    alt.Chart(veg_rank)
                    .mark_bar()
                    .encode(
                        x=alt.X("Avg Preference Score:Q", scale=alt.Scale(domain=[0, 3])),
                        y=alt.Y("Vegetable:N", sort="-x"),
                        tooltip=["Vegetable", alt.Tooltip("Avg Preference Score:Q", format=".2f")]
                    )
                    .properties(height=240, title="Vegetable preference (session)")
                )
                st.altair_chart(bar, use_container_width=True)
            else:
                st.caption("No vegetable preference entries yet.")

        with st.expander("How to use this data"):
            st.write(
                """
                - If your dog consistently dislikes a protein, swap it out in the pantry list.
                - If a vegetable correlates with softer stool, reduce its share or rotate less frequently.
                - For allergy suspicion, discuss an elimination strategy with a veterinarian.
                """
            )
    else:
        st.info("Your taste log is empty. Add entries to unlock preference analytics.")


# =========================
# Footer
# =========================

st.markdown("---")
st.caption(
    "Nebula Paw Kitchen™ is an educational planner for cooked fresh feeding. "
    "For long-term complete nutrition, especially for puppies or medical cases, "
    "consult a veterinarian or a board-certified veterinary nutritionist."
)
