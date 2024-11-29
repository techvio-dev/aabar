import requests

import json

# Load HF API key from JSON file
with open('apis_keys.json') as f:
    data = json.load(f)
token = data['huggingface']['api_key']
url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

def llm(query):
  parameters = {
      "max_new_tokens": 5000,
      "temperature": 0.01,
      "top_k": 50,
      "top_p": 0.95,
      "return_full_text": False
      }
  
  prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>You are a helpful and smart assistant. You accurately provide answer to the provided user query.<|eot_id|><|start_header_id|>user<|end_header_id|> Here is the query: ```{query}```.
      Provide precise and concise answer.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
  
  headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/json'
  }
  
  prompt = prompt.replace("{query}", query)
  
  payload = {
      "inputs": prompt,
      "parameters": parameters
  }
  
  response = requests.post(url, headers=headers, json=payload)
  response_text = response.json()[0]['generated_text'].strip()

  return response_text

response = llm("ما هي مدينة مراكش؟")

# write the response to a file, using arabic encoding
with open('response.txt', 'w', encoding='utf-8') as f:
    f.write(response)