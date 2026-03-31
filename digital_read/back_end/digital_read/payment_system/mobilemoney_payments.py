from rave_python import Rave, RaveExceptions, Misc
from settings import Config
from digital_read.payment_system.payment_configs import get_ipaddress


rave = Rave(Config.rave_public_key, Config.rave_secret_key,
            production=Config.production, usingEnv=Config.usingEnv)


def ugmobilemoney(amount, email, phone_number, reason, tx_ref):
    payload = {
        "amount": amount,
        "email": email,
        "phonenumber": phone_number,
        "txRef": tx_ref,
        # CALL WHEN PAYMENT IS SUCCESSFUL
        # "redirect_url": "http://127.0.0.1:8080/payment-complete",
        "IP": get_ipaddress(),
        "narration": reason
    }

    try:
        charge_response = rave.UGMobile.charge(payload)
        print("Charge Response:", charge_response)

        if charge_response.get("status") == "success":
            return {
                "status": "pending",
                "tx_ref": tx_ref
            }
        else:
            return False

    except Exception as e:
        print("Payment Error:", e)
        return False
