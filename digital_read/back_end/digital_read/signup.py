import uuid
import bcrypt
from flask import Blueprint, request, jsonify
from models.models import DatabaseManager

signup_bp = Blueprint('signup_bp', __name__)

# ------------------ Utilities ------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

# ------------------ Route ------------------
@signup_bp.route('/signup', methods=['POST'])
def Signup():
    res = request.json
    username= res.get("username")
    email = res.get("email")
    password = res.get('password')
    
    db = DatabaseManager()

    try:    
        #check if all fields are filled
        if not email or not password or not username:
            return jsonify({"error":"Fill in all fields"}),400
        
        #check if password if more than 6 characters.. make it stronger later
        if len(password) < 6:
            return jsonify({"error":"Password must be at least 6 characters."}), 401
        
        #check if email is correct error 402 if its wrong

        #check in db if email exists
        elif db.email_exists(email):
            return jsonify({"error":"Email already in use."}), 403
        
        #check in db if username exists
        elif db.username_exists(username):
            return jsonify({"error":"User name already in use."}), 405
        
        #add user when everything is correct
        else:
            hashed_password = hash_password(password) #encrypt the password
            relative_path="https://picsum.photos/200/300"#no default profile picture, but one will change in seetings
            db.add_user(username=username, email=email, password=hashed_password, profile_path=relative_path)

            #have to generate token then save it in SESSIONS then pass return
            token = str(uuid.uuid4())
            db.add_session(email, token)
            return jsonify({"message":"Account Created successfully.","token":token}), 200

    #except an error return error 404
    except Exception as e:
        return jsonify({"error":"An unexpected error occurred. Please try again."}), 404
    
    #close database finally
    finally:
        db.close_connection()
    
