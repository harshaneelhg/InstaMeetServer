from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import math

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
                        'page': 'get_nearby_users',
                        'code': 400,
                        'message':'Bad Request. Username and password cannot be empty.',
                        'status': 'FAILED'
                        })
    username = request.form['username']
    password = request.form['password']
    display_name = request.form['display_name'] if 'display_name' in request.form else ''

    return module_create_user(username, password, display_name)

@app.route('/api/instameet/update_user/', methods=['POST'])
def update_user():
    if 'username' not in request.form or 'password' not in request.form or 'email' not in request.form or 'phone' not in request.form or 'display_name' not in request.form or 'discover' not in request.form:
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
    display_name = request.form['display_name']
    discover = request.form['discover']

    return module_update_user(username, password, email, phone, display_name, discover)

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

@app.route('/api/instameet/update_interest/', methods=['POST'])
def update_interest():
    if 'username' not in request.form or 'password' not in request.form or 'interest_id' not in request.form or 'interest_value' not in request.form:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })

    username = request.form['username']
    password = request.form['password']
    interest_id = request.form['interest_id']
    interest_value = request.form['interest_value']

    try:
        temp = int(interest_id)
        temp = int(interest_value)
    except ValueError:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Parameters. Could not cast interest_id or interest_value to an integer.',
                        'status': 'FAILED'
                        })

    return module_update_interest(username, password, interest_id, interest_value)

@app.route('/api/instameet/get_nearby_users/', methods=['POST'])
def get_nearby():
    if 'username' not in request.form or 'password' not in request.form:
        return jsonify({
                        'page': 'get_user',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })

    username = request.form['username']
    password = request.form['password']
    reply = get_nearby_users("Mac","abcd")
    if type(reply) != type([]):
        return reply

    user_details = module_get_user(username)
    profile = json.loads(user_details.get_data())['user']
    scores = []
    for user in reply:
        scores.append((user, get_cosine_sim(profile['interests'],[0,0,0,0,0,0,0,0,0,0])))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    ret_users = [s[0] for s in scores]
    for r in ret_users:
        r.pop('_id')
    return jsonify({
            'page': 'get_user',
            'code': 200,
            'message': 'user found',
            'near_users': [s[0] for s in scores],
            'status': 'SUCCESS'
        })
    pass

@app.route('/api/instameet/toggle_discovery/', methods=['POST'])
def toggle_discovery():
    if 'username' not in request.form or 'password' not in request.form or 'discover' not in request.form:
        return jsonify({
                        'page': 'toggle_discovery',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })

    username = request.form['username']
    password = request.form['password']
    discover = request.form['discover']

    return module_toggle_discovery(username, password, discover)

@app.route('/api/instameet/add_history/', methods=["POST"])
def add_history():
    if 'username' not in request.form or 'password' not in request.form or 'user1' not in request.form or 'user2' not in request.form:
        return jsonify({
                        'page': 'add_history',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })
    username = request.form['username']
    password = request.form['password']
    user1 = request.form['user1']
    user2 = request.form['user2']

    return module_add_history(username, password, user1, user2)

@app.route('/api/instameet/get_history/', methods=["POST"])
def get_history():
    if 'username' not in request.form or 'password' not in request.form:
        return jsonify({
                        'page': 'get_history',
                        'code': 400,
                        'message':'Bad Request. Insufficiant parameters.',
                        'status': 'FAILED'
                        })
    username = request.form['username']
    password = request.form['password']

    return module_get_history(username, password)

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

def module_create_user(username, password, display_name):
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
        'display_name': display_name,
        'email': '',
        'phone': '',
        'location': '',
        'discover': 'True',
        'interests': [0,0,0,0,0,0,0,0,0,0]
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

def module_update_user(username, password, email, phone, display_name, discover):
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
                "display_name": display_name,
                "discover": discover
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

