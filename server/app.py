#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def restaurants_route():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
        }
        restaurants.append(restaurant_dict)
    
    response = make_response(
        restaurants,
        200,
        {"Content-Type": "application/json"}
    )

    return response

@app.route("/restaurants/<int:id>", methods=["GET"])
def restaurants_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return make_response(restaurant.to_dict(), 200)
    else:
        return make_response({"error": "Restaurant not found"}, 404)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    else:
        return make_response({"error": "Restaurant not found"}, 404)


@app.route("/pizzas", methods=["GET"])
def pizzas_route():
    pizzas = []
    for pizza in Pizza.query.all():
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name,
        }
        pizzas.append(pizza_dict)

    response = make_response(
        pizzas,
        200,
        {"Content-Type": "application/json"}
    )

    return response

@app.route("/restaurant_pizzas", methods=["POST"])
def create_new_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")
    
    try:
        pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    
        db.session.add(pizza)
        db.session.commit()

        response = make_response(
            pizza.to_dict(), 
            201,
            {"Content-Type": "application/json"}
        )

    except ValueError:
        response = make_response(
            {"errors": ["validation errors"]},
            400,
            {"Content-Type": "application/json"}
        )
    
    return response


if __name__ == "__main__":
    app.run(port=5555, debug=True)
