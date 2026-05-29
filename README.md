# ⚾ MLB Rest-of-Season (ROS) Home Run Predictor

![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![XGBoost](https://img.shields.io/badge/XGBoost-127900?style=for-the-badge&logo=xgboost&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

An end-to-end machine learning application that generates live home run projections for the current MLB season. It uses an XGBoost model, real-time Statcast physics data (Max Exit Velocity, Hard Hit Rate, xwOBA), and multi-year Bayesian shrinkage to calculate stabilized Rest-of-Season forecasts.

## Local Installation & Setup

The project is decoupled into a Python backend and a React frontend. You will need two terminal windows to run the application.

### Start the FastAPI Backend and Next.js Frontend
```bash
git clone https://github.com/ManvilB/MLB-ROS-Predictor.git
cd mlb-ros-predictor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload

cd frontend
npm install
npm run dev
```