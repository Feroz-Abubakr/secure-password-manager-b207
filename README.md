Secure Password Manager
This is my B207 Cyber Security project. I built a small password manager using Python, Flask and SQLite.
The user can register, login, save website credentials, generate strong password, view saved credentials, delete saved credentials and logout.
Technologies
Python, Flask, SQLite, HTML, CSS, cryptography and Flask-WTF.
Main Features
•	Register and login
•	Save website credentials
•	View saved credentials
•	Delete saved credentials
•	Generate strong password
•	Hash login passwords
•	Encrypt saved website passwords
•	CSRF protection in forms
•	SQL queries with placeholders
How to Run
Clone the project:
git clone https://github.com/Feroz-Abubakr/secure-password-manager-b207.git
cd secure-password-manager-b207
Create and activate virtual environment:
python3 -m venv venv
source venv/bin/activate
Install requirements:
pip install -r requirements.txt
Run the app:
python3 app.py
Open in browser:
http://127.0.0.1:5000
How to Use
First register a new account. After that login with your username and password.
After login, dashboard will open. In dashboard user can add website name, username or email, password and note.
User can also generate strong password. Saved credentials can be viewed and deleted from dashboard.
Security Note
Login passwords are not saved as plain text. They are saved as hashes.
Saved website passwords are encrypted before storing in SQLite database. The project also uses CSRF tokens in forms and SQL placeholders to make database queries safer.
This project is for learning purpose and not for real production use.

