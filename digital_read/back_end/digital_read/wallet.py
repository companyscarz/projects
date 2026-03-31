from flask import Blueprint, request, jsonify
import uuid
import requests
from settings import Config
from models.models import DatabaseManager
from digital_read.payment_system.Mpesa import Mpesa_payment
from digital_read.payment_system.mobilemoney_payments import ugmobilemoney
from digital_read.payment_system.card_payment import card_payment


# --------------------___________________________route for subscribing to digital read_______________________________-----------------------
# first check if user is subscribed, if yes raise error 402 otherwise raise  200 and add subscription
subscription_bp = Blueprint('subscription_bp', __name__)


@subscription_bp.route('/subscribe', methods=["POST"])
def subscription():
    res = request.json
    # GET ALL THE DATA FROM THE JSON POST SENT
    token = res.get("client_token")  # get the token from the json post sent
    subscription_plan = res.get("subscription_plan")
    amount = res.get("amount")
    phone_number = res.get("phone_number")
    payment_method = res.get("payment_method")

    db = DatabaseManager()
    try:
        # enter token from request header and get related email, if exits then continue else raise error
        email = db.token_gateway(token)

        # get token of user through the email assigned to token
        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        # check if subscription plan is selected, if not raise error
        if not all([subscription_plan, amount, payment_method]):
            return jsonify({"message": "Some content is missing"}), 400

        else:
            # check if user is already subscribed, if yes raise error 402 otherwise continue to payment
            if db.user_subscribed(email):
                return jsonify({"message": "Already on a subscription plan."}), 402

            else:
                reason = f"{subscription_plan} by {email}"
                # since the mobile money payment function requires a tx_ref, we generate it here and pass it to the function
                tx_ref = f"DR-{uuid.uuid4()}"

                # create a pending payment in the database with the generated tx_ref, so that when the webhook is called after successful payment we can activate the subscription
                db.create_pending_payment(tx_ref=tx_ref, flw_ref=None, user_email=email, subscription_plan=subscription_plan,
                                          amount=amount, currency="UGX", payment_method=payment_method, status="pending")

                # check the payment method and call the respective function to make payment, if successful return 200 otherwise return 403
                if payment_method == "MPESA":
                    # charge customer through mpesa
                    success = Mpesa_payment(
                        amount=amount,
                        phone_number=phone_number,
                        email=email,
                        reason=reason,
                        tx_ref=tx_ref
                    )

                    if success:
                        return jsonify({
                            "status": "pending",
                            "message": "Payment initiated. Complete on your phone.",
                            "tx_ref": tx_ref
                        }), 200
                    else:
                        return jsonify(
                            {"error": "Payment failed"}), 403

                elif payment_method == "MOBILE MONEY":
                    # charge customer through mobile money
                    success = ugmobilemoney(
                        amount=amount,
                        phone_number=phone_number,
                        email=email,
                        reason=reason,
                        tx_ref=tx_ref
                    )

                    if success:
                        return jsonify({
                            "status": "pending",
                            "message": "Payment initiated. Complete on your phone.",
                            "tx_ref": tx_ref
                        }), 200
                    else:
                        return jsonify(
                            {"error": "Payment failed"}), 403

                elif payment_method == "CARD":
                    success = card_payment(amount=amount, email=email, card_number=request.json.get("card_number"), expiry_date=request.json.get("expiry_date"), CVV_password=request.json.get(
                        "CVV_password"), reason=reason, firstname=request.json.get("firstname"), lastname=request.json.get("lastname"), expirymonth=request.json.get("expirymonth"), phonenumber=phone_number)

                    if success:
                        return jsonify({
                            "status": "pending",
                            "message": "Payment initiated. Complete on your phone."
                        }), 200
                    else:
                        return jsonify(
                            {"error": "Payment failed"}), 403

    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# its called every time the user wants to check the status of their payment, it takes the tx_ref as a parameter and checks the database for the status of that payment, if found return the status otherwise return not found

