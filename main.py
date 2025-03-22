from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure AWS - support for local DynamoDB for development
use_local_dynamodb = os.getenv('USE_LOCAL_DYNAMODB', 'False').lower() == 'true'

if use_local_dynamodb:
    # Connect to local DynamoDB instance
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='local',
        endpoint_url='http://localhost:8000',
        aws_access_key_id='mock',
        aws_secret_access_key='mock'
    )
    print("Using local DynamoDB instance")
else:
    # Connect to AWS DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    print("Using AWS DynamoDB")

# DynamoDB table - replace with your table name
table_name = os.getenv('DYNAMODB_TABLE', 'PromptResponses')
table = dynamodb.Table(table_name)

@app.route('/')
def index():
    # Scan the DynamoDB table for all items
    response = table.scan()
    items = response.get('Items', [])
    
    # Group items by prompt for better organization
    prompts = {}
    for item in items:
        prompt = item.get('prompt')
        if prompt not in prompts:
            prompts[prompt] = []
        prompts[prompt].append(item)
    
    # Sort each group by timestamp
    for prompt, responses in prompts.items():
        prompts[prompt] = sorted(responses, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return render_template('index.html', prompts=prompts)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        response_text = request.form.get('response')
        
        if prompt and response_text:
            # Create item with timestamp
            timestamp = datetime.now().isoformat()
            item_id = f"{prompt}_{timestamp}"
            
            # Check if there's an existing item for this prompt
            existing_item = None
            try:
                query_response = table.query(
                    IndexName='PromptIndex',
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('prompt').eq(prompt)
                )
                existing_items = query_response.get('Items', [])
                if existing_items:
                    existing_item = existing_items[0]
            except Exception as e:
                print(f"Error querying for existing prompt: {e}")
            
            if existing_item:
                # Update existing item with new response
                responses = existing_item.get('responses', [])
                responses.append({
                    'text': response_text,
                    'timestamp': timestamp
                })
                
                table.update_item(
                    Key={'id': existing_item['id']},
                    UpdateExpression="SET responses = :r",
                    ExpressionAttributeValues={':r': responses}
                )
            else:
                # Create new item
                table.put_item(
                    Item={
                        'id': item_id,
                        'prompt': prompt,
                        'responses': [{
                            'text': response_text,
                            'timestamp': timestamp
                        }],
                        'timestamp': timestamp
                    }
                )
            
            return redirect(url_for('index'))
    
    return render_template('add.html')

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True)
