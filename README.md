# Care Plus

Care Plus is an AI-based personal health and fitness assistant for adults aged 40+.

## Project objective

The application provides users with food recognition, nutrition analysis, calorie-burn prediction, health monitoring, medication reminders, water tracking, exercise tracking, sleep tracking, progress monitoring and secure report sharing.

## Features

- User registration and login
- Profile management
- BMI calculation and health records
- Food logging with manual nutrition entries
- Nutrition lookup from SQLite
- Food logs and activity logs
- Calorie-burn prediction via the existing trained model file
- Water, exercise, sleep, medication and reminder tracking
- Progress dashboards and health reports
- PDF report generation
- Secure sharing links with expiry and revocation
- Light and dark theme support

## Technology stack

- Python
- Flask
- SQLAlchemy
- SQLite
- Jinja2 templates
- Bootstrap-style custom CSS
- ReportLab
- scikit-learn (for the trained calorie model)

## Installation

1. Create a virtual environment:
   python -m venv venv
2. Activate it:
   venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Initialise the database:
   python init_db.py
5. Seed nutrition data:
   python seed_database.py
6. Run the app:
   python app.py

## Database setup

By default, the application uses SQLite at `instance/care_plus.db`. For XAMPP MySQL:

1. Start **MySQL** in the XAMPP Control Panel.
2. Run the SQL in `database/create_mysql.sql` using phpMyAdmin, or run:
   `C:\xampp\mysql\bin\mysql.exe -u root -p < database\create_mysql.sql`
3. Copy `.env.example` to `.env` and set `DATABASE_URL` to your MySQL connection string.
4. Install dependencies and run `python init_db.py` to create the application tables.

Example for the default XAMPP `root` user with no password:

`DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/care_plus?charset=utf8mb4`

Medication and wellness reminders compare schedule times using the configured application timezone (default: `Asia/Colombo`), not the laptop's local timezone. Keep an authenticated Care Plus page open for browser reminders. Set `APP_TIMEZONE` in `.env` to change the application timezone.

## Nutrition seed data

Seed data is loaded by the `seed_database.py` script. It populates verified nutrition entries in the `nutrition` table.

## Running tests

Use:

pytest

## Security

- Password hashing with Werkzeug
- Login required for protected routes
- Database ownership checks in queries
- Secure token-based report sharing with expiry and revocation
- File upload validation in model integrations

## Troubleshooting

- If the database is missing, run `python init_db.py`.
- If no nutrition records exist, run `python seed_database.py`.
- If the models cannot be loaded, verify that the trained files still exist in the `models` folders.

## Future model replacement/update process

- Keep the original trained model file in its current folder.
- Validate the new model with standalone tests.
- Update the file path only if the new artifact is verified and compatible with the app.
- Update the service logic and re-run the relevant tests.