@subscription_bp.route("/payment-status/<tx_ref>", methods=["GET"])
def payment_status(tx_ref):
    db = DatabaseManager()
    try:
        payment = db.get_payment_details(tx_ref)

        if not payment:
            return jsonify({"status": "not_found"}), 404

        return jsonify({"status": payment["status"]}), 200
    except Exception as e:
        print(f"payment-status error: {e}")
    finally:
        db.close_connection()


# --------------------___________________________route for wallet coins content_______________________________-----------------------
wallet_bp = Blueprint('wallet_bp', __name__)


@wallet_bp.route('/wallet', methods=["GET"])
def wallet():
    # get the token from the json post sent
    token = request.headers.get("token")
    # content_type = request.headers.get("content_type")#get the content type from the json post sent

    if not token:
        return jsonify({"message": "Missing token"}), 401

    db = DatabaseManager()
    try:
        # enter token and email from request header, if true then continue else raise error
        email = db.token_gateway(token)

        # get token of user through the email assigned to token
        authur = db.get_username(email)

        if not email:
            return jsonify({"message": "Invalid or expired token"}), 401

        else:

            # get the current points of this user
            points = db.get_points(authur)

            # since a coin is equal to 100 points
            coins = points // 100  # convert these points to coins

            if coins == 0:  # if the coins got from points are equal to 0 just reutrn the current coins and points number
                return jsonify({
                    "coins": db.get_coins(authur),
                    "points": db.get_points(authur)
                }), 200  # when no coin got then return nothing
            else:
                points_used = coins * 100  # calculate the used points

                # delete the points converted to a coin
                db.deduct_points(authur, points_used)
                db.add_coins(authur, coins)  # add coins that have been added

            return jsonify({
                "coins": db.get_coins(authur),
                "points": db.get_points(authur)
            }), 200

    # except an error return error 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

    # close database finally
    finally:
        db.close_connection()


# handles the webhook from flutterwave to activate subscription after payment is successful
webhook_bp = Blueprint("webhook_bp", __name__)


@webhook_bp.route("/flutterwave-webhook", methods=["POST"])
def flutterwave_webhook():

    secret_hash = Config.encryption_key
    signature = request.headers.get("verif-hash")

    if signature != secret_hash:
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.json
    data = payload.get("data", {})

    status = data.get("status")
    tx_ref = data.get("tx_ref")
    transaction_id = data.get("id")
    flw_ref = data.get("flw_ref")

    if status != "successful":
        return jsonify({"status": "ignored"}), 200

    db = DatabaseManager()

    try:
        # 🔐 Server-to-server verification
        verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

        headers = {
            "Authorization": f"Bearer {Config.rave_secret_key}"
        }

        response = requests.get(verify_url, headers=headers)
        result = response.json()

        if result.get("status") != "success":
            return jsonify({"error": "Verification failed"}), 400

        verify_data = result.get("data", {})
        verify_amount = verify_data.get("amount")
        verify_currency = verify_data.get("currency")
        verify_tx_ref = verify_data.get("tx_ref")

        payment = db.get_payment_details(tx_ref)

        # check if payment response was not succesful and raise 404 error
        if not payment:
            db.update_payment("failed", tx_ref, flw_ref)
            return jsonify({"error": "Payment not found"}), 404

        # if successful then continue verify with amount and currency if the same in database
        if (
            verify_data.get("status") == "successful"
            and verify_amount == payment["amount"]
            and verify_currency == payment["currency"]
            and verify_tx_ref == tx_ref
        ):

            # if the payment is successful and the status in database is still pending then activate subscription and update payment status to successful, if the status is not pending then it means the webhook has been called before and the subscription has been activated so just return ignored to prevent activating subscription twice
            if payment["status"] == "pending":

                db.subscribe(
                    payment["user_email"],
                    payment["subscription_plan"]
                )

                # update the payment status to successful and add the flutterwave reference to the database
                db.update_payment("successful", tx_ref, flw_ref)
                return jsonify({"status": "subscription activated"}), 200

        # update the payment to failed when something goes wrong
        db.update_payment("failed", tx_ref, flw_ref)
        return jsonify({"status": "payment ignored"}), 403

    except Exception as e:
        print("Webhook Error:", e)
        return jsonify({"error": "Server error"}), 500

    finally:
        db.close_connection()
