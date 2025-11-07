# ⚽ ScoreSight: EPL Match Prediction System

**ScoreSight** is an English Premier League (EPL) match prediction platform that combines machine learning with real-time football analytics. It provides match outcome predictions, team performance insights, and conversational analysis through an AI-powered chatbot.

---

## 🔥 Key Highlights
- **Pre-Match Predictions** (75.7% accuracy) using ensemble ML models  
- **Half-Time Live Predictions** (68.1% accuracy) using real-time match stats  
- **Team Analytics**: form, head-to-head history, strengths & trends  
- **AI Chatbot**: ask match questions in natural language  
- **Secure Authentication** using JWT tokens  

---

## 🏗️ Tech Stack
| Component | Technologies |
|---------|--------------|
| Backend | FastAPI, Python, Scikit-learn, XGBoost, Pandas, NumPy |
| Frontend | React + TypeScript |
| Auth | JWT + secure password hashing |
| Data | Historical EPL Seasons (2010-2020), Football-Data.org API |

---

## 🚀 Quick Setup

### 1) Backend
```bash
git clone <repository-url>
cd scoresight/backend
pip install -r requirements.txt
cp .env.example .env   # Add your API keys here
uvicorn main:app --reload --port 8000

2) Frontend
cd ../frontend
npm install
npm start

📂 Project Structure
scoresight/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── auth.py           # User login & JWT
│   ├── chatbot_service.py # AI match assistant
│   └── ml-models/         # Trained ML models
└── frontend/
    └── src/
        ├── components/
        ├── pages/
        └── services/     # API calls

🎯 Example Usage

Match Prediction
GET /api/predict?home_team=Man City&away_team=Liverpool

Half-Time Prediction
POST /api/half-time-predict
{
  "shots_on_target": 4,
  "possession_home": 61,
  "possession_away": 39,
  ...
}

Team Analytics
GET /api/teams/Arsenal/analysis

📈 Model Overview
Model	Accuracy	Description
Pre-Match Ensemble	75.7%	Random Forest + XGBoost + Logistic Regression
Half-Time Model	68.1%	Real-time match feature analysis
