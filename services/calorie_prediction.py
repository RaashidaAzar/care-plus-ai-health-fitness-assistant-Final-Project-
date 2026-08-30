import os
from pathlib import Path
import numpy as np
import joblib
from config import Config

# Module-level model cache
_CALORIE_MODEL = None


def _get_calorie_model():
    global _CALORIE_MODEL
    if _CALORIE_MODEL is not None:
        return _CALORIE_MODEL

    model_path = Config.MODEL_CALORIE_PATH
    if not model_path.exists():
        return None

    try:
        _CALORIE_MODEL = joblib.load(str(model_path))
        return _CALORIE_MODEL
    except Exception as e:
        print(f"Error loading calorie burn model: {e}")
        return None


def predict_calorie_burn(payload):
    """
    Predicts calorie burn using the trained scikit-learn RandomForest pipeline model.
    Expected payload fields:
      - gender: 'male' or 'female'
      - age: float (years)
      - height: float (cm)
      - weight: float (kg)
      - duration_minutes: float (minutes)
      - heart_rate: float (bpm)
      - body_temp: float (Celsius, e.g., 37.0-40.0)
    """
    try:
        gender = str(payload.get('gender', 'male')).lower().strip()
        if gender not in ['male', 'female']:
            gender = 'male'

        age = float(payload.get('age', 40.0) or 40.0)
        height = float(payload.get('height', 170.0) or 170.0)
        weight = float(payload.get('weight', 70.0) or 70.0)
        duration = float(payload.get('duration_minutes', 30.0) or 30.0)
        heart_rate = float(payload.get('heart_rate', 110.0) or 110.0)
        body_temp = float(payload.get('body_temp', 38.5) or 38.5)
        activity_type = str(payload.get('activity_type', 'General Exercise')).strip()

        model = _get_calorie_model()

        if model is not None:
            try:
                # Extract preprocessor and model steps directly for numpy execution
                ct = model.named_steps['preprocessor']
                ohe = ct.named_transformers_['gender']
                rf = model.named_steps['model']

                X_gender = np.array([[gender]], dtype=object)
                g_encoded = ohe.transform(X_gender).toarray()

                X_num = np.array([[age, height, weight, duration, heart_rate, body_temp]], dtype=np.float64)
                X_combined = np.hstack([g_encoded, X_num])

                prediction = rf.predict(X_combined)
                estimate = float(prediction[0])
                return {
                    'estimate': round(max(0.0, estimate), 2),
                    'error': None,
                    'inputs': {
                        'gender': gender,
                        'age': age,
                        'height': height,
                        'weight': weight,
                        'duration_minutes': duration,
                        'heart_rate': heart_rate,
                        'body_temp': body_temp,
                        'activity_type': activity_type
                    }
                }
            except Exception as inner_e:
                print(f"Direct pipeline inference fallback: {inner_e}")

        # Physics-based fallback formula if model is missing or fails
        activity_factors = {
            'Walking': 1.0,
            'Light Stretching': 0.65,
            'Yoga': 0.75,
            'House Chores': 0.9,
            'Sitting Work Break Movement': 0.55,
        }
        activity_factor = activity_factors.get(activity_type, 1.0)
        fallback_estimate = max(0.0, ((duration * weight * 0.071) + (heart_rate * 0.5) + (age * 0.2)) * activity_factor)
        return {
            'estimate': round(fallback_estimate, 2),
            'error': None,
            'is_fallback': True,
            'inputs': {
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'duration_minutes': duration,
                'heart_rate': heart_rate,
                'body_temp': body_temp,
                'activity_type': activity_type
            }
        }
    except Exception as e:
        print(f"Error in calorie burn prediction service: {e}")
        return {'estimate': None, 'error': 'Unable to calculate calorie burn estimate. Please check your inputs.'}
