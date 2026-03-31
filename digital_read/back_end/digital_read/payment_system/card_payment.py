from rave_python import Rave, RaveExceptions, Misc
from settings import Config
from digital_read.payment_system.payment_configs import get_ipaddress


rave = Rave(Config.rave_public_key, Config.rave_secret_key,
            production=Config.production, usingEnv=Config.usingEnv)
# account payload


def card_payment(amount, email, card_number, expiry_date, CVV_password, reason, firstname, lastname, expirymonth, phonenumber):
    # Payload with pin
    payload = {
        "cardno": card_number,
        "cvv": CVV_password,
        "expirymonth": expirymonth,
        "expiryyear": expiry_date,
        "amount": amount,
        "email": email,
        "phonenumber": phonenumber,
        "firstname": firstname,
        "lastname": lastname,
        "IP": get_ipaddress(),
        "narration": reason
    }

    try:
        res = rave.Card.charge(payload)

        if res["suggestedAuth"]:
            arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])

            if arg == "pin":
                Misc.updatePayload(res["suggestedAuth"], payload, pin="3310")
            if arg == "address":
                Misc.updatePayload(res["suggestedAuth"], payload, address={
                                   "billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})

            res = rave.Card.charge(payload)

        if res["validationRequired"]:
            rave.Card.validate(res["flwRef"], "")

        res = rave.Card.verify(res["txRef"])
        print(res["transactionComplete"])
        return True

    except RaveExceptions.CardChargeError as e:
        print(e.err["errMsg"])
        print(e.err["flwRef"])
        return False

    except RaveExceptions.TransactionValidationError as e:
        print(e.err)
        print(e.err["flwRef"])
        return False

    except RaveExceptions.TransactionVerificationError as e:
        print(e.err["errMsg"])
        print(e.err["txRef"])
        return False
