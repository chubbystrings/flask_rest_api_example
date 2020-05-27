
import os
from flask import Flask, jsonify
from flask_restful import Api
# from flask_jwt import JWT
from flask_jwt_extended import JWTManager
from decouple import config

# from security import authenticate, identity --- using flask_JWT
from resources.user import (
    UserRegister,
    User,
    UserLogin,
    TokenRefresh,
    UserLogout
)
from resources.item import Item, ItemList
from db import db
from resources.store import Store, StoreList
from blacklist import BLACKLIST


LOCAL_DB_URL = config('LOCAL_DB_URL')
# LOCAL_DB_URL = 'sqlite:///data.db'

app = Flask(__name__)
app.secret_key = config('APP_SECRET_KEY')  # app.config['JWT_SECRET_KEY'] = jose # noqa
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', LOCAL_DB_URL)  # noqa
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


# jwt = JWT(app, authenticate, identity) # using flask_JWT /auth
jwt = JWTManager(app)


@jwt.user_claims_loader
def admin_claim(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(token):
    return token['jti'] in BLACKLIST


@jwt.expired_token_loader
def exp_token_callback():
    return jsonify({
        "description": "Token has expired",
        "error": "expired_token"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "description": "Token verification failed",
        "error": "invalid_token"
    }), 401


@jwt.unauthorized_loader
def unauthorized_token_callback(error):
    return jsonify({
        "description": "request doesnt contain an access token",
        "error": "authorization required"
    }), 401


@jwt.needs_fresh_token_loader
def fresh_token_callback():
    return jsonify({
        "description": "Fresh token needed",
        "error": "fresh_token"
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "This token has been revoked",
        "error": "revoked_token"
    }), 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
