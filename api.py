from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from src.data_loader import DataLoader
from src.models import XGBoostPoissonRegressor

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting API: Loading Multi-Year Statcast Feature Matrix...")
    start_date = "2026-03-26" 
    current_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_of_season = "2026-09-27"
    
    loader = DataLoader(start_dt=start_date, end_dt=current_date)
    df = loader.get_clean_hitter_matrix(min_batted_balls=50)
    
    # Define the expanded multi-year feature space
    feature_cols = [
        'xwOBA', 'avg_exit_velocity', 'max_exit_velocity', 'avg_launch_angle', 'hard_hit_rate',
        'xwOBA_2025', 'hr_2025', 'xwOBA_2024', 'hr_2024'
    ]
    
    X = df[feature_cols].values
    y = df['home_runs'].values
    
    print("Training Multi-Year XGBoost Poisson Engine...")
    model = XGBoostPoissonRegressor()
    model.fit(X, y)
    
    # --- Pacing Calculus ---
    days_played = (datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
    total_season_days = (datetime.strptime(end_of_season, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
    days_remaining = total_season_days - days_played
    
    ros_multiplier = days_remaining / days_played
    season_remaining_pct = days_remaining / total_season_days
    
    # 1. Get the raw machine learning projection
    raw_base_projection = model.predict(X) 
    raw_projected_ros_hrs = raw_base_projection * ros_multiplier
    
    # 2. Establish a conservative baseline (Last year's HRs scaled to the rest of this season)
    baseline_ros_hrs = df['hr_2025'] * season_remaining_pct
    
    # 3. Calculate Reliability via the Stabilization Constant
    # 100 batted balls is the general stabilization point for MLB power metrics
    stabilization_constant = 100
    reliability_weight = df['total_batted_balls'] / (df['total_batted_balls'] + stabilization_constant)
    
    # 4. Blend the raw projection with the safe baseline based on reliability
    df['projected_ros_hrs'] = (reliability_weight * raw_projected_ros_hrs) + ((1 - reliability_weight) * baseline_ros_hrs)
    
    # Final Total
    df['projected_total_hrs'] = df['home_runs'] + df['projected_ros_hrs']
    
    app_state['projections'] = df.sort_values('projected_total_hrs', ascending=False).to_dict(orient="records")
    print("Engine Ready! Serving multi-year stabilized predictions.")
    yield 
    app_state.clear()


app = FastAPI(title="MLB Rest of Season Projections", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/projections")
def get_projections(limit: int = 400):
    return {"data": app_state['projections'][:limit]}