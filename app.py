import datetime
import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
import re
from google.oauth2 import id_token
from google.auth.transport import requests

# Retrieve URI from .env file
load_dotenv()
uri = os.getenv("MONGODB_URI")

# Instantiate MongoClient
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.ihouse
events = db.events
users = db.users
debug = db.debug

app = Flask(__name__)


def decrypt_jwt(token):
    try:
        expected_audience = os.getenv("GOOGLE_CLIENT_ID")
        get_req = requests.Request()
        decoded_token = id_token.verify_oauth2_token(token, get_req, expected_audience)
        return decoded_token
    except Exception as e:
        # Handle invalid token, expired token, etc.
        print(f"Token verification failed")
        return None


def get_db_collection(field_type):
    collection_map = {
        'programs': db.programs,
        'cosponsors': db.cosponsors,
        'av': db.av,
        'caterers': db.caterers,
        'rooms': db.rooms,
        'statuses': db.statuses,
        'partners': db.partners,
        'custom_checklist': db.checklist,
        'users': db.users,
        'eventtype': db.eventtype
    }
    return collection_map.get(field_type)


@app.route("/")
def default():
    return "The API server is running"


@app.route("/users/login", methods=["POST"])
def validate_user():
    token = request.headers.get('Authorization')

    # Extract the token part from the header

    decoded_token = decrypt_jwt(token)

    # Check if the token was successfully decoded
    if not decoded_token:
        return jsonify({"message": "Invalid token"}), 401

    user_email = decoded_token.get('email')

    if not user_email:
        return jsonify({"message": "Email not found in token"}), 400

    user = users.find_one({"email": user_email})

    if user:
        return jsonify({"isValid": True}), 200
    else:
        return jsonify({"isValid": False}), 401


@app.route("/events", methods=["GET", "POST"])
def req_events():
    if request.method == "GET":
        # Filters
        filters = {key: value for key, value in request.args.items() if
                   value and key in ["organization", "cosponsor", "is_public", "status"]}

        # Timeframe handling
        timeframe = request.args.get('timeframe')
        if timeframe:
            today_date = datetime.datetime.now()
            if timeframe == 'upcoming':
                filters['date'] = {'$gte': today_date}
            else:
                filters['date'] = {'$lt': today_date}

        # Search handling
        search = request.args.get('search')
        if search:
            filters['eventName'] = {'$regex': re.compile(search, re.IGNORECASE)}

        # Sorting and Limit
        sorting = request.args.get('sorting', 'asc')
        sort_order = ASCENDING if sorting == 'asc' else DESCENDING
        limit = int(request.args.get('limit', 10))

        try:
            events_data = events.find(filters).sort('date', sort_order).limit(limit)
            events_list = [{**event, '_id': str(event['_id'])} for event in events_data]
            return jsonify(events_list)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if request.method == "POST":
        event_parameters = request.json
        try:
            # Convert date and time strings to datetime objects
            if 'date' in event_parameters:
                date_string = str(event_parameters['date']) + "T00:00:00.000Z"
                event_parameters['date'] = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.000Z")
            result = events.insert_one(event_parameters)
            return jsonify({"message": "Event added successfully", "id": str(result.inserted_id)}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route("/events/<event_id>", methods=("GET", "POST", "PUT", "DELETE"))
def edit_events(event_id=None):
    if request.method == "GET":
        try:
            event = events.find_one({"_id": ObjectId(event_id)})
            if event:
                return jsonify(event)
            else:
                return jsonify({"message": "Event not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if request.method == "DELETE":
        try:
            result = events.delete_one({"_id": ObjectId(event_id)})
            if result.deleted_count:
                return jsonify({"message": "Event deleted successfully"}), 200
            else:
                return jsonify({"message": "Event not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route("/fields", methods=("GET", "POST"))
def fields():
    db_field = get_db_collection(request.args.get('fields'))

    if request.method == "POST":
        program_parameters = request.json
        try:
            result = db_field.insert_one(program_parameters)
            return jsonify({"message": "Field added successfully", "_id": str(result.inserted_id)}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if request.method == "GET":
        try:
            all_fields = db_field.find({}).sort('date_added', ASCENDING)

            all_fields_list = [{**field, '_id': str(field['_id'])} for field in all_fields if field["is_active"]]

            if all_fields:
                return jsonify(all_fields_list)
            else:
                return jsonify({"message": "Fields not found"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route("/fields/<field>/<id>", methods=("PUT", "DELETE"))
def update_fields(field, id):
    db_field = get_db_collection(field)

    if request.method == "DELETE":
        try:
            result = db_field.update_one({"_id": ObjectId(id)}, {"$set": {"is_active": False}})
            if result.modified_count:
                return jsonify({"message": "Field deactivated successfully"}), 200
            else:
                return jsonify({"message": "Field not found"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if request.method == "PUT":

        field_parameters = request.json

        try:
            result = db_field.update_one({"_id": ObjectId(id)}, {"$set": field_parameters})
            if result.modified_count:
                return jsonify({"message": "Field label updated"}), 200
            else:
                return jsonify({"message": "Field not found"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
