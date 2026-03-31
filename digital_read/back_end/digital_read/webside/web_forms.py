
from flask import Blueprint, request, jsonify, render_template
from models.models import DatabaseManager


# --------------------____________________________route for uploading content to cloud using hrml page_________________________________-----------------------
forms_bp = Blueprint(
    'forms_bp', __name__, template_folder='templates')


@forms_bp.route('/upload_content_to_cloud/<int:content_id>/<temp_token>/<email>', methods=["POST"])
def upload_content_to_cloud(content_id, temp_token, email):
    # get the tempolary token from the json post sent
    temp_token = temp_token

    # if there is no token then show 401 error message
    if not temp_token:
        return jsonify({"message": "Missing tokens"}), 401

    # access database
    db = DatabaseManager()

    # handle errors with try
    try:
        # get email associated to the tempolary token
        validated_tempolary_email = db.validate_temp_token(temp_token)

        # if email from frontend does not match email associated to tempolary token then show error 401
        if email != validated_tempolary_email:
            return jsonify({"message": "Invalid or expired token"}), 401

        # if the emails match then extcract data then delete token and delete the temporary token
        else:
            # get user details that will be saved along the uploaded content
            user_details = db.get_user_details(email)
            subscribed = db.user_subscribed(email)  # is user subscribed

            # get document with that specific id, also get user details with matching email
            document = db.one_document(content_id)
            pdf_reader = f"""document:{document} subscribed:{subscribed} user details:{user_details}"""

            # load the html page
            return render_template("upload_form.html"), 200

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        # 🧪 How to confirm (debug tip) this is added tempolarily
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:

        # close database
        db.close_connection()
