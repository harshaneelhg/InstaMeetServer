from flask import Flask, jsonify, request
from pymongo import MongoClient

import json

app = Flask(__name__)
_mongo_client = MongoClient('localhost', 8000)
_db = _mongo_client.instameet

@app.route('/', methods=['GET'])
def index():
    return jsonify({'page': 'index', 'status': 200})

@app.route('/api/instameet/get_user/', methods=['POST'])
def get_user():
    if 'username' not in request.form:
        return jsonify({'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Invalid username.',
                        'status': 'FAILED'
                        })
    user = request.form['username']
    return module_get_user(user)


@app.route('/api/instameet/register_user/', methods=['POST'])
def register_user():
    if 'username' not in request.form or 'password' not in request.form:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Username and password cannot be empty.',
                        'status': 'FAILED'
                        })
    username = request.form['username']
    password = request.form['password']

    return module_create_user(username, password)



@app.route('/api/instameet/update_user/', methods=['POST'])
def update_user():
    if 'username' not in request.form or 'password' not in request.form or 'email' not in request.form or 'phone' not in request.form:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    return module_update_user(username, password, email, phone)
    pass

@app.route('/api/instameet/update_location/', methods=['POST'])
def update_location():
    if 'username' not in request.form or 'password' not in request.form or 'location' not in request.form:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })

    username = request.form['username']
    password = request.form['password']
    location = request.form['location']

    return module_update_location(username, password, location)

def module_get_user(username):
    users = _db.users
    ret_user = users.find_one({'username': username})
    if ret_user == None:
        return jsonify({'page': 'get_user',
                        'code': 404,
                        'message': 'User not found',
                        'status': 'FAILED'})
    ret_user.pop('_id')
    return jsonify({'page': 'get_user',
                    'code': 200,
                    'message': 'user found',
                    'user': ret_user,
                    'status': 'SUCCESS'})

def module_create_user(username, password):
    if ' ' in username or '$' in username or '&' in username:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':"Bad Request. Username cannot have ' ' or '$' or '&'.",
                        'status': 'FAILED'
                        })
    if password.strip() == '':
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':"Bad Request. Password cannot be empty",
                        'status': 'FAILED'
                        })
    new_user = {
        'username': username,
        'password': password,
        'email': '',
        'phone': '',
        'location': '',
        'discover': 'True'
    }
    users = _db.users
    dup_user = users.find_one({'username': username})
    if dup_user is not None:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':"Bad Request. Username already exists",
                        'status': 'FAILED'
                        })
    user_id = users.insert_one(new_user).inserted_id
    return jsonify({
        'page': 'register',
        'code': 200,
        'message': 'Added new user',
        'status': 'SUCCESS'
    })

def module_update_user(username, password, email, phone):
    user_details = module_get_user(username)
    if json.loads(user_details.get_data())['status'] == "FAILED":
        return jsonify({
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    else:
        if password != json.loads(user_details.get_data())['user']['password']:
            return jsonify({
                'code': 500,
                'status': 'FORBIDDEN',
                'message': 'Invalid password'
            })
    result = _db.users.update_one(
        {'username': username},
        {
            "$set":{
                "email": email,
                "phone": phone,
            },
            "$currentDate": {"lastModified": True}
        }
    )
    return jsonify({
        'code' : 200,
        'records_matched': result.matched_count,
        'records_updated': result.modified_count,
        'status': 'SUCCESS',
        'message': 'Successfully updated %d records'%result.modified_count
    })

def module_update_location(username, password, location):
    user_details = module_get_user(username)
    if json.loads(user_details.get_data())['status'] == "FAILED":
        return jsonify({
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    else:
        if password != json.loads(user_details.get_data())['user']['password']:
            return jsonify({
                'code': 500,
                'status': 'FORBIDDEN',
                'message': 'Invalid password'
            })

    result = _db.users.update_one(
        {'username': username},
        {
            "$set":{
                "location": location,
            },
            "$currentDate": {"lastModified": True}
        }
    )
    return jsonify({
        'code' : 200,
        'records_matched': result.matched_count,
        'records_updated': result.modified_count,
        'status': 'SUCCESS',
        'message': 'Successfully updated %d records'%result.modified_count
    })

if __name__ == '__main__':
    app.run(debug=True,port=8001)
