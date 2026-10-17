import os
import uuid
from config import Config
from werkzeug.utils import secure_filename

# Allowed image types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Max file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


# -------------------------
# Check file extension
# -------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------
# Save image safely
# -------------------------
def save_image(file):
    if not file:
        return None

    # Check extension
    if not allowed_file(file.filename):
        return None

    # Ensure upload folder exists (static/uploads)
    upload_folder = Config.UPLOAD_FOLDER
    os.makedirs(upload_folder, exist_ok=True)

    # Secure filename
    filename = secure_filename(file.filename)

    # Generate unique name
    unique_name = f"{uuid.uuid4()}_{filename}"

    # Full path (static/uploads/filename)
    full_path = os.path.join(upload_folder, unique_name)

    try:
        # Save file
        file.save(full_path)

        # OPTIONAL: Check file size
        if os.path.getsize(full_path) > MAX_FILE_SIZE:
            os.remove(full_path)
            return None

        # Return relative path (VERY IMPORTANT)
        # Example: uploads/abc.png
        return f"uploads/{unique_name}"

    except Exception as e:
        print("Error saving image:", str(e))
        return None