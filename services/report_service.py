from datetime import datetime
from zoneinfo import ZoneInfo

from config import Config
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib import colors
from services.bmi_service import calculate_bmi, get_bmi_category


def _app_datetime(value):
    timezone = ZoneInfo(Config.APP_TIMEZONE)
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo('UTC'))
    return value.astimezone(timezone)


def generate_pdf_report(user, start_date, end_date, report_type='last_30_days'):
    try:
        output_dir = Path('reports')
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / f'care_plus_report_user_{user.id}.pdf'

        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#4c1d95'),
            alignment=0
        )
        subtitle_style = ParagraphStyle(
            'ReportSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#6b7280')
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#6f42c1'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1f2937')
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Italic'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#6b7280'),
            spaceBefore=15
        )

        story = []

        # Logo Header Table
        logo_path = Path('static/images/care-plus-logo.png')
        header_data = []

        brand_text = Paragraph("<b>Care Plus</b><br/><font size=9 color='#6b7280'>AI-Based Personal Health & Fitness Assistant</font>", title_style)
        meta_text = Paragraph(f"<b>Report Date:</b> {datetime.now(ZoneInfo(Config.APP_TIMEZONE)).strftime('%B %d, %Y')}<br/><b>Period:</b> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}<br/><b>Prepared For:</b> {user.profile.full_name if user.profile else user.username}", subtitle_style)

        if logo_path.exists():
            img = Image(str(logo_path), width=50, height=50)
            header_table = Table([[img, brand_text, meta_text]], colWidths=[60, 260, 220])
        else:
            header_table = Table([[brand_text, meta_text]], colWidths=[320, 220])

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6f42c1'), spaceBefore=2, spaceAfter=12))

        # 1. Profile & Health Overview
        story.append(Paragraph("1. User Health Overview", heading_style))
        profile = user.profile
        latest_health = user.health_records[-1] if user.health_records else None
        h_weight = latest_health.weight_kg if latest_health and latest_health.weight_kg else (profile.weight_kg if profile else 0.0)
        h_height = latest_health.height_cm if latest_health and latest_health.height_cm else (profile.height_cm if profile else 0.0)
        h_bmi = calculate_bmi(h_weight, h_height)
        bmi_cat, _ = get_bmi_category(h_bmi)

        overview_data = [
            ['Metric', 'Current Status', 'Target / Reference Range'],
            ['Age / Gender', f"{profile.age if profile and profile.age else 'N/A'} yrs / {profile.gender.capitalize() if profile and profile.gender else 'N/A'}", 'Adult 40+'],
            ['Height / Weight', f"{h_height} cm / {h_weight} kg", 'User Profile'],
            ['Body Mass Index (BMI)', f"{h_bmi} ({bmi_cat})", '18.5 - 24.9 (Normal weight)'],
            ['Blood Pressure', f"{latest_health.blood_pressure if latest_health and latest_health.blood_pressure else 'N/A'}", '120/80 mmHg'],
            ['Blood Sugar', f"{latest_health.blood_sugar if latest_health and latest_health.blood_sugar else 'N/A'}", '70 - 99 mg/dL (Fasting)'],
            ['Heart Rate', f"{latest_health.heart_rate if latest_health and latest_health.heart_rate else 'N/A'} bpm", '60 - 100 bpm'],
        ]
        t_overview = Table(overview_data, colWidths=[180, 180, 180])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 10))

        # 2. Nutrition & Food Log Summary
        story.append(Paragraph("2. Nutrition & Food Log Summary", heading_style))
        food_records = [r for r in user.food_records if r.consumed_at >= start_date]
        total_cals = sum(r.calories for r in food_records)
        total_prot = sum(r.protein for r in food_records)
        total_carbs = sum(r.carbohydrates for r in food_records)
        total_fat = sum(r.fat for r in food_records)

        food_summary_data = [
            ['Food Item', 'Portion (g)', 'Consumed Date', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
        ]
        for r in food_records[:8]:
            food_summary_data.append([
                r.food_name,
                f"{getattr(r, 'serving_amount_g', 100.0)}g",
                _app_datetime(r.consumed_at).strftime('%Y-%m-%d %H:%M'),
                f"{r.calories:.1f}",
                f"{r.protein:.1f}",
                f"{r.carbohydrates:.1f}",
                f"{r.fat:.1f}"
            ])
        if len(food_summary_data) == 1:
            food_summary_data.append(['No meals logged for selected period', '-', '-', '0.0', '0.0', '0.0', '0.0'])

        food_summary_data.append(['TOTALS', '-', f"{len(food_records)} meals logged", f"{total_cals:.1f}", f"{total_prot:.1f}", f"{total_carbs:.1f}", f"{total_fat:.1f}"])

        t_food = Table(food_summary_data, colWidths=[130, 60, 95, 70, 65, 60, 60])
        t_food.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8540f5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f3e8ff')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        story.append(t_food)
        story.append(Spacer(1, 10))

        # 3. Wellness & Activity Summary
        story.append(Paragraph("3. Wellness & Exercise Tracking", heading_style))
        activities = [a for a in user.activities if datetime.combine(a.date, datetime.min.time()) >= start_date]
        total_burned = sum(a.calories_burned or 0 for a in activities)
        water_records = [w for w in user.water_records if w.recorded_at >= start_date]
        total_water_ml = sum(w.amount_ml for w in water_records)
        sleep_records = [s for s in user.sleep_records if datetime.combine(s.date, datetime.min.time()) >= start_date]
        avg_sleep = (sum(s.duration_hours for s in sleep_records) / len(sleep_records)) if sleep_records else 0.0

        wellness_data = [
            ['Category', 'Recorded Summary', 'Status / Target'],
            ['Calorie Burn Activities', f"{len(activities)} activities logged ({total_burned:.1f} total kcal burned)", 'AI-Predicted & Logged'],
            ['Hydration (Water Intake)', f"{total_water_ml / 1000.0:.2f} Liters total ({len(water_records)} logs)", 'Daily Goal: 2.0L - 2.5L'],
            ['Sleep Tracking', f"{avg_sleep:.1f} hours average nightly sleep", 'Recommended: 7.0 - 8.0 hrs'],
        ]
        t_wellness = Table(wellness_data, colWidths=[150, 240, 150])
        t_wellness.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(t_wellness)
        story.append(Spacer(1, 10))

        # 4. Medication Checklist
        story.append(Paragraph("4. Medication Schedule & Reminders", heading_style))
        meds = user.medications
        med_data = [['Medication Name', 'Dosage', 'Frequency', 'Scheduled Time', 'Status']]
        for m in meds:
            med_data.append([m.name, m.dosage or 'As directed', m.frequency or 'Daily', m.time or 'Morning', 'Active' if m.is_active else 'Inactive'])
        if len(med_data) == 1:
            med_data.append(['No medications active', '-', '-', '-', '-'])

        t_med = Table(med_data, colWidths=[140, 100, 100, 100, 100])
        t_med.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4c1d95')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(t_med)

        # Health Disclaimer
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#9ca3af'), spaceBefore=4, spaceAfter=8))
        disclaimer_text = ("<b>Health Disclaimer:</b> Care Plus provides general health, nutrition, and fitness tracking for adults aged 40+. "
                           "AI-generated food recognition and calorie prediction outputs are scientific estimates and should not be considered "
                           "a medical diagnosis, prescription, or professional medical advice.")
        story.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(story)
        return str(file_path)
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        return None
