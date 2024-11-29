import requests

# Replace with your Hugging Face API Key
HF_API_KEY = "your_huggingface_api_key"

# Set the model URL (example: GPT-J)
model_url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-j-6B"

# Define headers with API Key for authentication
headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# Define the input prompt for the model
data = {
    "inputs": "What is the capital of France?"
}

# Make the POST request to the Hugging Face API
response = requests.post(model_url, json=data, headers=headers)

# Handle the response
if response.status_code == 200:
    result = response.json()
    print("Generated Text:", result[0]['generated_text'])
else:
    print(f"Error: {response.status_code} - {response.text}")
