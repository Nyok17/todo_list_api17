from flask import Blueprint, request, jsonify
from models import User, Todo
from extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


auth_bp = Blueprint('auth', __name__)
todo_bp = Blueprint('todos', __name__)


@auth_bp.route('/')
def home():
    """A function to display the default route"""
    return "Hello Auth!"

@auth_bp.route('/register', methods=['POST'])
def register_users():
    """A function to register and save users to db"""
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data or 'password' not in data:
            raise ValueError("Name, email and password are required")
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already exists")
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(name=data['name'], email=data['email'], password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        }), 201
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login_users():
    """A function to login users using email and password"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            raise ValueError("Email and password are required")
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            raise ValueError("Wrong email or password")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "status": "success",
            "message": "Logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


#todo routes
@todo_bp.route('/add', methods=['POST'])
@jwt_required()
def add_todo():
    """A function to add and save a todo in the db"""
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())

        if not user_id:
            raise ValueError("Invalid or missing token")
        if not data or 'title' not in data or 'description' not in data:
            raise ValueError("Title and description are required")
        
        new_todo = Todo(title=data['title'], description=data['description'], user_id = user_id)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Todo added successfully"
        }), 201
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
    
@todo_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    """A function to retrieve all the todos"""
    try:
        user_id = int(get_jwt_identity())

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        if per_page > 100:
            per_page = 100

        query = Todo.query.filter_by(user_id=user_id)
        total = query.count()
        todos = query.offset((page - 1) * per_page).limit(per_page).all()
        todos_list = [{"id": todo.id, "title": todo.title, "description": todo.description, "completed": todo.completed, "date": todo.created_at, "user_id": todo.user_id}for todo in todos]

        return jsonify({
            "status": "success",
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "todos": todos_list
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
        }), 500
    
@todo_bp.route('/todos/<int:id>', methods=['GET'])
@jwt_required()
def get_todo(id):
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(user_id=user_id, id=id).first()

        return jsonify({
            "status": "success",
            "todo": [{
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "date": todo.created_at,
                "completed": todo.completed,
                "user_id": todo.user_id
        }]
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
    
@todo_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
    """A function to update a todo"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data or 'title' not in data or 'description' not in data:
            raise ValueError("Title and description are required")
        todo = Todo.query.filter_by(user_id=user_id, id=id).first_or_404()

        if 'title' in data:
           todo.title = data['title']
        if 'description' in data:
           todo.description = data['description']

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Todo: {id} updated successfully"
        }), 200
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
    
@todo_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_todo(id):
    try:
        user_id = int(get_jwt_identity())
        todo = Todo.query.filter_by(user_id=user_id, id=id).first()
        db.session.delete(todo)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Todo: {id} deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


