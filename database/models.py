from datetime import datetime
from database.db import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    food_records = db.relationship('FoodRecord', back_populates='user', cascade='all, delete-orphan')
    health_records = db.relationship('HealthRecord', back_populates='user', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='user', cascade='all, delete-orphan')
    water_records = db.relationship('WaterRecord', back_populates='user', cascade='all, delete-orphan')
    sleep_records = db.relationship('SleepRecord', back_populates='user', cascade='all, delete-orphan')
    medications = db.relationship('Medication', back_populates='user', cascade='all, delete-orphan')
    medication_logs = db.relationship('MedicationLog', back_populates='user', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    report_shares = db.relationship('ReportShare', back_populates='user', cascade='all, delete-orphan')


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    birth_year = db.Column(db.Integer)  # Added birth year
    gender = db.Column(db.String(20))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    activity_level = db.Column(db.String(30), default='moderate')
    theme_preference = db.Column(db.String(20), default='light')
    bmi_onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)  # Added BMI onboarding state
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='profile')


class Nutrition(db.Model):
    __tablename__ = 'nutrition'
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    serving_size_g = db.Column(db.Float, default=100.0, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fibre = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FoodRecord(db.Model):
    __tablename__ = 'food_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nutrition_id = db.Column(db.Integer, db.ForeignKey('nutrition.id'))
    food_name = db.Column(db.String(120), nullable=False)
    meal_name = db.Column(db.String(80), default='Meal')
    serving_amount_g = db.Column(db.Float, default=100.0, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fibre = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    consumed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='food_records')
    nutrition = db.relationship('Nutrition')


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    bmi = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    blood_sugar = db.Column(db.String(20))
    cholesterol = db.Column(db.String(20))
    heart_rate = db.Column(db.String(20))
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='health_records')


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(80), nullable=False)
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Float, default=0)
    date = db.Column(db.Date, default=datetime.utcnow().date())
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='activities')


class WaterRecord(db.Model):
    __tablename__ = 'water_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount_ml = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='water_records')


class SleepRecord(db.Model):
    __tablename__ = 'sleep_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sleep_time = db.Column(db.DateTime, nullable=False)
    wake_time = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Float, default=0)
    date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='sleep_records')


class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='medications')
    logs = db.relationship('MedicationLog', back_populates='medication', cascade='all, delete-orphan')


class MedicationLog(db.Model):
    __tablename__ = 'medication_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    taken_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='medication_logs')
    medication = db.relationship('Medication', back_populates='logs')


class Reminder(db.Model):
    __tablename__ = 'reminders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reminder_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text)
    scheduled_for = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reminders')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')


class ReportShare(db.Model):
    __tablename__ = 'report_shares'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    report_type = db.Column(db.String(50), default='health_report')
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='report_shares')
