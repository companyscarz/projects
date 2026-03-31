# here you can control reactions for content
# like #
# viewed #
# download #
# comment
# more_content

from flask import Blueprint, request, jsonify
from models.models import DatabaseManager
import requests


# --------------------______________________route for comment on content_____________________________-----------------------
comment_content_bp = Blueprint('comment_content_bp', __name__)


@comment_content_bp.route('/comment_content', methods=["POST"])
def comment_content():
    res = request.json
    token = res.get("token")
    content_type = res.get("content_type")
    comment = res.get("comment")
    content_id = res.get("content_id")
    username = res.get("username")

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)
        # get user id using email assigned to token
        user_id = db.get_user_id(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401
        else:
            print(user_id, content_id, comment, content_type, username)
            db.add_comment(user_id, content_id, comment,
                           content_type, username)
            return jsonify({"message": "comment saved"}), 200
    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# --------------------___________________________route for liked content_______________________________-----------------------
liked_content_bp = Blueprint('liked_content_bp', __name__)


@liked_content_bp.route('/like_content', methods=["POST"])
def liked_content():

    res = request.json
    token = res.get("token")
    content_type = res.get("content_type")
    content_id = res.get("content_id")

    db = DatabaseManager()
    reaction_points = 10

    try:
        email = db.token_gateway(token)
        # get user id using email assigned to token
        user_id = db.get_user_id(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        # ⭐ STOP HERE IF ALREADY LIKED
        if db.liked_already(
                content_id=content_id,
                user_id=user_id,
                content_type=content_type
        ):
            # then unlike the document but has no effect on points it helps in showing if one like or not
            db.content_unlike(
                content_id=content_id,
                user_id=user_id,
                content_type=content_type
            )
            return jsonify({
                "message": "Already liked — no extra points given"
            }), 203

        # ⭐ FIRST TIME LIKE
        db.content_liked(
            content_id=content_id,
            user_id=user_id,
            content_type=content_type
        )

        # reward the authur of the content
        if content_type == "DOCUMENT":
            authur = db.document_authur(content_id)
            # reward add points to the owner of the post
            db.add_points(authur, reaction_points)
            return jsonify({
                "message": "Content liked + points added"
            }), 200

        if content_type == "PODCAST":
            authur = db.podcast_authur(content_id)
            # reward add points to the owner of the post
            db.add_points(authur, reaction_points)
            return jsonify({"message": "downloaded"}), 200

        if content_type == "VIDEO":
            authur = db.video_authur(content_id)
            db.video_authur(content_id)
            # reward add points to the owner of the post
            db.add_points(authur, reaction_points)
            return jsonify({"message": "downloaded"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        db.close_connection()


# --------------------_________________________route for download content__________________________-----------------------
download_content_bp = Blueprint('download_content_bp', __name__)


@download_content_bp.route('/download_content', methods=["POST"])
def download_content():
    res = request.json
    token = res.get("token")
    content_type = res.get("content_type")
    content_id = res.get("content_id")

    db = DatabaseManager()
    reaction_points = 15

    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)
        # get user id using email assigned to token
        user_id = db.get_user_id(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401
        else:
            if db.downloaded_already(
                content_id=content_id,
                person_id=user_id,
                content_type=content_type
            ):
                return jsonify({"message": "Already downloaded"}), 402
            else:
                db.download_content(
                    content_id=content_id,
                    person_id=user_id,
                    content_type=content_type
                )

                if content_type == "DOCUMENT":
                    authur = db.document_authur(content_id)
                    # reward add points to the owner of the post
                    db.add_points(authur, reaction_points)
                    return jsonify({"message": "downloaded"}), 200

                if content_type == "PODCAST":
                    authur = db.podcast_authur(content_id)
                    # reward add points to the owner of the post
                    db.add_points(authur, reaction_points)
                    return jsonify({"message": "downloaded"}), 200

                if content_type == "VIDEO":
                    authur = db.video_authur(content_id)
                    db.video_authur(content_id)
                    # reward add points to the owner of the post
                    db.add_points(authur, reaction_points)
                    return jsonify({"message": "downloaded"}), 200

    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# --------------------__________________________route for viewed content______________________________-----------------------
view_content_bp = Blueprint('view_content_bp', __name__)


@view_content_bp.route('/view_content', methods=["POST"])
def view_content():
    res = request.json
    token = res.get("token")
    content_type = res.get("content_type")
    content_id = res.get("content_id")

    db = DatabaseManager()
    reaction_points = 15

    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)
        # get user id using email assigned to token
        user_id = db.get_user_id(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401
        else:
            db.view_content(
                person_id=user_id,
                content_id=content_id,
                content_type=content_type
            )
            # add points to the person of the content.. so its content_owner_id

            if content_type == "DOCUMENT":
                authur = db.document_authur(content_id)
                # reward add points to the owner of the post
                db.add_points(authur, reaction_points)
                return jsonify({"message": "downloaded"}), 200

            if content_type == "PODCAST":
                authur = db.podcast_authur(content_id)
                # reward add points to the owner of the post
                db.add_points(authur, reaction_points)
                return jsonify({"message": "downloaded"}), 200

            if content_type == "VIDEO":
                authur = db.video_authur(content_id)
                db.video_authur(content_id)
                # reward add points to the owner of the post
                db.add_points(authur, reaction_points)
                return jsonify({"message": "downloaded"}), 200

    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# ______________________________------------------------update the cover and file details in database------------------------------___________________________#
delete_content_bp = Blueprint('delete_content_bp', __name__)


@delete_content_bp.route('/delete_content', methods=['POST'])
def update_content():
    # get data from request
    res = request.json
    token = res.get("token")
    content_type = res.get("content_type")  # VIDEO/PODCAST/DOCUMENT
    content_id = res.get("content_id")  # get the id of the content

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()

    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)

        # if no email is returned then the token does not exist so, return 401 error
        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            # call db function that deletes the specific content
            db.delete_content(
                content_id=content_id,
                email=email,
                content_type=content_type
            )

            # db.remove_likes_for_removed_conent(content_id, content_type)
            # db.remove_downloads_for_removed_conent(content_id, content_type)
            # db.remove_views_for_removed_conent(content_id, content_type)
            return jsonify({"message": "Content deleted successfully"}), 200

    # except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        # 🧪 How to confirm (debug tip) this is added tempolarily
        # import traceback
        # traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

    # close database
    finally:
        db.close_connection()
