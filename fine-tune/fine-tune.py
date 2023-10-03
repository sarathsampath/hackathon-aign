
import openai
import time
openai.api_key = "---------api-key------------"

training_file_response = openai.File.create(
  file=open("modified_medi.jsonl", "rb"),
  purpose='fine-tune'
)

training_file_id = training_file_response['id']

# Create a fine-tuning job
while True:
    training_file_info = openai.File.retrieve(training_file_id)
    if training_file_info['status'] == 'processed':
        break
    else:
        time.sleep(10)  

# You can now monitor the status of the fine-tuning job using the fine_tuning_job object
fine_tuning_job = openai.FineTuningJob.create(
  model="gpt-3.5-turbo",
  training_file=training_file_id
)

# You can now monitor the status of the fine-tuning job using the fine_tuning_job object
print("Fine-tuning job ID:", fine_tuning_job['id'])
print(openai.FineTuningJob.retrieve(fine_tuning_job['id']))


#  https://huggingface.co/datasets/gretelai/symptom_to_diagnosis/blob/main/test.jsonl
# https://huggingface.co/datasets/BI55/MedText/viewer/default/train?row=26