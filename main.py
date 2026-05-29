import pandas as pd
import numpy as np
from src.data_loader import DataLoader
from src.models import CustomPoissonRegressor
from src.evaluate import ModelEvaluator

def run_pipeline():
    print("--- Starting MLB Rest of Season Projection Pipeline ---\n")
    
    # 1. Load Data (Expanded to two months: April & May)
    # Note: This API call will take a few minutes longer because of the larger date range
    loader = DataLoader(start_dt="2024-03-28", end_dt="2024-05-31")
    
    # 2. Require at least 50 batted balls to filter out the noise
    df = loader.get_clean_hitter_matrix(min_batted_balls=50)
    
    # 2. Shuffle and Split Data (80% Train, 20% Test)
    # Using a fixed random state so our results are reproducible
    train_df = df.sample(frac=0.8, random_state=42)
    test_df = df.drop(train_df.index)
    
    X_train = train_df[['xwOBA']].values
    y_train = train_df['home_runs'].values
    
    X_test = test_df[['xwOBA']].values
    y_test = test_df['home_runs'].values
    
    # 3. Train the Custom GLM
    print("\nTraining Custom Poisson Model via Newton's Method...")
    model = CustomPoissonRegressor()
    model.fit(X_train, y_train)
    
    # 4. Generate Predictions on UNSEEN test data
    y_pred = model.predict(X_test)
    
    # 5. Generate Naive Baseline Predictions (Guessing the mean of the training set)
    naive_guess = np.mean(y_train)
    y_naive_pred = np.full(shape=y_test.shape, fill_value=naive_guess)
    
    # 6. Evaluate and Compare!
    print("\n")
    ModelEvaluator.print_report(y_test, y_pred, model_name="Custom Poisson GLM")
    ModelEvaluator.print_report(y_test, y_naive_pred, model_name="Naive Baseline (Average)")

if __name__ == "__main__":
    run_pipeline()