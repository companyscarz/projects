from flask import request, Blueprint, jsonify
import boto3
import os
import uuid
from models.models import DatabaseManager
from settings import Config


def generate_unique_filename(original_filename: str) -> str:
    """
    Generates a unique filename using UUID while keeping the original extension.
    Args:
        original_filename (str): The original filename, e.g., "mydoc.pdf"

    Returns:
        str: A unique filename, e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf"
    """
    # Split the filename into name and extension
    name, ext = os.path.splitext(original_filename)

    # Generate a UUID string
    unique_id = str(uuid.uuid4())

    # Combine UUID and original extension
    return f"{unique_id}{ext}"

# ---------- Helper: Extension Check ----------


def is_allowed(filename, file_type):
    allowed = {
        'image': {'png', 'jpg', 'jpeg', 'gif'},
        'VIDEO': {'mp4', 'webm', 'mkv'},
        'PODCAST': {'mp3', 'wav', 'ogg'},
        'DOCUMENT': {'pdf', 'docx', 'doc', 'epub', 'txt'}
    }
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed[file_type]


validate_upload_bp = Blueprint('validate_upload_bp', __name__)


@validate_upload_bp.route('/validate_cover', methods=['POST'])
def validate_cover():
    # get data from request
    res = request.json
    token = res.get("token")
    cover_photo = res.get("cover_photo")  # cover_photot object.. the file name
    upload_type = res.get("upload_type")  # VIDEO/PODCAST/DOCUMENT

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
            # Missing required fields.
            if not all([upload_type, cover_photo]):
                return jsonify({"error": "Missing required fields"}), 400

            # Invalid cover image format.
            if not is_allowed(cover_photo, 'image'):
                return jsonify({"error": "Invalid cover image format"}), 406

            # when the cover photo is valid
            else:
                # generate_unique_filename
                cover_name = generate_unique_filename(cover_photo)

                # return the generated cover names according to upload type
                if upload_type == 'VIDEO':
                    return jsonify({"UUID_cover_name": cover_name}), 200
                elif upload_type == 'DOCUMENT':
                    return jsonify({"UUID_cover_name": cover_name}), 200
                elif upload_type == 'PODCAST':
                    return jsonify({"UUID_cover_name": cover_name}), 200

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

# _______________________-------------here we validate the actual content-------------_______________________________________________


@validate_upload_bp.route('/validate_content', methods=['POST'])
def validate_content():
    # get data from request
    res = request.json
    token = res.get("token")
    title = res.get("title")
    theme = res.get("theme")
    level = res.get("level")
    description = res.get("description")
    access_type = res.get("access_type")  # free or subscribale
    upload_type = res.get("upload_type")  # VIDEO/PODCAST/DOCUMENT
    media = res.get("media")  # media object... file name

    if not token:
        return jsonify({"error": "Missing token"}), 401

    db = DatabaseManager()

    try:
        # enter token and get associated email from request header, if true then continue else raise error
        email = db.token_gateway(token)

        # if no email is returned then the token does not exist so, return 401 error
        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:
            # Missing required fields.
            if not all([title, theme, description, level, upload_type, access_type, media]):
                return jsonify({"error": "Missing required fields"}), 400

            if access_type not in ("free", "paid"):
                return jsonify({"error": "Invalid access type"}), 400

            # check media type extension and validate
            if upload_type == 'VIDEO' and not is_allowed(media, 'VIDEO'):
                return jsonify({"error": "Invalid VIDEO format"}), 422
            elif upload_type == 'PODCAST' and not is_allowed(media, 'PODCAST'):
                return jsonify({"error": "Invalid PODCAST format"}), 422
            elif upload_type == 'DOCUMENT' and not is_allowed(media, 'DOCUMENT'):
                return jsonify({"error": "Invalid DOCUMENT format"}), 422
            # when media is valid
            else:
                if upload_type == 'VIDEO':
                    video_name = generate_unique_filename(media)
                    # generate presigned urls for wasabi upload
                    return jsonify({"UUID_video_name": video_name}), 200

                elif upload_type == 'DOCUMENT':
                    document_name = generate_unique_filename(media)
                    return jsonify({"UUID_document_name": document_name}), 200

                elif upload_type == 'PODCAST':
                    podcast_name = generate_unique_filename(media)
                    return jsonify({"UUID_podcast_name": podcast_name}), 200

                else:
                    return jsonify("error", "invalid upload type"), 403

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


# ______________________________-----------save the media file names  to database and update the cover image------------------------------___________________________#
save_upload_bp = Blueprint('save_upload_bp', __name__)


