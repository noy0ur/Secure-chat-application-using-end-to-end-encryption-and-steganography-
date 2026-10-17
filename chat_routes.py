from flask import Blueprint, render_template, request, session, redirect, jsonify
from database.db import get_db
from modules.encryption import encrypt_message, decrypt_message
from modules.steganography import hide_data, extract_data
from modules.utils import save_image, allowed_file
import os

chat_bp = Blueprint('chat', __name__)


def login_required():
    return 'user_id' in session


# -------------------------
# Dashboard
# -------------------------
@chat_bp.route('/dashboard')
def dashboard():
    if not login_required():
        return redirect('/')

    conn = get_db()
    users = conn.execute(
        "SELECT * FROM users WHERE id != ?",
        (session['user_id'],)
    ).fetchall()

    return render_template('dashboard.html', users=users)


# -------------------------
# Chat Page
# -------------------------
@chat_bp.route('/chat/<int:user_id>')
def chat(user_id):
    if not login_required():
        return redirect('/')

    conn = get_db()

    messages = conn.execute("""
        SELECT * FROM messages 
        WHERE (sender_id=? AND receiver_id=?) 
        OR (sender_id=? AND receiver_id=?)
        ORDER BY timestamp ASC
    """, (session['user_id'], user_id, user_id, session['user_id'])).fetchall()

    return render_template(
        'chat.html',
        messages=messages,
        receiver_id=user_id,
        current_user=session['user_id']
    )


# -------------------------
# Send Message
# -------------------------
@chat_bp.route('/send', methods=['POST'])
def send():
    if not login_required():
        return redirect('/')

    file = request.files.get('image')
    message = request.form.get('message')
    key = request.form.get('key')
    receiver_id = request.form.get('receiver_id')

    if not file or not message or not key:
        return "Missing Data", 400

    if not allowed_file(file.filename):
        return "Invalid file type", 400

    try:
        # -------------------------
        # Save Image
        # -------------------------
        # save_image returns: uploads/filename.png
        relative_original_path = save_image(file)

        if not relative_original_path:
            return "File save failed", 500

        # Correct full path
        full_original_path = os.path.join("static", relative_original_path)

        # Ensure file exists
        if not os.path.exists(full_original_path):
            return f"File not found: {full_original_path}", 500

        # -------------------------
        # Encrypt Message
        # -------------------------
        encrypted = encrypt_message(message, key)

        # -------------------------
        # Create Stego Image
        # -------------------------
        filename = os.path.basename(relative_original_path)
        name, ext = os.path.splitext(filename)

        stego_filename = f"{name}_stego.png"

        # DB path
        stego_relative_path = os.path.join("uploads", stego_filename)

        # Actual file path
        full_stego_path = os.path.join("static", stego_relative_path)

        # Ensure upload folder exists
        os.makedirs(os.path.dirname(full_stego_path), exist_ok=True)

        # -------------------------
        # Hide Data
        # -------------------------
        hide_data(full_original_path, encrypted, full_stego_path)

        # -------------------------
        # Delete Original Image
        # -------------------------
        if os.path.exists(full_original_path):
            os.remove(full_original_path)

        # -------------------------
        # Save to DB
        # -------------------------
        conn = get_db()
        conn.execute(
            "INSERT INTO messages (sender_id, receiver_id, image_path) VALUES (?, ?, ?)",
            (session['user_id'], receiver_id, stego_relative_path)
        )
        conn.commit()

        return redirect(f"/chat/{receiver_id}")

    except Exception as e:
        return f"Error in send(): {str(e)}", 500


# -------------------------
# Decrypt Message
# -------------------------
@chat_bp.route('/decrypt', methods=['POST'])
def decrypt():
    if not login_required():
        return jsonify({"message": "Unauthorized"}), 401

    image_path = request.form.get('image_path')  # uploads/xxx.png
    key = request.form.get('key')

    if not image_path or not key:
        return jsonify({"message": "Invalid input"}), 400

    try:
        # Correct full path
        full_path = os.path.join("static", image_path)

        if not os.path.exists(full_path):
            return jsonify({"message": "Image not found"}), 404

        encrypted = extract_data(full_path)

        message = decrypt_message(encrypted, key)

        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500