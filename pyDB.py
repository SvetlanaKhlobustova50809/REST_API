from flask import Flask, request, jsonify
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from validate_email_address import validate_email
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import  Integer, String, Column

app = Flask(__name__)

USERNAME = "postgres"  # замените на свой логин

connection_string = f"postgresql+psycopg2://{USERNAME}:@localhost:5433/{USERNAME}"
engine = create_engine(connection_string)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    token = Column(String(1000), nullable=True)
    
Base.metadata.create_all(engine)
def access_token(user):
    token = jwt.encode({"user_id": user.user_id}, "secret_key", algorithm="HS256")
    try:
        decoded = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return token
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.json['email']
    password = request.json['password']

    # Проверка валидности email
    if not validate_email(email):
        return jsonify({"error": "Invalid email"}), 400

    user = session.query(User).filter_by(email=email).first()
    if user:
        return jsonify({"error": "User with this email already exists"}), 400

    if len(password) < 8:
        return jsonify({"error": "Weak password"}), 400
    
    new_user = User(email=email, password=generate_password_hash(password))
    session.add(new_user)
    session.commit()
    
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in "!@#$%^&*()-_+=~`[]{}|;:,.<>?/" for char in password)
    if has_upper and has_lower and has_digit and has_special:
        return jsonify({"user_id": new_user.user_id, "password_check_status": "perfect"}), 200
    else:
        return jsonify({"user_id": new_user.user_id, "password_check_status": "good"}), 200

@app.route('/authorize', methods=['GET','POST'])
def authorize():
    email = request.json['email']
    password = request.json['password']

    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = access_token(user)
    user.token = token
    session.commit()
    return jsonify({"access_token": token}), 200


@app.route('/feed', methods=['GET','POST'])
def feed():
    token = session.query(User).order_by(User.user_id.desc()).limit(1).first().token
    try:
        decoded = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return '', 200
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        return jsonify({"error": "unauthorized"}), 401

if __name__ == '__main__':
    app.run(debug=True)
