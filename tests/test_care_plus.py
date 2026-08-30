import pytest
from datetime import datetime, timedelta
from app import create_app
from database.db import db
from database.models import User, Profile, Nutrition, FoodRecord, HealthRecord, Activity, WaterRecord, SleepRecord, Medication, MedicationLog, ReportShare
from services.bmi_service import calculate_bmi, get_bmi_category
from services.calorie_prediction import predict_calorie_burn
from services.report_service import generate_pdf_report
from werkzeug.security import generate_password_hash, check_password_hash


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()

            item1 = Nutrition(food_name='apple', serving_size_g=100.0, calories=52.0, protein=0.3, carbohydrates=13.8, fat=0.2, fibre=2.4, sugar=10.4)
            item2 = Nutrition(food_name='biryani', serving_size_g=100.0, calories=170.0, protein=7.5, carbohydrates=24.0, fat=5.2, fibre=1.2, sugar=0.8)
            db.session.add_all([item1, item2])
            db.session.commit()

        yield client


def test_password_hashing():
    pw = "SuperSecret123"
    hashed = generate_password_hash(pw)
    assert check_password_hash(hashed, pw) is True
    assert check_password_hash(hashed, "WrongPassword") is False


def test_bmi_service():
    bmi = calculate_bmi(70.0, 170.0)
    assert bmi == 24.22
    cat, badge = get_bmi_category(bmi)
    assert cat == "Normal weight"
    assert badge == "success"

    obese_bmi = calculate_bmi(100.0, 170.0)
    assert obese_bmi == 34.60
    cat_o, badge_o = get_bmi_category(obese_bmi)
    assert cat_o == "Obese"
    assert badge_o == "danger"


def test_user_registration_and_login(client):
    res_reg = client.post('/register', data={
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_reg.status_code == 200

    res_login = client.post('/login', data={
        'identifier': 'john_doe',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'Welcome back' in res_login.data or b'Dashboard' in res_login.data


def test_calorie_prediction_model():
    payload = {
        'gender': 'male',
        'age': 45.0,
        'height': 175.0,
        'weight': 75.0,
        'duration_minutes': 30.0,
        'heart_rate': 110.0,
        'body_temp': 38.5
    }
    res = predict_calorie_burn(payload)
    assert res['error'] is None
    assert res['estimate'] is not None
    assert res['estimate'] > 0.0


def test_food_saving_and_portion_scaling(client):
    client.post('/register', data={'username': 'fooduser', 'email': 'food@example.com', 'password': 'pass'}, follow_redirects=True)
    client.post('/login', data={'identifier': 'fooduser', 'password': 'pass'}, follow_redirects=True)

    res_save = client.post('/food/save', data={
        'food_name': 'apple',
        'meal_name': 'Lunch',
        'serving_amount_g': 150.0,
        'calories': 52.0,
        'protein': 0.3,
        'carbohydrates': 13.8,
        'fat': 0.2,
        'fibre': 2.4,
        'sugar': 10.4
    }, follow_redirects=True)
    assert res_save.status_code == 200

    with client.application.app_context():
        user = User.query.filter_by(username='fooduser').first()
        assert len(user.food_records) == 1
        rec = user.food_records[0]
        assert rec.food_name == 'apple'
        assert rec.serving_amount_g == 150.0
        assert rec.calories == 78.0


def test_user_data_isolation(client):
    client.post('/register', data={'username': 'usera', 'email': 'usera@example.com', 'password': 'pass'}, follow_redirects=True)
    client.post('/register', data={'username': 'userb', 'email': 'userb@example.com', 'password': 'pass'}, follow_redirects=True)

    client.post('/login', data={'identifier': 'usera', 'password': 'pass'}, follow_redirects=True)
    client.post('/wellness', data={'record_type': 'water', 'amount_ml': 500}, follow_redirects=True)

    client.post('/login', data={'identifier': 'userb', 'password': 'pass'}, follow_redirects=True)

    with client.application.app_context():
        user_a = User.query.filter_by(username='usera').first()
        user_b = User.query.filter_by(username='userb').first()

        assert len(user_a.water_records) == 1
        assert len(user_b.water_records) == 0


def test_pdf_report_and_share_revocation(client):
    client.post('/register', data={'username': 'reportuser', 'email': 'rep@example.com', 'password': 'pass'}, follow_redirects=True)
    client.post('/login', data={'identifier': 'reportuser', 'password': 'pass'}, follow_redirects=True)

    # 1. Generate PDF
    res_gen = client.post('/reports', data={'range_days': '30'}, follow_redirects=True)
    assert res_gen.status_code == 200

    # 2. Create Share Link
    res_share = client.post('/reports/share', follow_redirects=True)
    assert res_share.status_code == 200

    with client.application.app_context():
        share = ReportShare.query.first()
        assert share is not None
        token = share.token
        share_id = share.id

    # 3. Access shared report link
    res_access = client.get(f'/shared-report/{token}')
    assert res_access.status_code == 200
    assert b'Care Plus' in res_access.data

    # 4. Revoke link
    res_revoke = client.post(f'/reports/revoke/{share_id}', follow_redirects=True)
    assert res_revoke.status_code == 200

    # 5. Access revoked link -> expect 404
    res_blocked = client.get(f'/shared-report/{token}')
    assert res_blocked.status_code == 404
