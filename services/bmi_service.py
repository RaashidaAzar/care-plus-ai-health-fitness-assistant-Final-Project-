def calculate_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm:
        return 0.0
    try:
        w = float(weight_kg)
        h_m = float(height_cm) / 100.0
        if h_m <= 0 or w <= 0:
            return 0.0
        return round(w / (h_m ** 2), 2)
    except Exception:
        return 0.0


def get_bmi_category(bmi):
    if not bmi or bmi <= 0:
        return 'Unknown', 'secondary'
    if bmi < 18.5:
        return 'Underweight', 'info'
    elif 18.5 <= bmi < 25.0:
        return 'Normal weight', 'success'
    elif 25.0 <= bmi < 30.0:
        return 'Overweight', 'warning'
    else:
        return 'Obese', 'danger'
