import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from dotenv import load_dotenv
load_dotenv()
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_session import Session
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, supports_credentials=True)
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_SESSION_COOKIE_SECURE", "False").lower() == "true"
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("FLASK_SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Bloco para garantir a criação das tabelas e logging de conexão ao banco de dados (executado via comando de inicialização no Render)
with app.app_context():
    try:
        # Tenta conectar ao banco de dados para verificar a acessibilidade
        db.engine.connect()
        logging.info("Conexão com o banco de dados estabelecida com sucesso.")
        if os.getenv("FLASK_RUN_MIGRATIONS") == "true":
            logging.info("Executando db.create_all() para criar tabelas.")
            db.create_all()
        else:
            logging.info("Criação de tabelas ignorada. Defina FLASK_RUN_MIGRATIONS=true para executar.")
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        # Em caso de erro crítico, pode ser útil encerrar a aplicação para evitar mais problemas
        # sys.exit(1) # Descomente se quiser que a aplicação pare em caso de falha na DB

app.config["SESSION_SQLALCHEMY"] = db
session_flask = Session(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.register_blueprint(user_bp, url_prefix="/api")

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
