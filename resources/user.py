from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required
)
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()

_user_parser.add_argument("username",
                          type=str,
                          required=True,
                          help="This field cannot be blank"
                          )

_user_parser.add_argument("password",
                          type=str,
                          required=True,
                          help="This field cannot be blank"
                          )


class UserRegister(Resource):

    def post(self):

        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "username already exists"}, 400

        # user = UserModel(data["username"], data["password"])
        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully"}, 201


class User(Resource):

    @jwt_required
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404

        return user.json()

    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User does not exist"}, 404

        user.delete_from_db()
        return {"message": "user deleted successfully"}, 200  # noqa


class UserLogin(Resource):

    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                "id": user.id,
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        return {"message": "invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully Logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
