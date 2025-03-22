from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to AWS DynamoDB using CLI credentials
region_name = os.getenv('AWS_REGION', 'us-east-2')
session = boto3.Session(region_name=region_name)
dynamodb = session.resource('dynamodb')
print(f"Using AWS DynamoDB with default credentials")

# DynamoDB table - hardcoded name
table = dynamodb.Table('PromptResponses')

@app.route('/')
def index():
    # Scan the DynamoDB table for all items
    response = table.scan()
    items = response.get('Items', [])
    
    # Group items by prompt for better organization
    prompts = {}
    for item in items:
        prompt = item.get('prompt', '')
        if prompt not in prompts:
            prompts[prompt] = []
        prompts[prompt].append(item)
    
    # Sort each group by timestamp
    for prompt, responses in prompts.items():
        try:
            prompts[prompt] = sorted(responses, key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            # Keep original order if sorting fails
            print(f"Error sorting responses for prompt '{prompt}': {e}")
    
    return render_template('index.html', prompts=prompts)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        response_text = request.form.get('response')
        
        if prompt and response_text:
            # Create item with timestamp
            timestamp = datetime.now().isoformat()
            
            try:
                # Create new item
                item = {
                    'prompt': prompt,
                    'response': response_text,
                    'timestamp': timestamp
                }
                
                table.put_item(Item=item)
                print(f"Successfully added item for prompt: {prompt}")
            except Exception as e:
                print(f"Error adding item: {e}")
            
            return redirect(url_for('index'))
    
    return render_template('add.html')

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
