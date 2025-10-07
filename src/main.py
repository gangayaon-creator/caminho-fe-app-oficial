import os
import sys
from dotenv import load_dotenv
load_dotenv()
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from flask_session import Session # LINHA NOVA

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), \'static\'))
CORS(app, supports_credentials=True)
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_SESSION_COOKIE_SECURE", "False").lower() == "true"
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("FLASK_SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_TYPE"] = "sqlalchemy" # LINHA NOVA

# Configuração do banco de dados deve vir antes da inicialização da sessão
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), \'database\', \'app.db\')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

app.config["SESSION_SQLALCHEMY"] = db # LINHA NOVA
session_flask = Session(app) # LINHA NOVA: Inicializa a extensão Flask-Session

app.config[\'SECRET_KEY\'] = os.getenv(\'SECRET_KEY\')

app.register_blueprint(user_bp, url_prefix=\'/api\')

@app.route(\'/\', defaults={\'path\': \'\'}) # Removido o comentário
@app.route(\'/<path:path>\') # Removido o comentário
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, \'index.html\')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, \'index.html\')
        else:
            return "index.html not found", 404


if __name__ == \'__main__\':
    app.run(host=\'0.0.0.0\', port=5000, debug=True)
