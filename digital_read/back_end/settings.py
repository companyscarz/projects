import secrets

# from users.models.models_company import COmpany


class Config():
    SECRET_KEY = secrets.token_hex(4020)
    DEBUG = True
    host = '0.0.0.0'
    port = 8080

    ## ---------wasabi settings----------------##
    region_name = 'ap-northeast-1'
    wasabi_access_key = 'U3CV76VMLWJXQNM5QVG8'
    wasabi_secret_key = '7VSi9r2z8LtUp6fD1efOsrJhXn8D5BCHiGAMPnbI'
    wasabi_bucket_name = 'digitalread'
    # ----cover upload url-----#

    # Backblaze cloud
    Backblaze_keyID = "396d9b4c9454"
    Backblaze_bucketname = "digitalread"
    Backblaze_applicationKey = "005cbe83f658d2e17c5aa5b9301e468d3fb84002cd"
    Backblaze_endpoint = "https://s3.us-east-005.backblazeb2.com"

    # rave python flutterwave settings
    rave_public_key = 'FLWPUBK_TEST-04671e8a01a8969a5f8b10eaaa969c86-X'
    rave_secret_key = 'FLWSECK_TEST-388026004ea7665f31fd5425da03ce2e-X'
    encryption_key = 'FLWSECK_TESTbd01a68baa23'
    usingEnv = False
    production = False
