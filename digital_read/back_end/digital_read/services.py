# here you can control you settings account
# change password #
# change username #
# change payment #
# change view theme, size,
# logout to delete session from database
#  terminate account

from flask import Blueprint, request, jsonify
from models.models import DatabaseManager


# --------------------route for logout-----------------------
logout_bp = Blueprint('logout_bp', __name__)


@logout_bp.route('/logout', methods=["POST"])
def Logout():

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        gate_way = db.token_gateway(None, None)
        if not gate_way:
            return jsonify({"message": "Access denied, login fast"}), 400
        else:
            # return content
            pass

    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 404

    # close database finally
    finally:
        db.close_connection()
