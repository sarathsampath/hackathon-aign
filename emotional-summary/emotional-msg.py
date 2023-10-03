import json
import openai

openai.api_key = "---------api-key------------"  

def lambda_handler(event, context):
    message = event['message']
    chat = [{"role": "user", "content": f"Convert this text {message}  as an emotional message to the patient based on severity of disease in 100 words "}]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 engine
        messages = chat,
        max_tokens=2000,
        temperature = 0
    )
    print(completion['choices'][0]['message']['content'])
    return {
        'statusCode': 200,
        'body': {
            'message':completion['choices'][0]['message']['content']
        },
        'headers': {"Access-Control-Allow-Origin": "*"}
    }
