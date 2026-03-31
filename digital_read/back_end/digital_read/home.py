from flask import Blueprint, request, jsonify
from models.models import DatabaseManager

# --------------------_______________________________route for getting all media related to the user from database and user details______________________________-----------------------
home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/home', methods=["GET"])
def home():
    # get the token from the json post sent
    token = request.headers.get("token")
    # content_type = request.headers.get("content_type")#get the content type from the json post sent

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)
        # get user details and pass them along with the content
        user_details = db.get_user_details(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            # get users all highly liked content
            return jsonify({
                "message": "get the content",
                "user_details": user_details
            }), 200

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        # 🧪 How to confirm (debug tip) this is added tempolarily
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
