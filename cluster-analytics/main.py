
from vector import handle_insert, handle_search, flush_vector_db, handle_isolation
from flask import Flask, jsonify, request
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
  

@app.route('/analytics', methods = ['POST'])
def insert():
    print('Inserting data')
    data = request.json
    handle_insert(data)
    response = {
        "data": "Data inserted"
    }
    return jsonify(response)

@app.route('/analytics/clusters', methods = ['GET'])
def search_clusters():
    print('Searching data')
    result = handle_search()
    response = {
        "data": result
    }
    return response
  
@app.route('/analytics/vector-db', methods = ['DELETE'])
def delete_all():
    print("Flushing vector db")
    flush_vector_db()
    response = {
        "data": "Data flushed"
    }
    return jsonify(response)

@app.route('/analytics/isolation', methods = ['GET'])
def search_isolation():
    print('Searching data')
    result = handle_isolation()
    response = {
        "data": result
    }
    return response

# driver function
if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0")