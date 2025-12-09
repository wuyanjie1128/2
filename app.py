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
# Ingredient Knowledge Base (expanded)
# Approximate cooked values.
# =========================

def build_ingredients() -> Dict[str, Ingredient]:
    items = [
        # --- Meats / Proteins ---
        Ingredient("Chicken (lean, cooked)", "Meat", 165, 31, 3.6, 0,
                   "B vitamins, selenium.",
                   ["High-quality protein for muscle maintenance",
                    "Generally well tolerated",
                    "Good base protein for rotation diets"],
                   ["Avoid if chicken allergy suspected",
                    "Remove skin to reduce fat if pancreatitis risk"]),

        Ingredient("Turkey (lean, cooked)", "Meat", 150, 29, 2.0, 0,
                   "Niacin, selenium.",
                   ["Lean protein option", "Useful for weight-aware plans", "Mild flavor for picky dogs"],
                   ["Avoid processed/deli products"]),

        Ingredient("Beef (lean, cooked)", "Meat", 200, 26, 10, 0,
                   "Iron, zinc, B12.",
                   ["Supports red blood cell health", "Rich in iron and zinc", "Great for active adult dogs"],
                   ["Higher fat depending on cut", "Avoid if beef allergy suspected"]),

        Ingredient("Lamb (lean, cooked)", "Meat", 206, 25, 12, 0,
                   "Zinc, carnitine.",
                   ["Alternative protein for rotation", "High palatability", "Useful if poultry sensitivity"],
                   ["Can be richer; adjust for pancreatitis risk"]),

        Ingredient("Pork (lean, cooked)", "Meat", 195, 27, 9, 0,
                   "Thiamine-rich protein.",
                   ["Good rotation option", "Often highly palatable", "Supports energy metabolism"],
                   ["Use lean cuts; avoid processed pork"]),

        Ingredient("Duck (lean, cooked)", "Meat", 190, 24, 11, 0,
                   "Rich flavor, B vitamins.",
                   ["Great for rotation", "Useful for dogs bored of poultry", "High palatability"],
                   ["Moderate fat; manage for pancreatitis risk"]),

        Ingredient("Venison (lean, cooked)", "Meat", 158, 30, 3.2, 0,
                   "Often considered novel protein.",
                   ["Good for rotation", "Potential option for some allergy plans", "Lean and nutrient-dense"],
                   ["Novel protein strategies should be vet-guided"]),

        Ingredient("Rabbit (cooked)", "Meat", 173, 33, 3.5, 0,
                   "Very lean, novel option.",
                   ["Lean protein", "Rotation diversity", "Often well tolerated"],
                   ["Ensure sourcing and thorough cooking"]),

        Ingredient("Sardines (cooked, deboned)", "Meat", 208, 25, 11, 0,
                   "Omega-3, calcium (if bones removed, less).",
                   ["Skin/coat support", "High palatability", "Good micro-fatty acids"],
                   ["Watch sodium if canned; choose no-salt when possible"]),

        Ingredient("Egg (cooked)", "Meat", 155, 13, 11, 1.1,
                   "Complete amino acid profile.",
                   ["Excellent protein quality", "Palatability booster", "Good for rotation variety"],
                   ["Introduce gradually for sensitive stomachs"]),

        Ingredient("Salmon (cooked)", "Meat", 208, 20, 13, 0,
                   "Omega-3, vitamin D.",
                   ["Supports skin/coat health", "Anti-inflammatory fatty acids", "Great for senior/joint-focused plans"],
                   ["Higher fat; portion carefully", "Remove bones; cook thoroughly"]),

        Ingredient("White Fish (cod, cooked)", "Meat", 105, 23, 0.9, 0,
                   "Very lean protein.",
                   ["Great for weight management", "Gentle for sensitive stomach", "Clean taste"],
                   ["Ensure plain cooking"]),

        # --- Vegetables ---
        Ingredient("Pumpkin (cooked)", "Veg", 26, 1, 0.1, 6.5,
                   "Beta-carotene, soluble fiber.",
                   ["Supports stool quality", "Gentle fiber for GI health", "Helpful in transition periods"],
                   ["Too much can reduce calorie density"]),

        Ingredient("Carrot (cooked)", "Veg", 35, 0.8, 0.2, 8,
                   "Beta-carotene.",
                   ["Antioxidant support", "Low calorie nutrient boost", "Good texture variety"],
                   ["Chop/soften for small dogs"]),

        Ingredient("Broccoli (cooked)", "Veg", 34, 2.8, 0.4, 7,
                   "Vitamin C, K.",
                   ["Antioxidant-rich", "Good rotation vegetable", "Adds micronutrient diversity"],
                   ["Large amounts may cause gas"]),

        Ingredient("Zucchini (cooked)", "Veg", 17, 1.2, 0.3, 3.1,
                   "Hydration-friendly veggie.",
                   ["Very low calorie", "Great for volumizing meals", "Mild taste for picky dogs"],
                   ["Avoid seasoning"]),

        Ingredient("Green Beans (cooked)", "Veg", 31, 1.8, 0.1, 7,
                   "Fiber and low-calorie bulk.",
                   ["Helpful for weight management", "Gentle fiber", "Good texture variety"],
                   []),

        Ingredient("Sweet Peas (cooked)", "Veg", 84, 5.4, 0.4, 15.6,
                   "Plant protein + fiber.",
                   ["Adds variety", "Good for active dogs in small portions"],
                   ["Moderate starch; control for weight plans"]),

        Ingredient("Cauliflower (cooked)", "Veg", 25, 1.9, 0.3, 5,
                   "Low-cal cruciferous veggie.",
                   ["Adds volume", "Rotation-friendly micronutrients"],
                   ["May cause gas in some dogs"]),

        Ingredient("Cabbage (cooked, small portions)", "Veg", 23, 1.3, 0.1, 5.5,
                   "Fiber, vitamin C.",
                   ["Budget-friendly fiber", "Adds variety"],
                   ["May cause gas; start small"]),

        Ingredient("Kale (cooked, small portions)", "Veg", 35, 2.9, 1.5, 4.4,
                   "Dense micronutrient profile.",
                   ["Adds antioxidant variety", "Good in small rotation amounts"],
                   ["Use small portions; some dogs are sensitive"]),

        Ingredient("Cucumber (peeled, small portions)", "Veg", 15, 0.7, 0.1, 3.6,
                   "Hydrating low-cal veggie.",
                   ["Cooling treat-like veggie", "Weight-friendly"],
                   ["Chop small for tiny breeds"]),

        Ingredient("Bell Pepper (red, cooked)", "Veg", 31, 1, 0.3, 6,
                   "Vitamin-rich color veggie.",
                   ["Antioxidant variety", "Palatability and color diversity"],
                   ["Avoid spicy varieties/seasoning"]),

        Ingredient("Mushroom (common edible, cooked)", "Veg", 22, 3.1, 0.3, 3.3,
                   "Umami micro-boost.",
                   ["Adds flavor complexity", "Small rotation option"],
                   ["Only dog-safe edible types; avoid wild mushrooms"]),

        Ingredient("Spinach (cooked, small portions)", "Veg", 23, 2.9, 0.4, 3.6,
                   "Folate, magnesium.",
                   ["Adds micronutrient variety", "Antioxidant support"],
                   ["Use small portions due to oxalates"]),

        # --- Carbs ---
        Ingredient("Sweet Potato (cooked)", "Carb", 86, 1.6, 0.1, 20,
                   "Beta-carotene, potassium.",
                   ["Energy source with micronutrients", "Highly palatable", "Good controlled carb"],
                   ["Portion for weight control"]),

        Ingredient("Brown Rice (cooked)", "Carb", 123, 2.7, 1.0, 25.6,
                   "Gentle starch base.",
                   ["Easy-to-digest base", "Neutral flavor", "Good transition carb"],
                   ["Lower carb for diabetic/overweight plans"]),

        Ingredient("White Rice (cooked)", "Carb", 130, 2.4, 0.3, 28.2,
                   "Very gentle GI carb.",
                   ["Helpful for sensitive stomach phases", "Very bland and digestible"],
                   ["Lower micronutrients than brown rice"]),

        Ingredient("Oats (cooked)", "Carb", 71, 2.5, 1.4, 12,
                   "Soluble fiber (beta-glucans).",
                   ["Supports satiety", "Gentle energy source", "Useful for gut-friendly plans"],
                   ["Introduce slowly for sensitive stomachs"]),

        Ingredient("Quinoa (cooked)", "Carb", 120, 4.4, 1.9, 21.3,
                   "Higher protein for a carb.",
                   ["Good option for variety", "Amino acid diversity", "Often well tolerated"],
                   ["Rinse well before cooking"]),

        Ingredient("Barley (cooked)", "Carb", 123, 2.3, 0.4, 28,
                   "Fiber-rich grain.",
                   ["Satiety-friendly carb", "Good rotation starch"],
                   ["Introduce gradually"]),

        Ingredient("Buckwheat (cooked)", "Carb", 92, 3.4, 0.6, 19.9,
                   "Alternative pseudo-grain.",
                   ["Variety option", "Often gentle"],
                   ["Cook thoroughly"]),

        Ingredient("Potato (cooked, plain)", "Carb", 87, 2, 0.1, 20,
                   "Simple starch.",
                   ["Palatable, easy carb", "Useful in limited-ingredient plans"],
                   ["Never feed raw potato; avoid green parts"]),

        # --- Oils ---
        Ingredient("Fish Oil (supplemental)", "Oil", 900, 0, 100, 0,
                   "EPA/DHA omega-3s.",
                   ["Skin/coat support", "Anti-inflammatory support", "May benefit cognitive/joint support"],
                   ["Dose carefully; can loosen stool", "Check with vet if on blood thinners"]),

        Ingredient("Olive Oil (small amounts)", "Oil", 884, 0, 100, 0,
                   "Monounsaturated fats.",
                   ["Palatability booster", "Helps calorie density for thin dogs"],
                   ["Too much fat may trigger GI upset"]),

        Ingredient("MCT Oil (very small amounts)", "Oil", 900, 0, 100, 0,
                   "Medium-chain triglycerides.",
                   ["May help some senior cognition plans (vet-guided)"],
                   ["Can cause diarrhea; use cautiously"]),

        Ingredient("Flaxseed Oil (small amounts)", "Oil", 884, 0, 100, 0,
                   "ALA omega-3 (plant-based).",
                   ["Alternative fatty acid source", "Rotation fat option"],
                   ["ALA conversion to EPA/DHA is limited"]),

        # --- Treat-like Add-ons (optional category) ---
        Ingredient("Blueberries (lightly mashed)", "Treat", 57, 0.7, 0.3, 14.5,
                   "Antioxidant fruit option.",
                   ["Small antioxidant topper", "Palatability boost"],
                   ["Use small portions to avoid excess sugar"]),

        Ingredient("Apple (peeled, no seeds)", "Treat", 52, 0.3, 0.2, 14,
                   "Hydrating sweet crunch.",
                   ["Low-cal treat topper", "Adds variety"],
                   ["Remove seeds/core; use small portions"]),
    ]

    return {i.name: i for i in items}


