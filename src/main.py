import os
import sys
from dotenv import load_dotenv
load_dotenv()
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_cors import CORS
from flask_session import Session # Importar Flask-Session
from src.models.user import db
from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, supports_credentials=True, origins=['https://caminho-fe-app-oficial.onrender.com'])

# Configurações da sessão
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "flask_session_"
app.config["SESSION_COOKIE_SECURE"] = True # Essencial para HTTPS em produção
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None" # Essencial para requisições cross-origin
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # Carrega a SECRET_KEY da variável de ambiente

# Inicializar Flask-Session
Session(app)

app.register_blueprint(user_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    if os.getenv("FLASK_RUN_MIGRATIONS") == "true":
        print("Executando db.create_all() para criar tabelas.")
        db.create_all()
    else:
        print("Criação de tabelas ignorada. Defina FLASK_RUN_MIGRATIONS=true para executar.")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
