from flask import Flask, Blueprint, jsonify,request, send_file, safe_join
from flask_restplus import Api, Resource, Namespace
from ma import ma
from db import db
from resources.store import Store, StoreList, store_ns, stores_ns
from resources.item import Item, ItemList, items_ns, item_ns
from marshmallow import ValidationError
import json
import yaml
import os

app = Flask(__name__)

authorizations = {
    'basic' : {
        'type' : 'basic',
#        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY',
        'x-basicInfoFunc': 'app.basic_auth'
    }
}

bluePrint = Blueprint('api', __name__, url_prefix='/api')

api = Api(bluePrint, version='0.9', doc='/doc', title='Sample Flask-RestPlus 5GMeta', authorizations=authorizations)
app.register_blueprint(bluePrint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = 'thisisthesecretkey'

api.add_namespace(item_ns)
api.add_namespace(items_ns)
api.add_namespace(store_ns)
api.add_namespace(stores_ns)

"fifiugo"
ns_yml = Namespace('export_yaml', description='Generale file format yaml')
api.add_namespace(ns_yml)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message' : 'Token is missing.'}, 401

        if token != 'mytoken':
            return {'message' : 'Your token is wrong, wrong, wrong!!!'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated

@app.before_first_request
def create_tables():
    db.create_all()


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(error.messages), 400

#ns_yml = api.namespace('Generate file yaml', description='Generate a file with format swagger yaml')
@ns_yml.route('/swagger.yml')
class export_yaml(Resource):
    def get(self):
       data = json.loads(json.dumps(api.__schema__))
       with open('5GmetaApi.yml', 'w') as yamlf:
           yaml.dump(data, yamlf, allow_unicode=True, default_flow_style=False)
           file = os.path.abspath(os.getcwd())
#           try:
#               @after_this_request
#               def remove_file(resp):
#                   try:
#                       os.remove(safe_join(file, '1111.yml'))
#                   except Exception as error:
#                       log.error("Error removing or closing downloaded file handle", error)
#                   return resp

           return send_file(safe_join(file, '5GmetaApi.yml'), as_attachment=True, attachment_filename='5GmetaApi.yml', mimetype='application/x-yaml')
#           except FileExistsError:
#               abort(404)

item_ns.add_resource(Item, '/<int:id>')
items_ns.add_resource(ItemList, "")
store_ns.add_resource(Store, '/<int:id>')
stores_ns.add_resource(StoreList, "")

if __name__ == '__main__':
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True,host='0.0.0.0') when is used in vm
#    app.run(port=5000, debug=True)
