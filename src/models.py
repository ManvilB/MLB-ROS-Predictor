import numpy as np
import xgboost as xgb

class XGBoostPoissonRegressor:
    """
    Industry-standard XGBoost model optimized for count data.
    Automatically handles non-linear interactions (e.g., Exit Velo + Launch Angle).
    """
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=5):
        self.model = xgb.XGBRegressor(
            objective='count:poisson',
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=42 # Set a seed for reproducible results
        )
        
    def fit(self, X, y):
        self.model.fit(X, y)
        return self
        
    def predict(self, X):
        return self.model.predict(X)

class CustomPoissonRegressor:
    """
    A custom implementation of Poisson Regression using Newton's Method.
    Optimized for predicting discrete count data (e.g., Home Runs).
    """
    def __init__(self, max_iter=100, tolerance=1e-5):
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.theta = None
        
    def fit(self, X, y):
        # Add an intercept term (column of 1s)
        m, n = X.shape
        X_b = np.c_[np.ones((m, 1)), X]
        
        # Initialize weights
        self.theta = np.zeros(X_b.shape[1])
        
        for i in range(self.max_iter):
            lambda_pred = np.exp(X_b.dot(self.theta))
            
            # Newton's Method Calculus: Gradient and Hessian
            gradient = X_b.T.dot(y - lambda_pred)
            W = np.diag(lambda_pred)
            hessian = -X_b.T.dot(W).dot(X_b)
            
            # Weight Update
            try:
                theta_new = self.theta - np.linalg.inv(hessian).dot(gradient)
            except np.linalg.LinAlgError:
                raise ValueError("Singular matrix encountered. Optimization failed.")
                
            # Convergence check
            if np.linalg.norm(theta_new - self.theta) < self.tolerance:
                self.theta = theta_new
                return self
                
            self.theta = theta_new
            
        return self
        
    def predict(self, X):
        if self.theta is None:
            raise RuntimeError("Model must be fitted before calling predict.")
            
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        return np.exp(X_b.dot(self.theta))
