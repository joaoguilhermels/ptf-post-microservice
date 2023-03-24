import os
import boto3
from flask import Flask, request, jsonify, abort
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(table_name)

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

# Create a Post
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()

    # Data validation
    if 'title' not in data or 'description' not in data:
        abort(400)

    title = data['title']
    description = data['description']
    
    # Save to DynamoDB
    response = table.put_item(
        Item={
            'title': title,
            'description': description,
        }
    )

    return jsonify({"message": "Post created"}), 201

# Read a Post
@app.route('/posts/<string:title>', methods=['GET'])
def read_post(title):
    response = table.get_item(Key={'title': title})
    if 'Item' in response:
        return jsonify(response['Item'])
    else:
        return jsonify({"message": "Post not found"}), 404

# Update a Post
@app.route('/posts/<string:title>', methods=['PUT'])
def update_post(title):
    data = request.get_json()

    # Data validation
    if 'description' not in data:
        abort(400)

    description = data['description']

    # Update in DynamoDB
    response = table.update_item(
        Key={'title': title},
        UpdateExpression='SET description = :description',
        ExpressionAttributeValues={':description': description}
    )

    if response['Attributes']:
        return jsonify({"message": "Post updated"})
    else:
        return jsonify({"message": "Post not found"}), 404

# Delete a Post
@app.route('/posts/<string:title>', methods=['DELETE'])
def delete_post(title):
    response = table.delete_item(Key={'title': title})

    if 'Attributes' in response:
        return jsonify({"message": "Post deleted"})
    else:
        return jsonify({"message": "Post not found"}), 404

# List all Posts
@app.route('/posts', methods=['GET'])
def list_posts():
    response = table.scan()
    return jsonify(response['Items'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

