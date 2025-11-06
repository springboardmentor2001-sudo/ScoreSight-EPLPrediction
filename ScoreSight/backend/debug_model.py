import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def debug_model():
    """Debug what features the model expects"""
    try:
        # Load the CatBoost model
        model_path = os.path.join(MODELS_DIR, 'catboost_points_model_20251022_080502.pkl')
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print("=" * 60)
        print("MODEL DEBUG INFORMATION")
        print("=" * 60)
        
        # Get feature names from the model
        if hasattr(model, 'feature_names_'):
            print(f"Model feature names: {model.feature_names_}")
            print(f"Number of features: {len(model.feature_names_)}")
        
        # Try other common attribute names
        if hasattr(model, 'get_feature_names'):
            print(f"Feature names (get_feature_names): {model.get_feature_names()}")
        
        # For CatBoost specifically
        if hasattr(model, 'feature_names'):
            print(f"Feature names (feature_names): {model.feature_names}")
        
        # Check model type and attributes
        print(f"Model type: {type(model)}")
        print(f"Model attributes: {dir(model)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_model()