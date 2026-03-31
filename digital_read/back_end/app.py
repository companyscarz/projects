from flask import Flask
from settings import Config

# importing blueprints
from digital_read.signup import signup_bp
from digital_read.login import login_bp
from digital_read.account import (my_content_bp)
from digital_read.services import (logout_bp)
from digital_read.get_content import (
    get_content_bp, one_content_bp, get_comments_bp)
from digital_read.save import (
    validate_upload_bp, save_upload_bp, generate_url_bp, verify_upload_bp)
# from digital_read.test_monkey import (
#    validate_upload_bp, save_upload_bp, generate_url_bp, verify_upload_bp)
from digital_read.reactions import (
    liked_content_bp, download_content_bp, comment_content_bp, delete_content_bp)
from digital_read.home import home_bp
from digital_read.wallet import (subscription_bp, wallet_bp)
from digital_read.viewer import (web_pdf_viewer_bp)

app = Flask(__name__)
app.config.from_object(Config)

# registering blueprints)
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(get_content_bp)
app.register_blueprint(get_comments_bp)
app.register_blueprint(one_content_bp)
app.register_blueprint(validate_upload_bp)
app.register_blueprint(save_upload_bp)
app.register_blueprint(generate_url_bp)
app.register_blueprint(liked_content_bp)
app.register_blueprint(download_content_bp)
app.register_blueprint(comment_content_bp)
app.register_blueprint(my_content_bp)
app.register_blueprint(home_bp)
# app.register_blueprint(validate_upload_edit_bp)
# app.register_blueprint(update_content_bp)
app.register_blueprint(delete_content_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(verify_upload_bp)
app.register_blueprint(web_pdf_viewer_bp)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=Config.port, host=Config.host)
