import streamlit as st
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch

# ═══════════════════════════════════════════════════════════════════
#  CLIP zero-shot food classifier — identifies 200+ foods including
#  international cuisines, and can detect multiple items per image.
# ═══════════════════════════════════════════════════════════════════

MODEL_ID = "openai/clip-vit-base-patch32"

FOOD_LABELS = [
    # South Asian
    "biryani", "chicken biryani", "naan bread", "dal lentils", "samosa",
    "tandoori chicken", "butter chicken", "chicken tikka masala",
    "paratha", "roti", "paneer", "palak paneer", "gulab jamun",
    "jalebi", "pakora", "dosa", "idli", "pav bhaji", "chole bhature",
    "korma", "nihari", "haleem", "seekh kebab", "chicken karahi",
    "chapli kebab", "pulao rice", "raita", "chutney", "kulfi",
    # Middle Eastern
    "hummus", "falafel", "shawarma", "kebab", "baklava", "pita bread",
    # East Asian
    "sushi", "ramen", "fried rice", "dumplings", "pad thai",
    "spring rolls", "pho", "bibimbap", "tempura", "udon noodles",
    "miso soup", "tofu", "gyoza", "takoyaki", "bao buns",
    "kung pao chicken", "chow mein", "peking duck", "sashimi",
    "dim sum", "egg fried rice", "wonton soup",
    # Western
    "hamburger", "cheeseburger", "pizza", "pasta", "steak",
    "french fries", "hot dog", "sandwich", "club sandwich",
    "caesar salad", "greek salad", "bread", "cake", "pie",
    "donut", "waffle", "pancake", "omelette", "scrambled eggs",
    "bacon", "sausage", "fish and chips", "lasagna", "risotto",
    "mac and cheese", "fried chicken", "grilled chicken",
    "roast chicken", "mashed potatoes", "onion rings",
    "chicken wings", "chicken nuggets", "garlic bread",
    "croissant", "bagel", "pretzel", "spaghetti",
    "ravioli", "pork chop", "ribs", "meatloaf", "soup", "stew",
    # Mexican
    "tacos", "burrito", "nachos", "quesadilla", "guacamole",
    "churros", "enchiladas", "empanadas",
    # Fruits
    "apple", "banana", "orange", "mango", "strawberry", "grapes",
    "watermelon", "pineapple", "peach", "pear", "kiwi",
    "pomegranate", "papaya", "blueberries", "cherries", "avocado",
    # Vegetables
    "broccoli", "carrot", "tomato", "potato", "corn", "cucumber",
    "mushroom", "bell pepper", "eggplant", "cauliflower", "cabbage",
    "spinach", "sweet potato",
    # Desserts
    "ice cream", "chocolate cake", "cheesecake", "tiramisu",
    "creme brulee", "brownie", "macaron", "cupcake", "pudding",
    "apple pie", "cinnamon roll", "red velvet cake", "cookies",
    "frozen yogurt", "fruit tart",
    # Seafood
    "grilled salmon", "shrimp", "lobster", "crab", "calamari",
    "fish fillet", "mussels",
    # Drinks
    "coffee", "tea", "juice", "smoothie", "milkshake",
    # Breakfast / Snacks
    "cereal", "oatmeal", "french toast", "toast", "eggs benedict",
    "popcorn", "chips", "cheese", "yogurt", "nuts",
]

MULTI_DETECT_THRESHOLD = 0.04  # 4% — show as "also detected"


@st.cache_resource(show_spinner="🔄 Loading Food Recognition model…")
def load_model():
    """Load CLIP and pre-compute text embeddings for all food labels."""
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    model = CLIPModel.from_pretrained(MODEL_ID)
    model.eval()

    prompts = [f"a photo of {f}" for f in FOOD_LABELS]
    text_inputs = processor(
        text=prompts, return_tensors="pt", padding=True, truncation=True
    )
    with torch.no_grad():
        text_features = model.get_text_features(**text_inputs)
    # Some transformer/transformers versions return a BaseModelOutputWithPooling
    # object instead of a raw tensor. Handle both cases by extracting the
    # pooled/text embedding tensor if necessary.
    if not isinstance(text_features, torch.Tensor):
        if hasattr(text_features, "pooler_output") and text_features.pooler_output is not None:
            text_features = text_features.pooler_output
        elif hasattr(text_features, "last_hidden_state") and text_features.last_hidden_state is not None:
            # fallback: mean pool the last hidden state
            text_features = text_features.last_hidden_state.mean(dim=1)
        else:
            raise RuntimeError("Unexpected return type from model.get_text_features()")

    text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return processor, model, text_features


