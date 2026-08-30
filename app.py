import os
os.environ.setdefault('KERAS_BACKEND', 'jax')

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import inspect, text

from config import Config
from database.db import db
from database.models import (
    User, Profile, HealthRecord, FoodRecord, Nutrition, Activity, WaterRecord,
    SleepRecord, Medication, MedicationLog, Reminder, Notification, ReportShare,
)
from services.bmi_service import calculate_bmi, get_bmi_category
from services.nutrition_service import lookup_nutrition
from services.food_recognition import food_model_status, predict_food_image
from services.calorie_prediction import predict_calorie_burn
from services.report_service import generate_pdf_report

DEFAULT_WELLNESS_REMINDERS = (
    ('walk', '10-minute walk', '09:00'),
    ('stretch', 'Light stretching', '11:00'),
    ('water', 'Drink water', '13:00'),
    ('move', 'Stand and move for 3 minutes', '15:00'),
    ('breathing', 'Relaxed breathing exercise', '20:00'),
)


def _age_from_birth_year(birth_year):
    today = _app_now().date()
    return today.year - birth_year


def _app_now():
    try:
        timezone = ZoneInfo(Config.APP_TIMEZONE)
    except Exception:
        timezone = ZoneInfo('UTC')
    return datetime.now(timezone).replace(tzinfo=None)


def _app_datetime(value):
    """Convert a UTC database timestamp to the configured display timezone."""
    if value is None:
        return None
    try:
        timezone = ZoneInfo(Config.APP_TIMEZONE)
    except Exception:
        timezone = ZoneInfo('UTC')
    # Existing database timestamps are stored as naive UTC values.
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo('UTC'))
    return value.astimezone(timezone)


