import os
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import io

app = Flask(__name__)

# --- DATABASE CONFIGURATION CHANGE ---
# We now get the password from a separate environment variable to avoid URL issues.
db_user = "neondb"
db_password = os.environ.get('DB_PASSWORD') # Get password from a new variable
db_host = "ep-fancy-smoke-af7x3gbf-pooler.c-2.us-west-2.aws.neon.tech"
db_name = "neondb"
# Construct the URL safely within the code
db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS (Unchanged) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- FUNCTION TO CREATE DATABASE TABLES (Unchanged) ---
@app.cli.command("create-db")
def create_db():
    with app.app_context():
        db.create_all()
    print("Database tables created!")

# --- ALL API ENDPOINTS (Unchanged) ---
@app.route('/register', methods=['POST'])
def register():
    # ... (code is unchanged)
@app.route('/login', methods=['POST'])
def login():
    # ... (code is unchanged)
# ... etc. all your other routes are unchanged ...
@app.route('/generate-ppt', methods=['POST'])
def generate_ppt_custom():
    # ... (code is unchanged)