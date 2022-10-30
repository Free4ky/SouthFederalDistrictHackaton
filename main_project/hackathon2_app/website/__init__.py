from flask import Flask


UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = ';lkawiyv78324b'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app
