# ⚽ **ScoreSight: EPL Match Prediction System**

**ScoreSight** is your matchday intelligence hub. It predicts EPL match outcomes, analyzes team strength, and lets you ask football questions through an **AI-powered chatbot** — all in real time.

---

## 🔥 **Features at a Glance**
- 🧠 **Pre-Match Predictions** — 75.7% accuracy using an ensemble ML model  
- ⏱️ **Half-Time Live Predictions** — 68.1% accuracy with real-time stats  
- 📊 **Team Analytics Dashboard** — form, head-to-head, trends, strength score  
- 🤖 **AI Football Chatbot** — ask anything, get football-specific insights  
- 🔐 **JWT Authentication** — secure account and session management  

---

## 🧱 **Tech Stack**
| Layer | Tools Used |
|------|------------|
| Backend | FastAPI, Python, Scikit-learn, XGBoost, Pandas, NumPy |
| Frontend | React + TypeScript |
| Authentication | JWT + Secure Password Hashing |
| Data Source | Football-Data.org API + EPL Historical Dataset (2010–2020) |

---

## 🚀 **Setup Instructions**

### **Backend Setup**
    git clone <repository-url>
    cd scoresight/backend
    pip install -r requirements.txt
    cp .env.example .env     # Add API keys in .env
    uvicorn main:app --reload --port 8000

### **Frontend Setup**
    cd ../frontend
    npm install
    npm start

---

## 📂 **Project Structure**
    scoresight/
    ├── backend/
    │   ├── main.py               # FastAPI server
    │   ├── auth.py               # JWT login / refresh
    │   ├── chatbot_service.py    # AI chatbot logic
    │   └── ml-models/            # Trained ML models
    └── frontend/
        └── src/
            ├── components/       # UI components
            ├── pages/            # Route-based screens
            └── services/         # API request handlers

---

## 🎯 **API Usage Examples**

**Match Prediction (Pre-match)**  
    GET /api/predict?home_team=Man City&away_team=Liverpool

**Half-Time Live Prediction**
    POST /api/half-time-predict
    {
      "shots_on_target": 4,
      "possession_home": 61,
      "possession_away": 39
    }

**Team Analysis**
    GET /api/teams/Arsenal/analysis

---

## 📈 **Model Performance**
| Model | Accuracy | Description |
|------|----------|-------------|
| Pre-Match Ensemble | **75.7%** | Random Forest + XGBoost + Logistic Regression |
| Half-Time Live Model | **68.1%** | Real-time stats prediction engine |

---

**ScoreSight** — where football meets data, and the numbers tell the story. ⚽📊
