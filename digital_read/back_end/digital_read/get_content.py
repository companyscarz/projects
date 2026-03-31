from flask import Blueprint, request, jsonify
from models.models import DatabaseManager

# --------------------_______________________________route for getting all media from database and user details______________________________-----------------------
get_content_bp = Blueprint('get_content_bp', __name__)


@get_content_bp.route('/get_content/<content_type>', methods=["GET"])
def get_content(content_type):
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
        subscribed = db.user_subscribed(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            if content_type == "DOCUMENT":
                # if its document, get all documents, also get user details with matching email from token
                documents = db.get_all_documents(limit_count=10)
                return jsonify({
                    "documents": documents,
                    "user_details": user_details,
                    "subscribed": subscribed
                }), 200

            elif content_type == "PODCAST":
                # if its podcast, get all podcasts, also get user details with matching email from token
                podcasts = db.get_all_podcasts(limit_count=10)
                return jsonify({
                    "podcasts": podcasts,
                    "user_details": user_details,
                    "subscribed": subscribed
                }), 200

            elif content_type == "VIDEO":
                # if its video, get all videos, also get user details with matching email from token
                videos = db.get_all_videos(limit_count=10)
                return jsonify({
                    "videos": videos,
                    "user_details": user_details,
                    "subscribed": subscribed
                }), 200

            else:
                return jsonify({"message": "Invalid content type"}), 400

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        # 🧪 How to confirm (debug tip) this is added tempolarily
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# --------------------____________________________route for getting one  media content from database by id_________________________________-----------------------
one_content_bp = Blueprint('one_content_bp', __name__)


@one_content_bp.route('/one_content/<int:content_id>/<content_type>', methods=["GET"])
def one_content(content_id, content_type):
    # get the token from the json post sent
    token = request.headers.get("token")

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            # get user details and pass them along with the content
            user_details = db.get_user_details(email)
            subscribed = db.user_subscribed(email)  # check is user subscribed

            temp_token = db.create_temp_token(
                email=email, content_type=content_type, content_id=content_id)

            if content_type == "DOCUMENT":  # if its document, get document with that specific id, also get user details with matching email from token
                documents = db.one_document(content_id)
                # GET THE TEMP TOKEN THAT ALLOWS ONE TO VIEW DOCUMENT ON BROWSER
                return (jsonify({
                    "documents": documents,
                    "user_details": user_details,
                    "subscribed": subscribed,
                    "temp_token": temp_token
                }), 200)

            elif content_type == "PODCAST":  # if its podcast, get podcast with that specific id, also get user details with matching email from token
                podcasts = db.one_podcast(content_id)
                return jsonify({
                    "podcasts": podcasts,
                    "user_details": user_details,
                    "subscribed": subscribed
                }), 200

            elif content_type == "VIDEO":  # if its video, get videos with that specific id, also get user details with matching email from token
                videos = db.one_video(content_id)
                return jsonify({
                    "videos": videos,
                    "user_details": user_details,
                    "subscribed": subscribed
                }), 200

            else:
                return jsonify({"message": "Invalid content type"}), 400

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        # 🧪 How to confirm (debug tip) this is added tempolarily
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "Internal server error... {e}"}), 500

    # close database finally
    finally:
        db.close_connection()


# --------------------__________________________________route for getting all comments from database_______________________________-----------------------
get_comments_bp = Blueprint('get_comments_bp', __name__)


@get_comments_bp.route('/get_comments/<content_type>/<int:content_id>', methods=["GET"])
def get_commtent(content_type, content_id):
    # get the token from the json post sent
    token = request.headers.get("token")
    # content_type = request.headers.get("content_type")#get the content type from the json post sent

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            get_comments = db.get_comments(content_id, content_type)
            return jsonify({
                "get_comments": get_comments,
            }), 200

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()