INGREDIENTS = build_ingredients()


# =========================
# Expanded Breed List
# (Broad global coverage, includes many common + regional breeds)
# =========================

BREED_LIST = [
    # --- Toy ---
    "Affenpinscher", "Brussels Griffon", "Cavalier King Charles Spaniel",
    "Chihuahua", "Chinese Crested", "English Toy Spaniel", "Italian Greyhound",
    "Japanese Chin", "Maltese", "Miniature Pinscher", "Papillon",
    "Pekingese", "Pomeranian", "Pug", "Russian Toy", "Shih Tzu",
    "Toy Fox Terrier", "Toy Poodle", "Yorkshire Terrier",

    # --- Small ---
    "Bichon Frise", "Boston Terrier", "Cairn Terrier", "Cardigan Welsh Corgi",
    "Pembroke Welsh Corgi", "Cotton de Tulear", "Dachshund (Mini)",
    "Dachshund (Standard)", "Fox Terrier (Smooth)", "Fox Terrier (Wire)",
    "Havanese", "Jack Russell Terrier", "Lhasa Apso", "Miniature Schnauzer",
    "Norfolk Terrier", "Norwich Terrier", "Parson Russell Terrier",
    "Patterdale Terrier", "Scottish Terrier", "Sealyham Terrier",
    "Shetland Sheepdog", "West Highland White Terrier", "Whippet",

    # --- Medium ---
    "American Cocker Spaniel", "Australian Shepherd", "Basenji", "Beagle",
    "Border Collie", "Border Terrier", "Brittany",
    "Bulldog", "Bull Terrier", "Chinese Shar-Pei",
    "Cocker Spaniel (English)", "Dalmatian", "Finnish Spitz",
    "French Bulldog", "Icelandic Sheepdog", "Keeshond",
    "Korean Jindo", "Lagotto Romagnolo", "Miniature American Shepherd",
    "Samoyed (medium-large)", "Shiba Inu", "Shikoku",
    "Schnauzer (Standard)", "Soft Coated Wheaten Terrier",
    "Staffordshire Bull Terrier", "Vizsla",

    # --- Large ---
    "Airedale Terrier", "Akita", "Alaskan Malamute",
    "American Bulldog", "Australian Cattle Dog",
    "Belgian Malinois", "Belgian Tervuren", "Belgian Sheepdog",
    "Bernese Mountain Dog", "Bloodhound", "Boxer",
    "Cane Corso", "Chesapeake Bay Retriever",
    "Collie (Rough)", "Collie (Smooth)",
    "Doberman", "Dutch Shepherd",
    "English Springer Spaniel", "Field Spaniel",
    "German Shepherd", "German Shorthaired Pointer",
    "Golden Retriever", "Gordon Setter", "Greyhound",
    "Irish Setter", "Irish Water Spaniel",
    "Labrador Retriever", "Nova Scotia Duck Tolling Retriever",
    "Old English Sheepdog", "Pointer",
    "Rottweiler", "Rhodesian Ridgeback",
    "Siberian Husky", "Standard Poodle", "Weimaraner",

    # --- Giant ---
    "Anatolian Shepherd", "Boerboel", "Borzoi",
    "Bullmastiff", "Dogue de Bordeaux",
    "Great Dane", "Great Pyrenees",
    "Irish Wolfhound", "Komondor", "Kuvasz",
    "Leonberger", "Mastiff", "Neapolitan Mastiff",
    "Newfoundland", "Saint Bernard", "Tibetan Mastiff",

    # --- Sighthounds & Primitive types ---
    "Afghan Hound", "Azawakh", "Basenji (primitive)",
    "Ibizan Hound", "Pharaoh Hound", "Saluki", "Sloughi",

    # --- Spitz & Northern ---
    "American Eskimo Dog", "Eurasier", "Finnish Lapphund",
    "Karelian Bear Dog", "Norwegian Elkhound",
    "Norwegian Buhund", "Norrbottenspets",
    "Swedish Vallhund", "Yakutian Laika",

    # --- Asian & regional ---
    "Chow Chow", "Chinese Chongqing Dog",
    "Thai Ridgeback", "Taiwan Dog",
    "Kishu Ken", "Kai Ken", "Hokkaido",
    "Tosa", "Tibetan Spaniel", "Tibetan Terrier",

    # --- Water & hunting ---
    "Barbet", "Curly-Coated Retriever", "Flat-Coated Retriever",
    "Irish Terrier", "Portuguese Water Dog",
    "Spinone Italiano", "Wirehaired Pointing Griffon",
    "German Wirehaired Pointer",

    # --- Herding (additional) ---
    "Australian Kelpie", "Bearded Collie",
    "Briard", "Catahoula Leopard Dog",
    "Entlebucher Mountain Dog",
    "Greater Swiss Mountain Dog",
    "Pyrenean Shepherd",

    # --- Terriers (additional) ---
    "American Staffordshire Terrier",
    "Bedlington Terrier", "Dandie Dinmont Terrier",
    "Kerry Blue Terrier", "Lakeland Terrier",
    "Manchester Terrier", "Mini Bull Terrier",
    "Rat Terrier",

    # --- Rare / emerging global recognition ---
    "Caucasian Shepherd Dog", "Central Asian Shepherd Dog",
    "Czechoslovakian Wolfdog", "Saarloos Wolfdog",
    "Xoloitzcuintli", "Peruvian Inca Orchid",

    # --- Catch-all ---
    "Mixed Breed / Unknown",
]

