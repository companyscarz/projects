from rave_python import Rave, RaveExceptions, Misc
from settings import Config
from digital_read.payment_system.payment_configs import get_ipaddress


rave = Rave(Config.rave_public_key, Config.rave_secret_key,
            production=Config.production, usingEnv=Config.usingEnv)


def Mpesa_payment(amount, phone_number, email, reason, tx_ref):
    # mpesa payload
    payload = {
        "amount": amount,
        "phonenumber": phone_number,
        "email": email,
        # "redirect_url": "http://127.0.0.1:8080/flutterwave-webhook",
        "txRef": tx_ref,
        # have imported the function that will call our ip address from the payment_config file
        "IP": get_ipaddress(),
        "narration": reason,
    }

    try:
        res = rave.Mpesa.charge(payload)

        print("Charge Response:", res)

        if res.get("status") == "success":
            return {
                "status": "pending",
                "tx_ref": tx_ref
            }
        else:
            return False

    except Exception as e:
        print("Payment Error:", e)
        return False
