from flask import request, jsonify
from flask_jwt import jwt_required
from flask_restplus import Resource, fields, Namespace
from flask_httpauth import HTTPBasicAuth
from functools import wraps
from models.item import ItemModel
from schemas.item import ItemSchema

ITEM_NOT_FOUND = "Item not found."
auth = HTTPBasicAuth()

item_ns = Namespace('item', description='Item related operations')
items_ns = Namespace('items', description='Items related operations')

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

# Model required by flask_restplus for expect
item = items_ns.model('Item', {
    'name': fields.String('Name of the Item'),
    'price': fields.Float(0.00),
    'store_id': fields.Integer
})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.authorization["username"]

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'Token is missing.'}, 401

        if token != 'mytoken':
            return {'message': 'Your token is wrong, wrong, wrong!!!'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated


@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == 'roy' and password == 'roy':
            return True
        else:
            return False
    return False


class Item(Resource):

    def get(self, id):
        item_data = ItemModel.find_by_id(id)
        if item_data:
            return item_schema.dump(item_data)
        return {'message': ITEM_NOT_FOUND}, 404

    def delete(self, id):
        item_data = ItemModel.find_by_id(id)
        if item_data:
            item_data.delete_from_db()
            return {'message': "Item Deleted successfully"}, 200
        return {'message': ITEM_NOT_FOUND}, 404

    @item_ns.expect(item)
    def put(self, id):
        item_data = ItemModel.find_by_id(id)
        item_json = request.get_json()

        if item_data:
            item_data.price = item_json['price']
            item_data.name = item_json['name']
        else:
            item_data = item_schema.load(item_json)

        item_data.save_to_db()
        return item_schema.dump(item_data), 200


class ItemList(Resource):
    @items_ns.doc('Get all the Items')
    @items_ns.doc(security='basic')
    #    @auth.login_required()
    @token_required
    def get(self):
        return item_list_schema.dump(ItemModel.find_all()), 200

    @items_ns.expect(item)
    @items_ns.doc('Create an Item')
    def post(self):
        item_json = request.get_json()
        item_data = item_schema.load(item_json)
        item_data.save_to_db()

        return item_schema.dump(item_data), 201
