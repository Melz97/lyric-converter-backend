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
# Final, corrected URL with the pg8000 driver and your last password
DATABASE_URL = "postgresql+pg8000://neondb:npg_eLKYft0OS2GI@ep-fancy-smoke-af7x3gbf-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

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
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required!'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 409
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Could not verify'}), 401
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Could not verify! Incorrect username or password.'}), 401
    return jsonify({'message': 'Login successful!', 'user_id': user.id}), 200

@app.route('/songs', methods=['POST'])
def add_song():
    data = request.get_json()
    if not data or 'title' not in data or 'lyrics' not in data or 'user_id' not in data:
        return jsonify({'message': 'Missing data!'}), 400
    new_song = Song(title=data['title'], lyrics=data['lyrics'], user_id=data['user_id'])
    db.session.add(new_song)
    db.session.commit()
    return jsonify({'message': 'Song created!', 'song_id': new_song.id}), 201

@app.route('/songs/<int:user_id>', methods=['GET'])
def get_songs(user_id):
    songs = Song.query.filter_by(user_id=user_id).order_by(Song.title).all()
    output = []
    for song in songs:
        song_data = {'id': song.id, 'title': song.title, 'lyrics': song.lyrics}
        output.append(song_data)
    return jsonify({'songs': output})

@app.route('/songs/<int:song_id>', methods=['PUT', 'DELETE'])
def manage_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({'message': 'Song not found!'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        song.title = data.get('title', song.title)
        song.lyrics = data.get('lyrics', song.lyrics)
        db.session.commit()
        return jsonify({'message': 'Song updated!'})
    if request.method == 'DELETE':
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted!'})

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
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor.from_string(bg_color_hex)
            
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