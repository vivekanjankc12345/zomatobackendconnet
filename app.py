from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/nanu_zomato'
mongo = PyMongo(app)

# Database collections
dishes_collection = mongo.db.dishes
orders_collection = mongo.db.orders
feedback_collection = mongo.db.feedback


@app.route('/dishes', methods=['GET'])
def get_dishes():
    dishes = dishes_collection.find()
    serialized_dishes = []
    for dish in dishes:
        dish['_id'] = str(dish['_id'])  # Convert ObjectId to string
        serialized_dishes.append(dish)
    return jsonify(serialized_dishes)
@app.route('/dishes', methods=['POST'])
def add_dish():
    dish_data = request.get_json()
    dish_id = dishes_collection.insert_one(dish_data).inserted_id
    return jsonify({'message': 'Dish added successfully', 'dish_id': str(dish_id)})

@app.route('/dishes/<dish_id>', methods=['PUT'])
def update_dish(dish_id):
    dish_data = request.get_json()
    dishes_collection.update_one({'_id': ObjectId(dish_id)}, {'$set': dish_data})
    return jsonify({'message': 'Dish updated successfully'})

@app.route('/dishes/<dish_id>', methods=['DELETE'])
def delete_dish(dish_id):
    dishes_collection.delete_one({'_id': ObjectId(dish_id)})
    return jsonify({'message': 'Dish deleted successfully'})

@app.route('/orders', methods=['POST'])
def take_order():
    order_data = request.get_json()
    # Check dish availability and process order
    order_id = orders_collection.insert_one(order_data).inserted_id
    return jsonify({'message': 'Order taken successfully', 'order_id': str(order_id)})

@app.route('/orders/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    order_data = request.get_json()
    orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': order_data})
    return jsonify({'message': 'Order status updated successfully'})
@app.route('/orderreview', methods=['GET'])
def get_dishes1():
    dishes = orders_collection.find()
    serialized_dishes = []
    for dish in dishes:
        dish['_id'] = str(dish['_id'])  # Convert ObjectId to string
        serialized_dishes.append(dish)
    return jsonify(serialized_dishes)
chatbot_responses = {
    'hours_of_operation': 'Our hours of operation are Monday to Friday, 9 AM to 6 PM.',
    'order_status': 'The status of your order is "In progress".',
    'popular_dish': 'Our most popular dish is the Zesty Zomato Special.',
    # Add more responses for different intents
}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_query = data['query']
    intent = classify_intent(user_query)

    if intent in chatbot_responses:
        response = chatbot_responses[intent]
    else:
        response = 'Sorry, I didn\'t understand your query.'

    return jsonify({'response': response})

def classify_intent(user_query):
    # Perform intent classification using NLU library or service
    # Return the intent based on the user query

    # Example classification using simple if-else statements
    if 'hours' in user_query:
        return 'hours_of_operation'
    elif 'status' in user_query or 'order' in user_query:
        return 'order_status'
    elif 'popular' in user_query or 'best' in user_query or 'favorite' in user_query:
        return 'popular_dish'
    else:
        return 'unknown'
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    order_id = data['order_id']
    rating = data['rating']
    review = data['review']

    # Store the feedback in the database
    feedback = {
        'order_id': order_id,
        'rating': rating,
        'review': review
    }
    feedback_collection.insert_one(feedback)

    # Update the order status to indicate that feedback has been submitted
    orders_collection.update_one({'_id': order_id}, {'$set': {'feedback_submitted': True}})

    return jsonify({'message': 'Feedback submitted successfully'})

# Route for retrieving feedback for a dish
@app.route('/dish_feedback/<dish_id>', methods=['GET'])
def get_dish_feedback(dish_id):
    # Retrieve the feedback for the given dish from the database
    feedbacks = feedback_collection.find({'dish_id': dish_id})

    # Prepare the response
    response = []
    for feedback in feedbacks:
        response.append({
            'rating': feedback['rating'],
            'review': feedback['review']
        })

    return jsonify(response)
if __name__ == '__main__':
    app.run(debug=True)
