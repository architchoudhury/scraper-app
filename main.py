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
        
        # Get responses list
        responses = item.get('responses', [])
        for resp in responses:
            response_item = {
                'response': resp.get('text', ''),
                'timestamp': resp.get('timestamp', '')
            }
            prompts[prompt].append(response_item)
    
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
            # Create timestamp for the new response
            timestamp = datetime.now().isoformat()
            
            try:
                # Create new response object
                new_response = {
                    'text': response_text,
                    'timestamp': timestamp
                }
                
                # Try to append to existing responses or create new item
                table.update_item(
                    Key={'prompt': prompt},
                    UpdateExpression="SET responses = list_append(if_not_exists(responses, :empty_list), :newval), last_updated = :t",
                    ExpressionAttributeValues={
                        ':empty_list': [],
                        ':newval': [new_response],
                        ':t': timestamp
                    }
                )
                print(f"Added response to prompt: {prompt}")
                
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
            
            return redirect(url_for('index'))
    
    return render_template('add.html')

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
