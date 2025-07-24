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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS (Unchanged) ---
class User(db.Model):
    # ...
class Song(db.Model):
    # ...

# --- NEW FUNCTION TO CREATE DATABASE TABLES ---
# This function allows Render to set up the database.
@app.cli.command("create-db")
def create_db():
    with app.app_context():
        db.create_all()
    print("Database tables created!")

# --- API ENDPOINTS (Unchanged) ---
@app.route('/register', methods=['POST'])
def register():
    # ...
@app.route('/login', methods=['POST'])
def login():
    # ...
# ... (all your other routes are unchanged) ...
@app.route('/generate-ppt', methods=['POST'])
def generate_ppt_custom():
    # ...

# The if __name__ == '__main__' block is no longer needed for deployment