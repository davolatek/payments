from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY
import validators
from src.models import User, db
from werkzeug.security import generate_password_hash
users = Blueprint("users", __name__, url_prefix="/api/users/")


@users.post("/")
def create_user():
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    email = request.json["email"]
    phone_number = request.json["phone_number"]
    password = request.json["password"]

    if not first_name:
        return jsonify({"error": "First name is required"}), HTTP_422_UNPROCESSABLE_ENTITY
    if not last_name:
        return jsonify({"error": "Last name is required"}), HTTP_422_UNPROCESSABLE_ENTITY
    if not email:
        return jsonify({"error": "Email is required"}), HTTP_422_UNPROCESSABLE_ENTITY
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), HTTP_422_UNPROCESSABLE_ENTITY
    if not password:
        return jsonify({"error": "Password is required"}), HTTP_422_UNPROCESSABLE_ENTITY
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), HTTP_422_UNPROCESSABLE_ENTITY
    if not validators.email(email):
        return jsonify({"error": "Email is invalid"}), HTTP_422_UNPROCESSABLE_ENTITY

    # check if email exists

    user = User.query.filter_by(email=email).first()

    if user is not None:
        return jsonify({"error": "Email already exists"}), HTTP_409_CONFLICT

    # check if phone number exists
    user_phone = User.query.filter_by(phone_number=phone_number).first()
    if user_phone is not None:
        return jsonify({"error": "Phone number already exists"}), HTTP_409_CONFLICT

    # hash password
    hashed_pasword = generate_password_hash(password)

    user = User(first_name=first_name, last_name=last_name,
                email=email, phone_number=phone_number, password=hashed_pasword)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",


    }), HTTP_201_CREATED


@users.get("/")
def get_by_id():
    userid = request.args.get('userid', default = 1, type = int)
    print(userid)
    user = User.query.filter_by(id=userid).first()

    if user is None:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND
    else:
        return jsonify({
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }

            }), HTTP_200_OK
    
@users.put("/")
def update_by_id():
    id = request.args.get('userid', default = 1, type = int)
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    phone_number = request.json["phone_number"]
    password = request.json["password"]

    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND
    else:
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.password = generate_password_hash(password)
        db.session.commit()

        return jsonify({"message": "User successfully updated"}), HTTP_200_OK
    
@users.delete("/")
def delete_by_id():
    id = request.args.get('userid', default = 1, type = int)
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND
    else:
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User successfully deleted"}), HTTP_200_OK
    
