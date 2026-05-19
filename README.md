# 🥗 AI-Powered Nutrition Planner

An intelligent Streamlit web application that generates **personalised 7-day meal plans** using Groq's Llama 3.3 LLM and identifies food items from photos using Google's Vision Transformer (ViT).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🍽️ Meal Planner** | Generate a complete 7-day meal plan tailored to your body metrics, dietary preferences, fitness goals, and restrictions |
| **📸 Food Analyser** | Upload a food photo and get instant identification with confidence scores using a Vision Transformer model |
| **📊 Nutritional Breakdown** | Every meal includes calories, protein, carbs, and fat — plus a weekly summary |
| **🎯 BMR Calculation** | Uses the Harris-Benedict equation to calculate your Basal Metabolic Rate and daily calorie target |
| **🔄 Regeneration** | Provide feedback and regenerate plans to fine-tune your meal plan |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com/keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/AI-powered-Nutrition-Planner.git
   cd Nutrition-Planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## 📁 Project Structure

```
AI-powered-Nutrition-Planner/
├── .env.example            # Environment variable template
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── app.py                  # Main entry point & navigation
├── pages/
│   ├── home.py             # Home / welcome page
│   ├── meal_planner.py     # Meal planner with Groq integration
│   └── food_analyzer.py    # Food image analyser with ViT
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — UI framework
- **[Groq](https://groq.com/)** — LLM API (Llama 3.3 70B Versatile)
- **[HuggingFace Transformers](https://huggingface.co/)** — Vision Transformer (ViT)
- **[Pillow](https://python-pillow.org/)** — Image processing
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Environment variable management

---

## 📋 Usage

### Meal Planner
1. Navigate to the **Meal Planner** page from the sidebar
2. Fill in your profile: age, gender, weight, height, activity level, goal, and dietary preferences
3. Click **Generate Meal Plan**
4. Browse your 7-day plan across daily tabs
5. Review the weekly nutritional summary
6. Optionally add feedback and regenerate for a refined plan

### Food Analyser
1. Navigate to the **Food Analyser** page
2. Upload a clear photo of a food item
3. View the identified food name and confidence score
4. Check the top-5 predictions for alternative matches

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
