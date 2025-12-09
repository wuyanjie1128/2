import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import pandas as pd
import streamlit as st
import altair as alt


# =========================
# Nebula Paw Kitchen - Theme
# =========================

APP_TITLE = "Nebula Paw Kitchen™"
APP_SUBTITLE = "Premium Fresh Meal Intelligence for Dogs"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🐶🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.stApp {
    background:
        radial-gradient(1200px 800px at 10% 10%, rgba(120, 140, 255, 0.16), transparent 60%),
        radial-gradient(1200px 800px at 90% 20%, rgba(255, 120, 220, 0.12), transparent 60%),
        radial-gradient(900px 700px at 20% 90%, rgba(120, 255, 200, 0.10), transparent 60%),
        linear-gradient(135deg, #070812 0%, #0a0c1a 40%, #0a0b14 100%);
    color: #F5F7FF;
}
h1, h2, h3, h4 { letter-spacing: 0.4px; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border-right: 1px solid rgba(255,255,255,0.06);
}
.nebula-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px 18px 12px 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.nebula-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    margin: 14px 0 18px 0;
}
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
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.04) !important;
    border-radius: 10px;
}
thead tr th { background-color: rgba(255,255,255,0.06) !important; }
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    margin-left: 6px;
}
.small-muted {
    opacity: 0.8;
    font-size: 0.9rem;
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
# Ingredient Knowledge Base (rich)
# Approximate cooked values.
# =========================

def build_ingredients() -> Dict[str, Ingredient]:
    items = [
        # --- Meats / Proteins ---
        Ingredient("Chicken (lean, cooked)", "Meat", 165, 31, 3.6, 0,
                   "B vitamins, selenium.",
                   ["High-quality protein for muscle maintenance",
                    "Generally well tolerated",
                    "Excellent base protein for rotation"],
                   ["Avoid if chicken allergy suspected",
                    "Remove skin for lower-fat plans"]),

        Ingredient("Turkey (lean, cooked)", "Meat", 150, 29, 2.0, 0,
                   "Niacin, selenium.",
                   ["Lean protein option", "Great for weight-aware plans", "Mild flavor"],
                   ["Avoid processed/deli products"]),

        Ingredient("Beef (lean, cooked)", "Meat", 200, 26, 10, 0,
                   "Iron, zinc, B12.",
                   ["Supports red blood cell health", "Strong palatability", "Good for active adults"],
                   ["Higher fat depending on cut"]),

        Ingredient("Lamb (lean, cooked)", "Meat", 206, 25, 12, 0,
                   "Zinc, carnitine.",
                   ["Alternative protein", "Rich taste for picky dogs", "Useful rotation option"],
                   ["Can be richer; adjust for pancreatitis risk"]),

        Ingredient("Pork (lean, cooked)", "Meat", 195, 27, 9, 0,
                   "Thiamine-rich protein.",
                   ["Good rotation variety", "Often highly palatable", "Supports energy metabolism"],
                   ["Use lean cuts; avoid processed pork"]),

        Ingredient("Duck (lean, cooked)", "Meat", 190, 24, 11, 0,
                   "Rich flavor, B vitamins.",
                   ["Great for variety", "High palatability", "Useful to prevent boredom"],
                   ["Moderate fat"]),

        Ingredient("Venison (lean, cooked)", "Meat", 158, 30, 3.2, 0,
                   "Often considered novel protein.",
                   ["Lean novel option", "Rotation diversity", "Good for some sensitive dogs"],
                   ["Novel protein strategies should be vet-guided"]),

        Ingredient("Rabbit (cooked)", "Meat", 173, 33, 3.5, 0,
                   "Very lean, novel option.",
                   ["Lean and light", "Excellent rotation diversity"],
                   ["Ensure safe sourcing"]),

        Ingredient("Egg (cooked)", "Meat", 155, 13, 11, 1.1,
                   "Complete amino acid profile.",
                   ["Top-tier protein quality", "Palatability booster"],
                   ["Introduce gradually"]),

        Ingredient("Salmon (cooked)", "Meat", 208, 20, 13, 0,
                   "Omega-3, vitamin D.",
                   ["Skin/coat support", "Anti-inflammatory profile", "Good for seniors"],
                   ["Higher fat; portion carefully"]),

        Ingredient("White Fish (cod, cooked)", "Meat", 105, 23, 0.9, 0,
                   "Very lean protein.",
                   ["Excellent for weight plans", "Gentle for GI-sensitive dogs"],
                   ["Keep it plain"]),

        Ingredient("Sardines (cooked, deboned)", "Meat", 208, 25, 11, 0,
                   "Omega-3 rich mini-fish.",
                   ["Great topper for coat/joints", "Very palatable"],
                   ["Watch sodium if canned"]),

        # --- Vegetables ---
        Ingredient("Pumpkin (cooked)", "Veg", 26, 1, 0.1, 6.5,
                   "Soluble fiber + beta-carotene.",
                   ["Supports stool quality", "Great transition veggie", "Gentle gut support"],
                   ["Too much can dilute calories"]),

        Ingredient("Carrot (cooked)", "Veg", 35, 0.8, 0.2, 8,
                   "Beta-carotene.",
                   ["Antioxidant support", "Low calorie micronutrient boost"],
                   ["Chop/soften for tiny breeds"]),

        Ingredient("Broccoli (cooked)", "Veg", 34, 2.8, 0.4, 7,
                   "Vitamin C, K.",
                   ["Rotation-friendly antioxidants", "Good micronutrient diversity"],
                   ["Large amounts may cause gas"]),

        Ingredient("Zucchini (cooked)", "Veg", 17, 1.2, 0.3, 3.1,
                   "Hydration-friendly veggie.",
                   ["Great for volumizing meals", "Mild taste"],
                   ["Avoid seasoning"]),

        Ingredient("Green Beans (cooked)", "Veg", 31, 1.8, 0.1, 7,
                   "Low-calorie bulk.",
                   ["Helpful for weight management", "Gentle fiber"],
                   []),

        Ingredient("Cauliflower (cooked)", "Veg", 25, 1.9, 0.3, 5,
                   "Low-cal crucifer.",
                   ["Adds volume", "Good rotation veggie"],
                   ["May cause gas"]),

        Ingredient("Sweet Peas (cooked)", "Veg", 84, 5.4, 0.4, 15.6,
                   "Plant protein + fiber.",
                   ["Adds variety", "Good texture mix-in"],
                   ["Moderate starch"]),

        Ingredient("Kale (cooked, small portions)", "Veg", 35, 2.9, 1.5, 4.4,
                   "Dense micronutrients.",
                   ["Small-dose antioxidant boost"],
                   ["Use small portions"]),

        Ingredient("Spinach (cooked, small portions)", "Veg", 23, 2.9, 0.4, 3.6,
                   "Folate, magnesium.",
                   ["Micronutrient variety"],
                   ["Use small portions due to oxalates"]),

        Ingredient("Bell Pepper (red, cooked)", "Veg", 31, 1, 0.3, 6,
                   "Colorful vitamin-rich veggie.",
                   ["Adds antioxidant color diversity"],
                   ["Avoid spicy/seasoned"]),

        Ingredient("Cabbage (cooked, small portions)", "Veg", 23, 1.3, 0.1, 5.5,
                   "Budget-friendly fiber.",
                   ["Adds variety"],
                   ["May cause gas"]),

        Ingredient("Cucumber (peeled, small portions)", "Veg", 15, 0.7, 0.1, 3.6,
                   "Hydrating crunch.",
                   ["Cooling low-cal add-on"],
                   ["Chop small"]),

        # --- Carbs ---
        Ingredient("Sweet Potato (cooked)", "Carb", 86, 1.6, 0.1, 20,
                   "Beta-carotene, potassium.",
                   ["Palatable energy base", "Great controlled carb"],
                   ["Portion for weight control"]),

        Ingredient("Brown Rice (cooked)", "Carb", 123, 2.7, 1.0, 25.6,
                   "Gentle starch base.",
                   ["Neutral, easy-to-digest"],
                   ["Lower if overweight/diabetic plan"]),

        Ingredient("White Rice (cooked)", "Carb", 130, 2.4, 0.3, 28.2,
                   "Very gentle GI carb.",
                   ["Useful during sensitive stomach phases"],
                   ["Lower micronutrients vs brown rice"]),

        Ingredient("Oats (cooked)", "Carb", 71, 2.5, 1.4, 12,
                   "Soluble fiber.",
                   ["Satiety support", "Gut-friendly option"],
                   ["Introduce gradually"]),

        Ingredient("Quinoa (cooked)", "Carb", 120, 4.4, 1.9, 21.3,
                   "Higher protein carb.",
                   ["Adds amino acid diversity"],
                   ["Rinse well before cooking"]),

        Ingredient("Barley (cooked)", "Carb", 123, 2.3, 0.4, 28,
                   "Fiber-rich grain.",
                   ["Satiety-friendly carb"],
                   ["Introduce gradually"]),

        Ingredient("Buckwheat (cooked)", "Carb", 92, 3.4, 0.6, 19.9,
                   "Alternative pseudo-grain.",
                   ["Variety option"],
                   ["Cook thoroughly"]),

        Ingredient("Potato (cooked, plain)", "Carb", 87, 2, 0.1, 20,
                   "Simple starch.",
                   ["Palatable limited-ingredient carb"],
                   ["Never raw; avoid green parts"]),

        # --- Oils ---
        Ingredient("Fish Oil (supplemental)", "Oil", 900, 0, 100, 0,
                   "EPA/DHA omega-3s.",
                   ["Skin/coat support", "Joint and inflammatory support"],
                   ["Dose carefully"]),

        Ingredient("Olive Oil (small amounts)", "Oil", 884, 0, 100, 0,
                   "Monounsaturated fats.",
                   ["Palatability booster"],
                   ["Too much may trigger GI upset"]),

        Ingredient("Flaxseed Oil (small amounts)", "Oil", 884, 0, 100, 0,
                   "ALA omega-3 (plant-based).",
                   ["Rotation fat option"],
                   ["ALA conversion to EPA/DHA is limited"]),

        Ingredient("MCT Oil (very small amounts)", "Oil", 900, 0, 100, 0,
                   "Specialized fat.",
                   ["Occasional vet-guided senior cognition support"],
                   ["Can cause diarrhea"]),

        # --- Treat / Fruits ---
        Ingredient("Blueberries (small portions)", "Treat", 57, 0.7, 0.3, 14.5,
                   "Antioxidant fruit topper.",
                   ["Small antioxidant boost", "Fun topper variety"],
                   ["Use small portions"]),

        Ingredient("Apple (peeled, no seeds)", "Treat", 52, 0.3, 0.2, 14,
                   "Hydrating sweet crunch.",
                   ["Low-cal treat topper"],
                   ["Remove seeds/core"]),

        Ingredient("Strawberries (small portions)", "Treat", 32, 0.7, 0.3, 7.7,
                   "Vitamin C + flavor variety.",
                   ["Light fruity enrichment"],
                   ["Use small portions"]),

    ]
    return {i.name: i for i in items}


INGREDIENTS = build_ingredients()


# =========================
# Expanded Breed List (broad coverage)
# =========================

BREED_LIST = [
    # Toy
    "Affenpinscher", "Brussels Griffon", "Cavalier King Charles Spaniel",
    "Chihuahua", "Chinese Crested", "English Toy Spaniel", "Italian Greyhound",
    "Japanese Chin", "Maltese", "Miniature Pinscher", "Papillon",
    "Pekingese", "Pomeranian", "Pug", "Russian Toy", "Shih Tzu",
    "Toy Fox Terrier", "Toy Poodle", "Yorkshire Terrier",

    # Small
    "Bichon Frise", "Boston Terrier", "Cairn Terrier",
    "Cardigan Welsh Corgi", "Pembroke Welsh Corgi",
    "Coton de Tulear", "Dachshund (Mini)", "Dachshund (Standard)",
    "Havanese", "Jack Russell Terrier", "Lhasa Apso",
    "Miniature Schnauzer", "Norfolk Terrier", "Norwich Terrier",
    "Scottish Terrier", "West Highland White Terrier", "Whippet",

    # Medium
    "American Cocker Spaniel", "Australian Shepherd", "Basenji", "Beagle",
    "Border Collie", "Brittany", "Bulldog", "Bull Terrier",
    "Chinese Shar-Pei", "Dalmatian", "French Bulldog",
    "Keeshond", "Korean Jindo", "Lagotto Romagnolo",
    "Miniature American Shepherd", "Shiba Inu", "Shikoku",
    "Schnauzer (Standard)", "Soft Coated Wheaten Terrier",
    "Staffordshire Bull Terrier", "Vizsla",

    # Large
    "Airedale Terrier", "Akita", "Alaskan Malamute", "American Bulldog",
    "Australian Cattle Dog", "Belgian Malinois", "Bernese Mountain Dog",
    "Bloodhound", "Boxer", "Cane Corso",
    "Collie (Rough)", "Collie (Smooth)",
    "Doberman", "German Shepherd", "German Shorthaired Pointer",
    "Golden Retriever", "Greyhound", "Irish Setter",
    "Labrador Retriever", "Old English Sheepdog",
    "Pointer", "Rottweiler", "Rhodesian Ridgeback",
    "Siberian Husky", "Standard Poodle", "Weimaraner",

    # Giant
    "Anatolian Shepherd", "Boerboel", "Borzoi", "Bullmastiff",
    "Dogue de Bordeaux", "Great Dane", "Great Pyrenees",
    "Irish Wolfhound", "Leonberger", "Mastiff",
    "Neapolitan Mastiff", "Newfoundland", "Saint Bernard",
    "Tibetan Mastiff", "Caucasian Shepherd Dog", "Central Asian Shepherd Dog",

    # Primitive/Northern/Regional
    "American Eskimo Dog", "Chow Chow", "Thai Ridgeback",
    "Taiwan Dog", "Kishu Ken", "Kai Ken", "Hokkaido", "Tosa",
    "Xoloitzcuintli", "Peruvian Inca Orchid",

    # Catch-all
    "Mixed Breed / Unknown",
]

BREED_SIZE_MAP = {b: "Unknown" for b in BREED_LIST}
for b in [
    "Chihuahua", "Pomeranian", "Yorkshire Terrier", "Maltese", "Toy Poodle",
    "Shih Tzu", "Papillon", "Japanese Chin", "Pekingese", "Russian Toy",
    "Affenpinscher", "Brussels Griffon", "Chinese Crested", "Pug",
    "Miniature Pinscher", "Toy Fox Terrier", "Italian Greyhound",
    "English Toy Spaniel", "Cavalier King Charles Spaniel",
    "Bichon Frise", "Boston Terrier", "Cairn Terrier",
    "Dachshund (Mini)", "Havanese", "Lhasa Apso",
    "Miniature Schnauzer", "Norfolk Terrier", "Norwich Terrier",
    "Scottish Terrier", "West Highland White Terrier",
]:
    BREED_SIZE_MAP[b] = "Toy/Small"

for b in [
    "Beagle", "French Bulldog", "Bulldog",
    "Border Collie", "Australian Shepherd",
    "Shiba Inu", "Korean Jindo", "Schnauzer (Standard)",
    "Staffordshire Bull Terrier", "Soft Coated Wheaten Terrier",
    "Vizsla", "Dalmatian", "Keeshond",
    "Cardigan Welsh Corgi", "Pembroke Welsh Corgi",
]:
    BREED_SIZE_MAP[b] = "Medium"

for b in [
    "Labrador Retriever", "Golden Retriever", "German Shepherd",
    "Siberian Husky", "Doberman", "Rottweiler",
    "Boxer", "Weimaraner", "Pointer",
    "Akita", "Alaskan Malamute", "Cane Corso",
    "Bernese Mountain Dog", "Standard Poodle",
]:
    BREED_SIZE_MAP[b] = "Large/Giant"

for b in [
    "Great Dane", "Mastiff", "Neapolitan Mastiff", "Saint Bernard",
    "Newfoundland", "Leonberger", "Great Pyrenees",
    "Tibetan Mastiff", "Caucasian Shepherd Dog", "Central Asian Shepherd Dog",
    "Irish Wolfhound"
]:
    BREED_SIZE_MAP[b] = "Large/Giant"


# =========================
# Life stage & energy helpers
# =========================

def age_to_life_stage(age_years: float) -> str:
    if age_years < 1:
        return "Puppy"
    if age_years < 7:
        return "Adult"
    return "Senior"


def calc_rer(weight_kg: float) -> float:
    return 70 * (weight_kg ** 0.75)


def mer_factor(life_stage: str, activity: str, neutered: bool) -> float:
    base = 1.6 if neutered else 1.8
    if life_stage == "Puppy":
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
# Ratio Presets
# =========================

RATIO_PRESETS = [
    RatioPreset("balanced", "Balanced Cooked Fresh (default)", 50, 35, 15,
                "A practical cooked-fresh ratio emphasizing lean protein and diverse vegetables."),
    RatioPreset("weight", "Weight-Aware & Satiety", 45, 45, 10,
                "Higher vegetable volume and slightly reduced energy density."),
    RatioPreset("active", "Active Adult Energy", 55, 25, 20,
                "More energy support for high activity while keeping vegetables present."),
    RatioPreset("senior", "Senior Gentle Balance", 48, 40, 12,
                "Fiber and micronutrient focus, moderate carbs."),
    RatioPreset("puppy", "Puppy Growth (cooked baseline)", 55, 30, 15,
                "Growth needs are complex; ensure calcium/vitamin balance with veterinary guidance."),
    RatioPreset("gentle_gi", "Gentle GI Rotation", 50, 40, 10,
                "A calmer profile leaning on easy proteins and soothing fiber veggies."),
]


# =========================
# Supplements (expanded)
# =========================

SUPPLEMENTS = [
    {"name": "Omega-3 (Fish Oil)",
     "why": "Supports skin/coat, joint comfort, and inflammatory balance.",
     "best_for": ["Dry/itchy skin", "Senior dogs", "Joint support plans"],
     "cautions": "Dose carefully; may loosen stool. Check with vet if on clotting-related meds.",
     "pairing": "Pairs well with lean proteins and antioxidant-rich vegetables."},

    {"name": "Probiotics",
     "why": "May improve gut resilience and stool stability.",
     "best_for": ["Sensitive stomach", "Diet transitions", "Stress-related GI changes"],
     "cautions": "Choose canine-specific options.",
     "pairing": "Works nicely with pumpkin, oats, and gentle proteins."},

    {"name": "Prebiotic Fiber (e.g., inulin, MOS)",
     "why": "Supports beneficial gut bacteria and stool quality.",
     "best_for": ["Soft stools", "Gut resilience goals"],
     "cautions": "Too much can cause gas.",
     "pairing": "Often paired with probiotics."},

    {"name": "Calcium Support (for home-cooked)",
     "why": "Home-cooked diets commonly need calcium balancing.",
     "best_for": ["Puppies", "Long-term cooked routines"],
     "cautions": "Over/under supplementation can be risky—vet nutritionist advised.",
     "pairing": "Essential when meals are fully home-prepared."},

    {"name": "Canine Multivitamin",
     "why": "Helps cover micronutrient gaps in simplified recipes.",
     "best_for": ["Limited ingredient variety", "Long-term home cooking"],
     "cautions": "Avoid human multivitamins unless approved.",
     "pairing": "Best with weekly rotation."},

    {"name": "Joint Support (Glucosamine/Chondroitin/UC-II)",
     "why": "May support mobility and cartilage health.",
     "best_for": ["Large breeds", "Senior dogs", "Highly active dogs"],
     "cautions": "Effects vary and take time.",
     "pairing": "Pairs with omega-3 and weight control."},

    {"name": "Vitamin E (as guided)",
     "why": "Antioxidant support often used alongside omega-3.",
     "best_for": ["Dogs on long-term fish oil"],
     "cautions": "Avoid excessive dosing.",
     "pairing": "Consider with fatty acid protocols."},

    {"name": "Dental Additives (vet-approved)",
     "why": "Helps reduce plaque when brushing is difficult.",
     "best_for": ["Small breeds", "Dental-prone dogs"],
     "cautions": "Not a substitute for brushing.",
     "pairing": "Pair with safe chewing strategies."},

    {"name": "L-Carnitine (vet-guided)",
     "why": "May assist some weight or cardiac strategies.",
     "best_for": ["Vet-supervised weight plans"],
     "cautions": "Use under professional advice.",
     "pairing": "Best with lean protein + veggie-heavy ratios."},
]


# =========================
# Core data utilities
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
    return df.sort_values(["Category", "Ingredient"]).reset_index(drop=True)


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
    mer = rer * mer_factor(stage, activity, neutered)

    adj = 1.0
    rationale = []

    if "Overweight / Weight loss goal" in special_flags:
        adj *= 0.85
        rationale.append("Weight-loss adjusted target.")
    if "Pancreatitis risk / Needs lower fat" in special_flags:
        adj *= 0.95
        rationale.append("Fat-sensitive conservative target.")
    if "Kidney concern (vet-managed)" in special_flags:
        adj *= 0.95
        rationale.append("Energy conservative; protein strategy must be vet-guided.")
    if "Very picky eater" in special_flags:
        rationale.append("Use palatability tactics & stronger rotation.")

    mer_adj = mer * adj
    explanation = stage + (" | " + " ".join(rationale) if rationale else "")

    return rer, mer, mer_adj, explanation


def ensure_ratio_sum(meat_pct: int, veg_pct: int, carb_pct: int) -> Tuple[int, int, int]:
    total = meat_pct + veg_pct + carb_pct
    if total == 100:
        return meat_pct, veg_pct, carb_pct
    meat = round(meat_pct / total * 100)
    veg = round(veg_pct / total * 100)
    carb = 100 - meat - veg
    carb = max(0, carb)
    if meat + veg + carb != 100:
        diff = 100 - (meat + veg + carb)
        meat = max(0, meat + diff)
    return meat, veg, carb


def estimate_food_grams_from_energy(daily_kcal: float, assumed_kcal_per_g: float) -> float:
    return daily_kcal / assumed_kcal_per_g


def grams_for_day(total_grams: float, meat_pct: int, veg_pct: int, carb_pct: int) -> Tuple[float, float, float]:
    return (
        total_grams * meat_pct / 100,
        total_grams * veg_pct / 100,
        total_grams * carb_pct / 100
    )


def day_nutrition_estimate(meat: str, veg: str, carb: str, meat_g: float, veg_g: float, carb_g: float) -> Dict[str, float]:
    def calc(name: str, grams: float) -> Dict[str, float]:
        ing = INGREDIENTS[name]
        f = grams / 100.0
        return {
            "kcal": ing.kcal_per_100g * f,
            "protein": ing.protein_g * f,
            "fat": ing.fat_g * f,
            "carbs": ing.carbs_g * f,
        }
    a, b, c = calc(meat, meat_g), calc(veg, veg_g), calc(carb, carb_g)
    return {
        "kcal": a["kcal"] + b["kcal"] + c["kcal"],
        "protein": a["protein"] + b["protein"] + c["protein"],
        "fat": a["fat"] + b["fat"] + c["fat"],
        "carbs": a["carbs"] + b["carbs"] + c["carbs"],
    }


# =========================
# Human-friendly recommender
# =========================

def recommend_ingredients(stage: str, special_flags: List[str]) -> Dict[str, List[str]]:
    """
    Returns recommended lists to enrich variety.
    This is educational logic, not medical prescription.
    """
    meats = []
    vegs = []
    carbs = []
    treats = []

    # base variety suggestions
    base_meats = [
        "Turkey (lean, cooked)", "White Fish (cod, cooked)",
        "Salmon (cooked)", "Egg (cooked)", "Lamb (lean, cooked)"
    ]
    base_vegs = [
        "Pumpkin (cooked)", "Zucchini (cooked)",
        "Green Beans (cooked)", "Carrot (cooked)", "Bell Pepper (red, cooked)"
    ]
    base_carbs = [
        "Sweet Potato (cooked)", "Brown Rice (cooked)",
        "Oats (cooked)", "Quinoa (cooked)"
    ]
    base_treats = [
        "Blueberries (small portions)", "Apple (peeled, no seeds)", "Strawberries (small portions)"
    ]

    meats.extend(base_meats)
    vegs.extend(base_vegs)
    carbs.extend(base_carbs)
    treats.extend(base_treats)

    # stage adjustments
    if stage == "Puppy":
        meats.extend(["Chicken (lean, cooked)", "Beef (lean, cooked)"])
        carbs.extend(["White Rice (cooked)"])
        vegs.extend(["Pumpkin (cooked)"])
    elif stage == "Senior":
        meats.extend(["White Fish (cod, cooked)", "Salmon (cooked)"])
        vegs.extend(["Pumpkin (cooked)", "Zucchini (cooked)"])

    # special flag adjustments
    if "Sensitive stomach" in special_flags:
        meats.extend(["Turkey (lean, cooked)", "White Fish (cod, cooked)"])
        vegs.extend(["Pumpkin (cooked)"])
        carbs.extend(["White Rice (cooked)", "Oats (cooked)"])

    if "Skin/coat concern" in special_flags:
        meats.extend(["Salmon (cooked)", "Sardines (cooked, deboned)"])
        treats.extend(["Blueberries (small portions)"])

    if "Overweight / Weight loss goal" in special_flags:
        meats.extend(["Turkey (lean, cooked)", "White Fish (cod, cooked)", "Rabbit (cooked)"])
        vegs.extend(["Green Beans (cooked)", "Zucchini (cooked)", "Cauliflower (cooked)"])
        carbs = [c for c in carbs if c not in ["Potato (cooked, plain)"]]

    if "Pancreatitis risk / Needs lower fat" in special_flags:
        meats = [m for m in meats if m not in ["Salmon (cooked)", "Duck (lean, cooked)", "Sardines (cooked, deboned)"]]
        meats.extend(["Turkey (lean, cooked)", "White Fish (cod, cooked)"])

    # dedupe while preserving order
    def dedupe(lst):
        seen = set()
        out = []
        for x in lst:
            if x in INGREDIENTS and x not in seen:
                out.append(x)
                seen.add(x)
        return out

    return {
        "Meat": dedupe(meats),
        "Veg": dedupe(vegs),
        "Carb": dedupe(carbs),
        "Treat": dedupe(treats),
    }


# =========================
# Smarter rotation engine
# =========================

def pick_rotation_smart(
    pantry_meats: List[str],
    pantry_vegs: List[str],
    pantry_carbs: List[str],
    allow_new: bool,
    recommendations: Dict[str, List[str]],
    days: int = 7,
    seed: Optional[int] = None
) -> List[Dict[str, str]]:
    rng = random.Random(seed if seed is not None else 42)

    all_meats = filter_ingredients_by_category("Meat")
    all_vegs = filter_ingredients_by_category("Veg")
    all_carbs = filter_ingredients_by_category("Carb")

    # Build pools
    if allow_new:
        meat_pool = list(dict.fromkeys(pantry_meats + recommendations.get("Meat", []) + all_meats))
        veg_pool = list(dict.fromkeys(pantry_vegs + recommendations.get("Veg", []) + all_vegs))
        carb_pool = list(dict.fromkeys(pantry_carbs + recommendations.get("Carb", []) + all_carbs))
    else:
        meat_pool = pantry_meats if pantry_meats else all_meats
        veg_pool = pantry_vegs if pantry_vegs else all_vegs
        carb_pool = pantry_carbs if pantry_carbs else all_carbs

    def choose(pool: List[str], last: Optional[str], last2: Optional[str]) -> str:
        if not pool:
            return rng.choice(all_meats)
        # avoid repeating same item 3 times in a row
        candidates = pool
        if last and last2 and last == last2:
            candidates = [x for x in pool if x != last] or pool
        # also reduce immediate repetition if possible
        if last and len(candidates) > 1:
            non_last = [x for x in candidates if x != last]
            if non_last:
                candidates = non_last
        return rng.choice(candidates)

    plan = []
    last_meat = last_meat2 = None
    last_veg = last_veg2 = None

    for _ in range(days):
        meat = choose(meat_pool, last_meat, last_meat2)
        veg = choose(veg_pool, last_veg, last_veg2) if veg_pool else rng.choice(all_vegs)
        carb = rng.choice(carb_pool) if carb_pool else rng.choice(all_carbs)

        plan.append({"Meat": meat, "Veg": veg, "Carb": carb})

        last_meat2, last_meat = last_meat, meat
        last_veg2, last_veg = last_veg, veg

    return plan


# =========================
# Ingredient image helper
# =========================

def ingredient_image_url(ingredient_name: str) -> str:
    """
    Lightweight external image source.
    Uses Unsplash "featured" search.
    Safe fallback even if blocked (image just won't load).
    """
    q = ingredient_name.split("(")[0].strip()
    q = q.replace("/", " ")
    # make it more food-like
    q = f"{q} food"
    return f"https://source.unsplash.com/featured/600x400/?{q}"


# =========================
# Session State
# =========================

if "taste_log" not in st.session_state:
    st.session_state.taste_log = []


# =========================
# Sidebar - Dog Profile
# =========================

st.sidebar.markdown(f"## 🐶🍳 {APP_TITLE}")
st.sidebar.caption("Cosmic-grade cooked fresh meal intelligence")

dog_name = st.sidebar.text_input("Dog name", value="", placeholder="e.g., Luna, Mochi, Nova")

breed = st.sidebar.selectbox("Breed", BREED_LIST, index=BREED_LIST.index("Mixed Breed / Unknown"))

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

meals_per_day = st.sidebar.select_slider(
    "Meals per day",
    options=[1, 2, 3, 4],
    value=2
)

assumed_kcal_per_g = st.sidebar.slider(
    "Assumed energy density (kcal per gram of cooked mix)",
    min_value=1.0, max_value=1.8, value=1.35, step=0.05,
    help="Cooked fresh mixes vary widely. This converts calories into approximate daily grams."
)

st.sidebar.markdown("---")
st.sidebar.caption("Educational tool; not a substitute for veterinary nutrition advice.")


# =========================
# Top Banner
# =========================

name_phrase = f"for {dog_name}" if dog_name.strip() else "for your dog"

st.markdown(
    f"""
    <div class="nebula-card">
      <h1>🐶🍲 {APP_TITLE}</h1>
      <p style="font-size: 1.05rem; opacity: 0.9;">
        {APP_SUBTITLE} <span class="badge">Cooked Fresh Focus</span>
      </p>
      <div class="nebula-divider"></div>
      <p style="opacity: 0.9;">
        A high-end, rotation-based cooked fresh planner {name_phrase}. 
        Build weekly menus, explore ingredient benefits, and shape a kinder, smarter routine.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# Tabs
# =========================

tab_home, tab_ingredients, tab_ratio, tab_planner, tab_supp, tab_feedback = st.tabs(
    [
        "🐶🍳 Command Deck",
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

    title_name = dog_name.strip() or "Your dog"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Name", title_name)
    c2.metric("Life stage", stage)
    c3.metric("RER (kcal/day)", f"{rer:.0f}")
    c4.metric("Target MER (adjusted)", f"{mer_adj:.0f}")

    st.caption(f"Breed size class: {size_class} · Meals/day: {meals_per_day}")
    st.caption(f"Context note: {explanation}")

    st.markdown("### What this app can reveal")
    show_system_map = st.toggle("Show Nebula System Map", value=True)
    if show_system_map:
        st.markdown(
            """
            <div class="nebula-card">
              <h4>🧭 Your navigation paths</h4>
              <ul>
                <li><b>Ingredient Cosmos</b> — deep benefits/cautions plus a dynamic photo wall.</li>
                <li><b>Ratio Lab</b> — compare presets and estimate daily grams.</li>
                <li><b>7-Day Intelligent Plan</b> — pantry-aware rotation + smart suggestions.</li>
                <li><b>Supplement Observatory</b> — conservative educational pairing logic.</li>
                <li><b>Taste & Notes</b> — learn what your dog loves and refine future plans.</li>
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
            - Medical conditions require a vet or veterinary nutritionist plan.
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
        cat_filter = st.selectbox("Category filter", ["All", "Meat", "Veg", "Carb", "Oil", "Treat"])
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

    st.dataframe(df_view, use_container_width=True, height=330)

    # ---- NEW: Photo wall replacing Visual Nutrition Lens ----
    st.markdown("### Ingredient Photo Wall")
    st.caption("Theme-friendly visual cues. If your deployment blocks external images, this section may appear blank.")

    show_photos = st.toggle("Show ingredient photos", value=True)
    if show_photos:
        # limit for performance
        preview_list = df_view["Ingredient"].tolist()[:12] if not df_view.empty else []
        if not preview_list:
            st.info("No ingredients match your filter.")
        else:
            cols = st.columns(4)
            for idx, ing_name in enumerate(preview_list):
                with cols[idx % 4]:
                    st.image(ingredient_image_url(ing_name), caption=ing_name, use_container_width=True)

    st.markdown("### Deep-dive cards")
    selected_ing = st.selectbox("Pick an ingredient to explore", df["Ingredient"].tolist())
    ing_obj = INGREDIENTS[selected_ing]

    cimg, cinfo = st.columns([1, 1.6])
    with cimg:
        st.image(ingredient_image_url(ing_obj.name), use_container_width=True)
    with cinfo:
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

    stage = age_to_life_stage(age_years)
    rer, mer, mer_adj, explanation = compute_daily_energy(
        weight_kg=weight_kg, age_years=age_years, activity=activity,
        neutered=neutered, special_flags=special_flags
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
    cat_means = ingredient_df().groupby("Category")[["kcal/100g", "Protein(g)", "Fat(g)", "Carbs(g)"]].mean()

    def est_cat_kcal(cat: str, grams: float) -> float:
        if cat not in cat_means.index:
            return 0.0
        return float(cat_means.loc[cat, "kcal/100g"]) * grams / 100.0

    ratio_kcal_df = pd.DataFrame([
        {"Component": "Meat (avg)", "kcal": est_cat_kcal("Meat", meat_g)},
        {"Component": "Veg (avg)", "kcal": est_cat_kcal("Veg", veg_g)},
        {"Component": "Carb (avg)", "kcal": est_cat_kcal("Carb", carb_g)},
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


# =========================
# 4) 7-Day Intelligent Plan
# =========================

with tab_planner:
    st.markdown("### Pantry-driven weekly generation")

    all_meats = filter_ingredients_by_category("Meat")
    all_vegs = filter_ingredients_by_category("Veg")
    all_carbs = filter_ingredients_by_category("Carb")
    all_treats = filter_ingredients_by_category("Treat")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        pantry_meats = st.multiselect("Meats you have", all_meats, default=[])
    with col_p2:
        pantry_vegs = st.multiselect("Vegetables you have", all_vegs, default=[])
    with col_p3:
        pantry_carbs = st.multiselect("Carbs you have", all_carbs, default=[])

    st.markdown("### Human-friendly planning style")

    col_mode1, col_mode2, col_mode3 = st.columns([1.1, 1.1, 1.6])
    with col_mode1:
        pantry_only = st.toggle("Pantry-only mode", value=False,
                                help="If ON, the plan strictly uses what you selected above (fallback to all if empty).")
    with col_mode2:
        allow_new = st.toggle("Smart rotation mode", value=True,
                              help="If ON, the plan may suggest and include new ingredients to prevent boredom.")
    with col_mode3:
        include_fruit_toppers = st.toggle("Allow fruit toppers (small)", value=True,
                                          help="Adds optional small fruit suggestions (Treat category).")

    stage = age_to_life_stage(age_years)
    recs = recommend_ingredients(stage, special_flags)

    st.markdown("### What we recommend adding (personalized)")
    rr1, rr2, rr3, rr4 = st.columns(4)
    with rr1:
        st.write("**Proteins**")
        st.write("\n".join([f"• {x}" for x in recs["Meat"][:8]]) if recs["Meat"] else "—")
    with rr2:
        st.write("**Vegetables**")
        st.write("\n".join([f"• {x}" for x in recs["Veg"][:8]]) if recs["Veg"] else "—")
    with rr3:
        st.write("**Carbs**")
        st.write("\n".join([f"• {x}" for x in recs["Carb"][:8]]) if recs["Carb"] else "—")
    with rr4:
        st.write("**Fruits (optional small)**")
        if include_fruit_toppers and recs["Treat"]:
            st.write("\n".join([f"• {x}" for x in recs["Treat"][:6]]))
        else:
            st.write("—")

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
        weight_kg=weight_kg, age_years=age_years, activity=activity,
        neutered=neutered, special_flags=special_flags
    )
    daily_grams = estimate_food_grams_from_energy(mer_adj, assumed_kcal_per_g)
    meat_g, veg_g, carb_g = grams_for_day(daily_grams, meat_pct, veg_pct, carb_pct)

    st.caption(
        f"Daily targets (assumption-based): "
        f"{daily_grams:.0f}g total → Meat {meat_g:.0f}g · Veg {veg_g:.0f}g · Carb {carb_g:.0f}g"
    )
    st.caption(f"Meals/day: {meals_per_day} → per-meal split will be shown in the plan.")

    seed = st.slider("Rotation randomness seed", 1, 999, 42,
                     help="Change this to reshuffle the weekly rotation.")
    generate = st.button("✨ Generate 7-Day Nebula Plan")

    # Determine whether new ingredients are allowed
    effective_allow_new = (allow_new and not pantry_only)

    if generate:
        rotation = pick_rotation_smart(
            pantry_meats=pantry_meats,
            pantry_vegs=pantry_vegs,
            pantry_carbs=pantry_carbs,
            allow_new=effective_allow_new,
            recommendations=recs,
            days=7,
            seed=seed
        )

        # optional fruit rotation suggestions (not part of macro grams)
        fruit_rotation = []
        if include_fruit_toppers and recs["Treat"]:
            rng = random.Random(seed + 7)
            for _ in range(7):
                fruit_rotation.append(rng.choice(recs["Treat"]))
        else:
            fruit_rotation = [None] * 7

        rows = []
        per_meal_total = daily_grams / meals_per_day
        per_meal_meat = meat_g / meals_per_day
        per_meal_veg = veg_g / meals_per_day
        per_meal_carb = carb_g / meals_per_day

        for i, combo in enumerate(rotation, start=1):
            mg, vg, cg = grams_for_day(daily_grams, meat_pct, veg_pct, carb_pct)
            nut = day_nutrition_estimate(combo["Meat"], combo["Veg"], combo["Carb"], mg, vg, cg)

            rows.append({
                "Day": f"Day {i}",
                "Meat": combo["Meat"],
                "Veg": combo["Veg"],
                "Carb": combo["Carb"],
                "Optional Fruit Topper": fruit_rotation[i-1] or "—",
                "Daily Meat (g)": round(mg),
                "Daily Veg (g)": round(vg),
                "Daily Carb (g)": round(cg),
                "Per-Meal Total (g)": round(per_meal_total),
                "Per-Meal Meat (g)": round(per_meal_meat),
                "Per-Meal Veg (g)": round(per_meal_veg),
                "Per-Meal Carb (g)": round(per_meal_carb),
                "Est kcal": round(nut["kcal"]),
                "Protein (g)": round(nut["protein"], 1),
                "Fat (g)": round(nut["fat"], 1),
                "Carbs (g)": round(nut["carbs"], 1),
            })

        plan_df = pd.DataFrame(rows)

        st.markdown(f"### {title_name}'s weekly plan")
        st.dataframe(plan_df, use_container_width=True, height=360)

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

        st.markdown("### Variety explainers")
        with st.expander("How this plan reduces boredom"):
            st.write(
                """
                - The rotation engine avoids repeating the same meat or vegetable too many days in a row.
                - When Smart rotation mode is ON, the planner can blend:
                  your pantry + recommended additions + the broader ingredient library.
                - This creates a more natural, human-like weekly rhythm.
                """
            )

        with st.expander("Cooking & serving protocol"):
            st.write(
                """
                - Cook proteins plainly; remove skin and visible fat if needed.
                - Steam/boil veggies; chop finely for small breeds.
                - Cook carbs thoroughly.
                - Mix, cool, portion.
                - For long-term fully home-cooked feeding,
                  consider **canine multivitamin + calcium strategy + omega-3** under professional guidance.
                """
            )


# =========================
# 5) Supplement Observatory
# =========================

with tab_supp:
    st.markdown("### Conservative supplement pairing guide")

    st.markdown(
        """
        Supplements can help fill gaps in simplified cooked diets,
        but the best strategy depends on your dog's health.
        This section provides **non-prescriptive** educational guidance.
        """
    )

    supp_df = pd.DataFrame(SUPPLEMENTS)
    st.dataframe(
        supp_df[["name", "why", "cautions", "pairing"]],
        use_container_width=True,
        height=280
    )

    st.markdown("### Personalized supplement lens")
    focus = st.multiselect(
        "What do you want to prioritize?",
        ["Skin/Coat", "Gut", "Joint/Mobility", "Puppy Growth Support",
         "Senior Vitality", "Weight Management", "Dental Support"],
        default=[]
    )

    def add_if(lst, item):
        if item not in lst:
            lst.append(item)

    suggestions = []
    if "Skin/Coat" in focus:
        add_if(suggestions, "Omega-3 (Fish Oil)")
        add_if(suggestions, "Vitamin E (as guided)")
    if "Gut" in focus:
        add_if(suggestions, "Probiotics")
        add_if(suggestions, "Prebiotic Fiber (e.g., inulin, MOS)")
    if "Joint/Mobility" in focus:
        add_if(suggestions, "Joint Support (Glucosamine/Chondroitin/UC-II)")
        add_if(suggestions, "Omega-3 (Fish Oil)")
    if "Puppy Growth Support" in focus:
        add_if(suggestions, "Calcium Support (for home-cooked)")
        add_if(suggestions, "Canine Multivitamin")
    if "Senior Vitality" in focus:
        add_if(suggestions, "Omega-3 (Fish Oil)")
        add_if(suggestions, "Joint Support (Glucosamine/Chondroitin/UC-II)")
        add_if(suggestions, "Probiotics")
    if "Weight Management" in focus:
        add_if(suggestions, "Probiotics")
        add_if(suggestions, "L-Carnitine (vet-guided)")
    if "Dental Support" in focus:
        add_if(suggestions, "Dental Additives (vet-approved)")

    if suggestions:
        st.markdown(
            f"""
            <div class="nebula-card">
              <h4>Suggested educational focus</h4>
              <ul>
                {''.join([f'<li>{s}</li>' for s in suggestions])}
              </ul>
              <div class="nebula-divider"></div>
              <p class="small-muted">
                For dosing and long-term protocols, confirm with a veterinarian,
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
    title_name = dog_name.strip() or "Your dog"
    st.markdown(f"### Taste tracking capsule for {title_name}")

    st.write(
        """
        Record how your dog responds to different proteins and vegetables.
        This log stays in your session and helps you refine future plan iterations.
        """
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        log_meat = st.selectbox("Observed protein", ["(skip)"] + filter_ingredients_by_category("Meat"))
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
            "Dog Name": dog_name.strip() or None,
            "Breed": breed,
            "Age (y)": round(age_years, 2),
            "Weight (kg)": round(weight_kg, 2),
            "Protein": None if log_meat == "(skip)" else log_meat,
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

        def pref_score(p: str) -> int:
            return {"Dislike": 0, "Neutral": 1, "Like": 2, "Love": 3}.get(p, 1)

        protein_records = log_df.dropna(subset=["Protein"]).copy()
        veg_records = log_df.dropna(subset=["Veg"]).copy()

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            if not protein_records.empty:
                protein_records["Score"] = protein_records["Preference"].map(pref_score)
                rank = protein_records.groupby("Protein")["Score"].mean().sort_values(ascending=False).reset_index()
                rank.columns = ["Protein", "Avg Preference Score"]

                bar = (
                    alt.Chart(rank)
                    .mark_bar()
                    .encode(
                        x=alt.X("Avg Preference Score:Q", scale=alt.Scale(domain=[0, 3])),
                        y=alt.Y("Protein:N", sort="-x"),
                        tooltip=["Protein", alt.Tooltip("Avg Preference Score:Q", format=".2f")]
                    )
                    .properties(height=240, title="Protein preference (session)")
                )
                st.altair_chart(bar, use_container_width=True)
            else:
                st.caption("No protein preference entries yet.")

        with col_s2:
            if not veg_records.empty:
                veg_records["Score"] = veg_records["Preference"].map(pref_score)
                rank = veg_records.groupby("Veg")["Score"].mean().sort_values(ascending=False).reset_index()
                rank.columns = ["Vegetable", "Avg Preference Score"]

                bar = (
                    alt.Chart(rank)
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
                - If a protein is consistently disliked, remove it from pantry selection.
                - If a vegetable correlates with softer stool, reduce its share or rotate less often.
                - If you suspect allergies, consider a vet-guided elimination approach.
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
    "For long-term complete nutrition—especially for puppies or medical cases—"
    "consult a veterinarian or a board-certified veterinary nutritionist."
)
