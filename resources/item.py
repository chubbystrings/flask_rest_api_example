from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, get_jwt_claims,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required
)
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="this field cannot be left blank"

    )

    parser.add_argument(
        "store_id",
        type=int,
        required=True,
        help="Must contain store id"

    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item does not exist"}, 404

        # new_item = next(filter(lambda x: x['name'] == name, items), None)
        # return {"item": new_item}, 200 if new_item else 404
    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"Item with name {name} already exists"}, 400

        request_data = Item.parser.parse_args()
        item = ItemModel(name, request_data["price"], request_data["store_id"])
        try:
            item.save_to_db()
        except Exception:
            return {"message": "An error Occurred"}, 500

        return item.json(), 201

    @jwt_required
    def put(self, name):
        request_data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(
                name, request_data["price"], request_data["store_id"])
        else:
            item.price = request_data["price"]

        item.save_to_db()
        return item.json(), 200

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required"}
        item = ItemModel.find_by_name(name)
        if item is None:
            return {"message": "No item exists with name"}

        item.delete_from_db()

        return {"message": "Item deleted"}, 200


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items": items}, 200
        return {
            "items": [item['name'] for item in items],
            "message": "More data available if you log in"
        }
        # return {"items": list(map(lambda x: x.json(), ItemModel.query.all()))}  # noqa
        # return {"items": [item.json() for item in ItemModel.find_all()]}
