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

# --- DATABASE CONFIGURATION ---
DATABASE_URL = "postgresql://neondb:npg_eLKYft0OS2GI@ep-fancy-smoke-af7x3gbf-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# This command ensures the tables exist every time the server starts.
with app.app_context():
    db.create_all()

# --- API ENDPOINTS ---
@app.route('/register', methods=['POST'])
def register():
    # ... (Your existing code is fine)
@app.route('/login', methods=['POST'])
def login():
    # ... (Your existing code is fine)
# (All your other song management endpoints are here and are fine)

# This is the endpoint our app will call
@app.route('/generate-ppt', methods=['POST'])
def generate_ppt_custom():
    try:
        data = request.get_json()
        lyrics = data.get('lyrics', '')
        song_title = data.get('title', 'Lyrics')
        bg_color_hex = data.get('backgroundColor', '000000')
        font_color_hex = data.get('fontColor', 'FFFFFF')
        font_size = int(data.get('fontSize', 44))
        font_name = data.get('fontName', 'Arial')

        prs = Presentation()
        prs.slide_width = Inches(16)
        prs.slide_height = Inches(9)
        blank_slide_layout = prs.slide_layouts[6]

        paragraphs = [p.strip() for p in lyrics.split('\n\n') if p.strip()]

        for paragraph in paragraphs:
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Set background color
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor.from_string(bg_color_hex)
            
            # Add and format text box
            txBox = slide.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(14.0), Inches(7.0))
            tf = txBox.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = paragraph
            p.alignment = PP_ALIGN.CENTER
            
            font = p.font
            font.name = font_name
            font.size = Pt(font_size)
            font.color.rgb = RGBColor.from_string(font_color_hex)

        file_stream = io.BytesIO()
        prs.save(file_stream)
        file_stream.seek(0)
        
        safe_filename = "".join([c for c in song_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=f"{safe_filename}.pptx",
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    except Exception as e:
        print(f"Error in /generate-ppt: {e}")
        return jsonify({"error": str(e)}), 500