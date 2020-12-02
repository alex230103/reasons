from flask import Flask
from flask_mongoalchemy import MongoAlchemy
from flask_restful import Api, Resource, reqparse, output_json
from flask_marshmallow import Marshmallow


class UnicodeApi(Api):
    """
    from here: https://github.com/flask-restful/flask-restful/issues/552
    """
    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = {
            'ensure_ascii': False
        }
        self.representations = {
            'application/json; charset=utf-8': output_json
        }


app = Flask(__name__)

# api = Api(app)
api = UnicodeApi(app)

app.config['MONGOALCHEMY_DATABASE'] = 'reasons'
app.config['MONGOALCHEMY_SERVER'] = '192.168.50.95'
db = MongoAlchemy(app)
ma = Marshmallow(app)


# Model
class ReasonModel(db.Document):
    document = db.StringField()
    contractor = db.StringField()
    product = db.StringField()
    reason = db.StringField()
    qty = db.IntField()

    @classmethod
    def exist(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()


class Capacity(db.Document):
    rack = db.StringField()
    tier = db.StringField()
    position = db.StringField()
    volume = db.IntField()
    pl_in_volume = db.IntField()
    pl_out_volume = db.IntField()

    @classmethod
    def exist(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()


# MarshMallow schema
class ReasonSchema(ma.Schema):
    class Meta:
        fields = ("document", "contractor", "product", "reason", "qty")


reason_schema = ReasonSchema()
reasons_schema = ReasonSchema(many=True)


# MarshMallow schema
class CapacitySchema(ma.Schema):
    class Meta:
        fields = ("rack", "tier", "position", "volume", "pl_in_volume", "pl_out_volume")


capacity_schema = CapacitySchema()
capacities_schema = CapacitySchema(many=True)

# parser args
parser = reqparse.RequestParser()
parser.add_argument("document", type=str, required=True)
parser.add_argument("contractor", type=str, required=True)
parser.add_argument("product", type=str, required=True)
parser.add_argument("reason", type=str, required=True)
parser.add_argument("qty", type=int, required=True)


class CapacityResource(Resource):
    def get (self):
        all_capacities = Capacity.query.all()
        return capacities_schema.dump(all_capacities)

    def post (self):
        parser_capacity = reqparse.RequestParser()
        parser_capacity.add_argument("rack", type=str, required=True)
        parser_capacity.add_argument("tier", type=str, required=True)
        parser_capacity.add_argument("position", type=str, required=True)
        parser_capacity.add_argument("volume", type=int, required=True)
        parser_capacity.add_argument("pl_in_volume", type=int, required=True)
        parser_capacity.add_argument("pl_out_volume", type=int, required=True)

        data = parser_capacity.parse_args()

        exist = Capacity.exist(**data)

        if exist is not None:
            return {'message': 'all ready exist'}, 401

        new_capacity = Capacity(**data)

        try:
            new_capacity.save()
            return capacity_schema.dump(new_capacity), 201
        except:
            return {'message': 'error creating'}, 400


# Resource
class ReasonResource(Resource):
    def get(self):
        reasons = ReasonModel.query.all()
        return reasons_schema.dump(reasons)

    def post(self):
        data = parser.parse_args()
        exist = ReasonModel.exist(**data)
        if exist is not None:
            return {'message': 'all ready exist'}, 401

        new_reason = ReasonModel(**data)
        try:
            new_reason.save()
            return reason_schema.dump(new_reason), 201
        except:
            return {'message': 'error creating'}, 400


class ReasonItemResource(Resource):
    def get(self):
        parser_item = reqparse.RequestParser()
        parser_item.add_argument('document', type=str)
        parser_item.add_argument('product', type=str)
        data = parser_item.parse_args()
        entry = ReasonModel.exist(**data)
        if entry is not None:
            return reason_schema.dump(entry)
        else:
            return {'message': 'not found'}, 404


api.add_resource(ReasonResource, '/reasons')
api.add_resource(ReasonItemResource, '/reason')

api.add_resource(CapacityResource, '/capacity')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



