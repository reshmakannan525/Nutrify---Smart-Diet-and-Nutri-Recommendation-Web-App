<div align="center">

# 🥗 Nutrify

**Smart Diet & Nutrition Recommendation Platform**

A machine-learning powered web app that recommends recipes based on your nutritional goals, identifies food from photos using AI, and helps you track your daily nutrition — built with Streamlit, FastAPI, and Scikit-learn.

<img src="Assets/logo_img1.jpg" width="500"/>

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Dataset](#-dataset)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📌 About

Eating well is hard when nutrition advice is generic and disconnected from what's actually in your kitchen. **Nutrify** solves this with a content-based recommendation engine that suggests recipes matched to your exact nutritional targets and available ingredients — plus an AI vision model that can identify a meal from a photo and pull up its nutrition facts instantly.

The goal: make personalized, data-driven nutrition guidance something anyone can use in seconds, not something that requires a nutritionist.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | Simple, secure login gating access to the app |
| 💪 **Diet Recommendation** | Get a personalized diet plan from your age, weight, height, and goals |
| 🔍 **Custom Food Recommendation** | Set nutritional targets and preferred ingredients to get matching recipes, ranked by similarity |
| 📸 **AI Image Food Tracking** | Upload a food photo — a fine-tuned vision model identifies the dish and fetches its nutrition profile automatically |
| 🥗 **Daily Nutrition Tracker** | Log meals throughout the day and monitor intake against your targets |

---

## 🧰 Tech Stack

**Frontend**
- Streamlit — multi-page interactive UI

**Backend**
- FastAPI — REST API serving recommendations
- Uvicorn — ASGI server

**Machine Learning / AI**
- Scikit-learn — Nearest Neighbors content-based recommender (cosine similarity)
- Hugging Face Transformers — image classification pipeline for food detection

**Data**
- Pandas / NumPy

**Infrastructure**
- Docker & Docker Compose — containerized multi-service deployment

---

## 🏗 Architecture

<div align="center">
<img src="Assets/Architecture_diagram.png" width="600"/>
</div>

The recommendation engine is powered by a **Nearest Neighbors** model using brute-force search with cosine similarity:

$$\cos(\theta) = \frac{A \cdot B}{\|A\| \, \|B\|}$$

This content-based approach means recommendations are generated purely from recipe/nutrition attributes — no other users' data is needed, there's no cold-start problem, and results stay transparent and explainable.

The Image Food Tracking feature runs a food-specific image classification model, matches the predicted label against the nutrition dataset (with fuzzy matching to handle naming differences), and falls back to manual selection when there's no confident match.

---

## 📂 Project Structure

```
Nutrify/
├── Streamlit_Frontend/
│   ├── Hello.py                    # Login / entry point
│   ├── auth.py                     # Authentication logic
│   ├── Generate_Recommendations.py
│   ├── ImageFinder/
│   ├── pages/
│   │   ├── Home.py
│   │   ├── 1_💪_Diet_Recommendation.py
│   │   ├── 2_🔍_Custom_Food_Recommendation.py
│   │   ├── 3_📸_Image_Food_Tracking.py
│   │   └── 4_🥗_Daily_Nutrition_Tracker.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── FastAPI_Backend/
│   ├── main.py
│   ├── model.py
│   ├── nutrition.py
│   ├── db.py
│   ├── config.py
│   ├── image_finder.py
│   └── Dockerfile
│
├── Data/
│   └── Indian_Food_Nutrition_Processed.csv
│
├── Assets/
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose (recommended), **or**
- Python 3.10+ if running services individually


### Option A — Run with Docker (recommended)
```bash
docker-compose up -d --build
```
App will be available at **http://localhost:8501**

### Option B — Run locally without Docker

**Frontend**
```bash
cd Streamlit_Frontend
pip install -r requirements.txt
streamlit run Hello.py
```

**Backend**
```bash
cd FastAPI_Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🖥 Usage

1. Log in through the entry page.
2. Choose a page from the sidebar:
   - **Diet Recommendation** for a full personalized plan
   - **Custom Food Recommendation** to set your own nutrition targets/ingredients
   - **Image Food Tracking** to snap or upload a photo and get instant nutrition info
   - **Daily Nutrition Tracker** to log meals and monitor your intake
3. Browse and explore recommended recipes with full nutrition breakdowns and instructions.

---

## 📊 Dataset

- Recipe recommendations are trained on the [Food.com Recipes & Reviews dataset](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews) (500K+ recipes, 1.4M+ reviews).
- Image-based food detection is matched against a processed Indian food nutrition dataset in `Data/`.

> **Note:** Large raw data files are excluded from version control. Place your dataset copy in `Data/` before running the app.

---

## 🗺 Roadmap

- [ ] Expand AI food detection to more cuisines
- [ ] Add user-specific saved recipes / favorites
- [ ] Weekly/monthly nutrition analytics dashboard
- [ ] Mobile-friendly UI improvements

---

## 🤝 Contributing

Contributions are welcome. Please open an issue to discuss what you'd like to change before submitting a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a PR

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
