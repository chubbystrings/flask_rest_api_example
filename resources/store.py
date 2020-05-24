from flask_restful import Resource
from models.store import StoreModel
from flask_jwt import jwt_required


class Store(Resource):

    @jwt_required()
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "store not found"}, 404

    @jwt_required()
    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"message": "Store with name {} already exists".format(name)}, 400  # noqa
        store = StoreModel(name)
        try:
            store.save_to_db()
        except Exception:
            return {"message": "an error occurred"}, 500
        return store.json(), 200

    @jwt_required()
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db(name)
        return {"message": "Store deleted successfully"}, 200


class StoreList(Resource):
    def get(self):
        return {"stores": [store.json() for store in StoreModel.query.all()]}
