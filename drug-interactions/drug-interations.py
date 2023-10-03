import openai
import mysql.connector
from datetime import datetime

openai.api_key = "---------api-key------------"  

def lambda_handler(event,context):
    old_medicines = getMedicineFromDB(int(event.get('patientId',1)))
    new_medicine = event.get('new_medicine','Benzodiazepines')
    alternate_medicines = []
    for medicine in old_medicines:
        chat = [
            {"role": "user", "content": f"check the drug {new_medicine} can taken along with {medicine} can cause any danger or diffuculties to the person"},
            {"role": "user", "content": f"Answer with Yes or No only.No general info"},
            #  {"role": "user", "content": f"If Yes. Suggest a alternate medicine for {old_medicines} and {new_medicine} drug combination"}
            ]
        completion = medi_chat(chat)
        print("completion",completion,medicine,new_medicine)
        if 'Yes' in completion:
            chat2 = [
                        {"role": "user", "content": f"Suggest an alternate medication for {new_medicine} in html forma"},
                        # {"role":"user","content":"Generate the  in html"}
                        ]
            medi_suggestion = medi_chat(chat2)
            # print(medi_suggestion)
 
            medi_data = { 'alternate_for':medicine,
                    'alternate_medicine':medi_suggestion,
                    'message':completion
                }
            alternate_medicines.append(medi_data)
    print(alternate_medicines)    
    return {
        'statusCode': 200,
            'body': {
                'message':alternate_medicines
            }
    }
def medi_chat(chat):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 engine
        messages = chat,
        max_tokens=2000,
        temperature = 0
    )
    return completion['choices'][0]['message']['content']

def getMedicineFromDB(patientId):
    medicines = []
    mydb = mysql.connector.connect(
    host="-----mysql-host-------",
    user="admin",
    password="-----mysql-password-----",
    database="openemr"
    )
    mycursor = mydb.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    mycursor.execute(f"SELECT title FROM lists where pid = {patientId} and enddate > {current_date}")
    personal_data = mycursor.fetchall()
    for i in personal_data:
        medicines.append(i[0])
        return medicines
    return medicines