def module_update_interest(username, password, interest_id, interest_value):
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
    user_profile = _db.users.find_one({'username': username})
    user_interests = user_profile['interests']
    user_interests[int(interest_id)] = 1 if int(interest_value) > 0 else 0
    result = _db.users.update_one(
        {'username': username},
        {
            "$set":{
                "interests": user_interests,
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

def get_nearby_users(username, password):
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
    near_users = []
    location1 = json.loads(user_details.get_data())['user']['location']
    lat1,long1 = 0.0,0.0
    if location1 != "":
        lat1 = location1.split(',')[0].strip()
        long1 = location1.split(',')[1].strip()
    users = _db.users.find({})
    for user in users:
        if str(user['username']) != username and user['discover'] == "True":
            location2 = user['location']
            lat2,long2 = 0.0,0.0
            if location2 != "":
                lat2 = location2.split(',')[0].strip()
                long2 = location2.split(',')[1].strip()
            dist = get_distance(lat1,lat2,long1,long2)
            if dist < 100000:
                user['distance'] = dist
                near_users.append(user)
    return near_users

def module_toggle_discovery(username, password, discover):
    user_details = module_get_user(username)
    if json.loads(user_details.get_data())['status'] == "FAILED":
        return jsonify({
            'page': 'toggle_discovery',
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    else:
        if password != json.loads(user_details.get_data())['user']['password']:
            return jsonify({
                'page': 'toggle_discovery',
                'code': 500,
                'status': 'FORBIDDEN',
                'message': 'Invalid password'
            })

    result = _db.users.update_one(
        {'username': username},
        {
            "$set":{
                "discover": discover,
            },
            "$currentDate": {"lastModified": True}
        }
    )
    return jsonify({
        'page': 'toggle_discovery',
        'code' : 200,
        'records_matched': result.matched_count,
        'records_updated': result.modified_count,
        'status': 'SUCCESS',
        'message': 'Successfully updated %d records'%result.modified_count
    })

def module_add_history(username, password, user1, user2):
    user1_details = module_get_user(user1)
    user2_details = module_get_user(user2)
    if json.loads(user1_details.get_data())['status'] == "FAILED":
        return jsonify({
            'page': 'add_history',
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    elif json.loads(user2_details.get_data())['status'] == "FAILED":
        return jsonify({
            'page': 'add_history',
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    else:
        if password != json.loads(user2_details.get_data())['user']['password']:
            return jsonify({
                'page': 'add_history',
                'code': 500,
                'status': 'FORBIDDEN',
                'message': 'Invalid password'
            })

    new_history ={
        'user1': user1,
        'user2': user2,
        'timestamp': str(datetime.now())
    }

    user_history = _db.user_history
    hist_id = user_history.insert_one(new_history).inserted_id

    return jsonify({
        'page': 'add_history',
        'page': 'register',
        'code': 200,
        'message': 'Added to the history',
        'status': 'SUCCESS'
    })

def module_get_history(username, password):
    user_details = module_get_user(username)
    if json.loads(user_details.get_data())['status'] == "FAILED":
        return jsonify({
            'page': 'toggle_discovery',
            'code': 400,
            'status': 'FAILED',
            'message': 'Error finding user'
        })
    else:
        if password != json.loads(user_details.get_data())['user']['password']:
            return jsonify({
                'page': 'toggle_discovery',
                'code': 500,
                'status': 'FORBIDDEN',
                'message': 'Invalid password'
            })

    user_history = _db.user_history
    ret_history = user_history.find({"$or":[{'user1': username},{'user2':username}]})
    user_list = [u for u in ret_history]
    for u in user_list:
        oid = u.pop('_id')
        u['pk_history'] = str(oid)

    return jsonify({'page': 'get_history',
                    'code': 200,
                    'message': 'Returning history.' if len(user_list) != 0 else 'No history found.',
                    'history': user_list,
                    'status': 'SUCCESS'})


def get_distance(latitude1, latitude2, longitude1, longitude2):
    lat1 = math.radians(float(latitude1))
    lat2 = math.radians(float(latitude2))
    long1 = math.radians(float(longitude1))
    long2 = math.radians(float(longitude2))
    dlat = lat1 - lat2
    dlong = long1 - long2
    a = (math.sin(dlat/2))**2 + math.cos(long1) * math.cos(long2) * (math.sin(dlong/2))**2
    c = 2 * math.atan2(a**0.5, (1-a)**0.5)
    d = 3961 * c
    return d

def get_cosine_sim(x,y):
    if len(x) != len(y):
        return -1
    dot = [x[i]*y[i] for i in range(len(x))]
    try:
        return (sum(dot)*1.0)/(sum(x)**0.5*sum(y)**0.5)
    except ZeroDivisionError:
        return 0

if __name__ == '__main__':
    app.run(debug=True,port=8001)
