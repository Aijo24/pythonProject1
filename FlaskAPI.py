from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil import parser
import sqlite3


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank_database.db'
db = SQLAlchemy(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    pinCode = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, nullable=False)
    dernier_retrait = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"User(name = {self.name}, pinCode = {self.pinCode}, dernier_retrait = {self.dernier_retrait})"

class RetraitModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Retrait(name = {self.name}, montant = {self.montant}, date = {self.date})"


user_put_args = reqparse.RequestParser()
user_put_args.add_argument("name", type=str, help="Name is required", required=True)
user_put_args.add_argument("pinCode", type=int, help="Pin code is required", required=True)
user_put_args.add_argument("sold", type=int, required=False)
user_put_args.add_argument("dernier_retrait", type=str, required=False)

retrait_put_args = reqparse.RequestParser()
retrait_put_args.add_argument("name", type=str, help="Name is required", required=True)
retrait_put_args.add_argument("montant", type=int, help="Amount is required", required=True)
retrait_put_args.add_argument("date", type=str, help="The date is required", required=True)

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'pinCode': fields.Integer,
    'sold': fields.Integer,
    'dernier_retrait': fields.DateTime(dt_format='iso8601')
}

resource_fields_retraits = {
    'id': fields.Integer,
    'name': fields.String,
    'montant': fields.Integer,
    'date': fields.DateTime(dt_format='iso8601')
}

class User(Resource):
    @marshal_with(resource_fields)
    def get(self, user_id):
        result = UserModel.query.filter_by(id=user_id).first()
        if not result:
            abort(404, message="No user with that id...")
        return result

    @marshal_with(resource_fields)
    def put(self, user_id):
        args = user_put_args.parse_args()
        result = UserModel.query.filter_by(id=user_id).first()
        if result:
            abort(409, message="User id taken...")

        dernier_retrait_str = args['dernier_retrait']
        dernier_retrait = None
        if dernier_retrait_str:
            dernier_retrait = parser.parse(dernier_retrait_str)

        user = UserModel(id=user_id, name=args['name'], pinCode=args['pinCode'], sold=args['sold'], dernier_retrait=dernier_retrait)
        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(resource_fields)
    def patch(self, user_id):
        args = user_put_args.parse_args()
        result = UserModel.query.filter_by(id=user_id).first()
        if not result:
            abort(404, message="User doesn't exist, cannot update")

        if args['name']:
            result.name = args['name']
        if args[('pinCode')]:
            result.pinCode = args['pinCode']
        if args['sold']:
            result.sold = args['sold']
        if args['dernier_retrait']:
            result.dernier_retrait = parser.parse(args['dernier_retrait'])

        db.session.commit()

        return result

class Retrait(Resource):
    @marshal_with(resource_fields_retraits)
    def get(self, retrait_id):
        result = RetraitModel.query.filter_by(id=retrait_id).first()
        if not result:
            abort(404, message="No withdraw with that id...")
        return result

    @marshal_with(resource_fields_retraits)
    def put(self, retrait_id):
        args = retrait_put_args.parse_args()
        result = RetraitModel.query.filter_by(id=retrait_id).first()
        if result:
            abort(409, message="Withdraw id taken...")

        date_str = args['date']
        date = None
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

        retrait = RetraitModel(id=retrait_id, montant=args['montant'], name=args['name'], date=date)
        db.session.add(retrait)
        db.session.commit()
        return retrait, 201

    @marshal_with(resource_fields)
    def patch(self, retrait_id):
        args = retrait_put_args.parse_args()
        result = RetraitModel.query.filter_by(id=retrait_id).first()
        if not result:
            abort(404, message="Aucun retrait avec cet id n'existe, cannot update")

        if args['name']:
            result.name = args['name']
        if args['montant']:
            result.montant = args['montant']
        if args['date']:
            result.date = args['date']

        db.session.commit()

@app.route('/retraits', methods=['GET'])
def get_all_withdrawals():
    try:
        conn = sqlite3.connect('bank_database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM retrait_model")
        withdrawals = c.fetchall()

        result = []
        for withdrawal in withdrawals:
            withdrawal_data = {
                'id': withdrawal[0],
                'name': withdrawal[1],
                'montant': withdrawal[2],
                'date': withdrawal[3]
            }
            result.append(withdrawal_data)

        conn.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        conn = sqlite3.connect('bank_database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM user_model")
        users = c.fetchall()

        result = []
        for user in users:
            user_data = {
                'id': user[0],
                'name': user[1],
                'pinCode': user[2],
                'sold': user[3],
                'dernier_retrait': user[4]
            }
            result.append(user_data)

        conn.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

api.add_resource(User, "/user/<int:user_id>")
api.add_resource(Retrait, "/retrait/<int:retrait_id>")

if __name__ == "__main__":
    app.run(debug=True)
