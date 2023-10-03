
from utilities import handle_insert, handle_search
from flask import Flask, jsonify, request
from flask_cors import CORS
  
# creating a Flask app
app = Flask(__name__)
CORS(app)  

@app.route('/', methods = ['POST'])
def insert():
    print('Inserting data')
    data = request.json
    result = handle_insert(data)
    print(f"Result {result}")
    response = {
        "Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "*",
	"Access-Control-Allow-Headers": "*",
	"statusCode": 200,
	"body": {
    		"data": result
	}
    }
    return response

@app.route('/search', methods = ['POST'])
def search():
    print('Searching data')
    data = request.json
    result = handle_search(data)
    response = {
        "Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "*",
	"Access-Control-Allow-Headers": "*",
	"statusCode": 200,
	"body": {
    		"data": result
	}
	}

    return response
  
  
# driver function
if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0')