# Rough size map (expanded but intentionally coarse)
BREED_SIZE_MAP = {b: "Unknown" for b in BREED_LIST}
for b in [
    "Chihuahua", "Pomeranian", "Yorkshire Terrier", "Maltese", "Toy Poodle",
    "Shih Tzu", "Papillon", "Japanese Chin", "Pekingese", "Russian Toy",
    "Affenpinscher", "Brussels Griffon", "Chinese Crested", "Pug",
    "Miniature Pinscher", "Toy Fox Terrier", "Italian Greyhound",
    "English Toy Spaniel", "Cavalier King Charles Spaniel"
]:
    BREED_SIZE_MAP[b] = "Toy/Small"

for b in [
    "Bichon Frise", "Boston Terrier", "Cairn Terrier",
    "Dachshund (Mini)", "Dachshund (Standard)",
    "Jack Russell Terrier", "Lhasa Apso", "Miniature Schnauzer",
    "Norfolk Terrier", "Norwich Terrier",
    "West Highland White Terrier", "Scottish Terrier", "Whippet",
    "Pembroke Welsh Corgi", "Cardigan Welsh Corgi",
    "Havanese", "Coton de Tulear"
]:
    BREED_SIZE_MAP[b] = "Toy/Small"

for b in [
    "Beagle", "French Bulldog", "Bulldog",
    "Border Collie", "Australian Shepherd",
    "Shiba Inu", "Korean Jindo", "Schnauzer (Standard)",
    "Staffordshire Bull Terrier", "Soft Coated Wheaten Terrier",
    "Vizsla", "Dalmatian", "Keeshond", "Brittany"
]:
    BREED_SIZE_MAP[b] = "Medium"

