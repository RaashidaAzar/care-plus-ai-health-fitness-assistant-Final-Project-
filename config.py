import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "instance" / "care_plus.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MODEL_FOOD_PATH = BASE_DIR / 'models' / 'food' / 'food66_efficientnetb0_final_finetuned.keras'
    MODEL_CALORIE_PATH = BASE_DIR / 'models' / 'calorie' / 'calorie_burn_prediction_model.pkl'
    APP_NAME = 'Care Plus'
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '').rstrip('/')
    APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'Asia/Colombo')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    @staticmethod
    def ensure_dirs():
        (BASE_DIR / 'instance').mkdir(exist_ok=True)
        (BASE_DIR / 'static' / 'uploads').mkdir(exist_ok=True)
        (BASE_DIR / 'reports').mkdir(exist_ok=True)

Config.ensure_dirs()