def _ensure_profile_columns():
    inspector = inspect(db.engine)
    columns = {column['name'] for column in inspector.get_columns('profiles')}
    additions = []
    if 'birth_year' not in columns:
        additions.append('ALTER TABLE profiles ADD COLUMN birth_year INTEGER')
    if 'bmi_onboarding_completed' not in columns:
        additions.append('ALTER TABLE profiles ADD COLUMN bmi_onboarding_completed BOOLEAN NOT NULL DEFAULT 0')
    for statement in additions:
        db.session.execute(text(statement))
    if additions:
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @app.template_filter('app_time')
    def format_app_time(value, time_format='%Y-%m-%d %H:%M'):
        """Render database datetimes in Asia/Colombo (or APP_TIMEZONE)."""
        converted = _app_datetime(value)
        return converted.strftime(time_format) if converted else ''

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        _ensure_profile_columns()
        # Keep the active database's 100 g nutrition records aligned with the
        # food-recognition labels. This also repairs old generic placeholder
        # values that made every recognised food show the same nutrition.
        from seed_database import seed_nutrition
        seed_nutrition(app)

    food_model_status()

    # The application uses one consistent light visual system.
    @app.context_processor
    def inject_user_context():
        theme = 'light'
        user_profile = None
        medication_reminders = []
        wellness_reminders = []
        if current_user.is_authenticated:
            user_profile = current_user.profile
            theme = user_profile.theme_preference if user_profile and user_profile.theme_preference in {'light', 'dark'} else 'light'
            medication_reminders = [
                {'id': medication.id, 'name': medication.name, 'time': medication.time}
                for medication in current_user.medications
                if medication.is_active and medication.time
            ]
            saved_reminders = {
                reminder.reminder_type.split(':', 1)[1]: reminder
                for reminder in current_user.reminders
                if reminder.reminder_type.startswith('wellness:')
            }
            for reminder_id, default_name, default_time in DEFAULT_WELLNESS_REMINDERS:
                reminder = saved_reminders.get(reminder_id)
                if reminder and not reminder.is_active:
                    continue
                wellness_reminders.append({
                    'id': reminder_id,
                    'db_id': reminder.id if reminder else None,
                    'name': reminder.title if reminder else default_name,
                    'time': reminder.scheduled_for.strftime('%H:%M') if reminder and reminder.scheduled_for else default_time,
                })
            default_ids = {reminder_id for reminder_id, _, _ in DEFAULT_WELLNESS_REMINDERS}
            for reminder_id, reminder in saved_reminders.items():
                if reminder.is_active and reminder_id not in default_ids:
                    wellness_reminders.append({
                        'id': reminder_id,
                        'db_id': reminder.id,
                        'name': reminder.title,
                        'time': reminder.scheduled_for.strftime('%H:%M') if reminder.scheduled_for else '09:00',
                    })
        return dict(current_theme=theme, user_profile=user_profile, medication_reminders=medication_reminders, wellness_reminders=wellness_reminders, reminder_timezone=Config.APP_TIMEZONE)

    # 1. LANDING & AUTH
    @app.route('/')
    def landing():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('landing.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            gender = request.form.get('gender', 'male').strip().lower() or 'male'
            birth_year_value = request.form.get('birth_year', '').strip()
            try:
                birth_year = int(birth_year_value)
                age = _age_from_birth_year(birth_year)
            except (TypeError, ValueError):
                birth_year = _app_now().year - 45
                age = 45

            if not username or not email or not password or gender not in {'male', 'female', 'other'}:
                flash('Please complete all fields.', 'danger')
                return render_template('register.html', now_year=_app_now().year)
            if age < 18 or age > 120:
                flash('Please enter a valid birth year for an adult account.', 'danger')
                return render_template('register.html', now_year=_app_now().year)
            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash('That username or email is already registered.', 'danger')
                return render_template('register.html', now_year=_app_now().year)

            user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.flush()

            # Initialize profile
            profile = Profile(user_id=user.id, full_name=username, age=age, birth_year=birth_year, gender=gender, activity_level='moderate', theme_preference='light', bmi_onboarding_completed=False)
            db.session.add(profile)
            db.session.commit()

            flash('Registration successful! Please log in to your Care Plus account.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', now_year=_app_now().year)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')
            user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                flash(f'Welcome back to Care Plus, {user.username}!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid username/email or password.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out safely.', 'success')
        return redirect(url_for('landing'))

    @app.route('/onboarding/bmi', methods=['POST'])
    @login_required
    def complete_bmi_onboarding():
        profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.username)
        if request.form.get('action') == 'skip':
            profile.bmi_onboarding_completed = True
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('dashboard'))

        try:
            weight = float(request.form.get('weight_kg', ''))
            height = float(request.form.get('height_cm', ''))
            if weight <= 0 or height <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash('Please enter valid height and weight values.', 'danger')
            return redirect(url_for('dashboard'))

        profile.weight_kg = weight
        profile.height_cm = height
        profile.bmi_onboarding_completed = True
        health_record = HealthRecord(
            user_id=current_user.id,
            weight_kg=weight,
            height_cm=height,
            bmi=calculate_bmi(weight, height),
            recorded_at=datetime.utcnow(),
        )
        db.session.add_all([profile, health_record])
        db.session.commit()
        flash(f'BMI check saved successfully: {health_record.bmi}', 'success')
        return redirect(url_for('dashboard'))

    # 2. DASHBOARD
    @app.route('/dashboard')
    @login_required
    def dashboard():
        profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.username)
        today = _app_now().date()

        # Food & Calorie stats for today
        today_food_records = [r for r in current_user.food_records if r.consumed_at.date() == today]
        total_calories = round(sum(r.calories for r in today_food_records), 1)
        macro_totals = {
            'protein': round(sum(r.protein or 0 for r in today_food_records), 1),
            'carbohydrates': round(sum(r.carbohydrates or 0 for r in today_food_records), 1),
            'fat': round(sum(r.fat or 0 for r in today_food_records), 1),
        }

        # Calorie burn stats for today
        today_activities = [a for a in current_user.activities if a.date == today]
        total_burned = round(sum(a.calories_burned or 0 for a in today_activities), 1)

        # Health stats
        latest_health = current_user.health_records[-1] if current_user.health_records else None
        latest_weight = latest_health.weight_kg if latest_health and latest_health.weight_kg else (profile.weight_kg or 0.0)
        latest_height = latest_health.height_cm if latest_health and latest_health.height_cm else (profile.height_cm or 0.0)
        latest_bmi = calculate_bmi(latest_weight, latest_height)
        bmi_cat, bmi_badge = get_bmi_category(latest_bmi)

        # Hydration stats today
        today_water_records = [w for w in current_user.water_records if w.recorded_at.date() == today]
        today_water = round(sum(w.amount_ml for w in today_water_records), 0)

        # Sleep stats today/latest
        latest_sleep = current_user.sleep_records[-1] if current_user.sleep_records else None
        sleep_duration = latest_sleep.duration_hours if latest_sleep else 0.0

        # Notifications count
        notif_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

        # Medication due today
        active_meds = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()

        activity_dates = {activity.date for activity in current_user.activities if activity.date}
        activity_streak = 0
        streak_day = today
        while streak_day in activity_dates:
            activity_streak += 1
            streak_day -= timedelta(days=1)
        streak_message = f'Streak day {activity_streak} completed' if activity_streak else 'Complete an activity to start your streak'

        return render_template(
            'dashboard.html',
            profile=profile,
            total_calories=total_calories,
            total_burned=total_burned,
            latest_weight=latest_weight,
            latest_height=latest_height,
            latest_bmi=latest_bmi,
            bmi_cat=bmi_cat,
            bmi_badge=bmi_badge,
            today_water=today_water,
            sleep_duration=sleep_duration,
            notif_count=notif_count,
            active_meds=active_meds,
            latest_health=latest_health,
            today_meals=today_food_records,
            today_activities=today_activities,
            macro_totals=macro_totals,
            activity_streak=activity_streak,
            streak_message=streak_message
        )

    # 3. PROFILE MANAGEMENT
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.username)
        if request.method == 'POST':
            profile.full_name = request.form.get('full_name', '').strip() or profile.full_name or current_user.username
            username = request.form.get('username', '').strip() or current_user.username
            email = request.form.get('email', '').strip() or current_user.email
            duplicate = User.query.filter(User.id != current_user.id, (User.username == username) | (User.email == email)).first()
            if duplicate:
                flash('That username or email is already in use.', 'danger')
                return render_template('profile.html', profile=profile, now_year=_app_now().year)
            current_user.username = username
            current_user.email = email
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            if new_password:
                if len(new_password) < 6 or new_password != confirm_password:
                    flash('New password must be at least 6 characters and match confirmation.', 'danger')
                    return render_template('profile.html', profile=profile, now_year=_app_now().year)
                current_user.password_hash = generate_password_hash(new_password)
            birth_year = int(request.form.get('birth_year', profile.birth_year or (_app_now().year - (profile.age or 45))))
            profile.birth_year = birth_year
            profile.age = _age_from_birth_year(birth_year)
            profile.gender = request.form.get('gender', profile.gender or 'male')
            profile.height_cm = float(request.form.get('height_cm', profile.height_cm or 170.0))
            profile.weight_kg = float(request.form.get('weight_kg', profile.weight_kg or 70.0))
            profile.activity_level = request.form.get('activity_level', profile.activity_level or 'moderate')
            profile.theme_preference = request.form.get('theme_preference', profile.theme_preference or 'light')

            db.session.add(profile)
            db.session.commit()
            flash('Your profile information has been updated successfully.', 'success')
            return redirect(url_for('profile'))
        return render_template('profile.html', profile=profile, now_year=_app_now().year)

    @app.route('/profile/theme', methods=['POST'])
    @login_required
    def update_theme():
        theme = request.form.get('theme', 'light')
        if theme not in {'light', 'dark'}:
            return jsonify({'success': False, 'error': 'Invalid theme.'}), 400
        profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.username)
        profile.theme_preference = theme
        db.session.add(profile)
        db.session.commit()
        return jsonify({'success': True, 'theme': theme})

    # 4. SETTINGS & PREFERENCES
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.username, theme_preference='light')
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'password':
                current_pw = request.form.get('current_password', '')
                new_pw = request.form.get('new_password', '')
                confirm_pw = request.form.get('confirm_password', '')

                if not check_password_hash(current_user.password_hash, current_pw):
                    flash('Current password is incorrect.', 'danger')
                elif not new_pw or len(new_pw) < 6:
                    flash('New password must be at least 6 characters long.', 'danger')
                elif new_pw != confirm_pw:
                    flash('New password and confirmation do not match.', 'danger')
                else:
                    current_user.password_hash = generate_password_hash(new_pw)
                    db.session.add(current_user)
                    db.session.commit()
                    flash('Your password has been changed successfully.', 'success')

            return redirect(url_for('settings'))
        return render_template('settings.html', profile=profile)

    # 5. FOOD RECOGNITION (CNN EfficientNetB0)
    @app.route('/food', methods=['GET', 'POST'])
    @login_required
    def food_recognition_page():
        result = None
        nutrition_options = Nutrition.query.order_by(Nutrition.food_name.asc()).all()
        if request.method == 'POST':
            file = request.files.get('image')
            if not file or not file.filename:
                flash('Please select a food image file to upload.', 'danger')
            else:
                upload_dir = Config.UPLOAD_FOLDER
                upload_dir.mkdir(parents=True, exist_ok=True)
                filename = secure_filename(f"food_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
                file_path = upload_dir / filename
                file.save(file_path)
                result = predict_food_image(file_path)
                result['image_url'] = url_for('static', filename=f'uploads/{filename}')
                if result.get('error'):
                    flash(result['error'], 'danger')
                else:
                    flash(f"Food item recognized as '{result['food_name']}' with {result['confidence_percent']}% confidence!", 'success')
        return render_template('food_recognition.html', result=result, nutrition_options=nutrition_options)

    @app.route('/predict', methods=['POST'])
    @login_required
    def predict_food_api():
        file = request.files.get('image')
        if not file or not file.filename:
            return jsonify({'success': False, 'error': 'Please select a food image file to upload.'}), 400
        upload_dir = Config.UPLOAD_FOLDER
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = secure_filename(f"food_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
        file_path = upload_dir / filename
        file.save(file_path)
        result = predict_food_image(file_path)
        if result.get('error'):
            file_path.unlink(missing_ok=True)
            return jsonify({'success': False, 'error': result['error']}), 400
        result['image_url'] = url_for('static', filename=f'uploads/{filename}')
        return jsonify(result)

    @app.route('/food/save', methods=['POST'])
    @login_required
    def save_food_record():
        food_name = request.form.get('food_name', '').strip()
        meal_name = request.form.get('meal_name', 'Meal').strip()
        serving_amount_g = float(request.form.get('serving_amount_g', 100.0) or 100.0)

        if not food_name:
            flash('Food name is required.', 'danger')
            return redirect(url_for('food_recognition_page'))

        # Look up 100g base nutrition
        base_nutrition = lookup_nutrition(food_name.lower().replace(' ', '_'))
        if not base_nutrition:
            base_nutrition = {
                'calories': float(request.form.get('calories', 150.0) or 150.0),
                'protein': float(request.form.get('protein', 5.0) or 5.0),
                'carbohydrates': float(request.form.get('carbohydrates', 20.0) or 20.0),
                'fat': float(request.form.get('fat', 5.0) or 5.0),
                'fibre': float(request.form.get('fibre', 2.0) or 2.0),
                'sugar': float(request.form.get('sugar', 2.0) or 2.0),
            }

        # Scale nutrition proportionally to portion size (g / 100g)
        multiplier = serving_amount_g / 100.0
        scaled_cals = round(base_nutrition['calories'] * multiplier, 1)
        scaled_prot = round(base_nutrition['protein'] * multiplier, 1)
        scaled_carbs = round(base_nutrition['carbohydrates'] * multiplier, 1)
        scaled_fat = round(base_nutrition['fat'] * multiplier, 1)
        scaled_fibre = round(base_nutrition['fibre'] * multiplier, 1)
        scaled_sugar = round(base_nutrition['sugar'] * multiplier, 1)

        nutrition_obj = Nutrition.query.filter_by(food_name=food_name.lower().replace(' ', '_')).first()

        record = FoodRecord(
            user_id=current_user.id,
            nutrition_id=nutrition_obj.id if nutrition_obj else None,
            food_name=food_name,
            meal_name=meal_name,
            serving_amount_g=serving_amount_g,
            calories=scaled_cals,
            protein=scaled_prot,
            carbohydrates=scaled_carbs,
            fat=scaled_fat,
            fibre=scaled_fibre,
            sugar=scaled_sugar,
            consumed_at=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()

        flash(f"Saved {serving_amount_g}g of '{food_name}' ({scaled_cals} kcal) to your food log.", 'success')
        return redirect(url_for('food_history'))

    @app.route('/food/history')
    @login_required
    def food_history():
        records = FoodRecord.query.filter_by(user_id=current_user.id).order_by(FoodRecord.consumed_at.desc()).all()
        today = _app_now().date()
        today_consumed = sum(record.calories or 0 for record in records if record.consumed_at.date() == today) or 0
        today_burned = sum(activity.calories_burned or 0 for activity in current_user.activities if activity.date == today) or 0
        return render_template('food_history.html', records=records, today_consumed=today_consumed, today_burned=today_burned)

    @app.route('/food/delete/<int:food_id>', methods=['POST'])
    @login_required
    def delete_food(food_id):
        record = FoodRecord.query.filter_by(id=food_id, user_id=current_user.id).first_or_404()
        db.session.delete(record)
        db.session.commit()
        flash('Food log entry deleted.', 'success')
        return redirect(url_for('food_history'))

    # 6. CALORIE BURN PREDICTION (Scikit-Learn Model)
    @app.route('/calorie-burn', methods=['GET', 'POST'])
    @login_required
    def calorie_burn():
        result = None
        profile = current_user.profile or Profile(user_id=current_user.id)
        if request.method == 'POST':
            payload = {
                'activity_type': request.form.get('activity_type', 'Walking'),
                'gender': request.form.get('gender', profile.gender or 'male'),
                'age': float(profile.age or 45),
                'height': float(request.form.get('height', profile.height_cm or 170.0)),
                'weight': float(request.form.get('weight', profile.weight_kg or 70.0)),
                'duration_minutes': float(request.form.get('duration_minutes', 30.0)),
                'heart_rate': float(request.form.get('heart_rate', 110.0)),
                'body_temp': float(request.form.get('body_temp', 38.5)),
            }
            try:
                result = predict_calorie_burn(payload)
            except Exception as e:
                result = {'error': str(e)}
            if 'error' in result:
                flash(result['error'], 'danger')
            else:
                flash(f"AI Calorie Burn Prediction: {result['estimate']} kcal burned!", 'success')
        return render_template('calorie_burn.html', result=result, profile=profile)

    @app.route('/calorie-burn/save', methods=['POST'])
    @login_required
    def save_activity():
        activity_type = request.form.get('activity_type', 'Exercise').strip() or 'Exercise'
        duration = int(float(request.form.get('duration_minutes', 30.0) or 30.0))
        calories = float(request.form.get('calories_burned', 0.0) or 0.0)
        notes = request.form.get('notes', '').strip()

        activity = Activity(
            user_id=current_user.id,
            activity_type=activity_type,
            duration_minutes=duration,
            calories_burned=calories,
            date=_app_now().date(),
            notes=notes
        )
        db.session.add(activity)
        db.session.commit()
        flash(f"Saved activity '{activity_type}' ({calories} kcal burned) to your log.", 'success')
        return redirect(url_for('calorie_burn'))

    # 8. HEALTH MONITORING (BP, Sugar, Heart Rate, BMI)
    @app.route('/health', methods=['GET', 'POST'])
    @login_required
    def health():
        profile = current_user.profile or Profile(user_id=current_user.id)
        if request.method == 'POST':
            weight = float(request.form.get('weight_kg', profile.weight_kg or 70.0) or 70.0)
            height = float(request.form.get('height_cm', profile.height_cm or 170.0) or 170.0)
            bmi = calculate_bmi(weight, height)

            record = HealthRecord(
                user_id=current_user.id,
                weight_kg=weight,
                height_cm=height,
                bmi=bmi,
                blood_pressure=request.form.get('blood_pressure', '').strip() or '120/80',
                blood_sugar=request.form.get('blood_sugar', '').strip() or '95',
                cholesterol=request.form.get('cholesterol', '').strip() or '180',
                heart_rate=request.form.get('heart_rate', '').strip() or '72',
                notes=request.form.get('notes', '').strip(),
                recorded_at=datetime.utcnow()
            )
            db.session.add(record)
            db.session.commit()

            flash(f"Health record saved successfully! BMI calculated: {bmi}", 'success')
            return redirect(url_for('health'))

        records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.recorded_at.desc()).all()
        return render_template('health.html', records=records, profile=profile)

    @app.route('/health/delete/<int:record_id>', methods=['POST'])
    @login_required
    def delete_health(record_id):
        record = HealthRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
        db.session.delete(record)
        db.session.commit()
        flash('Health measurement deleted.', 'success')
        return redirect(url_for('health'))

    # 9. MEDICATIONS & REMINDERS
    @app.route('/medications', methods=['GET', 'POST'])
    @login_required
    def medications():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            dosage = request.form.get('dosage', '').strip()
            time = request.form.get('time', '').strip()
            frequency = request.form.get('frequency', '').strip()
            notes = request.form.get('notes', '').strip()

            if not name:
                flash('Medication name is required.', 'danger')
            elif not time:
                flash('Please select a scheduled time.', 'danger')
            else:
                try:
                    datetime.strptime(time, '%H:%M')
                except ValueError:
                    flash('Please select a valid scheduled time.', 'danger')
                    return redirect(url_for('medications'))

                med = Medication(
                    user_id=current_user.id,
                    name=name,
                    dosage=dosage,
                    time=time,
                    frequency=frequency,
                    notes=notes,
                    is_active=True
                )
                db.session.add(med)
                db.session.commit()
                flash(f"Medication '{name}' added to your schedule.", 'success')
            return redirect(url_for('medications'))

        meds = Medication.query.filter_by(user_id=current_user.id).order_by(Medication.created_at.desc()).all()
        logs = MedicationLog.query.filter_by(user_id=current_user.id).order_by(MedicationLog.taken_at.desc()).limit(20).all()
        return render_template('medications.html', meds=meds, logs=logs)

    @app.route('/medications/taken/<int:med_id>', methods=['POST'])
    @login_required
    def mark_medication_taken(med_id):
        med = Medication.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
        log = MedicationLog(user_id=current_user.id, medication_id=med.id, status='taken', taken_at=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        flash(f"Marked '{med.name}' as taken.", 'success')
        return redirect(url_for('medications'))

    @app.route('/medications/delete/<int:med_id>', methods=['POST'])
    @login_required
    def delete_medication(med_id):
        med = Medication.query.filter_by(id=med_id, user_id=current_user.id).first_or_404()
        db.session.delete(med)
        db.session.commit()
        flash('Medication removed from your schedule.', 'success')
        return redirect(url_for('medications'))

    # 10. WELLNESS (Water, Exercise, Sleep)
    @app.route('/wellness', methods=['GET', 'POST'])
    @login_required
    def wellness():
        if request.method == 'POST':
            kind = request.form.get('record_type')
            if kind == 'reminders':
                default_values = {reminder_id: (default_name, default_time) for reminder_id, default_name, default_time in DEFAULT_WELLNESS_REMINDERS}
                for reminder_id in request.form.getlist('reminder_keys'):
                    default_name, default_time = default_values.get(reminder_id, ('Wellness activity', '09:00'))
                    name = request.form.get(f'reminder_name_{reminder_id}', default_name).strip() or default_name
                    scheduled_time = request.form.get(f'reminder_time_{reminder_id}', default_time).strip()
                    try:
                        scheduled_for = datetime.strptime(scheduled_time, '%H:%M').replace(year=2000, month=1, day=1)
                    except ValueError:
                        flash(f'Invalid time for {name}. Use the HH:MM format.', 'danger')
                        return redirect(url_for('wellness'))
                    reminder = Reminder.query.filter_by(
                        user_id=current_user.id,
                        reminder_type=f'wellness:{reminder_id}'
                    ).first()
                    if reminder is None:
                        reminder = Reminder(
                            user_id=current_user.id,
                            reminder_type=f'wellness:{reminder_id}',
                            title=name,
                        )
                        db.session.add(reminder)
                    reminder.title = name
                    reminder.scheduled_for = scheduled_for
                    reminder.is_active = True
                db.session.commit()
                flash('Wellness reminders updated successfully.', 'success')
                return redirect(url_for('wellness'))
            if kind == 'add_reminder':
                name = request.form.get('new_reminder_name', '').strip()
                scheduled_time = request.form.get('new_reminder_time', '').strip()
                if not name or len(name) > 120:
                    flash('Enter an activity name up to 120 characters.', 'danger')
                    return redirect(url_for('wellness'))
                try:
                    scheduled_for = datetime.strptime(scheduled_time, '%H:%M').replace(year=2000, month=1, day=1)
                except ValueError:
                    flash('Enter a valid reminder time.', 'danger')
                    return redirect(url_for('wellness'))
                reminder_key = f'custom:{uuid.uuid4().hex}'
                db.session.add(Reminder(
                    user_id=current_user.id,
                    reminder_type=f'wellness:{reminder_key}',
                    title=name,
                    scheduled_for=scheduled_for,
                    is_active=True,
                ))
                db.session.commit()
                flash('Wellness activity added successfully.', 'success')
                return redirect(url_for('wellness'))
            if kind == 'water':
                amount = float(request.form.get('amount_ml', 250.0) or 250.0)
                if amount > 0:
                    db.session.add(WaterRecord(user_id=current_user.id, amount_ml=amount, recorded_at=datetime.utcnow()))
                    flash(f"Added {amount:.0f} ml of water.", 'success')
            elif kind == 'exercise':
                activity_name = request.form.get('activity_name', 'Exercise').strip()
                duration = int(float(request.form.get('duration_minutes', 30) or 30))
                cals = float(request.form.get('calories_burned', 150.0) or 150.0)
                db.session.add(Activity(user_id=current_user.id, activity_type=activity_name, duration_minutes=duration, calories_burned=cals, date=_app_now().date()))
                flash(f"Logged exercise '{activity_name}' ({duration} mins).", 'success')
            elif kind == 'sleep':
                sleep_time = request.form.get('sleep_time')
                wake_time = request.form.get('wake_time')
                if sleep_time and wake_time:
                    try:
                        sleep_dt = datetime.fromisoformat(sleep_time)
                        wake_dt = datetime.fromisoformat(wake_time)
                        duration = round((wake_dt - sleep_dt).total_seconds() / 3600.0, 1)
                        db.session.add(SleepRecord(user_id=current_user.id, sleep_time=sleep_dt, wake_time=wake_dt, duration_hours=max(0.0, duration), date=sleep_dt.date()))
                        flash(f"Logged sleep duration of {duration} hours.", 'success')
                    except Exception as e:
                        flash('Invalid sleep/wake format.', 'danger')
            db.session.commit()
            return redirect(url_for('wellness'))

        water_records = WaterRecord.query.filter_by(user_id=current_user.id).order_by(WaterRecord.recorded_at.desc()).limit(15).all()
        exercise_records = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.created_at.desc()).limit(15).all()
        sleep_records = SleepRecord.query.filter_by(user_id=current_user.id).order_by(SleepRecord.date.desc()).limit(15).all()
        return render_template('wellness.html', water=water_records, exercise=exercise_records, sleep=sleep_records)

    @app.route('/wellness/reminders/delete/<int:reminder_id>', methods=['POST'])
    @login_required
    def delete_wellness_reminder(reminder_id):
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=current_user.id).first_or_404()
        if not reminder.reminder_type.startswith('wellness:'):
            abort(404)
        reminder.is_active = False
        db.session.commit()
        flash('Wellness reminder deleted.', 'success')
        return redirect(url_for('wellness'))

    @app.route('/wellness/reminders/clear', methods=['POST'])
    @login_required
    def clear_wellness_reminders():
        for reminder_id, default_name, _ in DEFAULT_WELLNESS_REMINDERS:
            reminder_type = f'wellness:{reminder_id}'
            reminder = Reminder.query.filter_by(
                user_id=current_user.id,
                reminder_type=reminder_type,
            ).first()
            if reminder is None:
                db.session.add(Reminder(
                    user_id=current_user.id,
                    reminder_type=reminder_type,
                    title=default_name,
                    is_active=False,
                ))
            else:
                reminder.is_active = False
        for reminder in current_user.reminders:
            if reminder.reminder_type.startswith('wellness:'):
                reminder.is_active = False
        db.session.commit()
        flash('All wellness reminders cleared.', 'success')
        return redirect(url_for('wellness'))

    # 11. PROGRESS & ANALYTICS (Chart.js)
    @app.route('/progress')
    @login_required
    def progress():
        return render_template('progress.html')

    @app.route('/progress/chart-data')
    @login_required
    def progress_chart_data():
        days = int(request.args.get('days', 30))
        start_date = _app_now() - timedelta(days=max(days - 1, 0))

        # Weight & BMI trend
        health_recs = HealthRecord.query.filter(
            HealthRecord.user_id == current_user.id,
            HealthRecord.recorded_at >= start_date
        ).order_by(HealthRecord.recorded_at.asc()).all()

        dates_health = [_app_datetime(r.recorded_at).strftime('%m-%d') for r in health_recs]
        weights = [r.weight_kg for r in health_recs]
        bmis = [r.bmi for r in health_recs]

        def systolic(value):
            try:
                return float(str(value).split('/')[0])
            except (TypeError, ValueError, IndexError):
                return None

        def diastolic(value):
            try:
                return float(str(value).split('/')[1])
            except (TypeError, ValueError, IndexError):
                return None

        def numeric(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        # Calories Consumed vs Burned
        food_recs = FoodRecord.query.filter(
            FoodRecord.user_id == current_user.id,
            FoodRecord.consumed_at >= start_date
        ).order_by(FoodRecord.consumed_at.asc()).all()

        act_recs = Activity.query.filter(
            Activity.user_id == current_user.id,
            Activity.created_at >= start_date
        ).order_by(Activity.created_at.asc()).all()

        # Group by day
        day_map = {}
        for i in range(days):
            d_str = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            day_map[d_str] = {'consumed': 0.0, 'burned': 0.0, 'water': 0.0}

        for f in food_recs:
            d_str = _app_datetime(f.consumed_at).strftime('%Y-%m-%d')
            if d_str in day_map:
                day_map[d_str]['consumed'] += f.calories

        for a in act_recs:
            d_str = _app_datetime(a.created_at).strftime('%Y-%m-%d')
            if d_str in day_map:
                day_map[d_str]['burned'] += (a.calories_burned or 0)

        water_recs = WaterRecord.query.filter(
            WaterRecord.user_id == current_user.id,
            WaterRecord.recorded_at >= start_date
        ).all()
        for w in water_recs:
            d_str = _app_datetime(w.recorded_at).strftime('%Y-%m-%d')
            if d_str in day_map:
                day_map[d_str]['water'] += w.amount_ml

        chart_labels = list(day_map.keys())
        consumed_vals = [round(day_map[d]['consumed'], 1) for d in chart_labels]
        burned_vals = [round(day_map[d]['burned'], 1) for d in chart_labels]
        water_vals = [round(day_map[d]['water'] / 1000.0, 2) for d in chart_labels]

        return jsonify({
            'dates_health': dates_health,
            'weights': weights,
            'bmis': bmis,
            'vitals_dates': dates_health,
            'systolic': [systolic(r.blood_pressure) for r in health_recs],
            'diastolic': [diastolic(r.blood_pressure) for r in health_recs],
            'blood_sugar': [numeric(r.blood_sugar) for r in health_recs],
            'heart_rate': [numeric(r.heart_rate) for r in health_recs],
            'labels': [d[5:] for d in chart_labels],
            'consumed': consumed_vals,
            'burned': burned_vals,
            'water': water_vals
        })

    # 12. HEALTH REPORTS & PDF & SECURE SHARING
    @app.route('/reports', methods=['GET', 'POST'])
    @login_required
    def reports():
        if request.method == 'POST':
            days = int(request.form.get('range_days', 30))
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            report_path = generate_pdf_report(current_user, start_date, end_date, f'last_{days}_days')

            if not report_path:
                flash('Unable to generate health report PDF. Please try again.', 'danger')
            else:
                flash('Health report generated successfully!', 'success')
            return redirect(url_for('reports'))

        shares = ReportShare.query.filter_by(user_id=current_user.id).order_by(ReportShare.created_at.desc()).all()
        return render_template('reports.html', shares=shares)

    @app.route('/reports/pdf')
    @login_required
    def reports_pdf():
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        report_path = generate_pdf_report(current_user, start_date, end_date, f'last_{days}_days')

        if not report_path or not Path(report_path).exists():
            flash('Unable to generate PDF report file.', 'danger')
            return redirect(url_for('reports'))

        filename = f"Care_Plus_Report_{current_user.username}_{_app_now().strftime('%Y%m%d')}.pdf"
        return send_file(report_path, as_attachment=True, download_name=filename)

    @app.route('/reports/share', methods=['POST'])
    @login_required
    def share_report():
        token = uuid.uuid4().hex
        expires = datetime.utcnow() + timedelta(days=7)
        share = ReportShare(user_id=current_user.id, report_type='health_summary', token=token, expires_at=expires)
        db.session.add(share)
        db.session.commit()

        share_path = url_for('shared_report', token=token)
        share_url = f"{Config.PUBLIC_BASE_URL}{share_path}" if Config.PUBLIC_BASE_URL else share_path
        flash(f'Secure shareable link created! Valid for 7 days: {share_url}', 'success')
        return redirect(url_for('reports'))

    @app.route('/shared-report/<token>')
    def shared_report(token):
        share = ReportShare.query.filter_by(token=token).first()
        if not share or share.revoked or share.expires_at < datetime.utcnow():
            return render_template('errors/shared_expired.html'), 404

        user = share.user
        start_date = datetime.utcnow() - timedelta(days=30)
        profile = user.profile
        latest_health = user.health_records[-1] if user.health_records else None
        food_records = [r for r in user.food_records if r.consumed_at >= start_date]

        return render_template(
            'shared_report.html',
            share=share,
            user=user,
            profile=profile,
            latest_health=latest_health,
            food_records=food_records
        )

    @app.route('/reports/revoke/<int:share_id>', methods=['POST'])
    @login_required
    def revoke_report(share_id):
        share = ReportShare.query.filter_by(id=share_id, user_id=current_user.id).first_or_404()
        share.revoked = True
        db.session.commit()
        flash('Report sharing link has been revoked.', 'success')
        return redirect(url_for('reports'))

    # ERROR HANDLERS
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
