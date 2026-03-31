import uuid
import bcrypt
from flask import Blueprint, request, jsonify
from models.models import DatabaseManager


login_bp = Blueprint('login_bp', __name__)

# --- Hashing Utility Function (Using bcrypt) ---
def check_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plain-text password against a stored bcrypt hash."""
    try:
        # Bcrypt requires both the plain password and the hash to be bytes.
        plain_bytes = plain_password.encode('utf-8')
        # The stored hash from the database is a string, so we encode it back to bytes.
        hashed_bytes = hashed_password.encode('utf-8')
        
        # bcrypt.checkpw safely verifies the password against the hash
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except ValueError:
        # Handle cases where the stored hash might be corrupted or in the wrong format
        print("Error: Stored password hash is invalid.")
        return False
# -----------------------------------------------
    
#--------------------route-----------------------
@login_bp.route('/login', methods=["POST"])
def login():
    res = request.json
    email = res.get("email")
    password = res.get('password')
    
    
    #check if all fields are filled
    if not email or not password:
        return jsonify({"error":"Fill in all fields"}),400
    
    db = DatabaseManager()
    try:    
        # Get the user's record from the database
        conn = db.conn
        cursor = conn.cursor()
        # Assuming 'password' column holds the bcrypt hash
        cursor.execute("SELECT email, password FROM USER WHERE email = ?", (email,))
        user_record = cursor.fetchone()

        if user_record:
            db_email, stored_hash = user_record
                
            # --- SECURITY STEP: USE BCRYPT TO VERIFY THE PASSWORD ---
            # Compare the user's input password against the stored hash
            if check_password(password, stored_hash):

                #have to generate token then save it in SESSIONS then return 200 with message
                token = str(uuid.uuid4())
                db.add_session(email, token)
                return jsonify({"message":"Successfully logged in", "token": token}), 200
            
            else:
                # Incorrect password
                return jsonify({"error":"Incorrect password."}), 401
        else:
            # Email not found in the database
            return jsonify({"error":"Email not found in the database"}), 402
        

    #except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error":"An unexpected error occurred. Please try again."}), 404
    
    #close database finally
    finally:
        db.close_connection()