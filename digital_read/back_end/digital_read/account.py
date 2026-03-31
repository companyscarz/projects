#here you can control you settings account
# change password # 
# change username #
# change payment # 
# change view theme, size, 
# logout to delete session from database
#  terminate account

from flask import Blueprint, request, jsonify
from models.models import DatabaseManager


#--------------------_______________________________route for getting all media related to the user from database and user details______________________________-----------------------
my_content_bp = Blueprint('my_conten_bp', __name__)
@my_content_bp.route('/my_content', methods=["GET"])
def my_content():
    token = request.headers.get("token")#get the token from the json post sent
    #content_type = request.headers.get("content_type")#get the content type from the json post sent
    
    if not token:
        return jsonify({"message": "Missing token"}), 401
    
    db = DatabaseManager()
    try:    
        email = db.token_gateway(token) #enter token and email from request header, if true then continue else raise error
        user_details = db.get_user_details(email)#get user details and pass them along with the content

        if not email:
            return jsonify({"message": "Invalid or expired token"}),401
        
        else:
            documents = db.get_all_documents_by_email(email) # get users all documents, also get user details with matching email from token
            podcasts = db.get_all_podcasts_by_email(email) #get users  all podcasts, also get user details with matching email from token
            videos = db.get_all_videos_by_email(email) #get users all videos, also get user details with matching email from token
            return jsonify({
                "documents":documents,
                "podcasts":podcasts,
                "videos":videos,
                "user_details":user_details
            }), 200

    #except an error return error 500
    except Exception as e:
        print("SERVER ERROR:", e)
        #🧪 How to confirm (debug tip) this is added tempolarily
        #import traceback
        #traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
    
