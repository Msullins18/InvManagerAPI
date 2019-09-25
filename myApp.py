from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from sqlalchemy import exc
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')

product_schema = ProductSchema(strict=True)
products_schema = ProductSchema(many=True, strict=True)

@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name,description,price,qty)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)

@app.route('/csv', methods=['POST'])
def add_products():
    c = 0
    for i in request.json:
        try:
            name = request.json[c]['name']
            description = request.json[c]['description']
            price = request.json[c]['price']
            qty = request.json[c]['qty']
            c += 1

            new_product = Product(name,description,price,qty)

            db.session.add(new_product)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session().rollback()
            continue

    return product_schema.jsonify(new_product)
        


@app.route('/product', methods=(['GET']))
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result.data)

@app.route('/product/<id>', methods=(['GET']))
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name=name
    product.description=description
    product.price=price
    product.qty=qty

    db.session.commit()

    return product_schema.jsonify(product)

@app.route('/product/delete', methods=(['DELETE']))
def delete_products():
    results = Product.query.all()
    for product in results:
        db.session.delete(product)
    db.session.commit()
    result = products_schema.dump(results)

    return jsonify(result.data)

@app.route('/product/<id>', methods=(['DELETE']))
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    
    return product_schema.jsonify(product)

# if __name__ == '__main__':
#     app.run()
