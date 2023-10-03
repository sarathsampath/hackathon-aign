import json
import openai

openai.api_key = "---------api-key------------"  


def getDiagnosis(patientConversation):
    print(patientConversation)
    chat = [{"role": "system", "content": "AIGen is a medi bot."}, {"role": "user", "content": patientConversation}]
    prompt = [
    {"role": "assistant", "content": "I'm a chatbot that specializes in providing diagnosis to Doctors.Help the doctors to diagnosis the disease ,If the user's inquiry is not related to the medical industry, respond with 'Sorry, I do not know.'"},
    {"role": "assistant", "content": "I'm a chatbot that specializes in providing diagnosis to Doctors.Help the doctors to diagnosis the disease  ,If the user's inquiry is not related to the medical symptoms or disease, respond with 'Sorry, I do not know.'"},
    {"role": "assistant", "content": "I'm a chatbot that specializes in providing diagnosis to Doctors.Help the doctors to diagnosis the disease , If the user is providing some random words, respond with 'Sorry, I do not know.'"},
    ]
    messages = [{"role": item["role"], "content": item["content"]} for item in chat] + prompt

    completion = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:presidio::82wXt1nL",  # Use GPT-3.5 engine
        messages = messages,
        max_tokens=2000,
        temperature = 0
    )
    return completion

def lambda_handler(event, context):
    print(event)
    user_convo = json.dumps(event['chat'])
    print(user_convo)
    chat = [ {"role":"system","content":"AI bot to identify the conversation"},
            {"role": "user", "content": f"The below is the conversation between a doctor and patient {user_convo}"},
            {"role": "user", "content": "Identify the  patient conversation"},
            {"role": "user", "content": "Correct the errors in the sentence"},
            {"role": "user", "content": "Identify the symptoms of the patient "}
    ]
    
    completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 engine
            messages = chat,
            max_tokens=1000,
            temperature =0 
    )
    print('convo completion',completion)
    print(completion['choices'][0]['message']['content'])
    chat2 = [
            {"role": "user", "content": f"Identify the exact symptoms in array format {completion['choices'][0]['message']['content']} "}
    ]
    completion2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 engine
            messages = chat2,
            max_tokens=1000,
            temperature =0 
    )
    diagnosisData = getDiagnosis(completion['choices'][0]['message']['content'])
    print(diagnosisData['choices'][0]['message']['content'])
    return {
        'statusCode': 200,
        'body': {
            'diagnosis':diagnosisData['choices'][0]['message']['content'],
            'summary':completion['choices'][0]['message']['content'],
            'symptoms':completion2['choices'][0]['message']['content']
        }
    }
