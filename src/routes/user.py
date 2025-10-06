from flask import Blueprint, jsonify, request, session
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'E-mail já cadastrado'}), 400
        
        # Criar novo usuário
        user = User(
            name=data['name'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Conta criada com sucesso!'}), 201
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        # Buscar usuário pelo e-mail
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            # Salvar ID do usuário na sessão
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'E-mail ou senha incorretos'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@user_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Não autenticado'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/user-data', methods=['PUT'])
def update_user_data():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Não autenticado'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.json
        user.set_user_data(data)
        db.session.commit()
        
        return jsonify({'message': 'Dados salvos com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Manter rotas originais para compatibilidade
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