def classify_image(image, processor, model, text_features):
    """Run CLIP inference and return sorted (label, confidence) list."""
    img_inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        img_features = model.get_image_features(pixel_values=img_inputs["pixel_values"])
    if not isinstance(img_features, torch.Tensor):
        if hasattr(img_features, "pooler_output") and img_features.pooler_output is not None:
            img_features = img_features.pooler_output
        elif hasattr(img_features, "last_hidden_state") and img_features.last_hidden_state is not None:
            img_features = img_features.last_hidden_state.mean(dim=1)
        else:
            raise RuntimeError("Unexpected return type from model.get_image_features()")

    img_features = img_features / img_features.norm(dim=-1, keepdim=True)

    scale = model.logit_scale.exp()
    similarity = (scale * img_features @ text_features.T).squeeze(0)
    probs = similarity.softmax(dim=0)

    top_probs, top_idx = torch.topk(probs, min(10, len(FOOD_LABELS)))
    return [(FOOD_LABELS[i.item()], p.item()) for p, i in zip(top_probs, top_idx)]


def fmt(label: str) -> str:
    return label.strip().replace("_", " ").title()


# ═══════════════════════════════════════════════════════════════════
#  PAGE UI
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="hero-banner">
        <h1>📸 Food Analyser</h1>
        <p>Upload a food photo and let AI identify it instantly</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "This tool uses **CLIP (zero-shot vision-language model)** to identify "
    "**200+ foods** across international cuisines — including South Asian, "
    "Middle Eastern, East Asian, and Western dishes. It can also detect "
    "**multiple food items** in a single photo."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload a food image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: JPG, JPEG, PNG, WEBP",
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    col_img, col_result = st.columns([1, 1], gap="large")

    with col_img:
        st.markdown('<p class="section-header">🖼️ Uploaded Image</p>', unsafe_allow_html=True)
        st.image(image, use_container_width=True)

    with col_result:
        st.markdown('<p class="section-header">🔍 Analysis Results</p>', unsafe_allow_html=True)

        with st.spinner("Analysing image…"):
            processor, model, text_features = load_model()
            results = classify_image(image, processor, model, text_features)

        # Primary prediction
        top_label, top_conf = results[0]
        st.markdown(
            f"""
            <div class="glass-card" style="text-align:center; padding:2rem;">
                <h3 style="font-size:1.6rem; margin-bottom:0.4rem;">{fmt(top_label)}</h3>
                <p style="font-size:1.1rem; color:#A78BFA;">
                    Confidence: <b>{top_conf:.1%}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Multiple items detected
        also_detected = [
            (l, c) for l, c in results[1:] if c >= MULTI_DETECT_THRESHOLD
        ]
        if also_detected:
            st.write("")
            st.markdown("**🍽️ Also Detected in Image**")
            for label, conf in also_detected:
                st.progress(conf, text=f"{fmt(label)} — {conf:.1%}")

        st.write("")
        st.markdown("**Top 5 Predictions**")
        for label, conf in results[:5]:
            st.progress(conf, text=f"{fmt(label)} — {conf:.1%}")

    st.divider()
    st.info(
        "💡 **Tip:** For best results, use a clear, well-lit photo. "
        "The model can identify **200+ foods** across many cuisines and "
        "detect multiple items in one image.",
        icon="📌",
    )
else:
    st.markdown(
        """
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <h3 style="font-size:1.4rem;">📤 Upload a Food Photo</h3>
            <p>
                Drag and drop or click the uploader above to get started.<br>
                The AI will identify the food and show you a confidence score.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="app-footer">Powered by OpenAI CLIP &middot; Zero-Shot Food Recognition</div>',
    unsafe_allow_html=True,
)