for b in [
    "Labrador Retriever", "Golden Retriever", "German Shepherd",
    "Siberian Husky", "Doberman", "Rottweiler",
    "Boxer", "Weimaraner", "Pointer", "Old English Sheepdog",
    "Chesapeake Bay Retriever", "Belgian Malinois",
    "Rhodesian Ridgeback", "Collie (Rough)", "Collie (Smooth)",
    "Standard Poodle"
]:
    BREED_SIZE_MAP[b] = "Large/Giant"

for b in [
    "Great Dane", "Mastiff", "Neapolitan Mastiff", "Saint Bernard",
    "Newfoundland", "Leonberger", "Great Pyrenees",
    "Bernese Mountain Dog", "Tibetan Mastiff",
    "Caucasian Shepherd Dog", "Central Asian Shepherd Dog",
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
                "A calmer profile leaning on easy proteins + soothing fiber veggies."),
]


# =========================
# Expanded Supplement Guidance
# =========================

SUPPLEMENTS = [
    {
        "name": "Omega-3 (Fish Oil)",
        "why": "Supports skin/coat, joint comfort, and inflammatory balance.",
        "best_for": ["Dry/itchy skin", "Senior dogs", "Joint support plans"],
        "cautions": "Dose carefully; may loosen stool. Check with vet if on medications affecting clotting.",
        "pairing": "Pairs well with lean proteins and antioxidant-rich vegetables."
    },
    {
        "name": "Probiotics",
        "why": "May improve gut resilience and stool stability.",
        "best_for": ["Sensitive stomach", "Diet transitions", "Stress-related GI changes"],
        "cautions": "Choose canine-specific or veterinary-formulated options.",
        "pairing": "Works nicely with pumpkin, oats, and gentle proteins."
    },
    {
        "name": "Prebiotic Fiber (e.g., inulin, MOS)",
        "why": "Feeds beneficial gut bacteria and may support stool quality.",
        "best_for": ["Soft stools", "Post-antibiotic recovery (vet guided)"],
        "cautions": "Too much can cause gas.",
        "pairing": "Combine with probiotics for a gentle synbiotic approach."
    },
    {
        "name": "Calcium Support (for home-cooked)",
        "why": "Home-cooked diets often need calcium balancing.",
        "best_for": ["Puppies", "Long-term cooked fresh routines"],
        "cautions": "Over/under supplementation can be risky—confirm with a vet nutritionist.",
        "pairing": "Essential when not using balanced commercial bases."
    },
    {
        "name": "Canine Multivitamin",
        "why": "Helps cover micronutrient gaps in simplified home recipes.",
        "best_for": ["Limited ingredient variety", "Long-term home cooking"],
        "cautions": "Avoid human multivitamins unless a vet approves.",
        "pairing": "Best used with rotation-based weekly menus."
    },
    {
        "name": "Joint Support (Glucosamine/Chondroitin/UC-II)",
        "why": "May support mobility and cartilage health.",
        "best_for": ["Large breeds", "Senior dogs", "Highly active dogs"],
        "cautions": "Effects vary and usually take time.",
        "pairing": "Pairs with omega-3 and weight control."
    },
    {
        "name": "Vitamin E (as guided)",
        "why": "Antioxidant support, often paired with higher fat/omega supplementation.",
        "best_for": ["Dogs receiving omega-3 long-term"],
        "cautions": "Avoid excessive dosing without guidance.",
        "pairing": "Consider when fish oil is used regularly."
    },
    {
        "name": "Zinc Support (vet-guided)",
        "why": "May support skin barrier and coat quality.",
        "best_for": ["Specific deficiency concerns", "Some dermatology plans"],
        "cautions": "Too much can be harmful; use only with professional guidance.",
        "pairing": "Works alongside balanced protein variety."
    },
    {
        "name": "Dental Additives (enzymatic or vet-approved)",
        "why": "Helps reduce plaque in dogs that resist brushing.",
        "best_for": ["Small breeds prone to dental issues"],
        "cautions": "Not a replacement for brushing.",
        "pairing": "Pairs with crunchy safe veggie textures when appropriate."
    },
    {
        "name": "L-Carnitine (vet-guided)",
        "why": "May assist certain weight management or cardiac support strategies.",
        "best_for": ["Vet-supervised weight plans"],
        "cautions": "Use under professional advice.",
        "pairing": "Best with lean proteins and higher vegetable ratios."
    },
    {
        "name": "Urinary Support (condition-specific)",
        "why": "Some dogs need tailored mineral/pH strategies.",
        "best_for": ["Vet-diagnosed urinary issues"],
        "cautions": "Dietary mineral balancing is medical—vet required.",
        "pairing": "Consider hydration-rich meal design."
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

    adj = 1.0
    rationale = []

    if "Overweight / Weight loss goal" in special_flags:
        adj *= 0.85
        rationale.append("Reduced target for weight loss.")
    if "Pancreatitis risk / Needs lower fat" in special_flags:
        adj *= 0.95
        rationale.append("Conservative energy target for fat-sensitive context.")
    if "Kidney concern (vet-managed)" in special_flags:
        adj *= 0.95
        rationale.append("Energy kept conservative; protein strategy must be vet-guided.")
    if "Very picky eater" in special_flags:
        rationale.append("Use palatability tactics (warm, rotate, gentle oils).")

    mer_adj = mer * adj
    explanation = stage
    if rationale:
        explanation += " | " + " ".join(rationale)

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
    last_meat = None
    for _ in range(days):
        meat_pool = pantry_meats if pantry_meats else all_meats
        veg_pool = pantry_vegs if pantry_vegs else all_vegs
        carb_pool = pantry_carbs if pantry_carbs else all_carbs

        meat = safe_choice(meat_pool, all_meats)
        if len(meat_pool) > 1 and meat == last_meat:
            meat = safe_choice([m for m in meat_pool if m != last_meat], all_meats)

        veg = safe_choice(veg_pool, all_vegs)
        carb = safe_choice(carb_pool, all_carbs)

        plan.append({"Meat": meat, "Veg": veg, "Carb": carb})
        last_meat = meat

    return plan


def grams_for_day(total_grams: float, meat_pct: int, veg_pct: int, carb_pct: int) -> Tuple[float, float, float]:
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
    st.session_state.taste_log = []


# =========================
# Sidebar - Dog Profile
# =========================

st.sidebar.markdown(f"## 🐶🍳 {APP_TITLE}")
st.sidebar.caption("Cosmic-grade cooked fresh meal intelligence")

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

st.markdown(
    f"""
    <div class="nebula-card">
      <h1>🐶🍲 {APP_TITLE}</h1>
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
# Optional imagery (tasteful)
# =========================

with st.expander("🖼️ Nebula Visual Mode (optional)", expanded=False):
    st.write("Lightweight decorative images to enhance theme. Safe to ignore if your deployment blocks external images.")
    show_images = st.toggle("Enable decorative images", value=False)
    if show_images:
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.image(
                "https://images.unsplash.com/photo-1517849845537-4d257902454a?q=80&w=1200&auto=format&fit=crop",
                caption="Companion energy"
            )
        with col_i2:
            st.image(
                "https://images.unsplash.com/photo-1542984335-6e7d2a1b5d6b?q=80&w=1200&auto=format&fit=crop",
                caption="Fresh prep vibes"
            )
        with col_i3:
            st.image(
                "https://images.unsplash.com/photo-1511689660979-10d2b1aada49?q=80&w=1200&auto=format&fit=crop",
                caption="Ingredient constellation"
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
                <li><b>Ingredient Cosmos</b> — filter meats/veg/carbs/oils/treats, see benefits and cautions.</li>
                <li><b>Ratio Lab</b> — visualize macro energy contributions and compare presets.</li>
                <li><b>7-Day Intelligent Plan</b> — generate a weekly menu from your pantry with gram targets.</li>
                <li><b>Supplement Observatory</b> — conservative pairing logic for cooked diets.</li>
                <li><b>Taste & Notes</b> — track preferences to refine your pantry choices.</li>
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

    with st.expander("Interpretation guide"):
        st.write(
            """
            - This is a **conceptual lens** based on category averages.
            - Real energy shifts with fat level, specific carb choices, and additions like oils.
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

        with st.expander("Why rotation matters"):
            st.write(
                """
                Rotation helps reduce over-reliance on one protein/plant,
                improves micronutrient diversity, and keeps meals interesting.
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
         "Senior Vitality", "Weight Management", "Dental Support", "Urinary Focus"],
        default=[]
    )

    def add_if(lst, item):
        if item not in lst:
            lst.append(item)

    suggestions = []
    if "Skin/Coat" in focus:
        add_if(suggestions, "Omega-3 (Fish Oil)")
        add_if(suggestions, "Vitamin E (as guided)")
        add_if(suggestions, "Zinc Support (vet-guided)")
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
        add_if(suggestions, "Dental Additives (enzymatic or vet-approved)")
    if "Urinary Focus" in focus:
        add_if(suggestions, "Urinary Support (condition-specific)")

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
                - If your dog consistently dislikes a protein, remove it from pantry selection.
                - If a vegetable correlates with softer stool, reduce its share or rotate less often.
                - For allergy suspicion, consider a vet-guided elimination approach.
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
