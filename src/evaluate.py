import numpy as np

class ModelEvaluator:
    """Utility class for calculating regression metrics."""
    
    @staticmethod
    def calculate_rmse(y_true, y_pred):
        """Calculates Root Mean Squared Error."""
        return np.sqrt(np.mean((y_true - y_pred) ** 2))
        
    @staticmethod
    def calculate_mae(y_true, y_pred):
        """Calculates Mean Absolute Error."""
        return np.mean(np.abs(y_true - y_pred))
        
    @staticmethod
    def print_report(y_true, y_pred, model_name="Model"):
        """Generates a clean terminal report."""
        rmse = ModelEvaluator.calculate_rmse(y_true, y_pred)
        mae = ModelEvaluator.calculate_mae(y_true, y_pred)
        
        print(f"--- {model_name} Evaluation ---")
        print(f"RMSE: {rmse:.4f} (Lower is better)")
        print(f"MAE:  {mae:.4f} (Average miss in Home Runs)")
        print("-" * 30)