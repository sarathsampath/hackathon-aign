
import mysql.connector
import json
import openai
import pinecone
import uuid
from openai.embeddings_utils import get_embedding
from flask import Flask, jsonify, request
from flask_cors import CORS
openai.api_key = "---------api-key------------"

pinecone.init(      
	api_key='-------pinecone-api-key---------',      
	environment='gcp-starter'      
)

app = Flask(__name__)
CORS(app)

@app.route('/', methods = ['POST'])
def insert():
    event = request.json
    print(event)
    userId = int(event.get('patientId',1))
    # TODO implement
    mydb = mysql.connector.connect(
        host="-----mysql-host-------",
        user="admin",
        password="-----mysql-password-----",
        database="openemr"
    )

    mycursor = mydb.cursor()
    
    mycursor.execute(f"SELECT fname, lname,dob,sex FROM patient_data where id = {userId}")
    personal_data = mycursor.fetchall()

    first_name, last_name, birth_date, gender = personal_data[0]

    # Create a dictionary with the extracted values
    personal_details = {
        'First Name': first_name,
        'Last Name': last_name,
        'Birth Date': birth_date.strftime('%Y-%m-%d'),
        'Gender': gender
    }

    # Print the resulting dictionary
    print("personal_details =", personal_details)

    mycursor.execute(f"SELECT ai_summary,ai_diagnosis FROM form_encounter where pid = {userId}")
    ai_data = mycursor.fetchall()
    ai_summary,ai_diagnosis = ai_data[0]
    ai_details = {
        'AI Summary': ai_summary,
        'AI Diagnosis': ai_diagnosis
    }
    print("AI Details =",ai_details)

    dischargeSummary = generateDischargeSumary(personal_details,ai_details,userId)
    convertHtmlValue = convertToHtml(dischargeSummary)
    return {
        'statusCode': 200,
        'body': {
            'diagnosis':dischargeSummary,
	    'htmlValue':convertHtmlValue
        }
    }

@app.route('/summarysearch', methods = ['POST'])
def search():
    print('Searching data')
    data = request.json
    summaryData = data['searchData']
    result = handle_search(summaryData,int(data.get('limit',1)))
    print(result)
    return {
        'statusCode': 200,
        'body': {
            "patientList": result
        }
    }

def generateDischargeSumary(personal_details,ai_details,patientId):
    openai.api_key = "---------api-key------------"
    discharge_summary = {
    "Personal_details":personal_details,
    "reason": ai_details['AI Summary'],
    "previous ilness":"Affected by covid 19",
    "AI_diagnosis":ai_details['AI Diagnosis'],
    "treatment":"While treatement we were able to find that he has trouble in breathing.He was the added to the ICU with ventilator and othe asq medicines.After two days he was fine",
    "Medicine":"paracetamol 50mg,DOLO 650 and aspirine"
    }    
    chat = [{"role": "user", "content": "Genrate an elaborated discharge summary"},
            {"role": "user","content":"Personal Details: Name: [Enter patient Name here],AI diagnosis:<>,Chief Complaint:<>,History of Illness:<>,Treatmeant given:<>,Medications:<Medications with reason>,Next Steps:<>"},
            {"role": "user", "content": json.dumps(discharge_summary)}]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 engine
        messages = chat,
        max_tokens=1000,
        temperature =0
        
    )
    print(completion['choices'][0]['message']['content'])
    handle_insert(patientId,completion['choices'][0]['message']['content'])
    return completion['choices'][0]['message']['content']

def handle_insert(patientId,data):
    try:
        return insert_vector_db(patientId,data)
    except Exception as error:
        print(f"Error in handle insert {error}")
        return error


def handle_search(summaryData,limit):
    try:
        return search_vector_db(summaryData, limit)
    except Exception as error:
        print(f"Error in handle search {error}")
        return error

def search_vector_db(search_text, limit=1):
    index = pinecone.Index("test-discharge-summary")
    search_emb = get_embedding(search_text)
    results = []
    query_result = index.query(vector = search_emb,top_k=limit, include_values=True, include_metadata=True,)
    for result in query_result['matches']:
        results.append(result['metadata'])
    return results

def insert_vector_db(patientId,dischargeSummary):
    index = pinecone.Index("test-discharge-summary")
    insert_emb = get_embedding(dischargeSummary)
    result = index.upsert([(str(uuid.uuid1()), insert_emb, {
                'patientId': patientId
            })])
    print(f"Insert completed {result}")
    return "Data inserted"   

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def convertToHtml(text):
    chat = [{"role": "user", "content": f"Convert the summary to html {text}"}]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 engine
        messages = chat,
        max_tokens=1000,
        temperature =0
    )
    return completion['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')


