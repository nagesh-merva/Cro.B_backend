from flask import Flask, render_template, request, make_response, jsonify
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, allow_headers="*", origins="*", methods=["OPTIONS", "POST"])
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

client = MongoClient(
    'mongodb+srv://nagesh:nagesh2245@mywebsites.btvk61i.mongodb.net/',
    connectTimeoutMS=30000, 
    socketTimeoutMS=None)
db = client['Crob_orders']
orderslist = db['orders']

@app.route('/', methods=['GET', 'POST'])
def index():
    orders_cursor = orderslist.find().sort('date_created', -1)
    orders = list(orders_cursor)
    response = make_response(render_template('index.html', orders=orders))
    response.headers['Permissions-Policy'] = 'interest-cohort=()'
    return response

@app.route('/api/save_form_data', methods=['POST', 'OPTIONS'])
def save_form_data():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'success', 'message': 'CORS preflight request handled successfully'}), 200

    data = request.json
    print("Received form data:", data)

    new_order = {
        'id': data['id'],
        'name': data['name'],
        'email': data['email'],
        'address': data['address'],
        'phone': data['phone'],
        'product_name': data['productName'],
        'product_price': data['productPrice'],
        'date_created': datetime.utcnow(),
        'fulfilled': False
    }
    orderslist.insert_one(new_order)

    return jsonify({'status': 'success', 'message': 'Form data saved successfully'}), 200


@app.route('/api/process_order', methods=['POST'])
def process_order():
    data = request.json
    order_id = data.get('id')
    if order_id:
        orderslist.update_one({'id': order_id}, {'$set': {'processed': True}})
        return jsonify({'status': 'success', 'message': f'Order {order_id} marked as processed'}), 200

    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route('/api/dispatch_order', methods=['POST'])
def dispatch_order():
    data = request.json
    order_id = data.get('id')
    if order_id:
        orderslist.update_one({'id': order_id}, {'$set': {'dispatched': True}})
        return jsonify({'status': 'success', 'message': f'Order {order_id} marked as dispatched'}), 200

    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route('/api/fulfill_order', methods=['POST'])
def fulfill_order():
    data = request.json
    order_id = data.get('id')
    if order_id:
        orderslist.update_one({'id': order_id}, {'$set': {'fulfilled': True}})
        return jsonify({'status': 'success', 'message': f'Order {order_id} marked as fulfilled'}), 200

    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route('/api/get_order_statuses', methods=['POST'])
def get_order_statuses():
    data = request.json
    order_ids = data.get('order_ids')

    if order_ids:
        statuses = []
        for order_id in order_ids:
            order = orderslist.find_one({'id': order_id})
            if order:
                status = {}
                status['id'] = order_id

                if order.get('fulfilled', False):
                    status['status'] = 'fulfilled'
                elif order.get('dispatched', False):
                    status['status'] = 'dispatched'
                elif order.get('processed', False):
                    status['status'] = 'processing'
                else:
                    status['status'] = 'not_found'

                statuses.append(status)
            else:
                statuses.append({'id': order_id, 'status': 'not_found'})
        return jsonify({'status': 'success', 'order_statuses': statuses}), 200

    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400