@save_upload_bp.route('/save_content', methods=['POST'])
def save_content():
    # get data from request
    res = request.json
    token = res.get("token")
    title = res.get("title")
    theme = res.get("theme")
    level = res.get("level")
    description = res.get("description")
    access_type = res.get("access_type")  # free or subscribale
    file_path = res.get("file_path")  # media object... uuid file name
    upload_type = res.get("upload_type")  # VIDEO/PODCAST/DOCUMENT

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
            # get the name of the authur.. the one posting
            authur = db.get_username(email)
            # Missing required fields.
            if not all([title, theme, description, level, upload_type, access_type, file_path]):
                return jsonify({"error": "Missing required details"}), 400

            # default cover image if the user does not upload one
            default_cover_pic = "https://picsum.photos/200/200?random=1"

            if upload_type == 'VIDEO':
                db.add_content(content_type=upload_type, title=title, theme=theme, level=level, description=description,
                               cover_path=default_cover_pic, file_path=file_path, email=email, authur=authur, access_type=access_type)
                return jsonify({"message": "Video upload saved successfully"}), 200

            elif upload_type == 'DOCUMENT':
                db.add_content(content_type=upload_type, title=title, theme=theme, level=level, description=description,
                               cover_path=default_cover_pic, file_path=file_path, email=email, authur=authur, access_type=access_type)
                return jsonify({"message": "document upload saved successfully"}), 200

            elif upload_type == 'PODCAST':
                db.add_content(content_type=upload_type, title=title, theme=theme, level=level, description=description,
                               cover_path=default_cover_pic, file_path=file_path, email=email, authur=authur, access_type=access_type)
                return jsonify({"message": "Podcast upload saved successfully"}), 200
            else:
                pass

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


# _______________________----------this is for saving and updating cover______________-------------------------
@save_upload_bp.route('/save_cover_pic', methods=['POST'])
def save_cover_pic():
    # get data from request
    res = request.json
    token = res.get("token")
    # cover_photo object.. the uuid generated file name
    cover_path = res.get("cover_photo")
    file_path = res.get("media")  # media object... uuid generated file name
    upload_type = res.get("upload_type")  # VIDEO/PODCAST/DOCUMENT

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
            # Missing required fields.
            if not all([upload_type, cover_path, file_path]):
                return jsonify({"error": "Missing required details"}), 400

            if upload_type == 'VIDEO':
                db.update_save_cover(
                    content_type=upload_type, cover_path=cover_path, file_path=file_path, email=email)
                # generate presigned urls for wasabi upload
                return jsonify({"message": "Cover photo for video upload saved successfully"}), 200

            elif upload_type == 'DOCUMENT':
                db.update_save_cover(
                    content_type=upload_type, cover_path=cover_path, file_path=file_path, email=email)
                return jsonify({"message": "document cover photo upload saved successfully"}), 200

            elif upload_type == 'PODCAST':
                db.update_save_cover(
                    content_type=upload_type, cover_path=cover_path, file_path=file_path, email=email)
                return jsonify({"message": "Podcast cover photo upload saved successfully"}), 200

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


# _________________________-----------------------cloud storage credentials-----------------------------_______________________________
# CLOUD_REGION = Config.region_name
CLOUD_ENDPOINT_URL = Config.Backblaze_endpoint
CLOUD_ACCESS_KEY = Config.Backblaze_keyID
CLOUD_SECRET_KEY = Config.Backblaze_applicationKey
CLOUD_BUCKET_NAME = Config.Backblaze_bucketname

# configure client with signature version version 4 for wasabi compatibility
session = boto3.session.Session()
s3_client = session.client(
    "s3",
    endpoint_url=CLOUD_ENDPOINT_URL,
    aws_access_key_id=CLOUD_ACCESS_KEY,
    aws_secret_access_key=CLOUD_SECRET_KEY,
    # signature_version="s3v4"
)

generate_url_bp = Blueprint("generate_url_bp", __name__)


@generate_url_bp.route("/generate-upload-urls", methods=["POST"])
def generate_upload_urls():

    res = request.json
    token = res.get("token")
    media_uuid_name = res.get("media_uuid_name")

    if not token:
        return jsonify({"message": "Missing token"}), 401

    if not media_uuid_name:
        return jsonify({"message": "Missing filenames"}), 400

    db = DatabaseManager()

    try:
        # Validate token
        email = db.token_gateway(token)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        # ⭐ Generate media Upload URL
        media_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": CLOUD_BUCKET_NAME,
                "Key": media_uuid_name
            },
            ExpiresIn=3600
        )
        print(s3_client.list_buckets())
        return jsonify({
            "media_url": media_url
        }), 200

    except Exception as e:
        print("Error generating presigned URLs:", e)
        return jsonify({"error": "Could not generate presigned URLs"}), 500

    finally:
        db.close_connection()


# function to confirm file was uploaded to wasabi cloud
verify_upload_bp = Blueprint("verify_upload_bp", __name__)


@verify_upload_bp.route("/verify_upload", methods=["POST"])
def verify_upload():

    res = request.json
    token = res.get("token")
    # the name of the file that was uploaded to wasabi
    uploaded_name = res.get("uploaded_name")

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()

    try:
        email = db.token_gateway(token)

        if not email:
            return jsonify({"message": "Invalid token"}), 401

        # 🔥 Check if objects exist in Wasabi
        s3_client.head_object(Bucket=CLOUD_BUCKET_NAME, Key=uploaded_name)

        return jsonify({"message": "Upload verified"}), 200

    except Exception as e:
        if "404" in str(e):
            return jsonify({"error": "File not found in storage"}), 404
        else:
            print("Verify error:", e)
            return jsonify({"error": "Verification failed"}), 500

    finally:
        db.close_connection()
